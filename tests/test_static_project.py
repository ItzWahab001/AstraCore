from pathlib import Path
import ast
ROOT=Path(__file__).parents[1]

def test_python_files_parse():
    for path in ROOT.rglob('*.py'):
        if '__pycache__' not in path.parts:
            ast.parse(path.read_text(encoding='utf-8'))

def test_no_common_placeholder_markers():
    bad=('TODO: IMPLEMENT','pass  # placeholder','YOUR_API_KEY_HERE','IMPLEMENT_ME')
    for path in ROOT.rglob('*.py'):
        text=path.read_text(encoding='utf-8')
        assert not any(marker in text for marker in bad), path
