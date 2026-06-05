import ctypes
import subprocess
from pathlib import Path

from tree_sitter import Language, Parser, Node

from jdw_billboarding.lib.line_classify import BillboardLine, BillboardLineType
from jdw_billboarding.lib.parse_classes import (
    EffectDefinition, TrackDefinition, SynthHeader, SynthSection,
)

_PACKAGE_DIR = Path(__file__).resolve().parent
_SIBLING_DIR = _PACKAGE_DIR.parent.parent.parent / "tree-sitter-jdw-billboarding" / "src"
_SO_PATH = _PACKAGE_DIR / "jdw_billboarding.so"


def _find_parser_source():
    sibling = _SIBLING_DIR / "parser.c"
    if sibling.exists():
        return sibling, str(_SIBLING_DIR)
    raise RuntimeError(
        "Could not find tree-sitter-jdw-billboarding parser source. "
        "Expected sibling at tree-sitter-jdw-billboarding/src/parser.c"
    )


def _build_shared_lib():
    if _SO_PATH.exists():
        return str(_SO_PATH)
    parser_c, include_dir = _find_parser_source()
    result = subprocess.run(
        ["cc", "-shared", "-fPIC", "-o", str(_SO_PATH),
         str(parser_c), f"-I{include_dir}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to build billboarding parser: {result.stderr}")
    return str(_SO_PATH)


def _load_language():
    lib_path = _build_shared_lib()
    lib = ctypes.CDLL(lib_path)
    func = lib.tree_sitter_jdw_billboarding
    func.restype = ctypes.c_void_p
    return Language(func())


_NODE_TYPE_TO_LINE_TYPE = {
    "group_filter": BillboardLineType.GROUP_FILTER,
    "synth_header": BillboardLineType.SYNTH_HEADER,
    "effect_definition": BillboardLineType.EFFECT_DEFINITION,
    "default_statement": BillboardLineType.DEFAULT_STATEMENT,
    "command": BillboardLineType.COMMAND,
    "track": BillboardLineType.TRACK_DEFINITION,
    "comment": BillboardLineType.COMMENT,
}


class TreeSitterBackend:
    def __init__(self):
        self._lang = _load_language()
        self._parser = Parser()
        self._parser.language = self._lang

    def parse(self, source_string: str):
        tree = self._parser.parse(source_string.encode("utf-8"))
        return tree.root_node

    def classify(self, source_string: str) -> list[BillboardLine]:
        root = self.parse(source_string)
        lines: list[BillboardLine] = []
        for child in root.children:
            if child.type == "ERROR":
                raise Exception(
                    f"Malformed input at ({child.start_point.row},{child.start_point.column})"
                )
            line_type = _NODE_TYPE_TO_LINE_TYPE.get(child.type)
            if line_type is not None:
                content = child.text.decode()
                # track nodes include shuttle_content — that is the meaningful part
                lines.append(BillboardLine(content, line_type))
        return lines

    def parse_synth_header(self, source_or_node) -> SynthHeader:
        node = self._resolve_node(source_or_node, "synth_header")
        text = node.text.decode()

        instrument_name = ""
        group_name = ""
        is_selected = False
        is_drone = False
        is_sampler = False

        for c in node.children:
            if c.type == "selected":
                is_selected = True
            elif c.type == "instrument_name":
                instrument_name = c.text.decode()
            elif c.type == "group_name":
                group_name = c.text.decode()

        # Use space-split for arg strings to match old code behavior
        # (the grammar's arg rule doesn't distinguish default_args from
        # additional_config cleanly).
        space_split = text.split(" ")
        default_args_string = space_split[1] if len(space_split) > 1 else ""
        additional_args_string = space_split[2] if len(space_split) > 2 else ""
        additional_args_string += " " + " ".join(space_split[3:]) if len(space_split) > 3 else ""

        if instrument_name.startswith("SP_"):
            instrument_name = instrument_name[3:]
            is_sampler = True
        elif instrument_name.startswith("DR_"):
            instrument_name = instrument_name[3:]
            is_drone = True

        return SynthHeader(
            instrument_name, is_drone, is_sampler, is_selected,
            default_args_string, additional_args_string, group_name,
        )

    def parse_track_definition(self, source_or_node, index: int) -> TrackDefinition:
        node = self._resolve_node(source_or_node, "track")
        content = node.text.decode()

        group_override = ""
        arg_override = ""

        for c in node.children:
            if c.type == "track_metadata":
                for cc in c.children:
                    if cc.type == "group_override":
                        group_override = cc.text.decode()
                    elif cc.type == "arg_list":
                        arg_override = self._arg_list_to_string(cc)

        return TrackDefinition(content, group_override, arg_override, index)

    def parse_effect_definition(self, source_or_node) -> EffectDefinition:
        node = self._resolve_node(source_or_node, "effect_definition")

        instrument_name = ""
        unique_suffix = ""
        args_string = ""

        for c in node.children:
            if c.type == "effect_type":
                instrument_name = c.text.decode()
            elif c.type == "effect_id":
                unique_suffix = c.text.decode()
            elif c.type == "arg_list":
                args_string = self._arg_list_to_string(c)

        return EffectDefinition(instrument_name, unique_suffix, args_string)

    def parse_synth_chunk(self, chunk: list[BillboardLine]) -> SynthSection:
        assert len(chunk) > 0, "Malformed synth chunk: no content"
        assert chunk[0].type == BillboardLineType.SYNTH_HEADER, \
            "Malformed synth chunk; does not start with synth header"

        header = self.parse_synth_header(chunk[0].content)

        tracks: list[TrackDefinition] = []
        effects: list[EffectDefinition] = []
        track_counter = 0

        from jdw_billboarding.lib.line_classify import is_commented

        for line in chunk[1:]:
            if line.type == BillboardLineType.TRACK_DEFINITION:
                if not is_commented(line.content.strip()):
                    td = self.parse_track_definition(line.content, track_counter)
                    tracks.append(td)
                track_counter += 1

            if line.type == BillboardLineType.EFFECT_DEFINITION:
                if not is_commented(line.content.strip()):
                    ed = self.parse_effect_definition(line.content)
                    effects.append(ed)

        return SynthSection(header, tracks, effects)

    def _resolve_node(self, source_or_node, expected_type: str) -> Node:
        if isinstance(source_or_node, str):
            root = self.parse(source_or_node)
            if root.child_count == 0:
                raise ValueError(f"Expected {expected_type}, got empty source")
            node = root.child(0)
            if node.type != expected_type:
                raise ValueError(
                    f"Expected {expected_type}, got {node.type}: {node.text.decode()!r}"
                )
            return node
        return source_or_node

    @staticmethod
    def _arg_list_to_string(node: Node) -> str:
        parts = []
        for c in node.children:
            if c.type == "arg":
                parts.append(c.text.decode().strip())
        return ",".join(parts)
