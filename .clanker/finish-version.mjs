import { execFileSync } from "node:child_process";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { extname, join } from "node:path";

const statePath = ".clanker/state.json";
const state = JSON.parse(readFileSync(statePath, "utf8"));
const completedVersion = state.currentVersion;
const pr = Number(process.env.PR_NUMBER || 0);
if (state.completedVersions.some((entry) => entry.pr === pr && pr !== 0)) {
  console.log(`PR ${pr} was already recorded.`);
  process.exit(0);
}

const event = {
  version: completedVersion,
  pr,
  sha: process.env.MERGE_SHA || execFileSync("git", ["rev-parse", "HEAD"], { encoding: "utf8" }).trim(),
  mergedAt: process.env.MERGED_AT || new Date().toISOString(),
};
state.completedVersions.push(event);
state.currentVersion = nextVersion(completedVersion);
state.coverage = detectCoverage();
state.lines = countLines();
state.lastMergedAt = event.mergedAt;
writeFileSync(statePath, `${JSON.stringify(state, null, 2)}\n`);

if (process.env.GITHUB_OUTPUT) {
  writeFileSync(process.env.GITHUB_OUTPUT, `completed_version=${completedVersion}\nnext_version=${state.currentVersion}\n`, { flag: "a" });
}
console.log(`Completed v${completedVersion}; next lap is v${state.currentVersion}.`);

function nextVersion(version) {
  const match = String(version).match(/^(\d+)\.(\d+)(?:\.(\d+))?$/);
  if (!match) throw new Error(`Invalid version: ${version}`);
  return `${Number(match[1])}.${Number(match[2]) + 1}`;
}

function detectCoverage() {
  if (existsSync("coverage/coverage-summary.json")) {
    return clamp(JSON.parse(readFileSync("coverage/coverage-summary.json", "utf8")).total?.lines?.pct);
  }
  for (const path of ["coverage.xml", "coverage/coverage.xml"]) {
    if (!existsSync(path)) continue;
    const match = readFileSync(path, "utf8").match(/line-rate=["']([0-9.]+)["']/);
    if (match) return clamp(Number(match[1]) * 100);
  }
  return 0;
}

function countLines() {
  const extensions = new Set([".c",".cc",".cpp",".css",".go",".h",".hpp",".html",".java",".js",".jsx",".kt",".m",".mjs",".php",".py",".r",".rb",".rs",".scala",".sh",".sql",".swift",".ts",".tsx",".vue"]);
  const excluded = /(^|\/)(\.clanker|dist|build|coverage|node_modules|vendor|\.venv|venv)(\/|$)|\.(min\.js|lock)$/i;
  return execFileSync("git", ["ls-files", "-z"])
    .toString().split("\0").filter(Boolean)
    .filter((file) => extensions.has(extname(file).toLowerCase()) && !excluded.test(file))
    .reduce((total, file) => {
      const buffer = readFileSync(join(process.cwd(), file));
      if (!buffer.length || buffer.includes(0)) return total;
      return total + 1 + [...buffer].filter((byte) => byte === 10).length;
    }, 0);
}

function clamp(value) {
  const number = Number(value);
  return Number.isFinite(number) ? Math.max(0, Math.min(100, number)) : 0;
}
