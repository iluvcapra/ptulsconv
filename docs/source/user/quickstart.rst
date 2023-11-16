Quick Start
===========

The workflow for creating ADR reports in `ptulsconv` is similar to other ADR 
spotting programs: spot ADR lines in Pro Tools with clips using a special 
code to take notes, export the tracks as text and then run the program.


Step 1: Use Pro Tools to Spot ADR Lines
---------------------------------------

`ptulsconv` can be used to spot ADR lines similarly to other programs.

#. Create a new Pro Tools session, name this session after your project.
#. Create new tracks, one for each character. Name each track after a 
   character.
#. On each track, create a clip group (or edit in some audio) at the time you 
   would like an ADR line to appear in the report. Name the clip after the 
   dialogue you are replacing at that time.


Step 2: Add More Information to Your Spots
------------------------------------------

Clips, tracks and markers in your session can contain additional information 
to make your ADR reports more complete and useful. You add this information 
with :ref:`tagging<tags>`.

* **Every ADR clip must have a unique cue number.** After the name of each
  clip, add the letters ``$QN=`` and then a unique number (any combination of
  letters or numbers that don't contain a space). You can type these yourself
  or add them with batch-renaming when you're done spotting.
* ADR spots should usually have a reason indicated, so you can remember exactly
  why you're replacing a particular line. Do this by adding the the text 
  ``{R=`` to your clip names after the prompt and then some short text 
  describing the reason, and then a closing ``}``. You can type anything, 
  including spaces.
* If, for example, a line is a TV cover line, you can add the text ``[TV]`` to 
  the end.

So for example, some ADR spot's clip name might look like::

    Get to the ladder! {R=Noise} $QN=J1001
    "Forget your feelings! {R=TV Cover} $QN=J1002 [TV]

These tags can appear in any order.

* You can add the name of an actor to a character's track, so this information
  will appear on your reports. In the track name, or in the track comments,
  type ``{Actor=xxx}`` replacing the xxx with the actor's name.
* Characters need to have a number (perhaps from the cast list) to express how
  they should be collated. Add ``$CN=xxx`` with 
  a unique number to each track (or the track's comments.)
* Set the scene for each line with markers. Create a marker at the beginning of 
  a scene and make it's name ``{Sc=xxx}``, replacing the xxx with the scene 
  number and name.


Step 3: Run `ptulsconv`
------------------------

In Pro Tools, select the tracks that contain your spot clips.

Then, in your Terminal, run the following command::

    ptulsconv

`ptulsconv` will connect to Pro Tools and read all of the clips on the selected
track. It will then create a folder named "Title_CURRENT_DATE", and within that 
folder it will create several PDFs and folders:

- "TITLE ADR Report" 📄 a PDF tabular report of every ADR line you've spotted.
- "TITLE Continuity" 📄 a PDF listing every scene you have indicated and its 
  timecode.
- "TITLE Line Count" 📄 a PDF tabular report giving line counts by reel, and the
  time budget per character and reel (if provided in the tagging).
- "CSV/" a folder containing CSV documents of all spotted ADR, groupd by 
  character and reel.
- "Director Logs/" 📁 a folder containing PDF tabular reports, like the overall
  report except groupd by character.
- "Supervisor Logs/" 📁 a folder containing PDF reports, one page per line, 
  designed for note taking during a session, particularly on an iPad.
- "Talent Scripts/" 📁 a folder containing PDF scripts or sides, with the timecode
  and prompts for each line, grouped by character but with most other 
  information suppressed.


