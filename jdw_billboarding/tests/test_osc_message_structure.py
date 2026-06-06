from jdw_billboarding.lib.element_osc_conversion import ElementConverter, ScaleData, InstrumentType, SC_DELAY_MS
from shuttle_notation.parsing.element import ResolvedElement


def make_converter(instrument="test_synth", common_id="0", inst_type=InstrumentType.SYNTH,
                   external_id_override=""):
    return ElementConverter(
        instrument_name=instrument,
        common_identifier=common_id,
        instrument_type=inst_type,
        external_id_override=external_id_override,
        scale_data=ScaleData("c", "maj", 4),
        id_counter=0,
    )


def test_note_on_timed_message_structure():
    converter = make_converter()
    element = ResolvedElement(prefix="c", index=4, suffix="", args={"sus": 1.0, "freq": 440.0})
    msg = converter.to_note_on_timed(element)

    assert msg.address == "/note_on_timed"
    assert msg.params[0] == "test_synth"                              # instrument_name
    assert msg.params[1].endswith("_{nodeId}")                        # external_id
    assert isinstance(msg.params[1], str)
    assert msg.params[2] == "1.0"                                      # gate_time
    assert msg.params[3] == SC_DELAY_MS                                # delay_ms
    assert len(msg.params) >= 5                                        # has room for osc args


def test_note_on_timed_external_id_format():
    converter = make_converter()
    e1 = ResolvedElement(prefix="c", index=4, suffix="", args={"sus": 0.5})
    e2 = ResolvedElement(prefix="d", index=5, suffix="", args={"sus": 0.5})

    id1 = converter.to_note_on_timed(e1).params[1]
    id2 = converter.to_note_on_timed(e2).params[1]

    assert id1 != id2
    assert id1.endswith("_{nodeId}")
    assert id2.endswith("_{nodeId}")
    assert id1.startswith("0_test_synth_0")
    assert id2.startswith("0_test_synth_1")


def test_note_on_message_structure():
    converter = make_converter()
    element = ResolvedElement(prefix="c", index=4, suffix="", args={"freq": 440.0})
    msg = converter.to_note_on(element)

    assert msg.address == "/note_on"
    assert msg.params[0] == "test_synth"
    assert msg.params[1].endswith("_{nodeId}")
    assert msg.params[2] == SC_DELAY_MS


def test_note_on_drone_override_uses_suffix_as_external_id():
    converter = make_converter()
    element = ResolvedElement(prefix="c", index=4, suffix="$my_drone_id", args={"freq": 440.0})
    msg = converter.resolve_message(element)

    assert msg is not None
    osc = msg.osc
    assert osc.address == "/note_on"
    assert osc.params[1] == "my_drone_id"  # $ is stripped before use


def test_note_mod_generated_external_id_has_template():
    converter = make_converter()
    element = ResolvedElement(prefix="c", index=4, suffix="", args={"freq": 440.0})
    msg = converter.to_note_mod(element)

    assert msg.address == "/note_modify"
    assert msg.params[0].endswith("_{nodeId}")
    assert msg.params[1] == SC_DELAY_MS


def test_note_mod_with_override_uses_override_directly():
    converter = make_converter(external_id_override="hdrone_vocal")
    element = ResolvedElement(prefix="c", index=4, suffix="", args={"freq": 440.0})
    msg = converter.to_note_mod(element)

    assert msg.address == "/note_modify"
    assert msg.params[0] == "hdrone_vocal"
    assert msg.params[1] == SC_DELAY_MS


def test_play_sample_message_structure():
    converter = ElementConverter(
        instrument_name="emulator",
        common_identifier="0",
        instrument_type=InstrumentType.SAMPLER,
        external_id_override="",
        scale_data=ScaleData("c", "maj", 4),
        id_counter=0,
    )
    element = ResolvedElement(prefix="kick", index=3, suffix="", args={"amp": 0.8})
    msg = converter.to_play_sample(element)

    assert msg.address == "/play_sample"
    assert msg.params[0].endswith("_{nodeId}")   # external_id
    assert msg.params[1] == "emulator"            # sample_pack
    assert msg.params[2] == 3                     # index
    assert msg.params[3] == "kick"                # category
    assert msg.params[4] == SC_DELAY_MS           # delay_ms


def test_effects_clear_regex():
    from jdw_billboarding.lib.billboard_running import get_effects_clear
    msg = get_effects_clear()
    assert msg.address == "/free_notes"
    assert msg.params[0] == "^effect_(.*)"


def test_silence_symbol_produces_empty_message():
    converter = make_converter()
    element = ResolvedElement(prefix="", index=0, suffix="x", args={})
    msg = converter.resolve_message(element)
    assert msg is not None
    assert msg.osc.address == "/empty_msg"


def test_ignore_symbol_returns_none():
    converter = make_converter()
    element = ResolvedElement(prefix="", index=0, suffix=".", args={})
    msg = converter.resolve_message(element)
    assert msg is None


def test_suffix_external_id_not_affected_by_template():
    converter = make_converter()
    element = ResolvedElement(prefix="c", index=4, suffix="my_custom_id", args={"freq": 440.0})
    msg = converter.to_note_on_timed(element)
    assert msg.params[1] == "my_custom_id"
