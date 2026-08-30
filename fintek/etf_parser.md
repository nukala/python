mkdir -p etf-tool && cd etf-tool
cat <<EOF > requirements.txt
pandas
requests
tabulate
pytest
EOF

cat <<EOF > README.md
# ETF Holdings Parser
Type-safe CLI tool for comparing Semiconductor and Korean ETF concentrations.

## Setup
1. Install dependencies: \`pip install -r requirements.txt\`
2. Run tests: \`pytest\`

## Usage Examples
- **Default (US):** \`python etf_parser.py\`
- **Korea Focus:** \`python etf_parser.py --kr\`
- **Custom Stocks:** \`python etf_parser.py --stocks NVDA,TSM,ARM\`
- **CSV Export:** \`python etf_parser.py --stocks MU,ASML --format csv\`
EOF
