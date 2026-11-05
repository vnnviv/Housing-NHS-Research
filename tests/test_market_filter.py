"""Round-value filter for reset Assessor values (FINDINGS 2026-11-05)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "analysis"))
import downpayment_scenarios as dps  # noqa: E402


def test_round_price_same_year_kept():
    assert dps.market_price(605_000, "2026") == 605_000
    assert dps.market_price(622_200, "2026") == 622_200


def test_indexed_one_year_is_converted_back():
    assert dps.market_price(round(587_300 * 1.02), "2025") == 587_300   # 599,046
    assert dps.market_price(round(641_900 * 1.02), "2025") == 641_900   # 654,738


def test_value_round_both_ways_is_read_as_unindexed():
    # 612,000 is whole-$100 and also 600,000 x 1.02. On the 2026 roll many 2025 base-year
    # values are not indexed, so the unindexed reading wins.
    assert dps.market_price(612_000, "2025") == 612_000


def test_indexing_not_allowed_for_current_base_year():
    # 612,000 = 600,000 x 1.02, but a 2026 base year on the 2026 roll has no indexing step;
    # it is still a whole-$100 value, so it stays as itself.
    assert dps.market_price(612_000, "2026") == 612_000
    assert dps.market_price(306_186, "2026") is None


def test_odd_values_dropped():
    assert dps.market_price(306_186, "2025") is None
    assert dps.market_price(593_382, "2025") is None


def test_bad_base_year_falls_back_to_no_indexing():
    assert dps.market_price(500_000, None) == 500_000
    assert dps.market_price(round(587_300 * 1.02), "") is None


def test_clean_prices_counts_add_up():
    rows = [[150_000, 0, 0, 0, "2026"], [605_000, 0, 0, 0, "2026"],
            [599_046, 0, 0, 0, "2025"], [306_186, 0, 0, 0, "2025"]]
    prices, kept, c = dps.clean_prices(rows)
    assert prices == [587_300, 605_000]
    assert len(kept) == 2
    assert c == {"pulled": 4, "below_floor": 1, "not_market": 1, "kept": 2}


def test_compton_file_counts():
    prices, kept, c = dps.clean_prices(dps.load_rows())
    assert c["pulled"] == c["below_floor"] + c["not_market"] + c["kept"]
    assert c["kept"] >= 100
