from jdw_billboarding.lib.line_classify import (
    BillboardLineType, BillboardLine, is_commented, decomment, line_split,
    begins_with, classify_lines,
)


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


def test_classify_group_filter():
    lines = classify_lines(">>> drums bass keys")
    assert len(lines) == 1
    assert lines[0].type == BillboardLineType.GROUP_FILTER
    assert lines[0].content == ">>> drums bass keys"


def test_classify_commented_group_filter():
    lines = classify_lines("#>>> hey")
    assert len(lines) == 1
    assert lines[0].type == BillboardLineType.GROUP_FILTER


def test_classify_indented_group_filter():
    lines = classify_lines("    >>> hey")
    assert len(lines) == 1
    assert lines[0].type == BillboardLineType.GROUP_FILTER


def test_classify_synth_header():
    lines = classify_lines("@synth")
    assert len(lines) == 1
    assert lines[0].type == BillboardLineType.SYNTH_HEADER


def test_classify_selected_synth_header():
    lines = classify_lines("*@synth")
    assert len(lines) == 1
    assert lines[0].type == BillboardLineType.SYNTH_HEADER


def test_classify_comment():
    lines = classify_lines("# hello")
    assert len(lines) == 1
    assert lines[0].type == BillboardLineType.COMMENT


def test_classify_effect_definition():
    lines = classify_lines("€yeah")
    assert len(lines) == 1
    assert lines[0].type == BillboardLineType.EFFECT_DEFINITION


def test_classify_track_definition():
    lines = classify_lines("@synth\nsomthing")
    assert len(lines) == 2
    assert lines[0].type == BillboardLineType.SYNTH_HEADER
    assert lines[1].type == BillboardLineType.TRACK_DEFINITION


def test_classify_command():
    lines = classify_lines("COMMAND /set_bpm 120")
    assert len(lines) == 1
    assert lines[0].type == BillboardLineType.COMMAND


def test_classify_bare_command():
    # NOTE: Bare OSC addresses are NOT classified by current Python code
    # (only lines starting with COMMAND/UPDATE_COMMAND/QUEUE_COMMAND are).
    # The tree-sitter grammar handles this correctly; this test documents
    # the current limitation.
    lines = classify_lines("/transpose 5")
    assert len(lines) == 0


def test_classify_default():
    lines = classify_lines("DEFAULT amp0.5,sus1.0")
    assert len(lines) == 1
    assert lines[0].type == BillboardLineType.DEFAULT_STATEMENT


def test_classify_mixed():
    # NOTE: Once tracks_started is True, comments after a synth header
    # are misclassified as TRACK_DEFINITION (current code limitation).
    # The tree-sitter grammar fixes this.
    src = "\n".join([
        ">>> drums",
        "COMMAND /set_bpm 120",
        "@moogBass",
        "  c4 d4",
        "  €reverb:main",
        "# a comment",
    ])
    lines = classify_lines(src)
    types = [l.type for l in lines]
    assert types == [
        BillboardLineType.GROUP_FILTER,
        BillboardLineType.COMMAND,
        BillboardLineType.SYNTH_HEADER,
        BillboardLineType.TRACK_DEFINITION,
        BillboardLineType.EFFECT_DEFINITION,
        BillboardLineType.TRACK_DEFINITION,  # misclassified
    ], types


def test_classify_empty():
    assert classify_lines("") == []
    assert classify_lines("   ") == []
    assert classify_lines("\n\n") == []
