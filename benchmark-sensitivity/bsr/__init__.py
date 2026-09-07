"""Diagnostics for disparity estimates that depend on a contested benchmark.

Two tools:

``bsr.sensitivity``
    Benchmark Sensitivity Ratio -- how much a measured disparity depends on
    which benchmark the analyst chose.

``bsr.coverage``
    Subgroup coverage auditing via split conformal prediction -- locating
    model failure without asserting any ground truth.
"""

from .coverage import CoverageReport, conformal_halfwidth, coverage_audit, coverage_by_group
from .sensitivity import (
    SensitivityReport,
    benchmark_sensitivity_ratio,
    disparity,
    sensitivity_report,
)

__version__ = "0.1.0"

__all__ = [
    "disparity",
    "benchmark_sensitivity_ratio",
    "sensitivity_report",
    "SensitivityReport",
    "conformal_halfwidth",
    "coverage_by_group",
    "coverage_audit",
    "CoverageReport",
]
