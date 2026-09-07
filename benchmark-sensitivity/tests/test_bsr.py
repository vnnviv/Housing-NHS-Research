import numpy as np
import pytest

from bsr import (
    benchmark_sensitivity_ratio,
    conformal_halfwidth,
    coverage_audit,
    coverage_by_group,
    disparity,
    sensitivity_report,
)


# --- disparity ---------------------------------------------------------------

def test_disparity_is_zero_for_identical_groups():
    m = np.array([1.0, 2.0, 1.0, 2.0])
    g = np.array([0, 0, 1, 1])
    assert disparity(m, g) == pytest.approx(0.0)


def test_disparity_sign_follows_focal_minus_reference():
    m = np.array([0.0, 0.0, 1.0, 1.0])
    g = np.array([0, 0, 1, 1])
    assert disparity(m, g, focal=1, reference=0) == pytest.approx(1.0)
    assert disparity(m, g, focal=0, reference=1) == pytest.approx(-1.0)


def test_disparity_rejects_empty_group():
    with pytest.raises(ValueError):
        disparity(np.array([1.0, 2.0]), np.array([0, 0]), focal=1, reference=0)


# --- BSR ---------------------------------------------------------------------

def test_bsr_is_one_when_all_benchmarks_agree():
    assert benchmark_sensitivity_ratio([0.05, 0.05, -0.05]) == pytest.approx(1.0)


def test_bsr_grows_with_disagreement():
    assert benchmark_sensitivity_ratio([0.01, 0.10]) == pytest.approx(10.0)


def test_bsr_ignores_exact_zeros_in_denominator():
    # A benchmark yielding exactly zero should not send BSR to infinity.
    assert np.isfinite(benchmark_sensitivity_ratio([0.0, 0.02, 0.04]))


def test_bsr_is_nan_when_every_estimate_is_zero():
    assert np.isnan(benchmark_sensitivity_ratio([0.0, 0.0]))


# --- sensitivity_report ------------------------------------------------------

def test_report_detects_sign_flip():
    g = np.repeat([0, 1], 50)
    up = np.where(g == 1, 1.0, 0.0)
    down = np.where(g == 1, 0.0, 1.0)
    rep = sensitivity_report({"a": up, "b": down}, g)
    assert rep.sign_flip is True
    assert rep.robust is False


def test_report_marks_agreeing_benchmarks_robust():
    g = np.repeat([0, 1], 50)
    a = np.where(g == 1, 0.10, 0.0)
    b = np.where(g == 1, 0.11, 0.0)
    rep = sensitivity_report({"a": a, "b": b}, g)
    assert rep.sign_flip is False
    assert rep.bsr == pytest.approx(1.1)
    assert rep.robust is True


def test_report_requires_a_benchmark():
    with pytest.raises(ValueError):
        sensitivity_report({}, np.array([0, 1]))


# --- conformal coverage ------------------------------------------------------

def test_marginal_coverage_hits_target_on_exchangeable_data():
    rng = np.random.default_rng(0)
    y = rng.normal(size=8000)
    pred = np.zeros_like(y)
    q = conformal_halfwidth(y[:4000], pred[:4000], alpha=0.10)
    cov = coverage_by_group(y[4000:], pred[4000:], q, np.zeros(4000))
    assert cov["marginal"] == pytest.approx(0.90, abs=0.02)


def test_conformal_halfwidth_is_conservative_for_tiny_calibration_sets():
    # With n small, ceil((n+1)(1-alpha))/n can exceed 1 and must be clipped.
    q = conformal_halfwidth(np.array([0.0, 1.0]), np.array([0.0, 0.0]), alpha=0.10)
    assert np.isfinite(q) and q >= 1.0


def test_conformal_halfwidth_rejects_empty_calibration():
    with pytest.raises(ValueError):
        conformal_halfwidth(np.array([]), np.array([]))


def test_audit_detects_subgroup_undercoverage():
    rng = np.random.default_rng(1)
    n = 12000
    group = rng.integers(0, 2, n)
    # Group 1 is three times noisier, so a shared interval undercovers it.
    y = rng.normal(0, 1 + 2 * group, n)
    pred = np.zeros_like(y)
    cal, test = slice(0, n // 2), slice(n // 2, None)
    rep = coverage_audit(y[cal], pred[cal], y[test], pred[test], group[test], alpha=0.10)
    assert rep.coverage[0] > rep.coverage[1]
    assert rep.worst_gap < 0
    assert rep.spread > 0.05


def test_audit_reports_no_spread_when_groups_are_alike():
    rng = np.random.default_rng(2)
    n = 12000
    group = rng.integers(0, 2, n)
    y = rng.normal(0, 1, n)
    pred = np.zeros_like(y)
    cal, test = slice(0, n // 2), slice(n // 2, None)
    rep = coverage_audit(y[cal], pred[cal], y[test], pred[test], group[test], alpha=0.10)
    assert rep.spread < 0.05
