#!/usr/bin/env python3

import os, sys, argparse, json


def check_files(filepath):

    fsize = os.path.getsize(filepath)
    ok = True

    if fsize > 1000000:
        if args.verbose:
            print(f"{filepath}: is {fsize}: NOT OK")
        ok = False
    else:
        if args.verbose:
            print(f"{filepath}: is {fsize}: OK")

    return ok


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Verbose mode')
        parser.add_argument('files', nargs='*', default=[], help='Files to check')
        args = parser.parse_args()

        if not args.files:
            sys.exit()

        if args.verbose:
            print('files:', args.files, '\n')

        checks = [check_files(file) for file in args.files]
        if False in checks:
            if args.verbose:
                print('FAILURE')
            sys.exit(1)

        elif args.verbose:
            print('SUCCESS')

    except KeyboardInterrupt:
        sys.exit()
