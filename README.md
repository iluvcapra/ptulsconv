![](https://img.shields.io/github/license/iluvcapra/ptulsconv.svg)
![](https://img.shields.io/pypi/pyversions/ptulsconv.svg) 
[![](https://img.shields.io/pypi/v/ptulsconv.svg)][pypi]
![Lint and Test](https://github.com/iluvcapra/ptulsconv/actions/workflows/python-package.yml/badge.svg) 

[pypi]: https://pypi.org/project/ptulsconv/


# ptulsconv

Read Pro Tools text exports and generate PDF reports, JSON output.

## Quick Start

For a quick overview of how to cue ADR with `ptulsconv`, check out the [Quickstart](doc/QUICKSTART.md).
 

## Theory of Operation

[Avid Pro Tools][avp] can be used to make spotting notes for ADR recording
sessions by creating spotting regions with descriptive text and exporting the
session as text. This file can then be dropped into Excel or any CSV-reading
app like Filemaker Pro.

**ptulsconv** accepts a text export from Pro Tools and automatically creates
PDF and CSV documents for use in ADR spotting, recording, editing and 
reporting, and supplemental JSON documents can be output for use with other
workflows.

### Reports Generated by ptulsconv by Default

1. "ADR Report" lists every line in an export with most useful fields, sorted 
   by time.
2. "Continuity" lists every scene sorted by time.
3. "Line Count" lists a count of every line, collated by reel number and by
   effort/TV/optional line designation.
4. "CSV" is a folder of files of all lines collated by character and reel
   as CSV files, for use by studio cueing workflows.
5. "Director Logs" is a folder of PDFs formatted like the "ADR Report" except
   collated by character.
6. "Supervisor Logs" creates a PDF report for every character, with one line
   per page, optimized for note-taking.
7. "Talent Scripts" is a minimal PDF layout of just timecode and line prompt,
   collated by character.


[avp]: http://www.avid.com/pro-tools



## Installation

The easiest way to install on your site is to use `pip`:

    % pip3 install ptulsconv
    
This will install the necessary libraries on your host and gives you 
command-line access to the tool through an entry-point `ptulsconv`. In a 
terminal window type `ptulsconv -h` for a list of available options.
