"""
Reporting logic. These methods provide reporting methods to the package and
take some pains to provide nice-looking escape codes if we're writing to a
tty.
"""

import sys


def print_banner_style(message):
    if sys.stderr.isatty():
        sys.stderr.write(f"\n\033[1m{message}\033[0m\n\n")
    else:
        sys.stderr.write(f"\n{message}\n\n")


def print_section_header_style(message):
    if sys.stderr.isatty():
        sys.stderr.write(f"\n\033[4m{message}\033[0m\n\n")
    else:
        sys.stderr.write(f"{message}\n\n")


def print_status_style(message):
    if sys.stderr.isatty():
        sys.stderr.write(f"\033[3m - {message}\033[0m\n")
    else:
        sys.stderr.write(f" - {message}\n")


def print_warning(warning_string):
    if sys.stderr.isatty():
        sys.stderr.write(f"\033[3m - {warning_string}\033[0m\n")
    else:
        sys.stderr.write(f" - {warning_string}\n")


def print_advisory_tagging_error(
    failed_string, position, parent_track_name=None, clip_time=None
):
    if sys.stderr.isatty():
        sys.stderr.write("\n")
        sys.stderr.write(" ! \033[33;1mTagging error: \033[0m")
        ok_string = failed_string[:position]
        not_ok_string = failed_string[position:]
        sys.stderr.write(
            f'\033[32m"{ok_string}\033[31;1m{not_ok_string}"\033[0m\n'
        )

        if parent_track_name is not None:
            sys.stderr.write(f' !   > On track "{parent_track_name}"\n')

        if clip_time is not None:
            sys.stderr.write(f" !   > In clip name at {clip_time}\n")
    else:
        sys.stderr.write("\n")
        sys.stderr.write(f' ! Tagging error: "{failed_string}"\n')
        sys.stderr.write(" ! %s _______________⬆\n" % (" " * position))

        if parent_track_name is not None:
            sys.stderr.write(f' !   > On track "{parent_track_name}"\n')

        if clip_time is not None:
            sys.stderr.write(f" !   > In clip name at {clip_time}\n")

    sys.stderr.write("\n")


def print_fatal_error(message):
    if sys.stderr.isatty():
        sys.stderr.write(f"\n\033[5;31;1m*** {message} ***\033[0m\n")
    else:
        sys.stderr.write(f"\n{message}\n")
