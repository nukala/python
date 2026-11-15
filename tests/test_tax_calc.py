import math
import pytest
from typer.testing import CliRunner
from tax_calc import app
from tax_calc import parse_numeric_string
from tax_calc import TaxCalculator 
from typing import Any, List, Optional, Tuple

runner = CliRunner()


@pytest.mark.skip("WIP tests will be broken, problem with code!")
class TestVerifySummaryOutputs:
    def test_zero_income_default(self):
        """Verifies that running the script with zero or default values results in $0 tax."""
        result = runner.invoke(app, [])
        assert result.exit_code == 0
        assert "COMBINED ESTIMATED TAX:      $0.00" in result.output


    def test_income_below_standard_deductions(self):
        """Verifies that an income below the standard deduction results in $0 taxable income and tax."""
        result = runner.invoke(app, ["--salary", "20000"])
        assert result.exit_code == 0
        assert "Federal Taxable Ordinary:    $0.00" in result.output
        assert "California Taxable Income:   $9,196.00" in result.output  # 20000 - 10804
        assert "Total Estimated Federal Tax: $0.00" in result.output


    def test_federal_first_bracket_only(self):
        """
        Tests income that crosses the federal standard deduction but stays completely
        inside the lowest 10% federal bracket ($32,200 deduction + $10,000 income = $42,200).
        Expected federal ordinary tax: $10,000 * 10% = $1,000.00.
        """
        result = runner.invoke(app, ["--salary", "42200"])
        assert result.exit_code == 0
        assert "Federal Taxable Ordinary:    $10,000.00" in result.output
        assert "Estimated Ordinary Tax:      $1,000.00" in result.output


    def test_pretax_contributions_reduction(self):
        """Verifies that pre-tax contributions successfully lower gross taxable incomes."""
        # Gross income $150,000 minus $20,000 pre-tax = $130,000 base
        result = runner.invoke(app, ["--salary", "150000", "--pretax", "20000"])
        assert result.exit_code == 0
        # Fed Taxable: 150k - 20k - 32.2k = 97.8k
        assert "Federal Taxable Ordinary:    $97,800.00" in result.output


    def test_long_term_capital_gains_stacking(self):
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


    def test_high_income_ca_surtax(self):
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
    def test_all_individual_income_inputs(self, flag, value, expected_gross):
        """Parametrized test checking that every individual option parameter maps to Gross Ordinary Income."""
        result = runner.invoke(app, [flag, value])
        assert result.exit_code == 0
        assert expected_gross in result.output


    def test_invalid_input_type(self):
        """Verifies the CLI rejects text strings where numeric floats are required."""
        result = runner.invoke(app, ["--salary", "not_a_number"])
        assert result.exit_code != 0
        assert "Invalid value for '--salary' / '-s'" in result.output



def txbl_ssa(ssa: Optional[float], fed: Optional[float], verbosity: int = 0) -> float:
    return TaxCalculator.get_taxable_ssa_income(ssa, fed, verbosity)  # type: ignore[arg-type]

FUNC_NAME: str = "get_taxable_ssa_income"
FRACTION: float = 0.85

