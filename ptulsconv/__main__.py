from ptulsconv.commands import convert
import ptulsconv.broadcast_timecode
from optparse import OptionParser
import sys

parser = OptionParser()
parser.usage = "ptulsconv TEXT_EXPORT.txt"
parser.add_option('-i', dest='in_time', help='Set in time to grab a subsequence of events. '
                                             'Give value as a timecode in current session\'s rate.')
parser.add_option('-o', dest='out_time', help='Set out time to grab a subsequence of events.')

if __name__ == "__main__":
    (options, args) = parser.parse_args(sys.argv)
    if len(args) < 2:
        print("Error: No input file",file=sys.stderr)
        parser.print_help(sys.stderr)
        exit(-1)

    convert(input_file=args[1], start=options.in_time, end=options.out_time, output=sys.stdout)
