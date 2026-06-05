from shuttle_notation.parsing.element import ResolvedElement
from shuttle_notation.parsing.full_parse import Parser
from shuttle_notation.parsing.information_parsing import DynamicArg

from jdw_billboarding.lib.parse_classes import TrackDefinition
from jdw_billboarding.lib.shuttle_hacks import parse_args


def cut_first(source: str, amount: int) -> str:
    possible = len(source) >= amount
    return "".join(source[amount:]) if possible else ""




# Parse the shuttle string of the track, resolving any arg inheritance, returning the list of its elements
def parse_track(track: TrackDefinition, default_arg_string: str) -> list[ResolvedElement]:
    # Easiest way to apply default args
    full_source = "(" + track.content + "):" + default_arg_string if default_arg_string != "" else track.content
    override_args = parse_args(track.arg_override, {})
    elements = Parser().parse(full_source)

    _arg_override(elements, override_args)

    return elements



# Applies args after the fact, mutating the elements
# Supports args with operators
def _arg_override(elements: list[ResolvedElement], override: dict[str,DynamicArg]):
    for arg_key in override:
        override_arg = override[arg_key]
        for element in elements:
            new_value = override_arg.value
            if arg_key in element.args:
                if override_arg.operator == "*":
                    element.args[arg_key] *= new_value
                elif override_arg.operator == "+":
                    element.args[arg_key] += new_value
                elif override_arg.operator == "-":
                    element.args[arg_key] -= new_value
                else:
                    element.args[arg_key] = new_value
            else:
                element.args[arg_key] = new_value
