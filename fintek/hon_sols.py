# by chatgpt - 
#######
# please summarize what you know from Honeywell and Soltice breakup. When will that happen? When will Solstice trade independently? By when should I buy HON? Timeline for advanced-materials breakup pls ask questions first
#
# Before pandas installation:
# Filesystem     1M-blocks   Used Available Use% Mounted on
# C:                975645 334463    641183  35% /cygdrive/c
# After:
# Filesystem     1M-blocks   Used Available Use% Mounted on
# C:                975645 334594    641052  35% /cygdrive/c
#                                       131
#######
import pandas as pd

# Assumptions
hon_current_price = 200  # Approx current HON share price
hon_dividend_yield = 0.0238  # 2.38% dividend yield
hon_annual_dividend = hon_current_price * hon_dividend_yield

# Spin-off allocation
solstice_est_spin_value_pct = 0.15  # Solstice is 15% of HON value
solstice_implied_value = hon_current_price * solstice_est_spin_value_pct
hon_remainco_value_post_spin = hon_current_price - solstice_implied_value

# Scenario modeling
scenarios = {
    'Bear Case': {
        'HON multiple change': -0.05,
        'SOLS multiple change': -0.20,
        'Probability': 0.4
    },
    'Base Case': {
        'HON multiple change': 0.00,
        'SOLS multiple change': 0.00,
        'Probability': 0.3
    },
    'Bull Case': {
        'HON multiple change': 0.10,
        'SOLS multiple change': 0.10,
        'Probability': 0.3
    }
}

results = []

for name, s in scenarios.items():
    hon_value = hon_remainco_value_post_spin * (1 + s['HON multiple change'])
    sols_value = solstice_implied_value * (1 + s['SOLS multiple change'])
    total_value = hon_value + sols_value
    total_return = (total_value + hon_annual_dividend) / hon_current_price - 1
    results.append({
        'Scenario': name,
        'HON Remainco Value': round(hon_value, 2),
        'SOLS Value': round(sols_value, 2),
        'Total Value (Post Spin)': round(total_value, 2),
        'Total Return (%)': round(total_return * 100, 2),
        'Probability': s['Probability']
    })

df = pd.DataFrame(results)
df['Expected Return'] = df['Total Return (%)'] * df['Probability']
expected_return = df['Expected Return'].sum()

print(df)
print(f"\nExpected Return (weighted average): {round(expected_return, 2)}%")
