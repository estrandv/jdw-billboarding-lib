from jdw_billboarding.lib.element_osc_conversion import ElementConverter, ScaleData, InstrumentType
from shuttle_notation.parsing.element import ResolvedElement


def test_external_id_counter_increments():
    converter = ElementConverter(
        instrument_name="test_synth",
        common_identifier="0",
        instrument_type=InstrumentType.SYNTH,
        external_id_override="",
        scale_data=ScaleData("c", "maj", 4),
        id_counter=0,
    )

    e1 = ResolvedElement(prefix="c", index=4, suffix="", args={})
    e2 = ResolvedElement(prefix="d", index=5, suffix="", args={})

    id1 = converter.resolve_external_id(e1)
    id2 = converter.resolve_external_id(e2)

    assert id1 != id2, "Two calls should produce different IDs"
    assert "{nodeId}" not in id1, "Placeholder {nodeId} should be resolved"
    assert "{nodeId}" not in id2, "Placeholder {nodeId} should be resolved"
    assert "0_4_0" in id1 or id1.endswith("_0"), f"First ID should contain counter 0: {id1}"
    assert "1_5_1" in id2 or id2.endswith("_1"), f"Second ID should contain counter 1: {id2}"


def test_external_id_uses_suffix_when_present():
    converter = ElementConverter(
        instrument_name="test",
        common_identifier="0",
        instrument_type=InstrumentType.SYNTH,
        external_id_override="",
        scale_data=ScaleData("c", "maj", 4),
        id_counter=5,
    )

    e = ResolvedElement(prefix="c", index=4, suffix="my_suffix", args={})
    assert converter.resolve_external_id(e) == "my_suffix"
