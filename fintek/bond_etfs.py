import argparse
import pandas as pd


# From - https://gemini.google.com/app/ec3d5a8dc56af103


########################
# Compare takehome and net gains for various ETFs by looking at their data
########################
def calculate_performance(initial_investment, annual_yield, roc_pct, fed_tax_rate, ca_tax_rate, ca_taxable_pct_of_income, months):
    current_value = initial_investment
    adjusted_basis = initial_investment
    total_fed_tax_paid_annually = 0
    total_ca_tax_paid_annually = 0
    total_dist_annually = 0
    
    monthly_yield = annual_yield / 12
    
    for _ in range(months):
        distribution = current_value * monthly_yield
        total_dist_annually += distribution
        roc_amount = distribution * roc_pct
        taxable_amount = distribution * (1 - roc_pct)
        
        # Taxes paid on distributions
        fed_tax = taxable_amount * fed_tax_rate
        ca_tax = (taxable_amount * ca_taxable_pct_of_income) * ca_tax_rate
        
        total_fed_tax_paid_annually += fed_tax
        total_ca_tax_paid_annually += ca_tax
        
        reinvest_amount = distribution - fed_tax - ca_tax
        
        # DRIP Logic
        current_value += reinvest_amount
        adjusted_basis = adjusted_basis + reinvest_amount - roc_amount
        
    # Exit calculations (LTCG Fed 15%, CA treats gains as ordinary 7.8%)
    if months > 12:
        exit_fed_rate = 0.15
    else:
        exit_fed_rate = fed_tax_rate
    exit_ca_rate = ca_tax_rate
    
    total_gain = current_value - adjusted_basis
    exit_tax_fed = max(0, total_gain * exit_fed_rate)
    exit_tax_ca = max(0, total_gain * exit_ca_rate)
    total_exit_tax = exit_tax_fed + exit_tax_ca
    
    take_home = current_value - total_exit_tax
    total_taxes_paid = total_fed_tax_paid_annually + total_ca_tax_paid_annually + total_exit_tax
    return {
        "Raw yield pct": f"{annual_yield:.2%}",
        "Final Value (Pre-Exit Tax)": current_value,
        "Adjusted Basis": adjusted_basis,
        "Total Gain at Exit": total_gain,
        "Total Dist": total_dist_annually,
        #" Dist Tax Fed": total_fed_tax_paid_annually,
        #" Dist Tax CA": total_ca_tax_paid_annually,
        "Total Dist tax": total_fed_tax_paid_annually + total_ca_tax_paid_annually,
        " Exit Tax Fed": exit_tax_fed,
        " Exit Tax CA": exit_tax_ca,
        "Total Exit Tax": total_exit_tax,
        "Total Taxes Paid (Total)": total_taxes_paid,
        "Net Take Home": take_home,
        "Net gain": take_home - initial_investment,
        #"Net gain pct": f"{(take_home - initial_investment)/initial_investment:.2%}"
    }

def display_results_table(results_dict, investment, months):
    """Uses pandas to generate a clean, scannable table."""
    df = pd.DataFrame(results_dict)
    # RNTODO Does not work, prints $ sign
    special_formats = {'Raw yield pct': '{:.2%}'}
    df.style.format(special_formats)
    pd.options.display.float_format = '${:,.2f}'.format

    print(f"\n--- Simulation Results ({months} months) ---")
    print(f"Initial Investment: ${investment:,.2f}")
    print(df)
    print("-" * 60)

def main():
    parser = argparse.ArgumentParser(description="Calculate tax implications for CSHI, BNDI, and VBIL.")
    parser.add_argument("-mon", "--months", type=int, default=36, help="Holding period")
    parser.add_argument("-irs", "--fed_tax_rate", type=float, default=0.305, help="Federal tax")
    parser.add_argument("-ftb", "-ca", "--ca_tax_rate", type=float, default=0.128, help="State tax")
    parser.add_argument("-amt", "-a", "--initial_investment", type=float, default=100000.0, help="Initial principal")
    
    args = parser.parse_args()

    # Fund Profiles (Approximate as of Dec 2025)
    # VBIL ca_taxable is ~0.6 because ~40% of its holdings are US Treasuries.
    # VGSH: Vanguard Short-Term Treasury ETF
    #   Yield: ~3.89% to 4.03% (based on Dec 2025 distributions)
    #   RoC: 0.00% (Treasury interest is ordinary income, not capital return)
    #   CA Taxable: 0.00 (100% of income is from US Govt Obligations, exempt from CA state tax)
    funds = {
        "CSHI": {"yield": 0.0494, "roc": 0.65, "ca_taxable": 0.0},
        "BNDI": {"yield": 0.0577, "roc": 0.72, "ca_taxable": 0.6},
        "VBIL": {"yield": 0.0440, "roc": 0.00, "ca_taxable": 0.6},
        "VGSH": {"yield": 0.0396, "roc": 0.00, "ca_taxable": 0.0},
        "RobinHood": {"yield": 0.0425, "roc": 0.00, "ca_taxable": 1.0},
        "SoFI": {"yield": 0.033, "roc": 0.00, "ca_taxable": 1.0},
    }

    all_results = {}
    for name, data in funds.items():
        all_results[name] = calculate_performance(
            args.initial_investment, data["yield"], data["roc"], 
            args.fed_tax_rate, args.ca_tax_rate, data["ca_taxable"],
            args.months
        )

    display_results_table(all_results, args.initial_investment, args.months)

if __name__ == "__main__":
    main()