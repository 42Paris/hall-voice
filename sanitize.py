#!/usr/bin/env python3

import os, argparse, tempfile, sox


def sanitize_file(filename):
    normalized_name = f"{filename}_normalized.mp3"

    tfm = sox.Transformer()
    tfm.set_globals(verbosity=1)
    tfm.set_input_format(file_type='mp3')
    tfm.set_output_format(file_type='mp3')

    if args.verbose:
        print(filename)

    try:
        tfm.gain(gain_db=args.db, normalize=True)
        tfm.trim(start_time=0, end_time=args.length)
        with tempfile.NamedTemporaryFile() as tmpfile:
            tmpname = f"{tmpfile.name}.mp3"
            tfm.build(input_filepath=filename, output_filepath=tmpname)
            os.rename(tmpname, filename)
    except Exception as e:
        if args.verbose is True:
            print(e)
        error = f"File `{filename}` seems invalid."
        if args.remove is True:
            error += "Removing."
            os.remove(filename)
        print(error, end='\n\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Verbose mode')
    parser.add_argument('-r', '--remove',  default=False, action='store_true', help='Remove invalid files')
    parser.add_argument('-d', '--db',      type=float, default=-13.0, help='dB level to normalize (default: -13.0)')
    parser.add_argument('-l', '--length',  type=float, default=10.0, help='Length/duration in seconds (default: 10.0)')
    parser.add_argument('path', nargs='*', help='Path to file or directory to sanitize')
    args = parser.parse_args()

    if args.verbose:
        print('Path:', args.path)
        print('dB level:', args.db)
        print('Length:', args.length)
        print('Remove invalid files:', args.remove, '\n')

    for path in args.path:
        if os.path.isfile(path):
            sanitize_file(path)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for filename in files:
                    sanitize_file(os.path.join(root, filename))
        else:
            print(f"File {path} does not exist.")

