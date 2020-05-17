from ptulsconv.commands import convert, dump_field_map, dump_xform_options
from ptulsconv import __name__, __version__, __author__
from optparse import OptionParser, OptionGroup
from .reporting import print_status_style, print_banner_style, print_section_header_style, print_fatal_error
import datetime
import sys

import traceback


def main():
    parser = OptionParser()
    parser.usage = "ptulsconv TEXT_EXPORT.txt"

    filter_opts = OptionGroup(title='Filtering Options', parser=parser)

    filter_opts.add_option('-i', dest='in_time', help="Don't output events occurring before this timecode.",
                           metavar='TC')
    filter_opts.add_option('-o', dest='out_time', help="Don't output events occurring after this timecode.",
                           metavar='TC')
    # parser.add_option('-P', '--progress', default=False, action='store_true', dest='show_progress',
    #                   help='Show progress bar.')
    filter_opts.add_option('-m', '--include-muted', default=False, action='store_true', dest='include_muted',
                           help='Include muted clips.')

    filter_opts.add_option('-R', '--reel', dest='select_reel', help="Output only events in reel N, and recalculate "
                                                                    " start times relative to that reel's start time.",
                           default=None, metavar='N')

    parser.add_option_group(filter_opts)

    output_opts = OptionGroup(title="Output Options", parser=parser)
    output_opts.add_option('--json', default=False, action='store_true', dest='write_json',
                           help='Output a JSON document instead of XML. If this option is enabled, --xform will have '
                                'no effect.')

    output_opts.add_option('--xform', dest='xslt', help="Convert with built-is XSLT transform.",
                           default=None, metavar='NAME')

    output_opts.add_option('--show-available-tags', dest='show_tags',
                           action='store_true',
                           default=False, help='Display tag mappings for the FMP XML output style and exit.')

    output_opts.add_option('--show-available-transforms', dest='show_transforms',
                           action='store_true',
                           default=False, help='Display available built-in XSLT transforms.')

    parser.add_option_group(output_opts)

    (options, args) = parser.parse_args(sys.argv)

    print_banner_style("%s %s (c) 2020 %s. All rights reserved." % (__name__, __version__, __author__))

    print_section_header_style("Startup")
    print_status_style("This run started %s" % (datetime.datetime.now().isoformat()))

    if options.show_tags:
        dump_field_map('ADR')
        sys.exit(0)

    if options.show_transforms:
        dump_xform_options()
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
        output_format = 'fmpxml'
        if options.write_json:
            output_format = 'json'

        convert(input_file=args[1], output_format=output_format, start=options.in_time, end=options.out_time,
                include_muted=options.include_muted, xsl=options.xslt, select_reel=options.select_reel,
                progress=False, output=sys.stdout, log_output=sys.stderr)
    except FileNotFoundError as e:
        print_fatal_error("Error trying to read input file")
        raise e
    except Exception as e:
        print_fatal_error("Error trying to convert file")
        print("\033[31m" + e.__repr__() + "\033[0m", file=sys.stderr)
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
