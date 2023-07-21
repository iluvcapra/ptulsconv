from optparse import OptionParser, OptionGroup
import datetime
import sys

from ptulsconv import __name__, __copyright__
from ptulsconv.commands import convert
from ptulsconv.reporting import print_status_style, \
    print_banner_style, print_section_header_style, \
    print_fatal_error


def dump_field_map(output=sys.stdout):
    from ptulsconv.docparser.tag_mapping import TagMapping
    from ptulsconv.docparser.adr_entity import ADRLine, GenericEvent

    TagMapping.print_rules(GenericEvent, output=output)
    TagMapping.print_rules(ADRLine, output=output)


def dump_formats():
    print_section_header_style("`raw` format:")
    sys.stderr.write("A JSON document of the parsed Pro Tools export.\n")
    print_section_header_style("`tagged` Format:")
    sys.stderr.write(
        "A JSON document containing one record for each clip, with\n"
        "all tags parsed and all tagging rules applied. \n")
    print_section_header_style("`doc` format:")
    sys.stderr.write("Creates a directory with folders for different types\n"
                     "of ADR reports.\n\n")


def main():
    """Entry point for the command-line invocation"""
    parser = OptionParser()
    parser.usage = "ptulsconv [options] [TEXT_EXPORT.txt]"

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
                            help='Suppress warnings for common '
                            'errors (missing code numbers etc.)')

    parser.add_option_group(warn_options)

    informational_options = OptionGroup(title="Informational Options",
                                        parser=parser,
                                        description='Print useful '
                                        'information '
                                        'and exit without processing '
                                        'input files.')

    informational_options.add_option(
        '--show-formats',
        dest='show_formats',
        action='store_true',
        default=False,
        help='Display helpful information about the available '
        'output formats.')

    informational_options.add_option(
        '--show-available-tags',
        dest='show_tags',
        action='store_true',
        default=False,
        help='Display tag mappings for the FMP XML output style '
        'and exit.')

    parser.add_option_group(informational_options)

    print_banner_style(__copyright__)

    (options, args) = parser.parse_args(sys.argv)

    print_section_header_style("Startup")
    print_status_style("This run started %s" %
                       (datetime.datetime.now().isoformat()))

    if options.show_tags:
        dump_field_map()
        sys.exit(0)

    elif options.show_formats:
        dump_formats()
        sys.exit(0)
    try:
        major_mode = options.output_format

        if len(args) < 2:
            print_status_style(
                "No input file provided, will connect to Pro Tools "
                "with PTSL...")
            convert(major_mode=major_mode,
                    warnings=options.warnings)
        else:
            convert(input_file=args[1],
                    major_mode=major_mode,
                    warnings=options.warnings)

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
