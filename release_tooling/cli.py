"""Explicit verify, publication, acceptance and retirement commands."""
import argparse
import json
from pathlib import Path

from .common import ignored_path, read, save
from .package import publish, verify_healthcare_release
from .registry import record_acceptance, retire, state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('verify', 'state', 'accept', 'retire'):
        p = commands.add_parser(name)
        p.add_argument('--package', type=Path, required=True)
        p.add_argument('--descriptor-sha256', required=True)
        if name != 'verify':
            p.add_argument('--registry', type=Path, required=True)
        if name == 'accept':
            p.add_argument('--approval', type=Path, required=True)
        if name == 'retire':
            p.add_argument('--reason', required=True)
            p.add_argument('--replacement')
    p = commands.add_parser('publish')
    p.add_argument('--staging', type=Path, required=True)
    p.add_argument('--destination', type=Path, required=True)
    p.add_argument('--descriptor-sha256', required=True)
    args = parser.parse_args()
    if args.command == 'publish':
        result = publish(ignored_path(args.staging), ignored_path(args.destination), args.descriptor_sha256)
    elif args.command == 'verify':
        result = verify_healthcare_release(args.package, args.descriptor_sha256)
    elif args.command == 'state':
        result = state(args.package, args.registry, args.descriptor_sha256)
    elif args.command == 'accept':
        result = record_acceptance(args.package, ignored_path(args.registry), args.descriptor_sha256, read(args.approval))
    else:
        result = retire(args.package, ignored_path(args.registry), args.descriptor_sha256, args.reason, args.replacement)
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
