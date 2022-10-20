#!/usr/bin/env python3

import os, sys, argparse


def check_files(login):
    sounds_path = os.environ['PWD'] + '/mp3/' + login
    for currentpath, folders, files in os.walk(sounds_path):
        ok = True
        for file in files:
            file_path = os.path.join(currentpath, file)
            fsize = os.path.getsize(file_path)

            if fsize > 1000000:
                if args.verbose:
                    print(f"{file}: is {fsize}: NOT OK")
                ok = False
            else:
                if args.verbose:
                    print(f"{file}: is {fsize}: OK")

    return ok


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Verbose mode')
        parser.add_argument('logins', nargs='*', default=[], help='Logins to check')
        args = parser.parse_args()

        if not args.logins:
            sys.exit()

        if args.verbose:
            print('Logins:', args.logins, '\n')

        checks = [check_files(login) for login in args.logins]
        if False in checks:
            sys.exit(1)
    except KeyboardInterrupt:
        sys.exit()
