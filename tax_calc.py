import typer
import re
from typing import Annotated


app = typer.Typer(help="2026 MFJ Federal & California Tax Estimator",
                  add_completion=False, rich_markup_mode="markdown",
                  context_settings={"help_option_names": ["-h", "--help", "-?"],
                                    "allow_extra_args": True,
                                    "ignore_unknown_options": True, }
                  )


# --- String Parsing Engine ---
def parse_numeric_string(value: str) -> float:
    """Converts shorthand strings (10k, 1.5M, $10_000) into floats."""
    if not isinstance(value, str):
        raise TypeError("Input must be a string")
    if not value or not value.strip():
        return 0.0

    cleaned = re.sub(r'[$,_]', '', value).strip().lower()

    suffixes = {
        'k': 1_000.0,
        'm': 1_000_000.0,
        'b': 1_000_000_000.0
    }

    last_char = cleaned[-1]
    if last_char in suffixes:
        multiplier = suffixes[last_char]
        number_part = cleaned[:-1].strip()
        if not number_part:
            raise ValueError(f"Missing numeric prefix before suffix in: '{value}'")
        try:
            return float(number_part) * multiplier
        except ValueError as e:
            raise ValueError(f"Could not parse numeric part of string: '{value}'") from e

    try:
        return float(cleaned)
    except ValueError as e:
        raise ValueError(f"Invalid numeric string format: '{value}'") from e


