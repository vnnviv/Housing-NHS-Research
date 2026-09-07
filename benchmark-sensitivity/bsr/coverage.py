"""Subgroup coverage auditing via split conformal prediction.

The benchmark problem in valuation research is that no observable quantity is
the "true" value of a home, so any residual-based disparity measure inherits the
properties of whichever benchmark was chosen (see :mod:`bsr.sensitivity`).

Coverage auditing sidesteps this. Instead of asking whether predictions are too
low in some neighborhoods -- which requires knowing what "correct" would have
been -- it asks whether calibrated prediction intervals actually contain the
prices at which homes *did* sell, at the advertised rate, within each subgroup.

That question is answerable from realized transactions alone. Undercoverage in a
subgroup is evidence the model is systematically worse there, and it is stated
without ever asserting what any house is worth.

Split conformal gives distribution-free *marginal* coverage under exchangeability.
It gives no subgroup guarantee, which is exactly why the audit is informative: a
model can hit its marginal target while badly undercovering a subgroup.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

__all__ = ["conformal_halfwidth", "coverage_by_group", "coverage_audit", "CoverageReport"]


def conformal_halfwidth(y_cal, pred_cal, alpha=0.10):
    """Split-conformal interval half-width from calibration residuals.

    Uses the finite-sample corrected quantile level ``ceil((n+1)(1-alpha))/n``,
    which is what delivers the marginal coverage guarantee rather than the naive
    empirical quantile.

    Parameters
    ----------
    y_cal, pred_cal : array_like
        Calibration outcomes and predictions, on whatever scale the intervals
        should be symmetric in. For prices, pass logs.
    alpha : float
        Miscoverage rate; ``alpha=0.10`` targets 90% coverage.

    Returns
    -------
    float
    """
    y_cal = np.asarray(y_cal, dtype=float)
    pred_cal = np.asarray(pred_cal, dtype=float)
    resid = np.abs(y_cal - pred_cal)
    n = resid.size
    if n == 0:
        raise ValueError("empty calibration set")
    level = min(1.0, np.ceil((n + 1) * (1 - alpha)) / n)
    return float(np.quantile(resid, level, method="higher"))


def coverage_by_group(y, pred, halfwidth, group):
    """Empirical coverage of the symmetric interval, overall and per group.

    Returns
    -------
    dict
        ``{"marginal": float, <group value>: float, ...}``
    """
    y = np.asarray(y, dtype=float)
    pred = np.asarray(pred, dtype=float)
    group = np.asarray(group)
    covered = np.abs(y - pred) <= halfwidth
    out = {"marginal": float(covered.mean())}
    for g in np.unique(group):
        out[g] = float(covered[group == g].mean())
    return out


@dataclass
class CoverageReport:
    """Result of :func:`coverage_audit`."""

    target: float = 0.90
    halfwidth: float = float("nan")
    coverage: dict = field(default_factory=dict)

    @property
    def gaps(self) -> dict:
        """Signed shortfall from target per group; negative means undercoverage."""
        return {g: c - self.target for g, c in self.coverage.items() if g != "marginal"}

    @property
    def worst_gap(self) -> float:
        g = self.gaps
        return min(g.values()) if g else float("nan")

    @property
    def spread(self) -> float:
        """Largest minus smallest subgroup coverage. The number that matters."""
        g = [c for k, c in self.coverage.items() if k != "marginal"]
        return float(max(g) - min(g)) if g else float("nan")

    def __str__(self) -> str:
        keys = [k for k in self.coverage if k != "marginal"]
        width = max((len(str(k)) for k in keys), default=6)
        lines = [f"  target coverage: {self.target:.0%}   half-width: {self.halfwidth:.3f}"]
        lines.append(f"  {'marginal':<{width}}  {self.coverage.get('marginal', float('nan')):.1%}")
        for k in keys:
            c = self.coverage[k]
            flag = "   <-- undercoverage" if c < self.target - 0.04 else ""
            lines.append(f"  {str(k):<{width}}  {c:.1%}{flag}")
        lines.append(f"  subgroup spread: {self.spread:.1%}")
        return "\n".join(lines)


def coverage_audit(y_cal, pred_cal, y_test, pred_test, group_test, alpha=0.10):
    """Calibrate on one split, then audit subgroup coverage on another.

    Parameters
    ----------
    y_cal, pred_cal : array_like
        Calibration split. Must not overlap the test split.
    y_test, pred_test, group_test : array_like
        Evaluation split and its group labels.
    alpha : float
        Miscoverage rate.

    Returns
    -------
    CoverageReport
    """
    q = conformal_halfwidth(y_cal, pred_cal, alpha=alpha)
    return CoverageReport(
        target=1 - alpha,
        halfwidth=q,
        coverage=coverage_by_group(y_test, pred_test, q, group_test),
    )
