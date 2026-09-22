"""Bounded original-archive replay plus independent raster-window calculation.

The pre-existing S3 pilot (zero burned records) was inspected before this run;
this is selected-case computational validation, not a blind accuracy holdout.
"""
import argparse
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile
import numpy as np
import pandas as pd
import rasterio
from rasterio.enums import MaskFlags
from rasterio.windows import Window
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from wildfire_exposure.runner import run_country_pipeline

PINS={
 'GHS_OBAT_CSV_LUX_E2020_R2024A_V1_0.zip':'1034976556805f37961794794fd388769315754f7ff03b565a8a0c0f95a72edd',
 'N50E005.tif':'ba5402ac25948b185c64efc3e65df1f44078ccef3705ba2c8147e2f7ffc83091',
 'N55E005.tif':'ce82106ca8122352147abb261e879a95e0f941f01fb9f9d3fdc1ff9b4ce36f66',
}

def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 return h.hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--inputs',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
 for name,sha in PINS.items():
  if digest(args.inputs/name)!=sha:raise ValueError(f'Input hash differs: {name}')
 args.output.mkdir(parents=True,exist_ok=True)
 archive=args.inputs/next(iter(PINS));members=[]
 with zipfile.ZipFile(archive) as z:
  csv_members=[m for m in z.infolist() if m.filename.endswith('.csv')]
  if len(csv_members)!=1:raise ValueError('Frozen LUX archive must have one CSV member')
  member=csv_members[0]; csv=args.inputs/Path(member.filename).name
  with z.open(member) as source,csv.open('wb') as target:target.write(source.read())
  members=[{'name':m.filename,'bytes':m.file_size,'crc32':m.CRC} for m in z.infolist()]
 frame=pd.read_csv(csv,dtype={'id':str})
 if len(frame)!=226721 or frame.id.isna().any() or frame.id.nunique()!=len(frame):raise ValueError('Unexpected record/identity count')
 lon,lat=frame.lon.to_numpy(),frame.lat.to_numpy()
 if not (np.isfinite(lon).all() and np.isfinite(lat).all()):raise ValueError('Invalid coordinates')
 tiles=[args.inputs/n for n in PINS if n.endswith('.tif')]
 output=run_country_pipeline('LUX',csv,tiles,out_dir=args.output,run_sensitivity=False).iloc[0]
 # Independent calculation: crop raw windows and index NumPy arrays directly.
 # Does not call production sampling/classification functions or rasterio.sample.
 values=np.full(len(frame),np.nan);extent=np.zeros(len(frame),bool);metadata=[]
 for tile in tiles:
  with rasterio.open(tile) as src:
   t=src.transform
   if src.crs.to_epsg()!=4326 or t.b or t.d or t.a<=0 or t.e>=0:raise ValueError('Unexpected frozen raster grid')
   cols=np.floor((lon-t.c)/t.a).astype(int);rows=np.floor((lat-t.f)/t.e).astype(int)
   inside=(cols>=0)&(cols<src.width)&(rows>=0)&(rows<src.height);extent|=inside
   indices=np.flatnonzero(inside)
   metadata.append({'file':tile.name,'crs':str(src.crs),'transform':list(t)[:6],'nodata':src.nodata,'mask_flags':[str(f) for f in src.mask_flag_enums[0]],'point_count':len(indices)})
   if not len(indices):continue
   c0,c1=cols[inside].min(),cols[inside].max();r0,r1=rows[inside].min(),rows[inside].max();window=Window(int(c0),int(r0),int(c1-c0+1),int(r1-r0+1))
   arr=src.read(1,window=window);sampled=arr[rows[inside]-r0,cols[inside]-c0]
   known=np.isin(sampled,[0,1])
   flags=set(src.mask_flag_enums[0])
   if flags!={MaskFlags.nodata} or src.nodata!=0:
    mask=src.read_masks(1,window=window);known&=mask[rows[inside]-r0,cols[inside]-c0]>0
   previous=values[indices]
   if np.any(known&np.isfinite(previous)&(previous!=sampled)):raise ValueError('Overlapping contradictory cells')
   values[indices[known]]=sampled[known]
 independent={'total_buildings':len(frame),'valid_coordinate_buildings':len(frame),'tile_covered_buildings':int(extent.sum()),'valid_gabam_pixel_buildings':int(np.isfinite(values).sum()),'exposed_buildings':int((values==1).sum())}
 comparisons={k:{'production':int(output[k]),'independent':v,'passed':int(output[k])==v} for k,v in independent.items()}
 report={'indicator_id':'6.1.1','country':'LUX','analysis_year':2024,'passed':all(x['passed'] for x in comparisons.values()),
  'validation_scope':'selected original-archive computational replay; not independent fire accuracy or a global error sample',
  'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
  'input_sha256':PINS,'archive_members':members,'unique_ids':int(frame.id.nunique()),'rasters':metadata,'comparisons':comparisons,
  'source_lineage':{'building_archive':'SHA256 matches independently acquired official JRC LUX archive in indicator6.1.5 release bc8f8ded588bee3aae2b633fd1da5701b3f35bdc',
   'hazard_tiles':'Existing private S3 mirror; exact tile bytes pinned, parent Zenodo ZIP linkage not independently re-established'},
  'limitations':['One selected country with pre-inspected zero-burn pilot; does not validate positive fire detection or transfer.',
   'Binary zero remains source-coded background, not independently verified observation availability.',
   'Source ID uniqueness and full archive-member coverage do not establish complete physical national stock.']}
 (args.output/'independent_replay.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
 print(json.dumps({'passed':report['passed'],'comparisons':comparisons}))
 if not report['passed']:raise SystemExit(1)

if __name__=='__main__':main()
