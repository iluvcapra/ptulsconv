# Quick Start for ADR Spotting and Reporting with `ptulsconv`

## Step 1: Use Pro Tools to spot ADR Lines

`ptulsconv` can be used to spot ADR lines similarly to other programs.

1. Create a new Pro Tools session, name this session after your project.
1. Create new tracks, one for each character. Name each track after a character.
1. On each track, create a clip group (or edit in some audio) at the time you 
   would like an ADR line to appear in the report. Name the clip after the 
   dialogue you are replacing at that time.


## Step 2: Add More Information to Your Spots

Clips, tracks and markers in your session can contain additional information 
to make your ADR reports more complete and useful. You add this information 
with *tagging*.

- Every ADR clip must have a unique cue number. After the name of each clip,
  add the letters "$QN=" and then a unique number (any combination of letters 
  or numbers that don't contain a space). You can type these yourself or add 
  them with batch-renaming when you're done spotting.
- ADR spots should usually have a reason indicated, so you can remember exactly
  why you're replacing a particular line. Do this by adding the the text "{R="
  to your clip names after the prompt and then some short text describing the 
  reason, and then a closing "}". You can type anything, including spaces.
- If a line is a TV cover line, you can add the text "[TV]" to the end.

So for example, some ADR spot's clip name might look like:

> "Get to the ladder! {R=Noise} $QN=J1001"
> "Forget your feelings! {R=TV Cover} $QN=J1002 [TV]"

These tags can appear in any order.

- You can add the name of an actor to a character's track, so this information
  will appear on your reports. In the track name, or in the track comments,
  type "{Actor=xxx}" replacing the xxx with the actor's name.
- Characters need to have a number (perhaps from the cast list) to express how
  they should be collated. Add "$CN=xxx" with a unique number to each track (or
  the track's comments.)
- Set the scene for each line with markers. Create a marker at the beginning of 
  a scene and make it's name "{Sc=xxx}", replacing the xxx with the scene 
  number and name.

Many tags are available to express different details of each line, charater or 
the project, find them by running `ptulsconv` with the `--show-available-tags`
option.

## Step 3: Export Relevant Tracks from Pro Tools as a Text File

Export the file as a UTF-8 and be sure to include clips and markers. Export 
using the Timecode time format.

Do not export crossfades.
