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
    assert "{nodeId}" in id1, "Placeholder {nodeId} should be present (filled by jdw-sc)"
    assert "{nodeId}" in id2, "Placeholder {nodeId} should be present (filled by jdw-sc)"
    assert id1.startswith("0_test_synth_0"), f"First ID should start with counter 0: {id1}"
    assert id2.startswith("0_test_synth_1"), f"Second ID should start with counter 1: {id2}"
    assert id1.endswith("_{nodeId}"), f"First ID should end with {{nodeId}}: {id1}"
    assert id2.endswith("_{nodeId}"), f"Second ID should end with {{nodeId}}: {id2}"


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
