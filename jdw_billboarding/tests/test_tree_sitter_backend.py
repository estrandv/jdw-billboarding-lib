from jdw_billboarding.lib.tree_sitter_backend import TreeSitterBackend
from jdw_billboarding.lib.line_classify import BillboardLineType


def test_classify_bare_command():
    b = TreeSitterBackend()
    lines = b.classify("/transpose 5\n")
    assert len(lines) == 1
    assert lines[0].type == BillboardLineType.COMMAND


def test_classify_commented_synth_header():
    b = TreeSitterBackend()
    lines = b.classify("# @synth\n")
    assert lines[0].type == BillboardLineType.COMMENT


def test_classify_command_not_track_after_synth():
    b = TreeSitterBackend()
    lines = b.classify("@synth\n/transpose 5\n")
    assert lines[0].type == BillboardLineType.SYNTH_HEADER
    assert lines[1].type == BillboardLineType.COMMAND


def test_classify_group_filter_chain():
    b = TreeSitterBackend()
    lines = b.classify(">>>a\n>>>b\n")
    assert lines[0].type == BillboardLineType.GROUP_FILTER
    assert lines[1].type == BillboardLineType.GROUP_FILTER


def test_classify_synth_header():
    b = TreeSitterBackend()
    lines = b.classify("@synth\n")
    assert lines[0].type == BillboardLineType.SYNTH_HEADER


def test_classify_track_definition():
    b = TreeSitterBackend()
    lines = b.classify("c4 e4 g4\n")
    assert lines[0].type == BillboardLineType.TRACK_DEFINITION


def test_classify_track_with_metadata():
    b = TreeSitterBackend()
    lines = b.classify("<harmony;amp*1.5> g4 a4 b4 c5\n")
    assert lines[0].type == BillboardLineType.TRACK_DEFINITION


def test_classify_effect_definition():
    b = TreeSitterBackend()
    lines = b.classify("€reverb:myEffect room=0.8\n")
    assert lines[0].type == BillboardLineType.EFFECT_DEFINITION


def test_classify_default_statement():
    b = TreeSitterBackend()
    lines = b.classify("DEFAULT amp0.5\n")
    assert lines[0].type == BillboardLineType.DEFAULT_STATEMENT


def test_classify_comment():
    b = TreeSitterBackend()
    lines = b.classify("# just a comment\n")
    assert lines[0].type == BillboardLineType.COMMENT


def test_classify_selected_synth():
    b = TreeSitterBackend()
    lines = b.classify("*@synth\n")
    assert lines[0].type == BillboardLineType.SYNTH_HEADER


def test_classify_update_command():
    b = TreeSitterBackend()
    lines = b.classify("UPDATE_COMMAND /transpose 5\n")
    assert lines[0].type == BillboardLineType.COMMAND


def test_classify_queue_command():
    b = TreeSitterBackend()
    lines = b.classify("QUEUE_COMMAND /tempo 120\n")
    assert lines[0].type == BillboardLineType.COMMAND


def test_classify_empty_source():
    b = TreeSitterBackend()
    assert b.classify("") == []


def test_classify_mixed():
    b = TreeSitterBackend()
    source = "# intro\n@pad\nc4 e4\nDEFAULT amp0.5\n>>>all\n"
    lines = b.classify(source)
    assert [l.type.name for l in lines] == [
        "COMMENT", "SYNTH_HEADER", "TRACK_DEFINITION",
        "DEFAULT_STATEMENT", "GROUP_FILTER",
    ]


def test_classify_comment_not_track():
    b = TreeSitterBackend()
    lines = b.classify("@synth\n# comment\n/transpose 5\n")
    assert lines[0].type == BillboardLineType.SYNTH_HEADER
    assert lines[1].type == BillboardLineType.COMMENT
    assert lines[2].type == BillboardLineType.COMMAND


def test_classify_group_filter_after_synth():
    b = TreeSitterBackend()
    lines = b.classify("@synth\n>>>drums\n")
    assert lines[1].type == BillboardLineType.GROUP_FILTER


def test_classify_standalone_track():
    b = TreeSitterBackend()
    lines = b.classify("c4 e4 g4\n")
    assert lines[0].type == BillboardLineType.TRACK_DEFINITION


def test_parse_synth_header_basic():
    b = TreeSitterBackend()
    h = b.parse_synth_header("@synth\n")
    assert h.instrument_name == "synth"
    assert h.group_name == ""
    assert h.default_args_string == ""
    assert h.additional_args_string == ""
    assert not h.is_selected
    assert not h.is_drone
    assert not h.is_sampler


