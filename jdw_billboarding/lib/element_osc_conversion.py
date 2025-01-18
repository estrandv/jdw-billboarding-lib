"""

TODO: replaces a lot of element conversion logic in jdw_osc_utils
- Probably best as a "service" rather than a wrapper around element
- So you frontload it with all the extra data and then pass elements in

TODO:
    - IMplement index-notes support by providing a scale
    - Remove the code in jdw_osc_utils that this replaces
    - Think about id clearing
        - As I see it, an id is permanent once locked in
        - So after just one loop, notes will become quiet
        - Since notes die off naturally when gate is turned off, you can't really clear them in the registry automatically
        - As such it might not be a good idea after all to ignore new notes with existing ids

        => Instead, we should re-solve the original issue
            - Drones should not recreate every single time you hit ctrl+j
            - ... but pycompose can't know what it has previously sent
            - ... so the best way to do things would be to pass a flag, maybe
                - With each note message that has an external id: allow override
                - Other options:
                    - No external id for non-drone note-ons (but this means you can't so note mods in regular tracks)
                        - Might not be so bad, since drone replaces a lot of it
                        - The idea of modifying notes of any type has been kinda replaced with kr-tracks
                        - ... but I still like the idea of all notes having something in commmon by-type
                    - Wildcard external ids
                        - Basically: my_id_[node_id] would tell jdw-sc to insert the current node_id
                        - This would preserve external id structure

"""
# TODO: Pass in, somehow...
SC_DELAY_MS = 70

from dataclasses import dataclass
from enum import Enum
from pythonosc.osc_message import OscMessage
from shuttle_notation.parsing.element import ResolvedElement

from jdw_billboarding.lib.billboard_classes import ElementMessage
from jdw_billboarding.lib.jdw_osc_utils import args_as_osc, create_msg, resolve_freq
from jdw_billboarding.lib.line_classify import begins_with
from jdw_billboarding.lib.parsing import cut_first

def is_symbol(element: ResolvedElement, sym: str) -> bool:
    return element.suffix.lower() == sym \
        and element.prefix == "" \
        and element.index == 0

class InstrumentType(Enum):
    SAMPLER = 0
    SYNTH = 1
    DRONE = 2

@dataclass
class ElementConverter:
    instrument_name: str
    common_identifier: str # Track index
    instrument_type: InstrumentType
    external_id_override: str
    id_counter: int = 0 # So as to give different ids to each sequential note in a track

    # TODO: Not sure if transpose steps is relevant here, should it be class level?
    def resolve_message(self, element: ResolvedElement, transpose_steps: int = 0) -> ElementMessage | None:
        if begins_with(element.suffix, "@"):
            # Remove symbol from suffix to create note mod external id
            return ElementMessage(element, self.to_note_mod(element, cut_first(element.suffix, 1), transpose_steps))
        elif is_symbol(element, "x"):
            # Silence
            return ElementMessage(element, create_msg("/empty_msg", []))
        elif is_symbol(element, "."):
            # Ignore
            return None
        elif is_symbol(element, "§"):
            # Loop start marker
            return ElementMessage(element, create_msg("/jdw_sc_event_trigger", ["loop_started", SC_DELAY_MS]))
        elif begins_with(element.suffix, "$"):
            # Drone, note that suffix is trimmed similar to for note mod
            return ElementMessage(element, self.to_note_on(element, cut_first(element.suffix, 1), transpose_steps))
        elif self.instrument_type == InstrumentType.DRONE:
            return ElementMessage(element, self.to_note_mod(element, transpose_steps))
        elif self.instrument_type == InstrumentType.SAMPLER:
            return ElementMessage(element, self.to_play_sample(element))
        else:
            return ElementMessage(element, self.to_note_on_timed(element, transpose_steps))

    def to_note_mod(self, element: ResolvedElement, transpose_steps: int = 0) -> OscMessage:
        external_id = self.resolve_external_id(element) if self.external_id_override == "" else self.external_id_override
        osc_args = args_as_osc(element.args, ["freq", resolve_freq(element, transpose_steps)])
        return create_msg("/note_modify", [external_id, SC_DELAY_MS] + osc_args)

    def to_note_on_timed(self, element: ResolvedElement, transpose_steps: int = 0) -> OscMessage:
        freq = resolve_freq(element, transpose_steps)

        external_id = self.resolve_external_id(element)

        sus: float = element.args["sus"] if "sus" in element.args else 0.0
        if sus == 0.0:
            print("WARN: Element converted to timed note press did not contain a sus arg (will be 0.0): ", element)

        gate_time = str(sus)
        osc_args = args_as_osc(element.args, ["freq", freq])
        return create_msg("/note_on_timed", [self.instrument_name, external_id, gate_time, SC_DELAY_MS] + osc_args)

    def to_play_sample(self, element: ResolvedElement) -> OscMessage:
        osc_args = args_as_osc(element.args, ["freq", resolve_freq(element)])
        return create_msg("/play_sample", [
            self.resolve_external_id(element), self.instrument_name, element.index, element.prefix, SC_DELAY_MS
        ] + osc_args)

    def to_note_on(self, element: ResolvedElement, external_id_override: str = "", transpose_steps: int = 0) -> OscMessage:
        external_id = self.resolve_external_id(element) if external_id_override == "" else external_id_override
        freq = resolve_freq(element, transpose_steps)
        osc_args = args_as_osc(element.args, ["freq", freq])
        return create_msg("/note_on", [self.instrument_name, external_id, SC_DELAY_MS] + osc_args)

    def resolve_external_id(self, element: ResolvedElement) -> str:
        resolved = element.suffix
        return resolved if resolved != "" else \
            self.common_identifier + "_" + self.instrument_name + "_" + str(self.id_counter) + str(element.index) + "_{nodeId}"
        self.id_counter += 1
