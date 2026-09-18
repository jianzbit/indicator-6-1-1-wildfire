from pathlib import Path

def test_repository_structure():
    root = Path(__file__).parents[1]
    assert (root / "src").is_dir()
    assert (root / "README.md").is_file()
    assert (root / "requirements.txt").is_file()
