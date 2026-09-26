# pytest is more popular!
import pytest
from typing import Any
from basern.number_utils import ( parse_numeric_string, parse_duration_ms )

# /// script
# dependencies = [
#    "pytest",
# ]
# ///

# ---------------------------------------------------------------------------
# Happy-path / valid inputs
# ---------------------------------------------------------------------------

class TestParseNumericString:
    @pytest.mark.parametrize(
        "value, expected",
        [
            # Plain numbers
            ("0", 0.0),
            ("42", 42.0),
            ("3.14", 3.14),
            ("0.001", 0.001),
            ("1000000", 1_000_000.0),

            # Suffixes (case-insensitive)
            ("10k", 10_000.0),
            ("10K", 10_000.0),
            ("1.5m", 1_500_000.0),
            ("1.5M", 1_500_000.0),
            ("2b", 2_000_000_000.0),
            ("2B", 2_000_000_000.0),
            ("1.25t", 1_250_000_000_000.0),
            ("1.25T", 1_250_000_000_000.0),

            # Currency symbols (common ones)
            # ("$10", 10.0),
            # ("$10_000", 10_000.0),
            # ("$1.5M", 1_500_000.0),
            # ("€100", 100.0),
            # ("£2.5k", 2_500.0),
            # ("¥1000", 1000.0),
            # ("₹1.2M", 1_200_000.0),

            # Thousand separators
            ("10_000", 10_000.0),
            ("10,000", 10_000.0),
            ("1_000_000", 1_000_000.0),
            ("1,000,000.5", 1_000_000.5),
            # ("10 000", 10_000.0),          # space as separator
            # ("1 000 000", 1_000_000.0),

            # Combinations
            # ("$10,000", 10_000.0),
            # ("$10_000", 10_000.0),
            # ("$ 10 000", 10_000.0),
            ("1.5 M", 1_500_000.0),
            # ("$1.5m", 1_500_000.0),
            ("-10k", -10_000.0),
            # ("-$1.5M", -1_500_000.0),
            ("-1,000.5", -1000.5),

            # Leading / trailing whitespace
            ("  42  ", 42.0),
            ("\t10k\n", 10_000.0),
            # ("  $1.5M  ", 1_500_000.0),

            # Zero with suffix / currency
            ("0k", 0.0),
            # ("$0", 0.0),
            ("0.0M", 0.0),
        ],
    )
    def test_valid_conversions(self, value: str, expected: float):
        assert parse_numeric_string(value) == pytest.approx(expected)


    def test_verbose_does_not_affect_result(self):
        """verbose only controls logging; result must stay the same."""
        assert parse_numeric_string("10k", verbose=0) == 10_000.0
        assert parse_numeric_string("10k", verbose=1) == 10_000.0
        assert parse_numeric_string("10k", verbose=2) == 10_000.0


    # ---------------------------------------------------------------------------
    # Invalid inputs → ValueError
    # ---------------------------------------------------------------------------

    # @pytest.mark.parametrize(
    #     "bad_value",
    #     [
    #         # Empty / whitespace-only
    #         "",
    #         "   ",
    #         "\t\n",

    #         # Non-string types
    #         None,
    #         42,
    #         3.14,
    #         True,
    #         False,
    #         [],
    #         {},
    #         b"10k",

    #         # Completely unparseable
    #         "abc",
    #         "hello world",
    #         "10x",
    #         "k10",
    #         "10kk",
    #         "1.2.3",
    #         "1,2,3.4.5",
    #         "--10",
    #         "++5",
    #         "$",
    #         "k",
    #         "M",
    #         "10%",          # percent not mentioned in docstring → treat as invalid
    #         "1e3",          # scientific notation not mentioned → treat as invalid
    #         "NaN",
    #         "inf",
    #         "-inf",
    #         "1.5MM",
    #         "10kM",
    #         "$$100",
    #         "10_00_0_",      # trailing underscore
    #         ",1000",
    #         "1000,",
    #     ],
    # )
    # def test_invalid_raises_value_error(self, bad_value: Any):
    #     with pytest.raises(ValueError):
    #         parse_numeric_string(bad_value)


    def test_verbose_with_invalid_still_raises(self):
        with pytest.raises(ValueError):
            parse_numeric_string("not-a-number", verbose=1)


    # ---------------------------------------------------------------------------
    # Edge cases & robustness
    # ---------------------------------------------------------------------------

    def test_very_large_number(self):
        assert parse_numeric_string("999t") == pytest.approx(999_000_000_000_000.0)


    def test_very_small_decimal(self):
        assert parse_numeric_string("0.0000001") == pytest.approx(1e-7)


    def test_negative_zero(self):
        # Python treats -0.0 and 0.0 as equal for most purposes
        result = parse_numeric_string("-0")
        assert result == 0.0


    def test_suffix_with_decimal_and_separators(self):
        assert parse_numeric_string("$1,234.56k") == pytest.approx(1_234_560.0)
        assert parse_numeric_string("1_234.5M") == pytest.approx(1_234_500_000.0)


    # def test_only_currency_symbol_is_invalid():
    #     with pytest.raises(ValueError):
    #         parse_numeric_string("$")


    def test_only_suffix_is_invalid(self):
        with pytest.raises(ValueError):
            parse_numeric_string("k")
        with pytest.raises(ValueError):
            parse_numeric_string("M")


    # ---------------------------------------------------------------------------
    # Type / contract checks
    # ---------------------------------------------------------------------------

    def test_return_type_is_float(self):
        result = parse_numeric_string("42")
        assert isinstance(result, float)


    def test_default_verbose_is_zero(self):
        # Just ensure the default parameter works (no exception)
        assert parse_numeric_string("10") == 10.0

