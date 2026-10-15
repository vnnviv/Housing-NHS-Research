"""Tests for analysis/assistance_sizing.py.

Run from the repo root:  python -m pytest tests
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "analysis"))

import assistance_sizing as az          # noqa: E402
import downpayment_scenarios as dps     # noqa: E402

PRICE = 600_000.0
INCOMES = list(dps.INCOME_TIERS.values())


def test_mi_banding_matches_existing_model_at_its_ltvs():
    for _label, down, is_fha in dps.SCENARIOS:
        ltv = 1 - down
        assert az.mi_rate_by_ltv(ltv, is_fha) == dps.mi_rate_for(down, is_fha)


def test_payment_matches_existing_model():
    for _label, down, is_fha in dps.SCENARIOS:
        mine = az.monthly_payment(PRICE, PRICE * (1 - down), is_fha)
        theirs = dps.total_monthly(PRICE, down, is_fha)
        assert mine == pytest.approx(theirs, abs=0.01)


@pytest.mark.parametrize("income", INCOMES)
@pytest.mark.parametrize("down,is_fha", [(0.03, False), (0.05, False), (0.10, False),
                                         (0.20, False), (dps.FHA_DOWN, True)])
def test_zero_income_gap_at_existing_max_price(income, down, is_fha):
    """At the price the existing model says the tier can just afford, no
    principal reduction should be needed."""
    price = dps.max_purchase_price(income, down, is_fha)
    r = az.assistance_needed(price, income, down, is_fha, savings=10**9)
    assert r["reduction"] == pytest.approx(0.0, abs=1.0)
    assert r["a_income"] == pytest.approx(0.0, abs=1.0)


@pytest.mark.parametrize("income", INCOMES)
def test_reduction_lands_exactly_on_budget(income):
    r = az.assistance_needed(PRICE, income, 0.03, False, 0)
    assert r["reduction"] > 0
    pay = az.monthly_payment(PRICE, PRICE * 0.97 - r["reduction"], False)
    budget = income * dps.HOUSING_DTI / 12.0
    assert pay <= budget + 1e-6
    # and a dollar less reduction would break the budget, unless the solution
    # sits on a mortgage-insurance cliff (e.g. 80% LTV)
    worse = az.monthly_payment(PRICE, PRICE * 0.97 - r["reduction"] + 1.0, False)
    assert worse > budget - 1e-6


@pytest.mark.parametrize("income", INCOMES)
def test_total_identity(income):
    s = 12_345.0
    r = az.assistance_needed(PRICE, income, 0.03, False, s)
    cap, _ = az.max_base_loan(PRICE, income, False)
    target = min(PRICE * 0.97, cap)
    expected = max(0.0, PRICE + PRICE * dps.CLOSING_COST_RATE - target - s)
    assert r["total"] == pytest.approx(expected, abs=0.01)
    assert r["total"] == pytest.approx(r["a_cash"] + r["a_income"])


def test_down_payment_choice_drops_out_of_conventional_total():
    inc = dps.INCOME_TIERS["Lower income (= moderate)"]
    a = az.assistance_needed(PRICE, inc, 0.03, False, 0)
    b = az.assistance_needed(PRICE, inc, 0.05, False, 0)
    assert a["total"] == pytest.approx(b["total"], abs=0.01)
    assert a["a_cash"] != pytest.approx(b["a_cash"])     # only the split differs


def test_savings_move_total_dollar_for_dollar():
    inc = dps.INCOME_TIERS["Area median income"]
    a = az.assistance_needed(PRICE, inc, 0.03, False, 0)["total"]
    b = az.assistance_needed(PRICE, inc, 0.03, False, 10_000)["total"]
    assert a - b == pytest.approx(10_000, abs=0.01)


def test_monotone_in_price_income_and_rate():
    inc = dps.INCOME_TIERS["Area median income"]
    prices = [450_000, 500_000, 550_000, 600_000, 650_000, 700_000]
    totals = [az.assistance_needed(p, inc, 0.03, False, 10_000)["total"] for p in prices]
    assert totals == sorted(totals)
    by_income = [az.assistance_needed(PRICE, i, 0.03, False, 10_000)["total"] for i in sorted(INCOMES)]
    assert by_income == sorted(by_income, reverse=True)
    low = az.with_rate(0.06, lambda: az.assistance_needed(PRICE, inc, 0.03, False, 10_000)["total"])
    high = az.with_rate(0.08, lambda: az.assistance_needed(PRICE, inc, 0.03, False, 10_000)["total"])
    assert high > low


def test_infeasible_when_taxes_and_insurance_exceed_budget():
    r = az.assistance_needed(PRICE, 20_000, 0.03, False, 0)
    assert r["feasible"] is False
    assert r["reduction"] == pytest.approx(PRICE * 0.97)


def test_rate_helper_restores_global():
    before = dps.RATE_ANNUAL
    az.with_rate(0.09, lambda: None)
    assert dps.RATE_ANNUAL == before


def test_mi_scale_changes_payment_but_restores():
    saved = az.MI_SCALE
    hi = az.with_settings(lambda: az.monthly_payment(PRICE, PRICE * 0.97, False), mi_scale=1.667)
    base = az.monthly_payment(PRICE, PRICE * 0.97, False)
    assert hi > base
    assert az.MI_SCALE == saved


def test_credit_band_does_not_change_total_when_loan_ends_at_or_below_80_ltv():
    inc = dps.INCOME_TIERS["Lower income (= moderate)"]
    totals = [az.with_settings(lambda: az.assistance_needed(PRICE, inc, 0.03, False, 10_000)["total"],
                               mi_scale=r / dps.PMI_BY_LTV[0.97]) for _, r in az.FICO_BANDS]
    assert max(totals) - min(totals) == pytest.approx(0.0, abs=1.0)


def test_with_settings_restores_rate_and_dti():
    r0, d0 = dps.RATE_ANNUAL, dps.HOUSING_DTI
    az.with_settings(lambda: None, rate=0.09, dti=0.40, mi_scale=2.0)
    assert (dps.RATE_ANNUAL, dps.HOUSING_DTI, az.MI_SCALE) == (r0, d0, 1.0)
