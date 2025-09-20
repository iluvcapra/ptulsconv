"""
Validation logic for enforcing various consistency rules.
"""

from dataclasses import dataclass
from ptulsconv.docparser.adr_entity import ADRLine
from typing import Iterator, Optional


@dataclass
class ValidationError:
    message: str
    event: Optional[ADRLine] = None

    def report_message(self):
        if self.event is not None:
            return (f"{self.message}: event at {self.event.start} with number"
                    "{self.event.cue_number}")
        else:
            return self.message


def validate_unique_count(input_lines: Iterator[ADRLine], field='title',
                          count=1):
    values = set(list(map(lambda e: getattr(e, field), input_lines)))
    if len(values) > count:
        yield ValidationError(
            message="Field {} has too many values (max={}): {}"
            .format(field, count, values)
        )


def validate_value(input_lines: Iterator[ADRLine], key_field, predicate):
    for event in input_lines:
        val = getattr(event, key_field)
        if not predicate(val):
            yield ValidationError(message='Field {} not in range'.format(val),
                                  event=event)


def validate_unique_field(input_lines: Iterator[ADRLine], field='cue_number',
                          scope=None):
    values = dict()
    for event in input_lines:
        this = getattr(event, field)
        if scope is not None:
            key = getattr(event, scope)
        else:
            key = '_values'

        values.setdefault(key, set())
        if this in values[key]:
            yield ValidationError(message='Re-used {}'.format(field),
                                  event=event)
        else:
            values[key].update(this)


def validate_non_empty_field(input_lines: Iterator[ADRLine],
                             field='cue_number'):
    for event in input_lines:
        if getattr(event, field, None) is None:
            yield ValidationError(message='Empty field {}'.format(field),
                                  event=event)


def validate_dependent_value(input_lines: Iterator[ADRLine], key_field,
                             dependent_field):
    """
    Validates that two events with the same value in `key_field` always have
    the same value in `dependent_field`
    """
    key_values = set((getattr(x, key_field) for x in input_lines))

    for key_value in key_values:
        rows = [(getattr(x, key_field), getattr(x, dependent_field))
                for x in input_lines
                if getattr(x, key_field) == key_value]
        unique_rows = set(rows)
        if len(unique_rows) > 1:
            message = "Non-unique values for key {} = ".format(key_field)
            for u in unique_rows:
                message = message + "\n - {} -> {}".format(u[0], u[1])

            yield ValidationError(message=message, event=None)
