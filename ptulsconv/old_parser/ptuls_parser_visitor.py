from parsimonious.nodes import NodeVisitor, Node


class DictionaryParserVisitor(NodeVisitor):

    def visit_document(self, node: Node, visited_children) -> dict:
        files = next(iter(visited_children[1]), None)
        clips = next(iter(visited_children[2]), None)
        plugins = next(iter(visited_children[3]), None)
        tracks = next(iter(visited_children[4]), None)
        markers = next(iter(visited_children[5]), None)

        return dict(header=visited_children[0],
                    files=files,
                    clips=clips,
                    plugins=plugins,
                    tracks=tracks,
                    markers=markers)

    @staticmethod
    def visit_header(node, visited_children):

        tc_drop = False
        for _ in visited_children[20]:
            tc_drop = True

        return dict(session_name=visited_children[2],
                    sample_rate=visited_children[6],
                    bit_depth=visited_children[10],
                    start_timecode=visited_children[15],
                    timecode_format=visited_children[19],
                    timecode_drop_frame=tc_drop,
                    count_audio_tracks=visited_children[25],
                    count_clips=visited_children[29],
                    count_files=visited_children[33])

    @staticmethod
    def visit_files_section(node, visited_children):
        return list(map(lambda child: dict(filename=child[0], path=child[2]), visited_children[2]))

    @staticmethod
    def visit_clips_section(node, visited_children):
        channel = next(iter(visited_children[2][3]), 1)

        return list(map(lambda child: dict(clip_name=child[0], file=child[2], channel=channel),
                        visited_children[2]))

    @staticmethod
    def visit_plugin_listing(node, visited_children):
        return list(map(lambda child: dict(manufacturer=child[0],
                                           plugin_name=child[2],
                                           version=child[4],
                                           format=child[6],
                                           stems=child[8],
                                           count_instances=child[10]),
                        visited_children[2]))

    @staticmethod
    def visit_track_block(node, visited_children):
        track_header, track_clip_list = visited_children
        clips = []
        for clip in track_clip_list:
            if clip[0] != None:
                clips.append(clip[0])

        plugins = []
        for plugin_opt in track_header[16]:
            for plugin in plugin_opt[1]:
                plugins.append(plugin[1])

        return dict(
            name=track_header[2],
            comments=track_header[6],
            user_delay_samples=track_header[10],
            state=track_header[14],
            plugins=plugins,
            clips=clips
        )

    @staticmethod
    def visit_track_listing(node, visited_children):
        return visited_children[1]

    @staticmethod
    def visit_track_clip_entry(node, visited_children):
        timestamp = None
        if isinstance(visited_children[14], list):
            timestamp = visited_children[14][0][0]

        return dict(channel=visited_children[0],
                    event=visited_children[3],
                    clip_name=visited_children[6],
                    start_time=visited_children[8],
                    end_time=visited_children[10],
                    duration=visited_children[12],
                    timestamp=timestamp,
                    state=visited_children[15])

    @staticmethod
    def visit_track_state_list(node, visited_children):
        states = []
        for next_state in visited_children:
            states.append(next_state[0][0].text)
        return states

    @staticmethod
    def visit_track_clip_state(node, visited_children):
        return node.text

    @staticmethod
    def visit_markers_listing(node, visited_children):
        markers = []

        for marker in visited_children[2]:
            markers.append(marker)

        return markers

    @staticmethod
    def visit_marker_record(node, visited_children):
        return dict(number=visited_children[0],
                    location=visited_children[3],
                    time_reference=visited_children[5],
                    units=visited_children[8],
                    name=visited_children[10],
                    comments=visited_children[12])

    @staticmethod
    def visit_formatted_clip_name(_, visited_children):
        return visited_children[1].text

    @staticmethod
    def visit_string_value(node, visited_children):
        return node.text.strip(" ")

    @staticmethod
    def visit_integer_value(node, visited_children):
        return int(node.text)

    # def visit_timecode_value(self, node, visited_children):
    #     return node.text.strip(" ")

    @staticmethod
    def visit_float_value(node, visited_children):
        return float(node.text)

    def visit_block_ending(self, node, visited_children):
        pass

    def generic_visit(self, node, visited_children):
        """ The generic visit method. """
        return visited_children or node
