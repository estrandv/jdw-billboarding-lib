from jdw_billboarding.lib.parsing import (
    cut_first, parse_effect_definition, parse_track_definition,
    parse_synth_header,
)
from jdw_billboarding.lib.parse_classes import (
    EffectDefinition, TrackDefinition, SynthHeader,
)
from jdw_billboarding.lib.line_classify import BillboardLine, BillboardLineType


def test_cut_first():
    assert cut_first("abcd", 3) == "d"
    assert cut_first("    ", 1) == "   "
    assert cut_first("a", 0) == "a"
    assert cut_first("a", 1) == ""
    assert cut_first("0", 2) == ""


def test_parse_effect_definition_basic():
    result = parse_effect_definition("€reverb:main room0.9,mix0.5")
    assert isinstance(result, EffectDefinition)
    assert result.instrument_name == "reverb"
    assert result.unique_suffix == "main"
    assert result.args_string == "room0.9,mix0.5"


def test_parse_effect_definition_no_args():
    result = parse_effect_definition("€delay:a")
    assert result.instrument_name == "delay"
    assert result.unique_suffix == "a"
    assert result.args_string == ""


def test_parse_track_definition_basic():
    result = parse_track_definition("c4 d4 e4", 0)
    assert isinstance(result, TrackDefinition)
    assert result.content == "c4 d4 e4"
    assert result.group_override == ""
    assert result.arg_override == ""
    assert result.index == 0


def test_parse_track_definition_with_group_override():
    result = parse_track_definition("<harmony> g4 a4", 1)
    assert result.content == " g4 a4"
    assert result.group_override == "harmony"
    assert result.arg_override == ""
    assert result.index == 1


def test_parse_track_definition_with_group_and_args():
    result = parse_track_definition("<harmony;amp*1.5> g4 a4", 2)
    assert result.content == " g4 a4"
    assert result.group_override == "harmony"
    assert result.arg_override == "amp*1.5"
    assert result.index == 2


def test_parse_track_definition_complex_content():
    result = parse_track_definition("(c4:0,sus4 c5:1):amp0.5", 3)
    assert result.content == "(c4:0,sus4 c5:1):amp0.5"
    assert result.group_override == ""
    assert result.arg_override == ""


def test_parse_synth_header_basic():
    result = parse_synth_header("@moogBass")
    assert isinstance(result, SynthHeader)
    assert result.instrument_name == "moogBass"
    assert not result.is_selected
    assert not result.is_drone
    assert not result.is_sampler
    assert result.group_name == ""
    assert result.default_args_string == ""
    assert result.additional_args_string == ""


def test_parse_synth_header_with_group_and_args():
    result = parse_synth_header("@moogBass:bass amp0.5,sus2.0")
    assert result.instrument_name == "moogBass"
    assert result.group_name == "bass"
    assert result.default_args_string == "amp0.5,sus2.0"
    assert result.additional_args_string == ""


def test_parse_synth_header_selected():
    result = parse_synth_header("*@moogBass:bass amp0.5")
    assert result.instrument_name == "moogBass"
    assert result.is_selected
    assert result.group_name == "bass"


def test_parse_synth_header_sampler():
    result = parse_synth_header("@SP_Roland808:drum ofs0,amp0.6 1:0 2:14")
    assert result.instrument_name == "Roland808"
    assert result.is_sampler
    assert not result.is_drone
    assert result.default_args_string == "ofs0,amp0.6"
    assert result.additional_args_string == "1:0 2:14"


def test_parse_synth_header_drone():
    result = parse_synth_header("@DR_aPad:experiment amp0.0,out90")
    assert result.instrument_name == "aPad"
    assert result.is_drone
    assert not result.is_sampler
    assert result.group_name == "experiment"
    assert result.default_args_string == "amp0.0,out90"


def test_parse_synth_header_no_group():
    result = parse_synth_header("@prophet")
    assert result.instrument_name == "prophet"
    assert result.group_name == ""
    assert not result.is_selected
