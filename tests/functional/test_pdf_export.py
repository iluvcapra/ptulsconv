import unittest

import tempfile

import os.path
import os
import glob

from ptulsconv import commands

# class TestBroadcastTimecode(unittest.TestCase):
#     def test_report_generation(self):
#         """
#         Setp through every text file in export_cases and make sure it can 
#         be converted into PDF docs without throwing an error
#         """
#         for path in glob.glob(os.path.dirname(__file__) + "/../export_cases/*.txt"):
#             tempdir = tempfile.TemporaryDirectory()
#             os.chdir(tempdir.name)
#             try:
#                 commands.convert(path, major_mode='doc')
#             except:
#                 assert False, "Error processing file %s" % path
#             finally:
#                 tempdir.cleanup()





if __name__ == '__main__':
    unittest.main()
