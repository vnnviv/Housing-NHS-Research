"""Tests for the pure helpers in analysis/hmda_validation.py (no network)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "analysis"))
import cap_sensitivity as cs          # noqa: E402
import hmda_validation as hv          # noqa: E402

SQUARE = [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]]


def test_point_in_rings_inside_and_outside():
    assert hv.point_in_rings(5, 5, SQUARE)
    assert not hv.point_in_rings(15, 5, SQUARE)


def test_point_in_rings_respects_holes():
    donut = SQUARE + [[[4, 4], [6, 4], [6, 6], [4, 6], [4, 4]]]
    assert hv.point_in_rings(1, 1, donut)
    assert not hv.point_in_rings(5, 5, donut)


def test_implied_front_end_matches_hand_calc():
    row = {"income": "150", "loan_amount": "600000", "interest_rate": "6.0",
           "property_value": "750000", "loan_term": "360"}       # LTV 80%, no MI
    pi = 600_000 * cs.payment_factor(0.06, 360)
    expected = (pi + 750_000 * 0.011 / 12 + 150.0) * 12 / 150_000
    assert hv.implied_front_end(row) == pytest.approx(expected)


def test_implied_front_end_missing_field_is_none():
    assert hv.implied_front_end({"income": "", "loan_amount": "1", "interest_rate": "6",
                                 "property_value": "1", "loan_term": "360"}) is None


def test_pct_suppressed_below_100():
    assert hv.pct(list(range(50)), 50) is None
