"""Small, dependency-free release primitives; production generators stay frozen."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha_file(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode()).hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.writing')
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n',
                         encoding='utf-8', newline='\n')
    os.replace(temporary, path)


def safe_relative(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value or '\x00' in value:
        raise ValueError('unsafe relative release path')
    parsed = PurePosixPath(value)
    if parsed.is_absolute() or any(part in ('', '.', '..') for part in value.split('/')):
        raise ValueError('unsafe relative release path')
    return parsed


def inside(root, relative):
    root = Path(root).resolve()
    path = root.joinpath(*safe_relative(relative).parts)
    resolved = path.resolve()
    if root not in resolved.parents or path.is_symlink():
        raise ValueError('release path escaped root or is a symbolic link')
    return resolved


def ignored_path(path):
    path = Path(path).resolve()
    if ROOT not in path.parents or path.relative_to(ROOT).parts[0] not in ('output', 'data'):
        raise ValueError('release workspace must be under ignored output/data')
    return path


def inventory(root):
    root = Path(root).resolve()
    result = {}
    folded = set()
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('symbolic links are not release artifacts')
        if path.is_file():
            name = path.relative_to(root).as_posix()
            safe_relative(name)
            if name.casefold() in folded:
                raise ValueError('case-colliding release paths')
            folded.add(name.casefold())
            result[name] = {'sha256': sha_file(path), 'bytes': path.stat().st_size}
    return result