def test_parse_synth_header_with_group():
    b = TreeSitterBackend()
    h = b.parse_synth_header("@pad:synth1\n")
    assert h.instrument_name == "pad"
    assert h.group_name == "synth1"


def test_parse_synth_header_with_args():
    b = TreeSitterBackend()
    h = b.parse_synth_header("@synth amp0.5,gain2.0\n")
    assert h.default_args_string == "amp0.5,gain2.0"


def test_parse_synth_header_selected():
    b = TreeSitterBackend()
    h = b.parse_synth_header("*@synth:group1 args1\n")
    assert h.instrument_name == "synth"
    assert h.group_name == "group1"
    assert h.is_selected
    assert h.default_args_string == "args1"


def test_parse_synth_header_sampler():
    b = TreeSitterBackend()
    h = b.parse_synth_header("@SP_Roland808:drum ofs0,amp0.6 1:0 2:14\n")
    assert h.instrument_name == "Roland808"
    assert h.group_name == "drum"
    assert h.is_sampler
    assert not h.is_drone
    assert h.default_args_string == "ofs0,amp0.6"
    assert h.additional_args_string == "1:0 2:14"


def test_parse_synth_header_drone():
    b = TreeSitterBackend()
    h = b.parse_synth_header("@DR_aPad:experiment amp0.0,out90\n")
    assert h.instrument_name == "aPad"
    assert h.group_name == "experiment"
    assert h.is_drone
    assert h.default_args_string == "amp0.0,out90"


def test_parse_synth_header_no_group():
    b = TreeSitterBackend()
    h = b.parse_synth_header("@moogBass amp0.5\n")
    assert h.instrument_name == "moogBass"
    assert h.group_name == ""
    assert h.default_args_string == "amp0.5"


def test_parse_effect_definition_basic():
    b = TreeSitterBackend()
    ed = b.parse_effect_definition("€reverb:myEffect room=0.8\n")
    assert ed.instrument_name == "reverb"
    assert ed.unique_suffix == "myEffect"
    assert ed.args_string == "room=0.8"


def test_parse_effect_definition_no_args():
    b = TreeSitterBackend()
    ed = b.parse_effect_definition("€delay:echo\n")
    assert ed.instrument_name == "delay"
    assert ed.unique_suffix == "echo"
    assert ed.args_string == ""


def test_parse_track_definition_basic():
    b = TreeSitterBackend()
    td = b.parse_track_definition("c4 e4 g4\n", 0)
    assert td.content == "c4 e4 g4"
    assert td.group_override == ""
    assert td.arg_override == ""
    assert td.index == 0


def test_parse_track_definition_with_group():
    b = TreeSitterBackend()
    td = b.parse_track_definition("<harmony> g4 a4 b4 c5\n", 2)
    assert td.group_override == "harmony"
    assert td.arg_override == ""


def test_parse_track_definition_with_group_and_args():
    b = TreeSitterBackend()
    td = b.parse_track_definition("<harmony;amp*1.5> g4 a4 b4 c5\n", 2)
    assert td.group_override == "harmony"
    assert td.arg_override == "amp*1.5"


def test_parse_track_definition_complex():
    b = TreeSitterBackend()
    td = b.parse_track_definition("c4 < e4 g4 > c5 c4\n", 0)
    assert "c4 < e4 g4 > c5 c4" in td.content


def test_parse_synth_chunk():
    b = TreeSitterBackend()
    chunk = b.classify("@pad\n<harmony;gain2.0> c4 e4 g4\n€reverb:myE room=0.8\n")
    ss = b.parse_synth_chunk(chunk)
    assert ss.header.instrument_name == "pad"
    assert len(ss.tracks) == 1
    assert ss.tracks[0].group_override == "harmony"
    assert ss.tracks[0].arg_override == "gain2.0"
    assert len(ss.effects) == 1
    assert ss.effects[0].instrument_name == "reverb"
    assert ss.effects[0].args_string == "room=0.8"


import pytest


def test_classify_malformed_raises():
    b = TreeSitterBackend()
    with pytest.raises(Exception, match="Malformed input"):
        b.classify("@@@\n")


def test_parse_synth_chunk_empty_raises():
    b = TreeSitterBackend()
    with pytest.raises(ValueError, match="no content"):
        b.parse_synth_chunk([])


def test_parse_synth_chunk_no_header_raises():
    b = TreeSitterBackend()
    lines = b.classify("c4 e4 g4\n")
    with pytest.raises(ValueError, match="does not start with synth header"):
        b.parse_synth_chunk(lines)
