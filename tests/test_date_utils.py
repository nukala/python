import pytest

from datetime import date, timedelta
from basern.wknum import parse_date   # adjust import as needed

# /// script
# dependencies = [
#    "pytest",
# ]
# ///

TODAY = date.today()


class TestParseDateValid4Digit:
    def test_iso_dash(self):
        assert parse_date("2023-10-05") == date(2023, 10, 5)

    def test_iso_slash(self):
        assert parse_date("2023/10/05") == date(2023, 10, 5)

    def test_iso_nosep(self):
        assert parse_date("20231005") == date(2023, 10, 5)

    def test_day_first_slash(self):
        assert parse_date("05/10/2023") == date(2023, 10, 5)

    def test_day_first_dash(self):
        assert parse_date("05-10-2023") == date(2023, 10, 5)

    def test_day_first_nosep(self):
        assert parse_date("05102023") == date(2023, 10, 5)

    def test_month_first_slash(self):
        assert parse_date("10/05/2023") == date(2023, 10, 5)

    def test_month_first_dash(self):
        assert parse_date("10-05-2023") == date(2023, 10, 5)

    def test_month_first_nosep(self):
        assert parse_date("10052023") == date(2023, 10, 5)


class TestParseDateValid2Digit:
    def test_iso_dash_yy(self):
        assert parse_date("23-10-05") == date(2023, 10, 5)

    def test_iso_slash_yy(self):
        assert parse_date("23/10/05") == date(2023, 10, 5)

    def test_iso_nosep_yy(self):
        assert parse_date("231005") == date(2023, 10, 5)

    def test_day_first_slash_yy(self):
        assert parse_date("05/10/23") == date(2023, 10, 5)

    def test_day_first_dash_yy(self):
        assert parse_date("05-10-23") == date(2023, 10, 5)

    def test_day_first_nosep_yy(self):
        assert parse_date("051023") == date(2023, 10, 5)

    def test_month_first_slash_yy(self):
        assert parse_date("10/05/23") == date(2023, 10, 5)

    def test_month_first_dash_yy(self):
        assert parse_date("10-05-23") == date(2023, 10, 5)

    def test_month_first_nosep_yy(self):
        assert parse_date("100523") == date(2023, 10, 5)

    def test_yy_2000_boundary(self):
        # strptime %y: 00-68 → 2000-2068, 69-99 → 1969-1999
        assert parse_date("00-01-01") == date(2000, 1, 1)
        assert parse_date("68-12-31") == date(2068, 12, 31)
        assert parse_date("69-01-01") == date(1969, 1, 1)
        assert parse_date("99-12-31") == date(1999, 12, 31)


class TestParseDateWhitespaceAndLeap:
    def test_leading_trailing_whitespace(self):
        assert parse_date("  2023-10-05  ") == date(2023, 10, 5)

    def test_leap_year_4digit(self):
        assert parse_date("2024-02-29") == date(2024, 2, 29)

    def test_leap_year_2digit(self):
        assert parse_date("24-02-29") == date(2024, 2, 29)

    def test_end_of_year(self):
        assert parse_date("2023-12-31") == date(2023, 12, 31)

    def test_start_of_year(self):
        assert parse_date("2023-01-01") == date(2023, 1, 1)


class TestParseDateInvalid:
    def test_empty_string(self):
        assert parse_date("") == TODAY

    def test_whitespace_only(self):
        assert parse_date("   ") == TODAY

    def test_garbage(self):
        assert parse_date("not-a-date") == TODAY

    def test_partial(self):
        assert parse_date("2023-10") == TODAY

    def test_impossible_day(self):
        assert parse_date("2023-02-30") == TODAY

    def test_impossible_month(self):
        assert parse_date("2023-13-01") == TODAY

    def test_non_leap_29_feb(self):
        assert parse_date("2023-02-29") == TODAY

    def test_wrong_length_nosep(self):
        assert parse_date("2023105") == TODAY
        assert parse_date("202310055") == TODAY
        assert parse_date("23105") == TODAY

    def test_letters_mixed(self):
        assert parse_date("2023-10-0a") == TODAY

    def test_only_numbers_wrong(self):
        assert parse_date("99999999") == TODAY


class TestParseDateDefaultParameter:
    def test_custom_default(self):
        fallback = date(2000, 1, 1)
        assert parse_date("invalid", default=fallback) == fallback

    def test_custom_default_with_valid(self):
        fallback = date(2000, 1, 1)
        assert parse_date("2023-10-05", default=fallback) == date(2023, 10, 5)

    def test_default_is_today(self):
        result = parse_date("bad")
        assert result == date.today()


# class TestParseDateVerbosity:
#     def test_verbosity_0_no_output(self, capsys):
#         parse_date("bad-input", verbosity=0)
#         captured = capsys.readouterr()
#         assert captured.out == ""

#     def test_verbosity_1_no_output(self, capsys):
#         parse_date("bad-input", verbosity=1)
#         captured = capsys.readouterr()
#         assert captured.out == ""

#     def test_verbosity_2_prints_error(self, capsys):
#         parse_date("bad-input", verbosity=2)
#         captured = capsys.readouterr()
#         assert "could not parse 'bad-input'" in captured.out

#     def test_verbosity_2_empty_input(self, capsys):
#         parse_date("", verbosity=2)
#         captured = capsys.readouterr()
#         assert "empty or non-string input" in captured.out

#     def test_verbosity_2_valid_input_silent(self, capsys):
#         parse_date("2023-10-05", verbosity=2)
#         captured = capsys.readouterr()
#         assert captured.out == ""


class TestParseDateEdgeCases:
    def test_zero_padded_required(self):
        assert parse_date("2023-01-05") == date(2023, 1, 5)
        assert parse_date("05/10/2023") == date(2023, 10, 5)
        # unpadded single digits fall through to default
        assert parse_date("2023-1-5") == TODAY
        assert parse_date("5/10/2023") == TODAY

    def test_future_date(self):
        future = (date.today() + timedelta(days=400)).strftime("%Y-%m-%d")
        assert parse_date(future) == date.today() + timedelta(days=400)

    def test_very_old_date(self):
        assert parse_date("1900-01-01") == date(1900, 1, 1)

    def test_year_2000(self):
        assert parse_date("2000-02-29") == date(2000, 2, 29)


@pytest.mark.parametrize(
    "raw, expected",
    [
        # 4-digit
        ("2024-03-15", date(2024, 3, 15)),
        ("15/03/2024", date(2024, 3, 15)),
        ("03/15/2024", date(2024, 3, 15)),
        ("20240315",   date(2024, 3, 15)),
        ("15032024",   date(2024, 3, 15)),
        ("03152024",   date(2024, 3, 15)),
        # 2-digit
        ("24-03-15",   date(2024, 3, 15)),
        ("15/03/24",   date(2024, 3, 15)),
        ("03/15/24",   date(2024, 3, 15)),
        ("240315",     date(2024, 3, 15)),
        ("150324",     date(2024, 3, 15)),
        ("031524",     date(2024, 3, 15)),
        # failures
        ("",           TODAY),
        ("abc",        TODAY),
        ("2024-02-30", TODAY),
        ("24-02-30",   TODAY),
    ],
)
def test_parametrized(raw, expected):
    assert parse_date(raw) == expected