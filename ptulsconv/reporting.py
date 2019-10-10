import sys

def print_banner_style(str):
    if sys.stderr.isatty():
        sys.stderr.write("\n\033[1m%s\033[0m\n\n" % str)
    else:
        sys.stderr.write("\n%s\n\n" % str)

def print_section_header_style(str):
    if sys.stderr.isatty():
        sys.stderr.write("\n\033[4m%s\033[0m\n\n" % str)
    else:
        sys.stderr.write("%s\n\n" % str)

def print_status_style(str):
    if sys.stderr.isatty():
        sys.stderr.write("\033[3m - %s\033[0m\n" % str)
    else:
        sys.stderr.write(" - %s\n" % str)

def print_advisory_tagging_error(failed_string, position, parent_track_name=None, clip_time=None):
    if sys.stderr.isatty():
        sys.stderr.write("\n")
        sys.stderr.write(" ! \033[33;1mTagging error: \033[0m")
        ok_string = failed_string[:position]
        not_ok_string = failed_string[position:]
        sys.stderr.write("\033[32m\"%s\033[31;1m%s\"\033[0m\n" % (ok_string, not_ok_string))

        if parent_track_name is not None:
            sys.stderr.write(" !   > On track \"%s\"\n" % (parent_track_name))

        if clip_time is not None:
            sys.stderr.write(" !   > In clip name at %s\n" % (clip_time))
    else:
        sys.stderr.write("\n")
        sys.stderr.write(" ! Tagging error: \"%s\"\n" % failed_string)
        sys.stderr.write(" ! %s _______________⬆\n" % (" " * position))

        if parent_track_name is not None:
            sys.stderr.write(" !   > On track \"%s\"\n" % (parent_track_name))

        if clip_time is not None:
            sys.stderr.write(" !   > In clip name at %s\n" % (clip_time))

    sys.stderr.write("\n")

def print_fatal_error(str):
    if sys.stderr.isatty():
        sys.stderr.write("\n\033[5;31;1m*** %s ***\033[0m\n" % str)
    else:
        sys.stderr.write("\n%s\n" % str)