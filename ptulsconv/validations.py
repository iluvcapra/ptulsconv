from dataclasses import dataclass
from sys import stderr


@dataclass
class ValidationError:
    message: str
    event: dict

    def report_message(self):
        return f"{self.message}: event at {self.event['PT.Clip.Start']} on track {self.event['PT.Track.Name']}"

def validate_value(input_dict, key_field, predicate):
    for event in input_dict['events']:
        val = event[key_field]
        if not predicate(val):
            yield ValidationError(message='Field {} not in range'.format(val),
                                  event=event)


def validate_unique_field(input_dict, field='QN'):
    values = set()
    for event in input_dict['events']:
        if event[field] in values:
            yield ValidationError(message='Re-used {}'.format(field), event=event)


def validate_non_empty_field(input_dict, field='QN'):
    for event in input_dict['events']:
        if field not in event.keys() or len(event[field]) == 0:
            yield ValidationError(message='Empty field {}'.format(field), event=event)


def validate_dependent_value(input_dict, key_field, dependent_field):
    """
    Validates that two events with the same value in `key_field` always have the
    same value in `dependent_field`
    """
    value_map = dict()
    for event in input_dict['events']:
        if key_field not in event.keys():
            continue

        if event[key_field] not in value_map.keys():
            value_map[event[key_field]] = event.get(dependent_field, None)
        else:
            if value_map[event[key_field]] != event.get(dependent_field, None):
                yield ValidationError(message='Field {} depends on key field {} (value={}), expected {}, was {}'
                                      .format(dependent_field, key_field, event[key_field], value_map[key_field],
                                              event.get(dependent_field, None)), event=event)




