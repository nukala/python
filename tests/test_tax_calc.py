import pytest
from typer.testing import CliRunner
from tax_calc import app
from tax_calc import parse_numeric_string

runner = CliRunner()

def test_zero_income_default():
    """Verifies that running the script with zero or default values results in $0 tax."""
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "COMBINED ESTIMATED TAX:      $0.00" in result.output


def test_income_below_standard_deductions():
    """Verifies that an income below the standard deduction results in $0 taxable income and tax."""
    result = runner.invoke(app, ["--salary", "20000"])
    assert result.exit_code == 0
    assert "Federal Taxable Ordinary:    $0.00" in result.output
    assert "California Taxable Income:   $9,196.00" in result.output  # 20000 - 10804
    assert "Total Estimated Federal Tax: $0.00" in result.output


def test_federal_first_bracket_only():
    """
    Tests income that crosses the federal standard deduction but stays completely
    inside the lowest 10% federal bracket ($32,200 deduction + $10,000 income = $42,200).
    Expected federal ordinary tax: $10,000 * 10% = $1,000.00.
    """
    result = runner.invoke(app, ["--salary", "42200"])
    assert result.exit_code == 0
    assert "Federal Taxable Ordinary:    $10,000.00" in result.output
    assert "Estimated Ordinary Tax:      $1,000.00" in result.output


def test_pretax_contributions_reduction():
    """Verifies that pre-tax contributions successfully lower gross taxable incomes."""
    # Gross income $150,000 minus $20,000 pre-tax = $130,000 base
    result = runner.invoke(app, ["--salary", "150000", "--pretax", "20000"])
    assert result.exit_code == 0
    # Fed Taxable: 150k - 20k - 32.2k = 97.8k
    assert "Federal Taxable Ordinary:    $97,800.00" in result.output


def test_long_term_capital_gains_stacking():
    """
    Verifies that Long Term Capital Gains (LTCG) do not get taxed under ordinary brackets
    federally, but DO get added to California taxable income.
    """
    result = runner.invoke(app, ["--salary", "60000", "--ltcg", "20000"])
    assert result.exit_code == 0
    assert "Federal Taxable Ordinary:    $27,800.00" in result.output
    assert "Federal Taxable LTCG:        $20,000.00" in result.output
    # CA taxes LTCG as ordinary income: 60k + 20k - 10804 = 69196
    assert "California Taxable Income:   $69,196.00" in result.output


def test_high_income_ca_surtax():
    """
    Verifies that the 1% California Mental Health Services Surtax kicks in
    accurately for incomes over $1,000,000.
    """
    # $1.5M salary means CA Taxable will be ~ $1,489,196.
    # Surtax should be 1% of the amount over $1,000,000 (~ $489,196 * 0.01 = $4,891.96)
    result = runner.invoke(app, ["--salary", "1500000"])
    assert result.exit_code == 0
    assert "CA Mental Health Surtax:" in result.output
    assert "CA Mental Health Surtax:     $0.00" not in result.output


@pytest.mark.parametrize(
    "flag, value, expected_gross",
    [
        ("--bonus", "5000", "Gross Ordinary Income:       $5,000.00"),
        ("--interest", "1200", "Gross Ordinary Income:       $1,200.00"),
        ("--stcg", "8500", "Gross Ordinary Income:       $8,500.00"),
        ("--business", "45000", "Gross Ordinary Income:       $45,000.00"),
        ("--rental", "12000", "Gross Ordinary Income:       $12,000.00"),
        ("--retirement", "30000", "Gross Ordinary Income:       $30,000.00"),
    ],
)
def test_all_individual_income_inputs(flag, value, expected_gross):
    """Parametrized test checking that every individual option parameter maps to Gross Ordinary Income."""
    result = runner.invoke(app, [flag, value])
    assert result.exit_code == 0
    assert expected_gross in result.output


def test_invalid_input_type():
    """Verifies the CLI rejects text strings where numeric floats are required."""
    result = runner.invoke(app, ["--salary", "not_a_number"])
    assert result.exit_code != 0
    assert "Invalid value for '--salary' / '-s'" in result.output


# --- SUCCESS CASES (INCLUDING MULTIPLE CASE VARIATIONS) ---

@pytest.mark.parametrize(
    "input_str, expected",
    [
        # Lowercase Suffixes
        ("10k", 10000.0),
        ("1.5m", 1500000.0),
        ("3b", 3000000000.0),
        
        # Uppercase Suffixes (Case Insensitivity Verification)
        ("10K", 10000.0),
        ("1.5M", 1500000.0),
        ("3B", 3000000000.0),
        
        # Casing combined with trailing spaces
        ("10 k ", 10000.0),
        ("10 K ", 10000.0),
        (" 1.5 M", 1500000.0),
        
        # Casing combined with currency formatting and underscores
        ("$10_000K", 10000000.0),
        ("$10_000k", 10000000.0),
        ("$-5.5M", -5500000.0),
        ("$-5.5m", -5500000.0),
        
        # Plain standard values without suffixes
        ("123.45", 123.45),
        ("0", 0.0),
    ],
)
def test_parse_numeric_string_case_insensitivity(input_str, expected):
    """Verifies that both lowercase and uppercase variations of suffixes parse to identical float targets."""
    assert parse_numeric_string(input_str) == expected


# --- FAILURE CASES ---

@pytest.mark.parametrize(
    "invalid_input",
    [
        "",                 # Empty string
        "   ",              # Whitespace only
        "abc",              # Letters only
        "K",                # Upper suffix with no numeric base
        "k",                # Lower suffix with no numeric base
        "10kM",             # Multiple nested suffixes
        "1.2.3",            # Broken decimal formatting
    ],
)
def test_parse_numeric_string_exceptions(invalid_input):
    """Verifies invalid or broken strings throw clean ValueError exceptions."""
    with pytest.raises(ValueError):
        parse_numeric_string(invalid_input)


def test_parse_numeric_string_none_type():
    """Confirms strong type checking limits work accurately against non-string elements."""
    with pytest.raises(TypeError):
        parse_numeric_string(None)  # type: ignore
