from parsimonious.grammar import Grammar

protools_text_export_grammar = Grammar(
    r"""
    document = header files_section? clips_section? plugin_listing? track_listing? markers_listing?
    header   = "SESSION NAME:" fs string_value rs 
               "SAMPLE RATE:" fs float_value rs 
               "BIT DEPTH:" fs string_value rs 
               "SESSION START TIMECODE:" fs timecode_value rs 
               "TIMECODE FORMAT:" fs float_value " Frame" rs 
               "# OF AUDIO TRACKS:" fs integer_value rs 
               "# OF AUDIO CLIPS:" fs integer_value rs 
               "# OF AUDIO FILES:" fs integer_value rs rs rs

    files_section        = files_header files_column_header ( file_record )* rs rs

    files_header         = "F I L E S  I N  S E S S I O N" rs
    files_column_header  = "Filename     " fs "Location" rs
    file_record          = string_value fs string_value rs

    clips_section        = clips_header clips_column_header ( clip_record )* rs rs
    clips_header         = "O N L I N E  C L I P S  I N  S E S S I O N" rs
    clips_column_header  = string_value fs string_value rs
    clip_record          = string_value fs string_value fs "[" integer_value "]" rs

    plugin_listing       = plugin_header plugin_column_header ( plugin_record rs )* rs rs
    plugin_header        = "P L U G - I N S  L I S T I N G" rs
    plugin_column_header = "MANUFACTURER            " fs "PLUG-IN NAME            " fs 
                           "VERSION         " fs "FORMAT          " fs "STEMS                   " fs 
                           "NUMBER OF INSTANCES" rs
    plugin_record        = string_value fs string_value fs string_value fs 
                           string_value fs string_value fs string_value rs


    track_listing        = track_listing_header ( track_list )*
    track_listing_header = "T R A C K  L I S T I N G" rs

    track_list           = "TRACK NAME:" fs string_value rs
                           "COMMENTS:" fs string_value rs
                           "USER DELAY:" fs integer_value " Samples" rs
                           "STATE: " ( fs string_value )* rs
                           "PLUG-INS: " ( fs string_value )* rs
                           track_clip_list rs rs

    track_clip_list      = "CHANNEL " fs "EVENT   " fs "CLIP NAME                     " fs 
                           "START TIME    " fs "END TIME      " fs "DURATION      " fs "STATE" rs
                           (track_clip_entry)*

    track_clip_entry     = integer_value isp fs 
                           integer_value isp fs 
                           string_value fs 
                           timecode_value fs timecode_value fs timecode_value fs 
                           track_clip_state rs
    track_clip_state     = ("Muted" / "Unmuted")

    markers_listing        = markers_listing_header markers_column_header marker_record*
    markers_listing_header = "M A R K E R S  L I S T I N G" rs
    markers_column_header  = "#   " fs "LOCATION     " fs "TIME REFERENCE    " fs 
                             "UNITS    " fs "NAME                             " fs "COMMENTS" rs

    marker_record = string_value fs string_value fs string_value fs 
                    string_value fs string_value fs string_value rs             

    fs = "\t"
    rs = "\n"
    string_value   = ~"[^\S\t\n]*" ~"[^\t\n]*"
    timecode_value = ~"[^\d\t\n]*" ~"\d\d" ":" ~"\d\d" ":" ~"\d\d" ":" ~"\d\d" ~"[^\d\t\n]*"
    integer_value  = ~"\d+"
    float_value    = ~"\d+(\.\d+)"
    isp            = ~"[^\d\t\n]*"    
    """)

from parsimonious.nodes import NodeVisitor, Node
from timecode import Timecode


class PTTextVisitor(NodeVisitor):
    def visit_document(self, node, visited_children):
        return {'header': visited_children[0],
                'files': visited_children[1][0],
                'clips': visited_children[2][0],
                'plugins': visited_children[3][0],
                'tracks': visited_children[4][0]
                }

    def visit_header(self, node, visited_children):
        return {
            'session_name': visited_children[2],
            'sample_rate': visited_children[6],
            'bit_depth': visited_children[10],
            'start_timecode': visited_children[14],
            'timecode_format': visited_children[18],
            'count_audio_tracks': visited_children[23],
            'count_clips': visited_children[27],
            'count_files': visited_children[31]
        }

    def visit_files_section(self, node, visited_children):
        return list(map(lambda child: {'filename': child[0], 'path': child[2]}, visited_children[2]))

    def visit_clips_section(self, node, visited_children):
        return list(map(lambda child: {'clip_name': child[0], 'file': child[2], 'channel': child[5]},
                        visited_children[2]))

    def visit_plugin_listing(self, node, visited_children):
        return list(map(lambda child: {'manufacturer': child[0], 'plugin_name': child[2],
                                       'version': child[4], 'format': child[6], 'stems': child[8],
                                       'count_instances': child[10]},
                        visited_children[2]))

    def visit_track_listing(self, node, visited_children):
        retval = []
        for child in visited_children[1]:
            state = list(map(lambda t: t.text, child[14]))
            plugs = list(map(lambda t: t.text, child[17]))
            retval.append({'track_name': child[2],
                           'comments': child[6],
                           'samples_delay': child[10],
                           'state': state,
                           'clips': child[19]})

        return retval

    def visit_track_clip_list(self, node, visited_children):
        return visited_children[14]

    def visit_track_clip_entry(self, node, visited_children):
        return {'channel': visited_children[0],
                'event': visited_children[3],
                'clip_name': visited_children[6],
                'start_time': visited_children[8],
                'end_time': visited_children[10],
                'duration': visited_children[12],
                'state': visited_children[14]
                }

    def visit_track_clip_state(self, node, visited_children):
        return node.text

    def visit_markers_listing(self, node, visited_children):
        return 'Markers'

    def visit_formatted_clip_name(self, node, visited_children):
        return visited_children[1].text

    def visit_string_value(self, node, visited_children):
        return visited_children[1].text

    def visit_integer_value(self, node, visited_children):
        return int(node.text)

    def visit_timecode_value(self, node, visited_children):
        return visited_children[1].text + visited_children[2].text + \
               visited_children[3].text + visited_children[4].text + \
               visited_children[5].text + visited_children[6].text + \
               visited_children[7].text

    def visit_float_value(self, node, visited_children):
        return float(node.text)

    def generic_visit(self, node, visited_children):
        """ The generic visit method. """
        return visited_children or node
