from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='ptulsconv',
      version='0.1',
      author='Jamie Hardt',
      author_email='jamiehardt@me.com',
      description='Parse and convert Pro Tools text exports',
      long_description_content_type="text/markdown",
      long_description=long_description,
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
          "Programming Language :: Python :: 3.7"],
      packages=['ptulsconv'],
      keywords='text-processing parsers film tv editing editorial',
      install_requires=['parsimonious', 'timecode']
      )