class TaxCalculator:

    # --- Main Command ---
    @staticmethod
    @app.command()
    def calculate_taxes(
            # Core inputs collected strictly as strings to prevent premature Typer errors
            salary_str: str = typer.Option("0", "--salary", "-s",
                                           help="Combined W-2 salary and wage income (e.g., 140k)"),
            bonus_str: str = typer.Option("0", "--bonus", "-b",
                                          help="Bonuses, commissions, and tips"),
            interest_str: str = typer.Option("0", "--interest", "-i",
                                             help="Taxable bank interest and ordinary dividends"),
            stcg_str: str = typer.Option("0", "--stcg", "-st",
                                         help="Short-Term Capital Gains (held 1 year or less)"),
            business_str: str = typer.Option("0", "--business", "-biz",
                                             help="Net business/freelance income"),
            rental_str: str = typer.Option("0", "--rental", "-rntl",
                                           help="Net rental income after expenses"),
            retirement_str: str = typer.Option("0", "--retirement", "-retr", "--retire-dist", "-dist",
                                               help="Traditional IRA / 401(k) withdrawals"),
            ltcg_str: str = typer.Option("0", "--ltcg", "-lt",
                                         help="Long-Term Capital Gains"),
            qualdv_str: str = typer.Option("0", "--qualdiv", "-qd",
                                           help="Qualified Dividends"),
            pretax_str: str = typer.Option("0", "--pretax", "-pt",
                                           help="Pre-tax traditional 401k/IRA/HSA contributions"),

            verbosity: Annotated[int, typer.Option("-v", count=True,
                                                   help="Set verbosity level. Use -v for warning, -vv for info, -vvv for debug.")] = 0,
            vlevel: Annotated[int, typer.Option("--verbosity", "-vrb",
                                                help="Specify a verbosity level, 1=warning, 2=info,3=debug etc.")] = 0,
    ):

        """
        Estimates 2026 Federal (IRS) and California state income taxes for Married Filing Jointly (MFJ).
        """

        if vlevel>0:
            verbosity=vlevel
        try:
            # Convert all incoming strings to real floats
            salary = parse_numeric_string(salary_str)
            bonus = parse_numeric_string(bonus_str)
            ordinary_interest = parse_numeric_string(interest_str)
            short_term_cg = parse_numeric_string(stcg_str)
            business_net = parse_numeric_string(business_str)
            rental_net = parse_numeric_string(rental_str)
            retirement_dist = parse_numeric_string(retirement_str)
            long_term_cg = parse_numeric_string(ltcg_str)
            pretax_contributions = parse_numeric_string(pretax_str)
            qualified_dividends = parse_numeric_string(qualdv_str)

            if verbosity>0:
                print(f" salary={salary}, bonus={bonus}, ordinary_interest={ordinary_interest},"
                      f" short_term_cg={short_term_cg}, business_net={business_net}, rental_net={rental_net},"
                      f" retirement_dist={retirement_dist}, long_term_cg={long_term_cg},"
                      f" pretax_contribs={pretax_contributions}, qualified_dividends={qualified_dividends}")
        except ValueError as e:
            typer.secho(f"\n❌ Error parsing inputs: {e}", fg=typer.colors.RED, bold=True)
            raise typer.Exit(code=1)

        # 1. Total Ordinary Income
        ordinary_income = (
                salary + bonus + ordinary_interest + short_term_cg +
                business_net + rental_net + retirement_dist
        )

        # if ordinary_income <= 0:
        #     if verbosity>=1:
        #         print(f" ordinary_income = {ordinary_income}, stopping")
        #     return

        # 2. Adjusted Gross Income (AGI)
        federal_agi = (ordinary_income + long_term_cg+qualified_dividends) - pretax_contributions

        # 3. Deductions (Using Projected 2026 Standard Deductions for MFJ)
        fed_standard_deduction = 32200.0
        ca_standard_deduction = 10804.0  # Estimated 2026 CA standard deduction for MFJ

        fed_taxable_ordinary = max(0.0, ordinary_income - pretax_contributions - fed_standard_deduction)
        fed_taxable_ltcg = max(0.0, long_term_cg+qualified_dividends)

        ca_taxable = max(0.0, (ordinary_income + long_term_cg+qualified_dividends) - pretax_contributions - ca_standard_deduction)

        fed_ordinary_tax, fed_ltcg_tax, fed_marginal_rate, fed_marginal_limit = TaxCalculator.fed_taxes(fed_taxable_ordinary, fed_taxable_ltcg)
        total_fed_tax = fed_ordinary_tax + fed_ltcg_tax

        ca_base_tax, ca_surtax, ca_marginal_rate, ca_marginal_limit = TaxCalculator.ca_taxes(ca_taxable)
        total_ca_tax = ca_base_tax + ca_surtax
        # --- Output Summary Generation ---
        if verbosity>1:
            typer.secho("\n")
        typer.secho("========== 2026 INCOME SUMMARY (MFJ) ==========", fg=typer.colors.CYAN, bold=True)
        typer.echo(f"Gross Ordinary Income:        ${ordinary_income:,.2f}")
        if verbosity>=1:
            typer.echo(f"Long-Term Capital Gains:      ${long_term_cg + qualified_dividends:,.2f}")
            typer.echo(f"Pre-Tax Deductions:           -${pretax_contributions:,.2f}")
        typer.echo(f"Fed Marginal rate and limit:  {fed_marginal_rate:,.2f}% and ${fed_marginal_limit:,.0f}")
        typer.echo(f"Federal AGI:                  ${federal_agi:,.2f}")

        if verbosity>1:
            typer.secho("\n")
        typer.secho("========== FEDERAL TAX (IRS) ==========", fg=typer.colors.GREEN, bold=True)
        typer.echo(f"Federal Taxable Ordinary:    ${fed_taxable_ordinary:,.2f}")
        if verbosity>=1:
            typer.echo(f"Federal Taxable LTCG:        ${fed_taxable_ltcg:,.2f}")
        typer.echo(f"Estimated Ordinary Tax:      ${fed_ordinary_tax:,.2f}")
        if verbosity>=2:
            typer.echo(f"Estimated LTCG Tax:          ${fed_ltcg_tax:,.2f}")
        fed_tax_rate = 0.0 if ordinary_income<=0 or fed_taxable_ordinary <= 0 \
            else (total_fed_tax*100.0)/(fed_taxable_ordinary+fed_taxable_ltcg)
        typer.secho(f"Total Estimated Federal Tax: ${total_fed_tax:,.2f}"
                    f" ({fed_tax_rate:,.2f}%)"
                    f" marginal={fed_marginal_rate:,.2f}%"
                    # CA taxable includes, income+ltcg+qual
                    f", remaining-bracket=${max(0.0, fed_marginal_limit - ca_taxable):,.0f}", bold=True)

        if verbosity>1:
            typer.secho("\n")
        typer.secho("========== CALIFORNIA STATE TAX ==========", fg=typer.colors.YELLOW, bold=True)
        typer.echo(f"California Taxable Income:   ${ca_taxable:,.2f} (Includes LTCG)")
        typer.echo(f"CA Marginal rate and limit:  {ca_marginal_rate:,.2f}% and ${ca_marginal_limit:,.0f}")
        if verbosity>=1:
            typer.echo(f"CA Base Progressive Tax:     ${ca_base_tax:,.2f}")
            typer.echo(f"CA Mental Health Surtax:     ${ca_surtax:,.2f}")
        ca_tax_rate = 0.0 if ordinary_income <= 0 else (total_ca_tax*100.0)/ca_taxable
        typer.secho(f"Total Estimated CA Tax:      ${total_ca_tax:,.2f}"
                    f" ({ca_tax_rate:,.2f}%)"
                    f" marginal={ca_marginal_rate:,.2f}%"
                    f", remaining-bracket=${max(0.0, ca_marginal_limit - ca_taxable):,.0f}", bold=True)

        if verbosity>1:
            typer.secho("\n")

        combined_rate:float = 0.0 if ordinary_income<=0 \
            else (total_fed_tax+total_ca_tax)/max((fed_taxable_ltcg+fed_taxable_ordinary), ca_taxable)
        roth_str=""
        if retirement_dist > 0:
            roth_str=f" roth=${(retirement_dist*(1-combined_rate)):,.0f}"

        typer.secho("=========================================", fg=typer.colors.CYAN)
        typer.secho(f"COMBINED ESTIMATED TAX:      ${total_fed_tax + total_ca_tax:,.2f}"
                    f" ({100.0*combined_rate:,.2f})%{roth_str}",
                    fg=typer.colors.MAGENTA,
                    bold=True)

    @staticmethod
    def fed_taxes(fed_taxable_ordinary: float | int,  fed_taxable_ltcg: float | int) \
            -> tuple[float, float, float, float]:
        """
        Calculates Ordinary Federal taxes from tax_tables and long term CG taxes
        :param fed_taxable_ltcg: Federal taxable long term capital gains income
        :param fed_taxable_ordinary: Federal taxable ordinary income

        Returns a tuple of:
        :return fed_ordinary_tax: Ordinary federal tax from tax_tables
        :return fed_ltgc_tax: Long term gains tax
        :return top_fed_rate: Federal marginal tax bracket as pct
        :return top_fed_limit: Limit of the marginal federal tax bracket
        """
        # 4. Calculate Federal Ordinary Tax (2026 Projected MFJ Brackets)
        fed_brackets = [
            (24800, 0.10),
            (100800, 0.12),
            (211400, 0.22),
            (403550, 0.24),
            (512450, 0.32),
            (768700, 0.35),
            (float('inf'), 0.37)
        ]

        fed_ordinary_tax = 0.0
        previous_limit = 0.0
        top_rate = 0.0
        top_limit = 0.0
        for limit, rate in fed_brackets:
            if fed_taxable_ordinary > previous_limit:
                taxable_in_bracket = min(fed_taxable_ordinary, limit) - previous_limit
                fed_ordinary_tax += taxable_in_bracket * rate
                previous_limit = limit
                top_rate = rate
                top_limit = limit
            else:
                break

        # 5. Calculate Federal Long-Term Capital Gains Tax (2026 MFJ Brackets)
        fed_ltcg_tax = 0.0

        if fed_taxable_ltcg > 0:
            # Official 2026 IRS MFJ Long-Term Capital Gains Thresholds
            ltcg_0_limit = 98900.0
            ltcg_15_limit = 613700.0

            # Capital Gains stack on top of ordinary taxable income
            ltcg_start = fed_taxable_ordinary
            ltcg_end = fed_taxable_ordinary + fed_taxable_ltcg

            # Portion in the 0% Bracket
            gains_in_0_bracket = max(0.0, min(ltcg_end, ltcg_0_limit) - ltcg_start)

            # Portion in the 15% Bracket
            gains_in_15_bracket = max(0.0, min(ltcg_end, ltcg_15_limit) - max(ltcg_start, ltcg_0_limit))

            # Portion in the 20% Bracket
            gains_in_20_bracket = max(0.0, ltcg_end - max(ltcg_start, ltcg_15_limit))

            # Compute final sum
            fed_ltcg_tax = (gains_in_0_bracket * 0.00) + (gains_in_15_bracket * 0.15) + (gains_in_20_bracket * 0.20)

        return fed_ordinary_tax, fed_ltcg_tax, top_rate*100.0, top_limit

    @staticmethod
    def ca_taxes(ca_taxable: float | int) -> tuple[float | int, float | int, float, float]:
        """
        Calculates total california tax, base and surchages
        :param ca_taxable: Taxable amount for California

        Returns a tuple of:
        :return ca_base_tax: Base tax from tax brackets
        :return ca_surtax: Surcharge for mental health services for AGI > 1m
        :return top_ca_rate: California marginal tax bracket as pct
        :return top_ca_limit: Limit of the marginal California tax bracket
        """
        # 6. Calculate California State Tax (CA progressive brackets double for MFJ)
        ca_brackets_2026 = [
            (21600, 0.01),
            (51190, 0.02),
            (80788, 0.04),
            (112000, 0.06),
            (141584, 0.08),
            (171178, 0.093),
            (874300, 0.103),
            (1049160, 0.113),
            (float('inf'), 0.123)
        ]

        ca_base_tax = 0.0
        previous_limit = 0.0
        top_rate = 0.0
        top_limit = 0.0
        for limit, rate in ca_brackets_2026:
            if ca_taxable > previous_limit:
                taxable_in_bracket = min(ca_taxable, limit) - previous_limit
                ca_base_tax += taxable_in_bracket * rate
                previous_limit = limit
                top_rate = rate
                top_limit = limit
            else:
                break

        # CA Mental Health Services Surtax (1% over $1M)
        ca_surtax = max(0.0, ca_taxable - 1000000.0) * 0.01
        return ca_base_tax, ca_surtax, top_rate*100.0, top_limit


if __name__ == "__main__":
    app()
