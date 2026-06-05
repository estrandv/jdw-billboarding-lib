from jdw_billboarding.lib.line_classify import (
    BillboardLineType, BillboardLine, is_commented, decomment, line_split,
    begins_with,
)
from jdw_billboarding.lib.tree_sitter_backend import TreeSitterBackend


def test_begins_with():
    assert begins_with("#comment", "#")
    assert begins_with(">>> filter", ">>>")
    assert not begins_with(".>>>", ">>>")
    assert begins_with("  @synth", "@")
    assert not begins_with("", "x")


def test_is_commented():
    assert is_commented("#@basic")
    assert is_commented("###")
    assert not is_commented("basic#")
    assert not is_commented("")
    assert is_commented("  # comment")
    assert not is_commented("code # inline")


def test_decomment():
    assert decomment("#hello") == "hello"
    assert decomment("##nested") == "nested"
    assert decomment("no comment") == "no comment"
    assert decomment("") == ""


def test_line_split():
    assert line_split("a\nb\nc") == ["a", "b", "c"]
    assert line_split("a\\\nb") == ["ab"]


_b = TreeSitterBackend()


def test_classify_group_filter():
    lines = _b.classify(">>> drums bass keys\n")
    assert len(lines) == 1
    assert lines[0].type == BillboardLineType.GROUP_FILTER


def test_classify_synth_header():
    lines = _b.classify("@synth\n")
    assert len(lines) == 1
    assert lines[0].type == BillboardLineType.SYNTH_HEADER


def test_classify_selected_synth_header():
    lines = _b.classify("*@synth\n")
    assert len(lines) == 1
    assert lines[0].type == BillboardLineType.SYNTH_HEADER


def test_classify_comment():
    lines = _b.classify("# hello\n")
    assert len(lines) == 1
    assert lines[0].type == BillboardLineType.COMMENT


def test_classify_effect_definition():
    lines = _b.classify("€reverb:main room0.9,mix0.5\n")
    assert len(lines) == 1
    assert lines[0].type == BillboardLineType.EFFECT_DEFINITION


def test_classify_track_definition():
    lines = _b.classify("@synth\nc4 d4\n")
    assert len(lines) == 2
    assert lines[0].type == BillboardLineType.SYNTH_HEADER
    assert lines[1].type == BillboardLineType.TRACK_DEFINITION


def test_classify_command():
    lines = _b.classify("COMMAND /set_bpm 120\n")
    assert len(lines) == 1
    assert lines[0].type == BillboardLineType.COMMAND


def test_classify_bare_command():
    lines = _b.classify("/transpose 5\n")
    assert len(lines) == 1
    assert lines[0].type == BillboardLineType.COMMAND


def test_classify_default():
    lines = _b.classify("DEFAULT amp0.5,sus1.0\n")
    assert len(lines) == 1
    assert lines[0].type == BillboardLineType.DEFAULT_STATEMENT


def test_classify_mixed():
    src = "\n".join([
        ">>> drums",
        "COMMAND /set_bpm 120",
        "@moogBass",
        "c4 d4",
        "€reverb:main room0.9",
        "# a comment",
        "/transpose 5",
    ])
    lines = _b.classify(src)
    types = [l.type for l in lines]
    assert types == [
        BillboardLineType.GROUP_FILTER,
        BillboardLineType.COMMAND,
        BillboardLineType.SYNTH_HEADER,
        BillboardLineType.TRACK_DEFINITION,
        BillboardLineType.EFFECT_DEFINITION,
        BillboardLineType.COMMENT,
        BillboardLineType.COMMAND,
    ], types


def test_classify_empty():
    assert _b.classify("") == []
