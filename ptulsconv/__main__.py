from ptulsconv.commands import convert
from optparse import OptionParser
import sys

parser = OptionParser()
parser.add_option('-t','--timecode', dest='convert_times', default=False, action='store_true',
                  help="Include timecode converted to seconds in output.")
parser.usage = "ptulsconv [-tz] TEXT_EXPORT.txt"

if __name__ == "__main__":
    (options, args) = parser.parse_args(sys.argv)
    if len(args) < 2:
        print("Error: No input file",file=sys.stderr)
        parser.print_help(sys.stderr)
        exit(-1)

    convert(input_file=args[1],
            convert_times=options.convert_times, output=sys.stdout)
