# PredictIt Arbitrage Engine

## ✅ Project Status: **WORKING**

This engine identifies risk-free arbitrage opportunities on PredictIt by analyzing "No" contract prices in mutually exclusive markets.

---

## 🚀 How to Run

### Option 1: Using Sample Data (Recommended for Testing)
The project comes with sample data and will run immediately:

```bash
python src/main.py
```

### Option 2: Using Live PredictIt Data
If you want to fetch live data from PredictIt:

1. **Manual Download** (Recommended - PredictIt blocks automated requests):
   - Open your browser and navigate to: `https://www.predictit.org/api/marketdata/all/`
   - Save the JSON response to: `predictit_data.json` in the project root
   - Run: `python src/main.py`

2. **Automated Fetch** (May be blocked):
   - The script will automatically attempt to fetch data
   - If blocked, it will fall back to the local `predictit_data.json` file

---

## 📊 Output Files

After running, you'll get:

- **`predictit_markets.csv`**: Raw market data snapshot
- **`arbitrage_opportunities.csv`**: Detailed list of profitable trades (if any found)

---

## 🎯 How It Works

### The Strategy
1. **Fetch Market Data**: Get all active PredictIt markets and contract prices
2. **Identify Candidates**: Find "Winner Take All" markets with multiple outcomes
3. **Calculate Arbitrage**: Use linear programming to find if buying "No" on all outcomes guarantees profit
4. **Optimize Quantities**: Determine the exact number of shares to buy for each contract

### Example
Market: "Who will win the election?"
- Candidate A: No @ $0.40
- Candidate B: No @ $0.35  
- Candidate C: No @ $0.30

**Total Cost**: $1.05 per set  
**Guaranteed Return**: $1.00 (one will win, two will lose)  
**Result**: No arbitrage (loss of $0.05)

But if prices were:
- Candidate A: No @ $0.25
- Candidate B: No @ $0.28
- Candidate C: No @ $0.30

**Total Cost**: $0.83 per set  
**Guaranteed Return**: $1.00  
**Profit**: $0.17 (20.5% ROI) ✅

---

## 🛠️ Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

**Dependencies**:
- `requests` - HTTP requests
- `pandas` - Data manipulation
- `pulp` - Linear programming solver

---

## 📁 Project Structure

```
Quant/
├── src/
│   ├── fetch_data.py    # Data fetching from PredictIt API
│   ├── optimizer.py     # Linear programming arbitrage calculator
│   └── main.py          # Main orchestration script
├── predictit_data.json  # Sample/cached market data
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── index.html          # Submission site
```

---

## ⚠️ Limitations

1. **Execution Risk**: Prices change between data fetch and order placement
2. **Liquidity**: Engine doesn't model full order book depth
3. **Fees**: PredictIt has complex fees (10% on profit + 5% withdrawal). The current model uses simplified 2% fee
4. **API Access**: PredictIt's API may block automated requests (use manual download method)

---

## 🧪 Testing

The project includes sample data in `predictit_data.json`. To test with different scenarios, edit this file to create arbitrage opportunities.

---


## 🔧 Troubleshooting

### "Error fetching data: 403"
- PredictIt is blocking the request with their Web Application Firewall (WAF)
- **Common Causes**:
  - Your IP address may be flagged or blocked by PredictIt
  - Automated requests from certain regions/ISPs are blocked
  - Rate limiting or anti-bot protection
- **Solutions**: 
  1. Manually download the JSON data (see Option 2 above)
  2. Try from a different network/IP address
  3. Use a VPN if your region is blocked
  4. The script will automatically fall back to using the local `predictit_data.json` file


### "No module named 'pulp'"
- Dependencies not installed
- **Solution**: Run `pip install -r requirements.txt`

### "No arbitrage opportunities found"
- This is normal! Arbitrage opportunities are rare
- Markets are usually efficient
- Try running at different times or with live data

---

## 📈 Markets Targeted

- Political elections (Presidential, Congressional)
- Party nominations
- Policy outcomes
- Any "Winner Take All" market with multiple mutually exclusive outcomes

---

## 🎓 Design Decisions

- **Linear Programming**: Uses `pulp` CBC solver for optimal ratio calculation
- **Integer Search**: Iterates through scales (1-10000) to find best integer approximation
- **Multiple Rounding**: Tests round/ceil/floor strategies for each scale
- **Early Exit**: Stops search when profit ≥ $2.00 to save computation time

