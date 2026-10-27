"""Tests for analysis/cap_sensitivity.py.

Run from the repo root:  python -m pytest tests
"""

import sys
from dataclasses import replace
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "analysis"))

import assistance_sizing as az          # noqa: E402
import cap_sensitivity as cs            # noqa: E402
import downpayment_scenarios as dps     # noqa: E402

PRICE = 600_000.0
P = cs.Params(rate=dps.RATE_ANNUAL)     # same rate as the existing module's default
INCOMES = list(dps.INCOME_TIERS.values())


# --- closed-form checks, independent of any repo code -----------------------

def test_amortization_known_values():
    # $100,000 at 6.00% for 30 years: payment 599.55 (standard published value)
    assert cs.payment_factor(0.06, 360) * 100_000 == pytest.approx(599.55, abs=0.01)
    # $200,000 at 7.00% for 30 years: 1,330.60
    assert cs.payment_factor(0.07, 360) * 200_000 == pytest.approx(1330.60, abs=0.01)


def test_zero_rate_is_straight_line():
    assert cs.payment_factor(0.0, 360) == pytest.approx(1 / 360)


def test_payment_by_hand():
    """No-MI, 20% down: payment = P&I + tax + insurance, computed from scratch."""
    p = cs.Params(rate=0.06, down=0.20)
    price = 500_000.0
    loan = 400_000.0
    expected = (loan * cs.payment_factor(0.06, 360)
                + price * p.tax_rate / 12.0 + p.insurance_monthly)
    assert cs.monthly_payment(price, loan, p) == pytest.approx(expected)


def test_mi_banding_edges():
    assert cs.mi_rate(0.97, P) == dps.PMI_BY_LTV[0.97]
    assert cs.mi_rate(0.95, P) == dps.PMI_BY_LTV[0.95]
    assert cs.mi_rate(0.90, P) == dps.PMI_BY_LTV[0.90]
    assert cs.mi_rate(0.80, P) == 0.0
    assert cs.mi_rate(0.8000000000000002, P) == 0.0       # float noise guard


# --- parity with the existing model -----------------------------------------

@pytest.mark.parametrize("price", [450_000.0, 600_000.0, 700_000.0])
@pytest.mark.parametrize("income", INCOMES)
@pytest.mark.parametrize("savings", [0.0, 10_000.0, 25_000.0, 60_000.0])
def test_assistance_matches_existing_model(price, income, savings):
    mine = cs.assistance_needed(price, income, replace(P, savings=savings))
    theirs = az.assistance_needed(price, income, 0.03, False, savings)
    assert mine["total"] == pytest.approx(theirs["total"], abs=0.01)
    assert mine["cash"] == pytest.approx(theirs["a_cash"], abs=0.01)
    assert mine["income"] == pytest.approx(theirs["a_income"], abs=0.01)


def test_fha_payment_matches_existing_model():
    p = replace(P, is_fha=True, down=dps.FHA_DOWN)
    loan = PRICE * (1 - dps.FHA_DOWN)
    assert cs.monthly_payment(PRICE, loan, p) == pytest.approx(
        dps.total_monthly(PRICE, dps.FHA_DOWN, True), abs=0.01)


# --- inverse relationship ---------------------------------------------------

@pytest.mark.parametrize("reduction", [0.0, 25_000.0, 50_000.0, 100_000.0, 150_000.0])
def test_round_trip_required_income_to_assistance(reduction):
    y = cs.required_income(PRICE, P, reduction)
    res = cs.assistance_needed(PRICE, y, P)
    assert res["income"] == pytest.approx(reduction, abs=1.0)


def test_income_at_required_income_just_affords_the_loan():
    y = cs.required_income(PRICE, P, 0.0)
    loan, feasible = cs.max_loan(PRICE, y, P)
    assert feasible
    assert loan == pytest.approx(cs.start_loan(PRICE, P), abs=1.0)


def test_below_required_income_cannot_buy_without_help():
    y = cs.required_income(PRICE, P, 0.0)
    assert cs.assistance_needed(PRICE, y - 1_000, P)["income"] > 0


# --- behavior ---------------------------------------------------------------

