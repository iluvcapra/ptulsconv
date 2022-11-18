Command-Line Reference
======================

Usage Form
-----------

Invocations of ptulsconv take the following form:

    ptulsconv [options] IN_FILE


Flags
-----

`-h`, `--help`:
    Show the help message.

`f FMT`, `--format=FMT`:
    Select the output format. By default this is `doc`, which will 
    generate :ref:`ADR reports<adr-reports>`.

    The :ref:`other available options<alt-output-options>` 
    are `raw` and `tagged`.


Informational Options
"""""""""""""""""""""

These options display information and exit without processing any
input documents.

`--show-formats`:
    Display information about available output formats.

`--show-available-tags`:
    Display information about tags that are used by the 
    report generator.


.. _alt-output-options:

Alternate Output Formats
------------------------

.. _raw-output:

`raw` Output
""""""""""""

The "raw" output format is a JSON document of the parsed input data.

The document is a top-level dictionary with keys for the main sections of the text export: `header`,
`files`, `clips`, `plugins`, `tracks` and `markers`, and the values for these are a list of section
entries, or a dictionary of values, in the case of `header`.

The text values of each record and field in the text export is read and output verbatim, no further 
processing is done.

.. _tagged-output:

`tagged` Output:
""""""""""""""""

The "tagged" output format is also a JSON document based on the parsed input data, after the additional 
step of processing all of the :ref:`tags<tags>` in the document.

The document is a top-level array of dictionaries, one for each recognized ADR spotting clip in the 
session. Each dictionary has a `clip_name`, `track_name` and `session_name` key, a `tags` key that
contains a dictionary of every parsed tag (after applying tags from all tracks and markers), and a 
`start` and `end` key. The `start` and `end` key contain the parsed timecode representations of these
values in rational number form, as a dictionary with `numerator` and `denominator` keys. 



