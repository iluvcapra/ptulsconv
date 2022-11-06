# How To Use `ptulsconv`

## What is `ptulsconv` Useful For?

The main purpose of `ptulsconv` is to read a Pro Tools text export and convert 
it into PDFs useful for ADR recording.

### Theory of Operation

[Avid Pro Tools][avp] exports a tab-delimited text file organized in multiple 
parts with an uneven syntax that usually can't "drop in" to other tools like 
Excel or Filemaker. This project implements a simple Mac OS X application that 
accepts a text export from Pro Tools and converts it into a [CSV][csv] of the 
clips, unfolding track and session data in the process, and also parsing 
additional columns from the clip, track, and session name.

Importing a normal text export outputs a CSV with one row for each clip, like 
this:

| PT.Session.Name | PT.Track.Name | PT.Clip.Number | PT.Clip.Name | PT.Clip.Start   | PT.Clip.Finish  | PT.Clip.Muted | ... |
|-----------------|---------------|----------------|--------------|-----------------|-----------------|---------------|-----|
| Test Session    | Track 1       | 1              | Audio 1-01   |01:00:00:05      |01:01:00:12      | Unmuted |...|
| Test Session    | Track 1       | 2              | Audio 1-02   |01:01:00:12      |01:01:00:20      | Unmuted |...|

etc... Each clip has a column for the track name of the clip in addition to the 
session name. A column for the track comments is also included. The first row 
of the output *always* contains column headings.

[avp]: http://www.avid.com/pro-tools
[csv]: https://tools.ietf.org/html/rfc4180

### Fields in Clip Names

Track names, track comments, and clip names can also contain meta-tags, or 
"fields," to add additional columns to the CSV output. Thus, if a clip has the 
name:

`Fireworks explosion {note=Replace for final} $V=1 [FX] [DESIGN]`

The row output for this clip will contain columns for the values:

|...| PT.Clip.Name| note | V | FX | DESIGN | ...|
|---|------------|------|---|----|--------|----|
|...| Fireworks explosion| Replace for final | 1 | FX | DESIGN | ... |

These fields can be defined in the clip name in three ways:
* `$NAME=VALUE` creates a field named `NAME` with a one-word value `VALUE`.
* `{NAME=VALUE}` creates a field named `NAME` with the value `VALUE`. `VALUE` 
  in this case may contain spaces or any chartacter up to the closing bracket.
* `[NAME]` creates a field named `NAME` with a value `NAME`. This can be used 
  to create a boolean-valued field; in the CSV output, clips with the field 
  will have it, and clips without will have the column with an empty value.

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

### Using `[AP]` to Combine Clips

A clip name setting the `[AP]` field will have its parsed clip name appended to the following cue, and the fields of 
following cues will be applied (earlier clips having precedence). The clips need not be touching, and the clips will 
be combined into a single row of the output. The start time of the first clip will become the start time of the row, 
and the finish time of the last clip will become the finish time of the row.


## Is it useful for anything else?


