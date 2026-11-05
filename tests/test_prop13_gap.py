"""Offline tests for analysis/prop13_gap.py (no network)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "analysis"))
import prop13_gap as g  # noqa: E402

SQ = [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
SQ2 = [[[1, 0], [2, 0], [2, 1], [1, 1], [1, 0]]]
TRACTS = [{"geoid": "A", "rings": SQ}, {"geoid": "B", "rings": SQ2}]


def parcel(x, y, value=500_000, base="2000", imp=None, sqft=1000):
    return {"CENTER_LON": x, "CENTER_LAT": y, "Roll_totLandImp": value,
            "Roll_LandBaseYear": base, "Roll_ImpBaseYear": imp or base, "SQFTmain": sqft}


def test_assign_places_points_and_counts_misses():
    out, missed = g.assign([parcel(0.5, 0.5), parcel(1.5, 0.5), parcel(5, 5),
                            {"CENTER_LON": None, "CENTER_LAT": None}], TRACTS)
    assert len(out["A"]) == 1 and len(out["B"]) == 1
    assert missed == 2


def test_reset_psf_uses_market_filter():
    ps = [parcel(0.5, 0.5, 600_000, "2026"),        # kept: whole $100
          parcel(0.5, 0.5, 600_123, "2026"),        # dropped: odd value
          parcel(0.5, 0.5, 600_000, "2026", "2010"),  # dropped: land/imp base years differ
          parcel(0.5, 0.5, 600_000, "2020")]        # dropped: not a 2025-26 reset
    assert g.reset_psf(ps) == [600.0]


def test_tract_row_ratios():
    ps = [parcel(0.5, 0.5, 300_000, "2000") for _ in range(3)]
    ps += [parcel(0.5, 0.5, 600_000, "2026") for _ in range(10)]
    row = g.tract_row("A", "SGV", ps, [600_000] * 20, {"A": [100, 10, 60, 20]})
    assert row["held_ratio"] == 0.5
    assert row["psf_ratio"] == 0.5
    assert row["pct_asian"] == 0.6 and row["pct_black_latino"] == 0.3
    assert row["n_resets"] == 10


def test_too_few_loans_gives_no_hmda_ratio():
    row = g.tract_row("A", "SGV", [parcel(0.5, 0.5)], [600_000] * 5, {})
    assert row["hmda_median_value"] is None and row["stock_ratio"] is None


def test_in_study_rules():
    base = {"n_parcels": 100, "pct_asian": 0.6, "pct_black_latino": 0.3}
    assert g.in_study(base | {"region": "SGV"})
    assert not g.in_study(base | {"region": "South LA"})
    assert not g.in_study(base | {"region": "SGV", "n_parcels": 10})


def test_cohort_ratios_hold_base_year_fixed():
    ps = [parcel(0.5, 0.5, 600_000, "2026") for _ in range(10)]
    ps += [parcel(0.5, 0.5, 150_000, "1985"), parcel(0.5, 0.5, 450_000, "2015")]
    c = g.cohort_ratios({"A": ps}, {"A"})
    assert c["1989 or earlier"] == [0.25]
    assert c["2013-19"] == [0.75]


def test_boot_diff_is_deterministic():
    a, b = [1.0, 2.0, 3.0] * 5, [0.0, 1.0, 2.0] * 5
    assert g.boot_diff(a, b) == g.boot_diff(a, b)
    assert g.boot_diff(a, b)[0] == 1.0
