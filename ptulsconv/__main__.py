from optparse import OptionParser, OptionGroup
import datetime
import sys

from ptulsconv import __name__, __version__, __author__
from ptulsconv.commands import convert
from ptulsconv.reporting import print_status_style, print_banner_style, print_section_header_style, print_fatal_error


# TODO: Support Top-level modes

# Modes we want:
#  - "raw" : Output the parsed text export document with no further processing, as json
#  - "tagged"? : Output the parsed result of the TagCompiler
#  - "doc" : Generate a full panoply of PDF reports contextually based on tagging


def dump_field_map(output=sys.stdout):
    from ptulsconv.docparser.tag_mapping import TagMapping
    from ptulsconv.docparser.adr_entity import ADRLine

    TagMapping.print_rules(ADRLine, output=output)


def main():
    """Entry point for the command-line invocation"""
    parser = OptionParser()
    parser.usage = "ptulsconv [options] TEXT_EXPORT.txt"

    parser.add_option('-f', '--format',
                      dest='output_format',
                      metavar='FMT',
                      choices=['raw', 'tagged', 'doc'],
                      default='doc',
                      help='Set output format, `raw`, `tagged`, `doc`.')

    warn_options = OptionGroup(title="Warning and Validation Options",
                               parser=parser)

    warn_options.add_option('-W', action='store_false',
                            dest='warnings',
                            default=True,
                            help='Suppress warnings for common errors (missing code numbers etc.)')

    parser.add_option_group(warn_options)

    informational_options = OptionGroup(title="Informational Options",
                                        parser=parser,
                                        description='Print useful information and exit without processing '
                                                    'input files.')

    informational_options.add_option('--show-available-tags',
                                     dest='show_tags',
                                     action='store_true',
                                     default=False,
                                     help='Display tag mappings for the FMP XML '
                                          'output style and exit.')

    parser.add_option_group(informational_options)

    (options, args) = parser.parse_args(sys.argv)

    print_banner_style("%s %s (c) 2021 %s. All rights reserved." % (__name__, __version__, __author__))

    print_section_header_style("Startup")
    print_status_style("This run started %s" % (datetime.datetime.now().isoformat()))

    if options.show_tags:
        dump_field_map()
        sys.exit(0)

    if len(args) < 2:
        print_fatal_error("Error: No input file")
        parser.print_help(sys.stderr)
        sys.exit(22)

    try:
        major_mode = options.output_format
        convert(input_file=args[1], major_mode=major_mode, warnings=options.warnings)

    except FileNotFoundError as e:
        print_fatal_error("Error trying to read input file")
        raise e

    except Exception as e:
        import traceback
        print_fatal_error("Error trying to convert file")
        print("\033[31m" + e.__repr__() + "\033[0m", file=sys.stderr)
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
