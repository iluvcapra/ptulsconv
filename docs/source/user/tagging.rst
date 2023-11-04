.. _tags:

Tagging
=======

Tags are used to add additional data to a clip in an organized way. The
tagging system in `ptulsconv` is flexible and can be used to add any kind of
extra data to a clip.

Fields in Clip Names
--------------------

Track names, track comments, and clip names can also contain meta-tags, or 
"fields," to add additional columns to the output. Thus, if a clip has the 
name:::

    Fireworks explosion {note=Replace for final} $V=1 [FX] [DESIGN]

The row output for this clip will contain columns for the values:


+---------------------+-------------------+---+----+--------+
| Clip Name           | note              | V | FX | DESIGN |
+=====================+===================+===+====+========+
| Fireworks explosion | Replace for final | 1 | FX | DESIGN |
+---------------------+-------------------+---+----+--------+


These fields can be defined in the clip name in three ways:

  * ``$NAME=VALUE`` creates a field named ``NAME`` with a one-word value
    ``VALUE``. 
  * ``{NAME=VALUE}`` creates a field named ``NAME`` with the value ``VALUE``. 
    ``VALUE`` in this case may contain spaces or any chartacter up  to the 
    closing bracket.
  * ``[NAME]`` creates a field named ``NAME`` with a value ``NAME``. This can 
    be used to create a boolean-valued field; in the output, clips with the 
    field will have it, and clips without will have the column with an empty
    value.

For example, if three clips are named:::

    "Squad fifty-one, what is your status?" [FUTZ] {Ch=Dispatcher} [ADR]

    "We are ten-eight at Rampart Hospital." {Ch=Gage} [ADR]

    (1M) FC callouts rescuing trapped survivors. {Ch=Group} $QN=1001 [GROUP]

The output will contain the range:


+----------------------------------------------+------------+------+-----+------+-------+
| Clip Name                                    | Ch         | FUTZ | ADR | QN   | GROUP |
+==============================================+============+======+=====+======+=======+
| "Squad fifty-one, what is your status?"      | Dispatcher | FUTZ | ADR |      |       |
+----------------------------------------------+------------+------+-----+------+-------+
| "We are ten-eight at Rampart Hospital."      | Gage       |      | ADR |      |       |
+----------------------------------------------+------------+------+-----+------+-------+
| (1M) FC callouts rescuing trapped survivors. | Group      |      |     | 1001 | GROUP |
+----------------------------------------------+------------+------+-----+------+-------+


.. _tag-track:
.. _tag-marker:

Fields in Track Names and Markers
---------------------------------

Fields set in track names, and in track comments, will be applied to *each* 
clip on that track. If a track comment contains the text ``{Dept=Foley}`` for 
example, every clip on that track will have a "Foley" value in a "Dept" column.

Likewise, fields set on the session name will apply to all clips in the session.

Fields set in markers, and in marker comments, will be applied to all clips 
whose finish is *after* that marker. Fields in markers are applied cumulatively 
from breakfast to dinner in the session. The latest marker applying to a clip has
precedence, so if one marker comes after the other, but both define a field, the 
value in the later marker

An important note here is that, always, fields set on the clip name have the 
highest precedence. If a field is set in a clip name, the same field set on the 
track, the value set on the clip will prevail.


.. _tag-range:

Apply Fields to a Time Range of Clips
-------------------------------------

A clip name beginning with ``@`` will not be included in the output, but its 
fields will be applied to clips within its time range on lower tracks.

If track 1 has a clip named ``@ {Sc=1- The House}``, any clips beginning within 
that range on lower tracks will have a field ``Sc`` with that value.


Combining Clips with Long Names or Many Tags
--------------------------------------------

A clip name beginning with ``&`` will have its parsed clip name appended to the 
preceding cue, and the fields of following cues will be applied, earlier clips 
having precedence. The clips need not be touching, and the clips will be 
combined into a single row of the output. The start time of the first clip will
become the start time of the row, and the finish time of the last clip will 
become the finish time of the row.


Setting Document Options
------------------------

.. note::
    Document options are not yet implemented.

..
  A clip beginning with ``!`` sends a command to `ptulsconv`. These commands can 
  appear anywhere in the document and apply to the entire document. Commands are 
  a list of words

  The following commands are available:

  page $SIZE=`(letter|legal|a4)`
      Sets the PDF page size for the output.

  font {NAME=`name`} {PATH=`path`}
      Sets the primary font for the output.

  sub `replacement text` {FOR=`text_to_replace`} {IN=`tag`}
      Declares a substitution. Whereever text_to_replace is encountered in the 
      document it will be replaced with "replacement text".

      If `tag` is set, this substitution will only be applied to the values of 
      that tag.


