# Rewrite of the billboarding library, focusing on less messy code at the end of the explorative phase

from dataclasses import dataclass
from enum import Enum

FILTER_HEADER: str = ">>> "
SYNTH_HEADER_HEADER: str = "@"
SELECTION_MARKER: str = "*"
EFFECT_DEF_HEADER: str = "€"
COMMENT_SYMBOL = "#"
UPDATE_COMMAND_SYMBOL = "UPDATE_COMMAND"
QUEUE_COMMAND_SYMBOL = "QUEUE_COMMAND"
ALL_COMMAND_SYMBOL = "COMMAND"
COMMAND_SYMBOLS = [UPDATE_COMMAND_SYMBOL, QUEUE_COMMAND_SYMBOL, ALL_COMMAND_SYMBOL]
DEFAULT_STATEMENT = "DEFAULT"

class BillboardLineType(Enum):
    COMMENT = 0 # Other types can also be commented; this is for raw information comments
    GROUP_FILTER = 1
    SYNTH_HEADER = 2
    TRACK_DEFINITION = 3
    EFFECT_DEFINITION = 4
    COMMAND = 5
    DEFAULT_STATEMENT = 6

@dataclass
class BillboardLine:
    content: str
    type: BillboardLineType

def is_commented(line: str):
    return "#" in line.strip() and line.strip()[0] == "#"

def decomment(line: str) -> str:
    return decomment("".join(line[1:])) if is_commented(line) else line

# Split by newline, treating backslash as line continuation
def line_split(source: str) -> list[str]:
    de_broken = source.replace("\\\n", "")
    return [line.strip().replace("\t", " ").replace("    ", " ") for line in de_broken.split("\n")]

def begins_with(source: str, beginning: str) -> bool:
    clean_source = source.strip()
    return len(clean_source) >= len(beginning) and "".join(clean_source[0:len(beginning)]) == beginning

# classify_lines removed in Phase 3 — use TreeSitterBackend.classify() instead.