def test_monotonic_directions():
    base = cs.required_income(PRICE, P, 0.0)
    assert cs.required_income(PRICE, replace(P, rate=P.rate + 0.01), 0.0) > base
    assert cs.required_income(PRICE * 1.1, P, 0.0) > base
    assert cs.required_income(PRICE, P, 50_000.0) < base
    assert cs.required_income(PRICE, replace(P, housing_dti=0.36), 0.0) < base
    assert cs.required_income(PRICE, replace(P, tax_rate=0.0125), 0.0) > base
    assert cs.required_income(PRICE, replace(P, insurance_monthly=300.0), 0.0) > base


def test_savings_below_cash_need_do_not_change_required_income():
    a = cs.required_income(PRICE, replace(P, savings=0.0), 0.0)
    b = cs.required_income(PRICE, replace(P, savings=25_000.0), 0.0)
    assert a == pytest.approx(b)
    assert cs.cash_gap(PRICE, replace(P, savings=0.0)) > cs.cash_gap(PRICE, replace(P, savings=25_000.0))


def test_surplus_savings_reduce_principal():
    rich = replace(P, savings=cs.cash_need(PRICE, P) + 40_000.0)
    assert cs.required_income(PRICE, rich, 0.0) < cs.required_income(PRICE, P, 0.0)
    assert cs.cash_gap(PRICE, rich) == 0.0


def test_credit_scale_matters_only_above_80_ltv():
    lo = replace(P, mi_scale=0.5)
    hi = replace(P, mi_scale=2.0)
    assert cs.required_income(PRICE, hi, 0.0) > cs.required_income(PRICE, lo, 0.0)
    big = PRICE * 0.20
    assert cs.required_income(PRICE, hi, big) == pytest.approx(
        cs.required_income(PRICE, lo, big))


def test_reach_share_is_monotone_in_income_and_reduction():
    prices = [450_000.0, 500_000.0, 600_000.0, 700_000.0]
    shares = [cs.reach_share(prices, y, P) for y in (80_000, 130_000, 200_000, 300_000)]
    assert shares == sorted(shares)
    assert cs.reach_share(prices, 130_000, P, 100_000) >= cs.reach_share(prices, 130_000, P, 0)


# --- flips, tornado, grid ---------------------------------------------------

def test_flip_point_lands_on_the_cap():
    price = 600_000.0
    # (low, high, cap): the cap must sit between required income at the two ends
    cases = {"rate": (0.0, 0.12, 150_000),            # 111,873 to 286,667
             "price_mult": (0.3, 1.5, 150_000),       # 64,562 to 298,961
             "tax_rate": (0.0, 0.03, 200_000)}        # 179,307 to 239,307
    for axis, (lo, hi, cap) in cases.items():
        f = cs.flip_point(axis, lo, hi, price, P, 0.0, cap)
        assert f["value"] is not None
        got = cs.required_at(price, P, 0.0, axis, f["value"])
        assert got == pytest.approx(cap, abs=5.0)


def test_flip_point_reports_side_when_no_crossing():
    f = cs.flip_point("rate", 0.06, 0.08, PRICE, P, 0.0, 10_000)
    assert f["value"] is None and f["side"] == "above"
    g = cs.flip_point("rate", 0.06, 0.08, PRICE, P, 0.0, 10_000_000)
    assert g["value"] is None and g["side"] == "below"


def test_tornado_is_sorted_and_nonnegative():
    rows = cs.tornado(PRICE, P, 0.0)
    swings = [r["swing"] for r in rows]
    assert swings == sorted(swings, reverse=True)
    assert all(s >= 0 for s in swings)
    assert {r["axis"] for r in rows} == set(cs.UNCERTAINTY_AXES)


def test_grid_labels_are_exhaustive():
    caps = [("tiny", 10_000, ""), ("huge", 10_000_000, "")]
    g = cs.grid_summary(PRICE, P, 0.0, 0.30, caps)
    assert g["labels"]["tiny"] == "unreachable in every cell"
    assert g["labels"]["huge"] == "reachable in every cell"
    assert g["min"] <= g["max"] and g["n"] == len(list(cs.grid_cells()))


# --- purity -----------------------------------------------------------------

def test_engine_does_not_mutate_existing_module_globals():
    before = (dps.RATE_ANNUAL, dps.HOUSING_DTI, az.MI_SCALE)
    cs.required_income(PRICE, replace(P, rate=0.09, housing_dti=0.40, mi_scale=2.0), 10_000)
    cs.grid_summary(PRICE, P, 0.0, 0.33, cs.CAPS)
    assert (dps.RATE_ANNUAL, dps.HOUSING_DTI, az.MI_SCALE) == before
