import unittest

import tempfile

import sys
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
        files = []
        files = [os.path.dirname(__file__) +
                 "/../export_cases/Robin Hood Spotting.txt"]
        for path in files:
            tempdir = tempfile.TemporaryDirectory()
            os.chdir(tempdir.name)
            try:
                commands.convert(input_file=path, major_mode='doc')
            except Exception as e:
                print("Error in test_report_generation")
                print(f"File: {path}")
                print(repr(e))
                raise e
            finally:
                tempdir.cleanup()

    def test_report_generation_track_markers(self):
        files = []
        files.append(os.path.dirname(__file__) +
                     "/../export_cases/Test for ptulsconv.txt")
        for path in files:
            tempdir = tempfile.TemporaryDirectory()
            os.chdir(tempdir.name)
            try:
                commands.convert(input_file=path, major_mode='doc')
            except Exception as e:
                print("Error in test_report_generation_track_markers")
                print(f"File: {path}")
                print(repr(e))
                raise e
            finally:
                tempdir.cleanup()


if __name__ == '__main__':
    unittest.main()
