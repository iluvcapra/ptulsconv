import unittest

import tempfile

import os.path
import os
import glob

from ptulsconv import commands

class TestPDFExport(unittest.TestCase):
    def test_report_generation(self):
        """
        Setp through every text file in export_cases and make sure it can 
        be converted into PDF docs without throwing an error
        """
        files = [os.path.dirname(__file__) + "/../export_cases/Robin Hood Spotting.txt"] 
        #files.append(os.path.dirname(__file__) + "/../export_cases/Robin Hood Spotting2.txt")
        for path in files:
            tempdir = tempfile.TemporaryDirectory()
            os.chdir(tempdir.name)
            try:
                commands.convert(input_file=path, major_mode='doc')
            except:
                assert False, "Error processing file %s" % path
            finally:
                tempdir.cleanup()





if __name__ == '__main__':
    unittest.main()
