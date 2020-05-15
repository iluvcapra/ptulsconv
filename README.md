[![Build Status](https://travis-ci.com/iluvcapra/ptulsconv.svg?branch=master)](https://travis-ci.com/iluvcapra/ptulsconv)
 ![](https://img.shields.io/github/license/iluvcapra/ptulsconv.svg) ![](https://img.shields.io/pypi/pyversions/ptulsconv.svg) [![](https://img.shields.io/pypi/v/ptulsconv.svg)](https://pypi.org/project/ptulsconv/) ![](https://img.shields.io/pypi/wheel/ptulsconv.svg)
 
 ![Upload Python Package](https://github.com/iluvcapra/ptulsconv/workflows/Upload%20Python%20Package/badge.svg)
 
# ptulsconv
Read Pro Tools text exports and generate XML, JSON, reports

## Quick Example

At this time we're using `ptulsconv` mostly for converting ADR notes in a Pro Tools session
into an XML document we can import into Filemaker Pro. 

    % ptulsconv STAR_WARS_IV_R1_ADR_Notes_PT_Text_Export.txt > SW4_r1_ADR_Notes.xml
    % xmllint --format SW4_r1_ADR_Notes.xml
    <?xml version="1.0"?>
    <FMPXMLRESULT xmlns="http://www.filemaker.com/fmpxmlresult">
      <ERRORCODE>0</ERRORCODE>
      <PRODUCT NAME="ptulsconv" VERSION="0.0.1"/>
      <DATABASE DATEFORMAT="MM/dd/yy" LAYOUT="summary" 
        NAME="STAR_WARS_IV_R1_ADR_Notes_PT_Text_Export.txt" 
        RECORDS="84" TIMEFORMAT="hh:mm:ss"/>
      <METADATA>
        <FIELD EMPTYOK="YES" MAXREPEAT="1" NAME="Title" TYPE="TEXT"/>
        <FIELD EMPTYOK="YES" MAXREPEAT="1" NAME="Supervisor" TYPE="TEXT"/>
        <FIELD EMPTYOK="YES" MAXREPEAT="1" NAME="Client" TYPE="TEXT"/>
        <FIELD EMPTYOK="YES" MAXREPEAT="1" NAME="Scene" TYPE="TEXT"/>
        <FIELD EMPTYOK="YES" MAXREPEAT="1" NAME="Version" TYPE="TEXT"/>
        <FIELD EMPTYOK="YES" MAXREPEAT="1" NAME="Reel" TYPE="TEXT"/>
        <FIELD EMPTYOK="YES" MAXREPEAT="1" NAME="Start" TYPE="TEXT"/>
        [... much much more] 

## Installation

The easiest way to install on your site is to use `pip`:

    % pip3 install ptulsconv
    
This will install the necessary libraries on your host and gives you command-line access to the tool through an 
entry-point `ptulsconv`. In a terminal window type `ptulsconv -h` for a list of available options.

## Theory of Operation

[Avid Pro Tools][avp] exports a tab-delimited text file organized in multiple parts with an uneven syntax that usually 
can't "drop in" to other tools like Excel or Filemaker. This tool accepts a text export from Pro Tools and produces an
XML file in the `FMPXMLRESULT` schema which Filemaker Pro can import directly into a new table.

In the default mode, all of the clips are parsed and converted into a flat list of events, one Filemaker Pro row per 
clip with a start and finish time,  track name, session name, etc. Timecodes are parsed and converted into frame counts 
and seconds. Text is then parsed for descriptive meta-tags and these are assigned to columns in the output list.

[avp]: http://www.avid.com/pro-tools

### Fields in Clip Names

Track names, track comments, and clip names can also contain meta-tags, or "fields," to add additional columns to the 
output. Thus, if a clip has the name:

`Fireworks explosion {note=Replace for final} $V=1 [FX] [DESIGN]`

The row output for this clip will contain columns for the values:

|...| PT.Clip.Name| note | V | FX | DESIGN | ...|
|---|------------|------|---|----|--------|----|
|...| Fireworks explosion| Replace for final | 1 | FX | DESIGN | ... |

These fields can be defined in the clip name in three ways:
* `$NAME=VALUE` creates a field named `NAME` with a one-word value `VALUE`.
* `{NAME=VALUE}` creates a field named `NAME` with the value `VALUE`. `VALUE` in this case may contain spaces or any 
    character up to the closing bracket.
* `[NAME]` creates a field named `NAME` with a value `NAME`. This can be used to create a boolean-valued field; in the 
    output, clips with the field will have it, and clips without will have the column with an empty value.

For example, if two clips are named:

`"Squad fifty-one, what is your status?" [FUTZ] {Ch=Dispatcher} [ADR]`

`"We are ten-eight at Rampart Hospital." {Ch=Gage} [ADR]`

The output will contain the range:

|...| PT.Clip.Name| Ch | FUTZ | ADR | ...|
|---|------------|------|---|----|-----|
|...| "Squad fifty-one, what is your status?"| Dispatcher | FUTZ | ADR | ... |
|...| "We are ten-eight at Rampart Hospital."| Gage |  | ADR | ... |


### Fields in Track Names and Markers

Fields set in track names, and in track comments, will be applied to *each* clip on that track. If a track comment 
contains the text `{Dept=Foley}` for example, every clip on that track will have a "Foley" value in a "Dept" column.

Likewise, fields set on the session name will apply to all clips in the session.

Fields set in markers, and in marker comments, will be applied to all clips whose finish is *after* that marker. Fields
in markers are applied cumulatively from breakfast to dinner in the session. The latest marker applying to a clip has
precedence, so if one marker comes after the other, but both define a field, the value in the later marker

An important note here is that, always, fields set on the clip name have the highest precedence. If a field is set in a clip
name, the same field set on the track, the value set on the clip will prevail.

### Using `@` to Apply Fields to a Span of Clips

A clip name beginning with "@" will not be included in the CSV output, but its fields will be applied to clips within 
its time range on lower tracks.

If track 1 has a clip named `@ {Sc=1- The House}`, any clips beginning within that range on lower tracks will have a 
field `Sc` with that value.

### Using `&` to Combine Clips

A clip name beginning with "&" will have its parsed clip name appended to the preceding cue, and the fields of following 
cues will be applied (later clips having precedence). The clips need not be touching, and the clips will be combined 
into a single row of the output. The start time of the first clip will become the start time of the row, and the finish 
time of the last clip will become the finish time of the row.

