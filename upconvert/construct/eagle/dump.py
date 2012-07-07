import sys

from construct import *
from fixed_length import FixedLengthRecord
from variable_length import VariableLengthRecord
from optparse import OptionParser
from eagle_struct import EAGLE_SCHEMATICS
from eagle_struct import EAGLE_FILE
from eagle_xml import print_xml
from utils import pretty_println
import codecs


SCHEMATICS_FILE = Struct("schematics",
    FixedLengthRecord("drawing"),
    MetaArray(
        lambda ctx: ctx.drawing.record_count - 1,
        FixedLengthRecord("flrecords", debug=True),
    ),
    OptionalGreedyRange(VariableLengthRecord("vlrecords")),
)

if __name__ == "__main__":

    op = OptionParser(usage="usage: %prog [options] eagle_file")
    op.add_option("-F", "--flat-dump", action="store_true", default=False,
                  help="Print flat dump of the records")
    op.add_option("-R", "--raw-dump", action="store_true", default=False,
                  help="Print raw dump of the records (no assumptions about record types)")
    op.add_option("-D", "--decoded-dump", action="store_true", default=False,
                  help="Print decoded dump (showing eagle file structure)")
    op.add_option("-X", "--eagle-xml", action="store_true", default=False,
                  help="Print eagle XML format")
    op.add_option("-l", "--line-length", type='int', default=170,
                  help="set the line length for the dump")
    op.add_option("-o", "--output-file", metavar="FILE", default='-',
                  help="Output file name, use - for standard output (default)")
    (options, args) = op.parse_args()

    if len(args) != 1:
        op.error("Missing eagle file name !")

    if options.output_file == '-':
        # TODO try to wrap the stdout in a UTF8 encoder
        out = sys.stdout
    else:
        out = codecs.open(options.output_file, "w", "UTF-8")


    if options.raw_dump:
        obj = SCHEMATICS_FILE.parse_stream(open(args[0], "rb"))
        pretty_println(out, obj, line_length=options.line_length)

    if options.decoded_dump:
        obj = EAGLE_FILE.parse_stream(open(args[0], "rb"))
        pretty_println(out, obj, line_length=options.line_length)

    if options.flat_dump:
        obj = EAGLE_SCHEMATICS.parse_stream(open(args[0], "rb"))
        pretty_println(out, obj, line_length=options.line_length)

    if options.eagle_xml:
        obj = EAGLE_FILE.parse_stream(open(args[0], "rb"))
        print_xml(out, obj)

