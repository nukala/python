import pandas as pd

# Define initial values
initial_price = 50.0
years = 8

# ETF characteristics
etfs = {
    "QQQI": {"yield": 0.14, "type": "ROC", "expense_ratio": 0.0068},
    "JEPQ": {"yield": 0.112, "type": "Ordinary", "expense_ratio": 0.0035},
    "ULTY": {"yield": 1.0, "type": "ROC", "expense_ratio": 0.0130},
}

# Tax rates (only on LTCG after basis exhausted)
ltcg_rate = 0.293

# Store result per ETF
results = {}

for etf_name, etf_data in etfs.items():
    price = initial_price
    share_count = 1.0
    basis_per_share = initial_price
    total_tax_paid = 0.0
    cumulative_take_home = 0.0
    
    records = []
    
    for year in range(1, years + 1):
        distribution = etf_data["yield"] * price * share_count
        new_shares = distribution / price
        taxes_this_year = 0.0
        take_home = 0.0

        if etf_data["type"] == "ROC":
            if basis_per_share > 0:
                total_basis_reduction = distribution / share_count
                basis_per_share -= total_basis_reduction
                if basis_per_share < 0:
                    excess = -basis_per_share * share_count
                    taxes_this_year = excess * ltcg_rate
                    take_home = distribution - taxes_this_year
                    basis_per_share = 0
                else:
                    take_home = distribution
            else:
                taxes_this_year = distribution * ltcg_rate
                take_home = distribution - taxes_this_year
        else:
            take_home = distribution

        total_tax_paid += taxes_this_year
        cumulative_take_home += take_home
        share_count += new_shares

        records.append({
            "Year": year,
            "Start Shares": round(share_count - new_shares, 4),
            "Distribution": round(distribution, 2),
            "New Shares": round(new_shares, 4),
            "Total Shares": round(share_count, 4),
            "Basis/Share": round(basis_per_share, 2),
            "Taxes Paid": round(taxes_this_year, 2),
            "Cumulative Taxes": round(total_tax_paid, 2),
            "Take-Home": round(take_home, 2),
            "Cumulative Take-Home": round(cumulative_take_home, 2),
        })

    results[etf_name] = pd.DataFrame(records)

# To display the tables:
for etf in results:
    print(f"\n=== {etf} ===")
    print(results[etf])

