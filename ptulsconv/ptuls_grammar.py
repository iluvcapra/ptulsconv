from parsimonious.grammar import Grammar

protools_text_export_grammar = Grammar(
    r"""
    document = header files_section? clips_section? plugin_listing? track_listing? markers_listing?
    header   = "SESSION NAME:" fs string_value rs 
               "SAMPLE RATE:" fs float_value rs 
               "BIT DEPTH:" fs integer_value "-bit" rs 
               "SESSION START TIMECODE:" fs string_value rs 
               "TIMECODE FORMAT:" fs float_value " Drop"? " Frame" rs 
               "# OF AUDIO TRACKS:" fs integer_value rs 
               "# OF AUDIO CLIPS:" fs integer_value rs 
               "# OF AUDIO FILES:" fs integer_value rs block_ending

    files_section        = files_header files_column_header file_record* block_ending
    files_header         = "F I L E S  I N  S E S S I O N" rs
    files_column_header  = "Filename" isp fs "Location" rs
    file_record          = string_value fs string_value rs

    clips_section        = clips_header clips_column_header clip_record* block_ending
    clips_header         = "O N L I N E  C L I P S  I N  S E S S I O N" rs
    clips_column_header  = string_value fs string_value rs
    clip_record          = string_value fs string_value (fs "[" integer_value "]")? rs

    plugin_listing       = plugin_header plugin_column_header plugin_record* block_ending
    plugin_header        = "P L U G - I N S  L I S T I N G" rs
    plugin_column_header = "MANUFACTURER            " fs "PLUG-IN NAME            " fs 
                           "VERSION         " fs "FORMAT          " fs "STEMS                   " fs 
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
                           "CHANNEL " fs "EVENT   " fs "CLIP NAME                     " fs 
                           "START TIME    " fs "END TIME      " fs "DURATION      " fs 
                           ("TIMESTAMP         " fs)? "STATE" rs
    
    track_state_list     = (track_state " ")*
    
    track_state          = "Solo" / "Muted" / "Inactive" / "Hidden"
    
    track_clip_entry     = integer_value isp fs 
                           integer_value isp fs 
                           string_value fs 
                           string_value fs string_value fs string_value fs (string_value fs)? 
                           track_clip_state rs
                           
    track_clip_state     = ("Muted" / "Unmuted")

    markers_listing        = markers_listing_header markers_column_header marker_record*
    markers_listing_header = "M A R K E R S  L I S T I N G" rs
    markers_column_header  = "#   " fs "LOCATION     " fs "TIME REFERENCE    " fs 
                             "UNITS    " fs "NAME                             " fs "COMMENTS" rs

    marker_record = integer_value isp fs string_value fs integer_value isp fs 
                    string_value fs string_value fs string_value rs             

    fs = "\t"
    rs = "\n"
    block_ending = rs rs
    string_value   = ~"[^\t\n]*"
    integer_value  = ~"\d+"
    float_value    = ~"\d+(\.\d+)"
    isp            = ~"[^\d\t\n]*"    
    """)
