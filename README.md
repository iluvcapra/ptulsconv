![](https://img.shields.io/github/license/iluvcapra/ptulsconv.svg)
![](https://img.shields.io/pypi/pyversions/ptulsconv.svg) 
[![](https://img.shields.io/pypi/v/ptulsconv.svg)][pypi]
![GitHub last commit](https://img.shields.io/github/last-commit/iluvcapra/pycmx)
[![Lint and Test](https://github.com/iluvcapra/ptulsconv/actions/workflows/python-package.yml/badge.svg)](https://github.com/iluvcapra/ptulsconv/actions/workflows/python-package.yml)

[pypi]: https://pypi.org/project/ptulsconv/


# ptulsconv

Read Pro Tools text exports and generate PDF reports, JSON output.

## Quick Start

For a quick overview of how to cue ADR with `ptulsconv`, check out the [Quickstart](doc/QUICKSTART.md).


## Installation

The easiest way to install on your site is to use `pip`:

    % pip3 install ptulsconv
    
This will install the necessary libraries on your host and gives you 
command-line access to the tool through an entry-point `ptulsconv`. In a 
terminal window type `ptulsconv -h` for a list of available options.


## Theory of Operation

[Avid Pro Tools][avp] can be used to make spotting notes for ADR recording
sessions by creating spotting regions with descriptive text and exporting the
session as text. This file can then be dropped into Excel or any CSV-reading
app like Filemaker Pro.

**ptulsconv** accepts a text export from Pro Tools and automatically creates
PDF and CSV documents for use in ADR spotting, recording, editing and 
reporting, and supplemental JSON documents can be output for use with other
workflows.

[avp]: http://www.avid.com/pro-tools


