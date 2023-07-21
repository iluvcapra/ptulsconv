from parsimonious.nodes import NodeVisitor
from parsimonious.grammar import Grammar

from .doc_entity import SessionDescriptor, HeaderDescriptor, TrackDescriptor,\
    FileDescriptor, TrackClipDescriptor, ClipDescriptor, PluginDescriptor,\
    MarkerDescriptor


protools_text_export_grammar = Grammar(
    r"""
    document = header files_section? clips_section? plugin_listing?
               track_listing? markers_listing?
    header   = "SESSION NAME:" fs string_value rs
               "SAMPLE RATE:" fs float_value rs
               "BIT DEPTH:" fs integer_value "-bit" rs
               "SESSION START TIMECODE:" fs string_value rs
               "TIMECODE FORMAT:" fs frame_rate " Drop"? " Frame" rs
               "# OF AUDIO TRACKS:" fs integer_value rs
               "# OF AUDIO CLIPS:" fs integer_value rs
               "# OF AUDIO FILES:" fs integer_value rs block_ending

    frame_rate           = ("60" / "59.94" / "30" / "29.97" / "25" / "24" /
                           "23.976")
    files_section        = files_header files_column_header file_record*
                           block_ending
    files_header         = "F I L E S  I N  S E S S I O N" rs
    files_column_header  = "Filename" isp fs "Location" rs
    file_record          = string_value fs string_value rs

    clips_section        = clips_header clips_column_header clip_record*
                           block_ending
    clips_header         = "O N L I N E  C L I P S  I N  S E S S I O N" rs
    clips_column_header  = string_value fs string_value rs
    clip_record          = string_value fs string_value
                           (fs "[" integer_value "]")? rs

    plugin_listing       = plugin_header plugin_column_header plugin_record*
                           block_ending
    plugin_header        = "P L U G - I N S  L I S T I N G" rs
    plugin_column_header = "MANUFACTURER            " fs
                           "PLUG-IN NAME            " fs
                           "VERSION         " fs
                           "FORMAT          " fs
                           "STEMS                   " fs
                           "NUMBER OF INSTANCES" rs
    plugin_record        = string_value fs string_value fs string_value fs
                           string_value fs string_value fs string_value rs

    track_listing        = track_listing_header track_block*
    track_block          = track_list_top ( track_clip_entry / block_ending )*

    track_listing_header = "T R A C K  L I S T I N G" rs
    track_list_top       = "TRACK NAME:" fs string_value rs
                           "COMMENTS:" fs string_value rs
                           "USER DELAY:" fs integer_value " Samples" rs
                           "STATE: " track_state_list rs
                           ("PLUG-INS: " ( fs string_value )* rs)?
                           "CHANNEL " fs "EVENT   " fs
                           "CLIP NAME                     " fs
                           "START TIME    " fs "END TIME      " fs
                           "DURATION      " fs
                           ("TIMESTAMP         " fs)? "STATE" rs

    track_state_list     = (track_state " ")*

    track_state          = "Solo" / "Muted" / "Inactive" / "Hidden"

    track_clip_entry     = integer_value isp fs
                           integer_value isp fs
                           string_value fs
                           string_value fs string_value fs string_value fs
                           (string_value fs)?
                           track_clip_state rs

    track_clip_state     = ("Muted" / "Unmuted")

    markers_listing        = markers_listing_header markers_column_header
                             marker_record*
    markers_listing_header = "M A R K E R S  L I S T I N G" rs
    markers_column_header  = "#   " fs "LOCATION     " fs
                             "TIME REFERENCE    " fs
                             "UNITS    " fs
                             "NAME                             " fs
                             "COMMENTS" rs

    marker_record = integer_value isp fs string_value fs integer_value isp fs
                    string_value fs string_value fs string_value rs

    fs = "\t"
    rs = "\n"
    block_ending = rs rs
    string_value   = ~r"[^\t\n]*"
    integer_value  = ~r"\d+"
    float_value    = ~r"\d+(\.\d+)?"
    isp            = ~r"[^\d\t\n]*"
    """)


def parse_document(session_text: str) -> SessionDescriptor:
    """
    Parse a Pro Tools text export.
    :param session_text: Pro Tools session text export
    :return: the session descriptor
    """
    ast = protools_text_export_grammar.parse(session_text)
    return DocParserVisitor().visit(ast)


