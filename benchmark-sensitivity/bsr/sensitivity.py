"""Benchmark Sensitivity Ratio (BSR).

A disparity estimate is only as good as the benchmark it is measured against.
When no ground truth exists -- as with home values, where every candidate
benchmark (sale price, appraised value, a model's own fit) is itself contested
-- the same data can yield disparity estimates that differ in magnitude and
even in sign depending on which benchmark the analyst picked.

BSR quantifies that fragility:

    BSR = max_b |D(b)| / min_b |D(b)|

over a class B of individually defensible benchmarks. BSR near 1 means the
finding is robust to benchmark choice. A large BSR, or a sign flip across B,
means the finding is a property of the benchmark rather than of the world.

The construction follows the Leakage Inflation Ratio (Chan, Husain & Si), which
applies the same idea to train/test split regimes in time-series forecasting:
compute one metric under two or more regimes, and let the ratio expose that the
metric was measuring the regime.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

import numpy as np

__all__ = ["disparity", "benchmark_sensitivity_ratio", "sensitivity_report", "SensitivityReport"]


def disparity(measure, group, focal=1, reference=0):
    """Mean difference in ``measure`` between the focal and reference groups.

    Parameters
    ----------
    measure : array_like
        Per-observation error measure, e.g. ``pred / sale_price - 1``.
    group : array_like
        Group label per observation.
    focal, reference : hashable
        Which group values to contrast. Result is ``mean(focal) - mean(reference)``.

    Returns
    -------
    float
    """
    measure = np.asarray(measure, dtype=float)
    group = np.asarray(group)
    f = measure[group == focal]
    r = measure[group == reference]
    if f.size == 0 or r.size == 0:
        raise ValueError(f"empty group: focal n={f.size}, reference n={r.size}")
    return float(f.mean() - r.mean())


def benchmark_sensitivity_ratio(estimates, tol=1e-12):
    """Ratio of the largest to smallest absolute disparity estimate.

    Parameters
    ----------
    estimates : sequence of float
        One disparity estimate per benchmark.
    tol : float
        Estimates with absolute value at or below ``tol`` are excluded from the
        denominator; a benchmark that yields exactly zero would otherwise send
        BSR to infinity and tell you nothing you did not already know.

    Returns
    -------
    float
        ``inf`` if every estimate is within ``tol`` of zero is *not* returned --
        that case yields ``nan``, since no ratio is meaningful.
    """
    vals = np.abs(np.asarray(list(estimates), dtype=float))
    nz = vals[vals > tol]
    if nz.size == 0:
        return float("nan")
    return float(nz.max() / nz.min())


@dataclass
class SensitivityReport:
    """Result of :func:`sensitivity_report`."""

    estimates: dict = field(default_factory=dict)
    bsr: float = float("nan")
    sign_flip: bool = False
    lo: float = float("nan")
    hi: float = float("nan")

    def __str__(self) -> str:
        width = max((len(k) for k in self.estimates), default=0)
        lines = [f"  {k:<{width}}  {v:+.4f}" for k, v in self.estimates.items()]
        lines.append("  " + "-" * (width + 10))
        lines.append(f"  {'range':<{width}}  {self.lo:+.4f} to {self.hi:+.4f}")
        lines.append(f"  {'sign flips':<{width}}  {'YES' if self.sign_flip else 'no'}")
        lines.append(f"  {'BSR':<{width}}  {self.bsr:.2f}")
        return "\n".join(lines)

    @property
    def robust(self) -> bool:
        """True when the finding survives benchmark choice by a conventional reading.

        Heuristic, not a test: BSR under 2 and no sign flip. Report the full
        specification curve alongside this; do not let one boolean stand in for it.
        """
        return (not self.sign_flip) and self.bsr < 2.0


def sensitivity_report(benchmarks: Mapping[str, np.ndarray], group, focal=1, reference=0):
    """Compute per-benchmark disparities, the range, sign-flip flag, and BSR.

    Parameters
    ----------
    benchmarks : mapping of str to array_like
        Name -> per-observation error measure under that benchmark.
    group, focal, reference
        Passed through to :func:`disparity`.

    Returns
    -------
    SensitivityReport
    """
    if not benchmarks:
        raise ValueError("need at least one benchmark")
    ests = {name: disparity(m, group, focal, reference) for name, m in benchmarks.items()}
    vals = np.array(list(ests.values()), dtype=float)
    return SensitivityReport(
        estimates=ests,
        bsr=benchmark_sensitivity_ratio(vals),
        sign_flip=bool(vals.min() < 0 < vals.max()),
        lo=float(vals.min()),
        hi=float(vals.max()),
    )
