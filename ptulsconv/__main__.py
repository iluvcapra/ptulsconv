from ptulsconv.commands import convert
from optparse import OptionParser
import sys

parser = OptionParser()
parser.usage = "ptulsconv TEXT_EXPORT.txt"
parser.add_option('-i', dest='in_time', help="Don't output events occurring before this timecode, and offset"
                                             " all events relative to this timecode.", metavar='TC')
parser.add_option('-o', dest='out_time', help="Don't output events occurring after this timecode.", metavar='TC')
parser.add_option('-P','--progress', default=False, action='store_true', dest='show_progress', help='Show progress bar.')
parser.add_option('-m','--include-muted', default=False, action='store_true', dest='include_muted', help='Read muted clips.')

if __name__ == "__main__":
    (options, args) = parser.parse_args(sys.argv)
    if len(args) < 2:
        print("Error: No input file",file=sys.stderr)
        parser.print_help(sys.stderr)
        exit(-1)

    convert(input_file=args[1], start=options.in_time, end=options.out_time, include_muted=options.include_muted,
            progress=options.show_progress, output=sys.stdout)