class DocParserVisitor(NodeVisitor):

    @staticmethod
    def visit_document(_, visited_children) -> SessionDescriptor:
        files = next(iter(visited_children[1]), None)
        clips = next(iter(visited_children[2]), None)
        plugins = next(iter(visited_children[3]), None)
        tracks = next(iter(visited_children[4]), None)
        markers = next(iter(visited_children[5]), None)

        return SessionDescriptor(header=visited_children[0],
                                 files=files,
                                 clips=clips,
                                 plugins=plugins,
                                 tracks=tracks,
                                 markers=markers)

    @staticmethod
    def visit_header(_, visited_children):

        tc_drop = False
        for _ in visited_children[20]:
            tc_drop = True

        return HeaderDescriptor(session_name=visited_children[2],
                                sample_rate=visited_children[6],
                                bit_depth=visited_children[10],
                                start_timecode=visited_children[15],
                                timecode_format=visited_children[19],
                                timecode_drop_frame=tc_drop,
                                count_audio_tracks=visited_children[25],
                                count_clips=visited_children[29],
                                count_files=visited_children[33])

    @staticmethod
    def visit_files_section(_, visited_children):
        return list(map(
            lambda child: FileDescriptor(filename=child[0], path=child[2]),
                    visited_children[2]))

    @staticmethod
    def visit_clips_section(_, visited_children):
        channel = next(iter(visited_children[2][3]), 1)

        return list(map(
            lambda child: ClipDescriptor(clip_name=child[0], file=child[2],
                                         channel=channel),
            visited_children[2]))

    @staticmethod
    def visit_plugin_listing(_, visited_children):
        return list(map(lambda child:
                        PluginDescriptor(manufacturer=child[0],
                                         plugin_name=child[2],
                                         version=child[4],
                                         format=child[6],
                                         stems=child[8],
                                         count_instances=child[10]),
                        visited_children[2]))

    @staticmethod
    def visit_track_block(_, visited_children):
        track_header, track_clip_list = visited_children
        clips = []
        for clip in track_clip_list:
            if clip[0] is not None:
                clips.append(clip[0])

        plugins = []
        for plugin_opt in track_header[16]:
            for plugin in plugin_opt[1]:
                plugins.append(plugin[1])

        return TrackDescriptor(
            name=track_header[2],
            comments=track_header[6],
            user_delay_samples=track_header[10],
            state=track_header[14],
            plugins=plugins,
            clips=clips
        )

    @staticmethod
    def visit_frame_rate(node, _):
        return node.text

    @staticmethod
    def visit_track_listing(_, visited_children):
        return visited_children[1]

    @staticmethod
    def visit_track_clip_entry(_, visited_children):
        timestamp = None
        if isinstance(visited_children[14], list):
            timestamp = visited_children[14][0][0]

        return TrackClipDescriptor(channel=visited_children[0],
                                   event=visited_children[3],
                                   clip_name=visited_children[6],
                                   start_time=visited_children[8],
                                   finish_time=visited_children[10],
                                   duration=visited_children[12],
                                   timestamp=timestamp,
                                   state=visited_children[15])

    @staticmethod
    def visit_track_state_list(_, visited_children):
        states = []
        for next_state in visited_children:
            states.append(next_state[0][0].text)
        return states

    @staticmethod
    def visit_track_clip_state(node, _):
        return node.text

    @staticmethod
    def visit_markers_listing(_, visited_children):
        markers = []

        for marker in visited_children[2]:
            markers.append(marker)

        return markers

    @staticmethod
    def visit_marker_record(_, visited_children):
        return MarkerDescriptor(number=visited_children[0],
                                location=visited_children[3],
                                time_reference=visited_children[5],
                                units=visited_children[8],
                                name=visited_children[10],
                                comments=visited_children[12])

    @staticmethod
    def visit_formatted_clip_name(_, visited_children):
        return visited_children[1].text

    @staticmethod
    def visit_string_value(node, _):
        return node.text.strip(" ")

    @staticmethod
    def visit_integer_value(node, _):
        return int(node.text)

    # def visit_timecode_value(self, node, visited_children):
    #     return node.text.strip(" ")

    @staticmethod
    def visit_float_value(node, _):
        return float(node.text)

    def visit_block_ending(self, node, visited_children):
        pass

    def generic_visit(self, node, visited_children):
        """ The generic visit method. """
        return visited_children or node
