For ADR Report Generation
=========================

Reports Created by the ADR Report Generator
-------------------------------------------

(FIXME: write this)


Tags Used by the ADR Report Generator
-------------------------------------


Project-Level Tags
""""""""""""""""""

It usually makes sense to place these either in the session name,
or on a :ref:`marker <tag-marker>` at the beginning of the session, so it will apply to
all of the clips in the session.

`Title`:
    The title of the project. This will appear at the top
    of every report.

`Supv`:
    The supervisor of the project. This appears at the bottom
    of every report.

`Client`:
    The client of the project. This will often appear under the
    title on every report.

`Spot`: 
    The date or version number of the spotting report.


Time Range Tags
"""""""""""""""

All of these tags can be set to different values on each clip, but
it often makes sense to use these tags in a :ref:`time range<tag-range>`.

`Sc`:
    The scene description. This appears on the continuity report
    and is used in the Director's logs.

`Ver`:
    The picture version. This appears beside the spot timecodes
    on most reports.

`Reel`: 
    The reel. This appears beside the spot timecodes
    on most reports and is used to summarize line totals on the
    line count report.


Line tags
"""""""""

`P`: 
    Priority.

`QN`: 
    Cue number. This appears on all reports.

.. warning::
    `ptulsconv` will verify that all cue numbers in a given title are unique.

    All lines must have a cue number in order to generate reports, if any lines
    do not have a cue number set, `ptulsconv` will fail.


`CN`: 
    Character number. This is used to collate character records
    and will appear on the line count and in character-collated 
    reports.

`Char`: 
    Character name. By default, a clip will set this to the 
    name of the track it appears on, but the track name can be
    overridden here.

`Actor`: 
    Actor name.

`Line`: 
    The prompt to appear for this ADR line. By default, this
    will be whatever text appears in a clip name prior to the first
    tag.

`R`: 
    Reason.

`Mins`: 
    Time budget for this line, in minutes. This is used in the
    line count report to give estimated times for each character. This 
    can be set for the entire project (with a :ref:`marker <tag-marker>`), or for individual 
    actors (with a tag in the :ref:`track comments<tag-track>`), or can be set for 
    individual lines to override these. 

`Shot`: 
    Shot. A Date or other description indicating the line has been
    recorded.


Boolean-valued ADR Tag Fields
"""""""""""""""""""""""""""""

`EFF`: 
    Effort. Lines with this tag are subtotaled in the line count report.

`TV`: 
    TV line. Lines with this tag are subtotaled in the line count report.

`TBW`: 
    To be written.

`ADLIB`:
    Ad-lib.

`OPT``: 
    Optional. Lines with this tag are subtotaled in the line count report.

