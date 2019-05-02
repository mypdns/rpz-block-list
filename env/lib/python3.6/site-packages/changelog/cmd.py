import re
import os
import tempfile
import shutil
import argparse
import sys


def release_notes_into_changelog_file(target_filename, version, release_date):
    output = tempfile.NamedTemporaryFile(delete=False)
    with open(target_filename) as handle:
        for line in handle:
            m = re.match(r".*:version: %s" % version, line)
            if m:
                output.write(line)
                output.write("    :released: %s\n" % release_date)
                continue

            m = re.match(r".*:include_notes_from: (.+)", line)
            if m:
                notes_dir = os.path.join(
                    os.path.dirname(target_filename),
                    m.group(1)
                )
                for fname in os.listdir(notes_dir):
                    if not fname.endswith(".rst"):
                        continue
                    fname_path = os.path.join(notes_dir, fname)
                    output.write("\n")
                    with open(fname_path) as inner:
                        for inner_line in inner:
                            output.write(("    " + inner_line).rstrip() + "\n")
                    os.system("git rm %s" % fname_path)
            else:
                output.write(line)
    output.close()
    shutil.move(output.name, target_filename)


def main(argv=None):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    subparser = subparsers.add_parser(
        "release-notes",
        help="Merge notes files into changelog and git rm"
    )
    subparser.add_argument("filename", help="target changelog filename")
    subparser.add_argument("version",
                           help="version string as it appears in changelog")
    subparser.add_argument("date", help="full text of datestamp to insert")
    subparser.set_defaults(
        cmd=(release_notes_into_changelog_file,
             ["filename", "version", "date"]))

    options = parser.parse_args(argv)
    fn, argnames = options.cmd
    fn(*[getattr(options, name) for name in argnames])

if __name__ == '__main__':
    main(sys.argv)
