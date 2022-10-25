#!/usr/bin/env python3

import os, sys, argparse, json


def check_json(filepath):
    ok = True
    f = open(filepath, "r")

    jsondata = json.load(f)

    for j in jsondata:
        fsize = os.path.getsize(j)
    
        if fsize > 1000000:
            if args.verbose:
                print(f"{j}: is {fsize}: NOT OK")
            ok = False
        else:
            if args.verbose:
                print(f"{j}: is {fsize}: OK")

    return ok


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Verbose mode')
        parser.add_argument('file', default='', help='Json file to check')
        args = parser.parse_args()

        if not args.file:
            sys.exit()

        if args.verbose:
            print('files:', args.file, '\n')

        checks = check_json(args.file)
        if not checks:
            if args.verbose:
                print('FAILURE')
            sys.exit(1)
        elif args.verbose:
            print('SUCCESS')

    except KeyboardInterrupt:
        sys.exit()
