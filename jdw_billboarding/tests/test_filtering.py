from jdw_billboarding.lib.line_classify import BillboardLine, BillboardLineType
from jdw_billboarding.lib.filtering import (
    extract_commands, extract_default_args, extract_group_filters,
    extract_synth_chunks,
)


def _line(content, type_):
    return BillboardLine(content, type_)


def test_extract_commands():
    lines = [
        _line("COMMAND /set_bpm 120", BillboardLineType.COMMAND),
        _line("c4 d4", BillboardLineType.TRACK_DEFINITION),
        _line("#COMMENT /foo", BillboardLineType.COMMAND),
    ]
    assert extract_commands(lines) == ["COMMAND /set_bpm 120"]


def test_extract_default_args_found():
    lines = [
        _line("DEFAULT amp0.5,sus1.0", BillboardLineType.DEFAULT_STATEMENT),
    ]
    assert extract_default_args(lines) == "amp0.5,sus1.0"


def test_extract_default_args_last_wins():
    lines = [
        _line("DEFAULT amp0.5", BillboardLineType.DEFAULT_STATEMENT),
        _line("DEFAULT sus2.0", BillboardLineType.DEFAULT_STATEMENT),
    ]
    assert extract_default_args(lines) == "sus2.0"


def test_extract_default_args_none():
    assert extract_default_args([]) == ""
    assert extract_default_args([
        _line("@synth", BillboardLineType.SYNTH_HEADER),
    ]) == ""


def test_extract_group_filters_all_collected():
    # NOTE: Current code has a bug — `started` is never set to True,
    # so the chain never breaks and ALL group filters are collected.
    lines = [
        _line(">>> drums", BillboardLineType.GROUP_FILTER),
        _line(">>> keys", BillboardLineType.GROUP_FILTER),
        _line("@synth", BillboardLineType.SYNTH_HEADER),
        _line(">>> bass", BillboardLineType.GROUP_FILTER),
    ]
    result = extract_group_filters(lines)
    assert len(result) == 3


def test_extract_group_filters_commented_does_not_break():
    lines = [
        _line(">>> drums", BillboardLineType.GROUP_FILTER),
        _line("#>>> keys", BillboardLineType.GROUP_FILTER),
        _line(">>> bass", BillboardLineType.GROUP_FILTER),
        _line("@synth", BillboardLineType.SYNTH_HEADER),
    ]
    result = extract_group_filters(lines)
    assert len(result) == 2  # commented ">>> keys" is skipped, ">>> bass" still in chain
    assert result[0] == [">>>", "drums"]
    assert result[1] == [">>>", "bass"]


def test_extract_group_filters_empty():
    assert extract_group_filters([]) == []


def test_extract_synth_chunks():
    lines = [
        _line("ignored", BillboardLineType.TRACK_DEFINITION),
        _line("synth", BillboardLineType.SYNTH_HEADER),
        _line("track", BillboardLineType.TRACK_DEFINITION),
        _line("#synth", BillboardLineType.SYNTH_HEADER),
        _line("effect", BillboardLineType.EFFECT_DEFINITION),
        _line("synth", BillboardLineType.SYNTH_HEADER),
        _line("comment", BillboardLineType.COMMENT),
    ]
    chunks = extract_synth_chunks(lines)
    assert len(chunks) == 2
    assert len(chunks[0]) == 3  # synth header + track + commented synth header
    assert len(chunks[1]) == 2  # synth header + comment


def test_extract_synth_chunks_empty():
    assert extract_synth_chunks([]) == []