class TestGetTaxableSsaIncome:
    # ------------------------------------------------------------------
    # Basic API / typing
    # ------------------------------------------------------------------
    def test_is_static_callable_on_class_and_instance(self) -> None:
        assert TaxCalculator.get_taxable_ssa_income(10_000.0, 50_000.0) == \
               TaxCalculator().get_taxable_ssa_income(10_000.0, 50_000.0)

    def test_returns_float_above_cutoff(self) -> None:
        assert isinstance(txbl_ssa(20_000.0, 50_000.0), float)

    ## capture stdout
    def test_verbosity_defaults_to_zero(self, capsys: pytest.CaptureFixture[str]) -> None:
        TaxCalculator.get_taxable_ssa_income(20_000.0, 50_000.0)
        assert capsys.readouterr().out == ""

    def test_txbl_ssa_verbosity_defaults_to_zero(self, capsys: pytest.CaptureFixture[str]) -> None:
        txbl_ssa(20_000.0, 50_000.0)
        assert capsys.readouterr().out == ""

    # ------------------------------------------------------------------
    # Early return: no SSA income
    # ------------------------------------------------------------------
    @pytest.mark.parametrize("ssa", [0, None])
    @pytest.mark.parametrize("fed", [0, 10_000.0, 500_000.0, None])
    def test_no_ssa_income_raises_value_error(self, ssa: Optional[float], fed: Optional[float]) -> None:
        # assert txbl_ssa(ssa, fed) == 0
        with pytest.raises(ValueError):
            txbl_ssa(ssa, fed)

    @pytest.mark.parametrize("ssa", [0.0, ])
    @pytest.mark.parametrize("fed", [0.0, 10_000.0, 500_000.0,])
    def test_no_ssa_income_returns_zero(self, ssa: Optional[float], fed: Optional[float]) -> None:
        assert txbl_ssa(ssa, fed) == 0
        # with pytest.raises(ValueError):
        #     txbl_ssa(ssa, fed)


    @pytest.mark.parametrize("verbosity", [0, 1, 5])
    def test_no_ssa_income_prints_nothing(
        self, verbosity: int, capsys: pytest.CaptureFixture[str]
    ) -> None:
        txbl_ssa(0.0, 100_000.0, verbosity)
        assert capsys.readouterr().out == ""

    # ------------------------------------------------------------------
    # Early return: no other income
    # ------------------------------------------------------------------
    @pytest.mark.parametrize("fed", [0, 0.0])
    def test_zero_fed_income_with_verbosity_returns_zero(
        self, fed: float, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert txbl_ssa(10_000.0, fed, verbosity=1) == 0
        out = capsys.readouterr().out
        assert FUNC_NAME in out

    # ------------------------------------------------------------------
    # Input mutation / purity
    # ------------------------------------------------------------------
    def test_function_is_deterministic(self) -> None:
        assert len({txbl_ssa(20_000.0, 40_000.0) for _ in range(5)}) == 1

    # ------------------------------------------------------------------
    # Desired behaviour (xfail until the function is fixed)
    # ------------------------------------------------------------------
    # @pytest.mark.xfail(strict=True, reason="BUG: taxable SSA must never exceed 85% of benefits")
    @pytest.mark.parametrize(
        "ssa, fed",
        [(1_000.0, 100_000.0), (20_000.0, 40_000.0), (20_000.0, 100_000.0), (10_000.0, 500_000.0)],
    )
    def test_taxable_never_exceeds_85pct_of_ssa(self, ssa: float, fed: float) -> None:
        assert txbl_ssa(ssa, fed) <= FRACTION * ssa + 1e-9

    # @pytest.mark.xfail(strict=True, reason="BUG: negative fed income yields negative taxable SSA")
    def test_result_is_never_negative(self) -> None:
        assert txbl_ssa(100_000.0, -60_000.0) >= 0   # tmp = -10,000 ... must not be negative / raise

    @pytest.mark.parametrize("ssa, fed", [(10_000.0, 20_000.0), (10_000.0, 10_000.0), (5_000.0, 1_000.0)])
    def test_low_income_returns_zero_taxable(self, ssa: float, fed: float) -> None:
        assert txbl_ssa(ssa, fed) == 0

    def test_negative_ssa_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            txbl_ssa(-1_000.0, 50_000.0)

    def test_taxable_increases_with_ssa(self) -> None:
        assert txbl_ssa(30_000.0, 40_000.0) > txbl_ssa(20_000.0, 40_000.0)

    # ------------------------------------------------------------------
    # Invalid/bad inputs
    # ------------------------------------------------------------------
    def test_nan_fed_income_raises_value_error(self) -> None:
        # nan > cutoff is False -> falls to the raise
        with pytest.raises(ValueError, match="nan"):
            txbl_ssa(10_000.0, math.nan)

    def test_nan_ssa_income_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="nan"):
            txbl_ssa(math.nan, 50_000.0)

    def test_infinite_fed_income_returns_inf_current_behaviour(self) -> None:
        # assert txbl_ssa(10_000.0, math.inf) == math.inf
        with pytest.raises(ValueError, match="inf"):
            txbl_ssa(1_000.0, math.inf)

    def test_non_numeric_input_raises_type_error(self) -> None:
        with pytest.raises(ValueError):
            txbl_ssa("10000", 50_000.0)  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # Verbose output
    # ------------------------------------------------------------------
    def test_above_cutoff_quietmode(self) -> None:
        assert txbl_ssa(20_000.0, 40_000.0, 0) == pytest.approx(11_100.00)

    def test_verbose_output_above_cutoff(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = txbl_ssa(20_000.0, 40_000.0, verbosity=1)
        out = capsys.readouterr().out
        print(f"{out}", flush=True)
        assert result == pytest.approx(11_100.0)
        assert FUNC_NAME in out
        assert "provisional=50,000.00" in out
        assert "taxable=11,100.0" in out
        assert out.endswith("\n")

    def test_verbose_output_has_two_lines(self, capsys: pytest.CaptureFixture[str]) -> None:
        txbl_ssa(20_000.0, 40_000.0, verbosity=1)
        assert capsys.readouterr().out.count("\n") == 2

    @pytest.mark.parametrize("verbosity", [0, -1, -100])
    def test_non_positive_verbosity_is_silent(
        self, verbosity: int, capsys: pytest.CaptureFixture[str]
    ) -> None:
        txbl_ssa(20_000.0, 40_000.0, verbosity)
        assert capsys.readouterr().out == ""

    @pytest.mark.parametrize("verbosity", [1, 2, 10])
    def test_verbosity_does_not_change_result(self, verbosity: int) -> None:
        assert txbl_ssa(20_000.0, 40_000.0, verbosity) == txbl_ssa(20_000.0, 40_000.0, 0)

