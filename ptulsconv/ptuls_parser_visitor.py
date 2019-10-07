from parsimonious.nodes import NodeVisitor

class PTTextVisitor(NodeVisitor):
    def visit_document(self, node, visited_children):
        files = None
        clips = None
        plugins = None
        tracks = None
        markers = None
        if isinstance(visited_children[1] ,list):
            files = visited_children[1][0]
        if isinstance(visited_children[2], list):
            clips = visited_children[2][0]
        if isinstance(visited_children[3], list):
            plugins = visited_children[3][0]
        if isinstance(visited_children[4], list):
            tracks = visited_children[4][0]

        return dict(header=visited_children[0],
                    files=files,
                    clips=clips,
                    plugins=plugins,
                    tracks=tracks,
                    markers=markers)

    def visit_header(self, node, visited_children):
        return dict(session_name=visited_children[2],
                    sample_rate=visited_children[6],
                    bit_depth=visited_children[10],
                    start_timecode=visited_children[15],
                    timecode_format=visited_children[19],
                    count_audio_tracks=visited_children[24],
                    count_clips=visited_children[28],
                    count_files=visited_children[32])

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

    def visit_track_block(self, node, visited_children):
        clips = []
        for clip in visited_children[1]:
            if clip[0] != None:
                clips.append(clip[0])

        plugins = []
        for plugin in visited_children[0][17]:
            plugins.append(plugin[1])

        return dict(
            name=visited_children[0][2],
            comments=visited_children[0][6],
            user_delay_samples=visited_children[0][10],
            state=visited_children[0][14],
            plugins=plugins,
            clips=clips
        )

    def visit_track_listing(selfs, node, visited_children):
        return visited_children[1]

    def visit_track_clip_entry(self, node, visited_children):
        timestamp = None
        if isinstance(visited_children[14], list):
            timestamp = visited_children[14][0][0]

        return {'channel': visited_children[0],
                'event': visited_children[3],
                'clip_name': visited_children[6],
                'start_time': visited_children[8],
                'end_time': visited_children[10],
                'duration': visited_children[12],
                'timestamp' : timestamp,
                'state': visited_children[15]
                }

    def visit_track_state_list(self, node, visited_children):
        states = []
        for next_state in visited_children:
            states.append(next_state[0][0].text)

        return states

    def visit_track_clip_state(self, node, visited_children):
        return node.text

    def visit_markers_listing(self, node, visited_children):
        return 'Markers'

    def visit_formatted_clip_name(self, node, visited_children):
        return visited_children[1].text

    def visit_string_value(self, node, visited_children):
        return node.text.strip(" ")

    def visit_integer_value(self, node, visited_children):
        return int(node.text)

    def visit_timecode_value(self, node, visited_children):
        return visited_children[1].text

    def visit_float_value(self, node, visited_children):
        return float(node.text)

    def visit_block_ending(self, node, visited_children):
        pass

    def generic_visit(self, node, visited_children):
        """ The generic visit method. """
        return visited_children or node
