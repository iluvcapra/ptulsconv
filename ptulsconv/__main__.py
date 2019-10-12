from ptulsconv.commands import convert, dump_field_map
from ptulsconv import __name__, __version__, __author__
from optparse import OptionParser, OptionGroup
from .reporting import print_status_style, print_banner_style, print_section_header_style, print_fatal_error
import datetime
import sys

def main():
    parser = OptionParser()
    parser.usage = "ptulsconv TEXT_EXPORT.txt"

    parser.add_option('-i', dest='in_time', help="Don't output events occurring before this timecode, and offset"
                                                 " all events relative to this timecode.", metavar='TC')
    parser.add_option('-o', dest='out_time', help="Don't output events occurring after this timecode.", metavar='TC')
    # parser.add_option('-P', '--progress', default=False, action='store_true', dest='show_progress',
    #                   help='Show progress bar.')
    parser.add_option('-m', '--include-muted', default=False, action='store_true', dest='include_muted',
                      help='Read muted clips.')

    parser.add_option('--show-available-tags', dest='show_tags',
                      action='store_true',
                      default=False, help='Display tag mappings for the FMP XML output style and exit.')

    (options, args) = parser.parse_args(sys.argv)

    print_banner_style("%s %s (c) 2019 %s. All rights reserved." % (__name__, __version__, __author__))

    print_section_header_style("Startup")
    print_status_style("This run started %s" % (datetime.datetime.now().isoformat() ) )

    if options.show_tags:
        dump_field_map('ADR')
        sys.exit(0)

    if len(args) < 2:
        print_fatal_error("Error: No input file")
        parser.print_help(sys.stderr)
        sys.exit(22)

    print_status_style("Input file is %s" % (args[1]))
    if options.in_time:
        print_status_style("Start at time %s" % (options.in_time))
    else:
        print_status_style("No start time given.")

    if options.out_time:
        print_status_style("End at time %s." % (options.out_time))
    else:
        print_status_style("No end time given.")

    if options.include_muted:
        print_status_style("Muted regions are included.")
    else:
        print_status_style("Muted regions are ignored.")

    try:
        convert(input_file=args[1], start=options.in_time, end=options.out_time,
                include_muted=options.include_muted,
                progress=False, output=sys.stdout, log_output=sys.stderr)
    except FileNotFoundError as e:
        print_fatal_error("Error trying to read input file")
        raise e
    except Exception as e:
        print_fatal_error("Error trying to convert file")
        print("\033[31m" + e.__repr__() + "\033[0m", file=sys.stderr)


if __name__ == "__main__":
    main()
