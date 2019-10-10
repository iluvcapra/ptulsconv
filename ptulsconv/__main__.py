from ptulsconv.commands import convert, dump_field_map
from optparse import OptionParser
import sys


def main():
    parser = OptionParser()
    parser.usage = "ptulsconv TEXT_EXPORT.txt"
    parser.add_option('-i', dest='in_time', help="Don't output events occurring before this timecode, and offset"
                                                 " all events relative to this timecode.", metavar='TC')
    parser.add_option('-o', dest='out_time', help="Don't output events occurring after this timecode.", metavar='TC')
    parser.add_option('-P', '--progress', default=False, action='store_true', dest='show_progress',
                      help='Show progress bar.')
    parser.add_option('-m', '--include-muted', default=False, action='store_true', dest='include_muted',
                      help='Read muted clips.')

    parser.add_option('--show-tags', dest='show_tags',
                      action='store_true',
                      default=False, help='Display tag mappings for the FMP XML output style and exit.')

    (options, args) = parser.parse_args(sys.argv)

    if options.show_tags:
        dump_field_map('ADR')
        sys.exit(0)

    if len(args) < 2:
        print("Error: No input file", file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(22)

    convert(input_file=args[1], start=options.in_time, end=options.out_time, include_muted=options.include_muted,
            progress=options.show_progress, output=sys.stdout)


if __name__ == "__main__":
    main()
