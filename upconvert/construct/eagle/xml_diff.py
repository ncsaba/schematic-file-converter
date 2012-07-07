
from optparse import OptionParser
from eagle_struct import EAGLE_FILE
from eagle_xml import print_xml
import codecs
import tempfile
import os
import os.path as path
import re
import subprocess

if __name__ == "__main__":

    op = OptionParser(usage="usage: %prog [options] eagle_file")
    op.add_option("--eagle-path", metavar="DIR", default='.',
                  help="Eagle deployment path (current directory is default)")
    op.add_option("-X", "--skip-xml", action="store_true", default=False,
                  help="Skip regenerating XML format")
    op.add_option("-R", "--skip-eagle", action="store_true", default=False,
                  help="Skip regenerating reference eagle format")
    (options, args) = op.parse_args()

    if len(args) != 1:
        op.error("Missing eagle file name !")

    tempdir = tempfile.gettempdir()
    test_dir = path.join(tempdir, 'eagle_xml_diff')
    print "Creating test dir {0}".format(test_dir)
    try:
        os.makedirs(test_dir)
    except:
        pass # ignore errors
    eagle_file = path.abspath(args[0])
    file_name, ext = path.splitext(path.basename(eagle_file))

    xml_file_name = re.sub('\s+', '_', path.join(test_dir, file_name + '_new_format.sch'))
    if path.isfile(xml_file_name) and not options.skip_eagle:
        os.remove(xml_file_name)
    if not path.isfile(xml_file_name):
        print "Convert file using eagle: {0} -> {1}".format(eagle_file, xml_file_name)
        os.environ['LD_LIBRARY_PATH'] = path.join(options.eagle_path,'libeagle')
        subprocess.call([
            path.join(options.eagle_path, 'bin', 'eagle'),
            "-C",
            "WRITE {0}; QUIT".format(xml_file_name),
            eagle_file,
        ])

    output_file_name = re.sub('\s+', '_', path.join(test_dir, file_name + '.xml'))
    if not options.skip_xml or not path.isfile(output_file_name):
        print "Parsing file: {0}".format(eagle_file)
        obj = EAGLE_FILE.parse_stream(open(eagle_file, "rb"))
        print "Dumping xml file: {0}".format(output_file_name)
        out = codecs.open(output_file_name, "w", "UTF-8")
        print_xml(out, obj)
        out.close()

    print "Run diff: {0} <-> {1}".format(eagle_file, output_file_name)
    subprocess.call([
        path.join('tkdiff'),
        xml_file_name,
        output_file_name,
    ])
