from decimal import Decimal
from jdw_billboarding.lib.shuttle_hacks import parse_orphaned_args


def test_orphaned_args_single():
    result = parse_orphaned_args(["amp0.5"])
    assert result == {"amp": Decimal("0.5")}


def test_orphaned_args_override():
    result = parse_orphaned_args(["amp0.5,sus1.0", "amp*2.0"])
    assert result["amp"] == Decimal("1.0")
    assert result["sus"] == Decimal("1.0")


def test_orphaned_args_operator_chain():
    result = parse_orphaned_args(["amp1.0", "amp+0.5", "amp*2.0"])
    assert result["amp"] == Decimal("3.0")


def test_orphaned_args_negation():
    result = parse_orphaned_args(["amp-0.5"])
    assert result["amp"] == Decimal("-0.5")


def test_orphaned_args_replace():
    result = parse_orphaned_args(["amp1.0", "amp2.0"])
    assert result["amp"] == Decimal("2.0")


def test_orphaned_args_empty():
    assert parse_orphaned_args([]) == {}
    assert parse_orphaned_args([""]) == {}
