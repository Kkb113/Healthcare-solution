"""Run release_tooling.offline_check where the producer commit already contains the release tools and docs.

Before any copy into an existing checkout directory, every file the check would
copy must be byte-identical to the committed checkout file. The check is otherwise unchanged.
"""
import hashlib, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
import release_tooling.offline_check as oc
original = shutil.copytree
compared = []
def verified_copytree(src, dst, *args, **kwargs):
    src, dst = Path(src), Path(dst)
    if dst.exists():
        for f in src.rglob('*'):
            if f.is_file():
                target = dst / f.relative_to(src)
                if f.name.endswith('.pyc') or '__pycache__' in f.parts:
                    continue
                if not target.exists() or hashlib.sha256(f.read_bytes()).digest() != hashlib.sha256(target.read_bytes()).digest():
                    raise ValueError('distributed file differs from the committed producer checkout: ' + str(target))
                compared.append(str(target))
        return original(src, dst, *args, dirs_exist_ok=True, **kwargs)
    return original(src, dst, *args, **kwargs)
oc.shutil.copytree = verified_copytree
result = oc.check(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3])
print({'status': result['status'], 'identical_files_verified_before_copy': len(compared), 'distributed_tool_tests': result['distributed_tool_tests']})
