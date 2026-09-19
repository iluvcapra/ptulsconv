"""
Validation logic for enforcing various consistency rules.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from ptulsconv.docparser.adr_entity import ADRLine


@dataclass
class ValidationError:
    message: str
    event: ADRLine | None = None

    def report_message(self):
        if self.event is not None:
            return (
                f"{self.message}: event at {self.event.start} with number"
                "{self.event.cue_number}"
            )
        else:
            return self.message


def validate_unique_count(input_lines: Iterator[ADRLine], field="title", count=1):
    values = {getattr(e, field) for e in input_lines}
    if len(values) > count:
        yield ValidationError(
            message=f"Field {field} has too many values (max={count}): {values}"
        )


def validate_value(input_lines: Iterator[ADRLine], key_field, predicate):
    for event in input_lines:
        val = getattr(event, key_field)
        if not predicate(val):
            yield ValidationError(message=f"Field {val} not in range", event=event)


def validate_unique_field(
    input_lines: Iterator[ADRLine], field="cue_number", scope=None
):
    values = {}
    for event in input_lines:
        this = getattr(event, field)
        if scope is not None:
            key = getattr(event, scope)
        else:
            key = "_values"

        values.setdefault(key, set())
        if this in values[key]:
            yield ValidationError(message=f"Re-used {field}", event=event)
        else:
            values[key].update(this)


def validate_non_empty_field(input_lines: Iterator[ADRLine], field="cue_number"):
    for event in input_lines:
        if getattr(event, field, None) is None:
            yield ValidationError(message=f"Empty field {field}", event=event)


def validate_dependent_value(
    input_lines: Iterator[ADRLine], key_field, dependent_field
):
    """
    Validates that two events with the same value in `key_field` always have
    the same value in `dependent_field`
    """
    key_values = {getattr(x, key_field) for x in input_lines}

    for key_value in key_values:
        rows = [
            (getattr(x, key_field), getattr(x, dependent_field))
            for x in input_lines
            if getattr(x, key_field) == key_value
        ]
        unique_rows = set(rows)
        if len(unique_rows) > 1:
            message = f"Non-unique values for key {key_field} = "
            for u in unique_rows:
                message = message + f"\n - {u[0]} -> {u[1]}"

            yield ValidationError(message=message, event=None)
