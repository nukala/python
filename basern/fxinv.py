from typing import List, Tuple, Dict
from tabulate import tabulate
import numpy as np


class ForeignInvestmentCalculator:
    def __init__(self, initial_usd: float, base_rate: float):
        """Initialize with USD amount and base exchange rate (e.g., EUR/USD)"""
        self.initial_usd = initial_usd
        self.base_rate = base_rate  # EUR/USD exchange rate
        self.initial_foreign = initial_usd / base_rate  # Convert USD to foreign currency
    
    def calculate_return(self, investment_change: float, currency_change: float) -> Tuple[float, float]:
        """Calculate final USD value and percent return based on investment and currency changes"""
        new_rate = self.base_rate * (1 + currency_change)
        final_foreign = self.initial_foreign * (1 + investment_change)
        final_usd = final_foreign * new_rate
        pct_return = (final_usd - self.initial_usd) / self.initial_usd
        return final_usd, pct_return
    
    def generate_table(self, 
                       investment_changes: List[float], 
                       currency_changes: List[float]) -> str:
        """Generate a formatted table of returns for different scenarios"""
        # Create headers
        headers = ["Capital\nGain/Loss"] + [f"EUR {c:.1%}\n{self.base_rate*(1.0+c):.2f}" for c in currency_changes]
        
        # Generate table data
        rows = []
        for inv_change in investment_changes:
            row = [f"{inv_change:.1%}"]
            for curr_change in currency_changes:
                final_usd, pct_return = self.calculate_return(inv_change, curr_change)
                row.append(f"${final_usd:.0f} ({pct_return:.1%})")
            rows.append(row)
        
        # Return formatted table
        return tabulate(rows, headers=headers, tablefmt="pipe")


if __name__ == "__main__":
    # Initialize calculator with $10,000 USD at 1.08 EUR/USD rate
    calculator = ForeignInvestmentCalculator(10000, 1.1253)
    
    # Define scenarios
    inv_changes = [0.10, 0.05, 0.0, -0.05, -0.10]  # +10% to -10%
    curr_changes = [-0.03, 0.0, 0.03, 0.07]  # -3% to +3%
    
    # Generate and print the table
    table = calculator.generate_table(inv_changes, curr_changes)
    print("# Foreign Investment Return Analysis")
    print(f"Initial Investment: ${calculator.initial_usd:,.0f} USD")
    print(f"Base Exchange Rate: €1 = ${calculator.base_rate:.2f}")
    print(f"Initial Foreign Amount: €{calculator.initial_foreign:,.0f}")
    print("\n## Return Scenarios (Final USD Value and % Return)")
    print(table)
