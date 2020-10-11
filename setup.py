from setuptools import setup

from ptulsconv import __author__, __license__, __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='ptulsconv',
      version=__version__,
      author=__author__,
      description='Parse and convert Pro Tools text exports',
      long_description_content_type="text/markdown",
      long_description=long_description,
      license=__license__,
      url='https://github.com/iluvcapra/ptulsconv',
      project_urls={
          'Source':
              'https://github.com/iluvcapra/ptulsconv',
          'Issues':
              'https://github.com/iluvcapra/ptulsconv/issues',
      },
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Topic :: Multimedia',
          'Topic :: Multimedia :: Sound/Audio',
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Development Status :: 4 - Beta",
          "Topic :: Text Processing :: Filters",
          "Topic :: Text Processing :: Markup :: XML"],
      packages=['ptulsconv'],
      keywords='text-processing parsers film tv editing editorial',
      install_requires=['parsimonious', 'tqdm'],
      package_data={
          "ptulsconv": ["*.xsl"]
      },
      entry_points={
          'console_scripts': [
              'ptulsconv = ptulsconv.__main__:main'
          ]
      }
      )
