from .Events import Event
from map_formats.bbmap import EventSequenceData


# NB: this is just for a single event currently.
# TODO: extend for event sequences.


class EventHandler():
    """ event_data is a list of EventSequenceData's """
    def __init__(self, event_data):
        self.event_sequences = event_data
        self.wuids = list()
        self.curr_event_seq = 0
        for event_seq in self.event_sequences:
            self.wuids.extend(
                list(event.wuid for event in event_seq.event_data))

    def new_event(self, kind):
        new_wuid = 0  # TODO: fix
        new_obj = Event.new(new_wuid, kind)
        if len(self.event_sequences) == 0:
            self.new_sequence()
        self.event_sequences[self.curr_event_seq].event_data.append(new_obj)
        return new_obj

    def new_sequence(self):
        self.event_sequences.append(EventSequenceData(fobj=None))
