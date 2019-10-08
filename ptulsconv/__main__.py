from ptulsconv.commands import convert
from optparse import OptionParser
import sys

parser = OptionParser()
parser.add_option('-t','--timecode', dest='convert_times', default=False, action='store_true',
                  help="Include timecode converted to seconds in output.")
parser.add_option('-z','--offset', dest='apply_start_offset', default=False, action='store_true',
                  help='Apply session start offset to converted start and finish timecodes on '
                       'clips and markers. Implies -t.')
parser.usage = "ptulsconv [-tz] TEXT_EXPORT.txt"

if __name__ == "__main__":
    (options, args) = parser.parse_args(sys.argv)
    if len(args) < 2:
        print("Error: No input file",file=sys.stderr)
        parser.print_help(sys.stderr)
        exit(-1)

    convert(input_file=args[1],
            convert_times=(options.convert_times or options.apply_start_offset),
            apply_session_start=options.apply_start_offset,
            output=sys.stdout)