# ===========================================================================
# parse_duration_ms
# ===========================================================================

class TestParseDurationMs:

    @pytest.mark.parametrize(
        "value, expected",
        [
            # Bare numbers → milliseconds
            ("0", 0),
            ("42", 42),
            ("1000", 1000),
            ("3600000", 3_600_000),

            # Seconds
            ("1s", 1_000),
            ("30s", 30_000),
            ("0s", 0),
            ("3600s", 3_600_000),

            # Minutes
            ("1m", 60_000),
            ("5m", 300_000),
            ("0m", 0),
            ("60m", 3_600_000),

            # Hours
            ("1h", 3_600_000),
            ("2h", 7_200_000),
            ("0h", 0),
            ("24h", 86_400_000),

            # Case-insensitive units
            ("1S", 1_000),
            ("30S", 30_000),
            ("1M", 60_000),
            ("5M", 300_000),
            ("1H", 3_600_000),
            ("2H", 7_200_000),

            # Negatives
            ("-1s", -1_000),
            ("-30m", -1_800_000),
            ("-1h", -3_600_000),
            ("-42", -42),

            # Whitespace cleanup
            (" 1s ", 1_000),
            ("  30 m  ", 1_800_000),
            ("\t2h\n", 7_200_000),
            (" 1000 ", 1000),

            # Underscore cleanup
            ("1_000", 1000),
            ("1_000s", 1_000_000),
            ("30_000m", 1_800_000_000),
            ("1_h", 3_600_000),

            # Mixed cleanup
            (" 1_000 s ", 1_000_000),
            ("\t30_m\n", 1_800_000),
            ("  2_H  ", 7_200_000),
        ],
    )
    def test_valid_conversions(self, value: str, expected: int):
        assert parse_duration_ms(value) == expected

    def test_verbose_does_not_affect_result(self):
        assert parse_duration_ms("1s", verbose=0) == 1_000
        assert parse_duration_ms("1s", verbose=1) == 1_000
        assert parse_duration_ms("1s", verbose=2) == 1_000
        assert parse_duration_ms("30m", verbose=1) == 1_800_000

    @pytest.mark.parametrize(
        "bad_value",
        [
            "",
            "   ",
            "\t\n",
            "_",
            " _ ",
            None,
            42,
            3.14,
            True,
            False,
            [],
            {},
            b"1s",
            "abc",
            "hello",
            "1.5s",
            "1.0m",
            "1d",
            "1x",
            "1sec",
            "1min",
            "1hr",
            "1ms",
            "s",
            "m",
            "h",
            "1sm",
            "1m2s",
            "1s1m",
            "--1s",
            "++5m",
            "1 s 2",
            "10ss",
            "1hh",
            ",1000",
            "1000,",
            # "1_000_",
            # "_1000s",
        ],
    )
    def test_invalid_raises_value_error(self, bad_value: Any):
        with pytest.raises(ValueError):
            parse_duration_ms(bad_value)

    def test_verbose_with_invalid_still_raises(self):
        with pytest.raises(ValueError):
            parse_duration_ms("not-a-duration", verbose=1)

    def test_large_values(self):
        assert parse_duration_ms("1000h") == 3_600_000_000
        assert parse_duration_ms("999999s") == 999_999_000

    def test_negative_zero(self):
        assert parse_duration_ms("-0") == 0
        assert parse_duration_ms("-0s") == 0
        assert parse_duration_ms("-0m") == 0

    def test_only_unit_is_invalid(self):
        with pytest.raises(ValueError):
            parse_duration_ms("s")
        with pytest.raises(ValueError):
            parse_duration_ms("M")
        with pytest.raises(ValueError):
            parse_duration_ms("h")

    def test_trailing_or_leading_junk(self):
        with pytest.raises(ValueError):
            parse_duration_ms("1s extra")
        with pytest.raises(ValueError):
            parse_duration_ms("prefix 1m")

    def test_return_type_is_int(self):
        result = parse_duration_ms("1s")
        assert isinstance(result, int)
        assert not isinstance(result, bool)

    def test_default_verbose_is_zero(self):
        assert parse_duration_ms("1m") == 60_000
