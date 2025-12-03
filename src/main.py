import pandas as pd
from fetch_data import fetch_predictit_data, markets_to_dataframe
from optimizer import find_no_arbitrage
import time

def main():
    print("Fetching PredictIt market data...")
    try:
        data = fetch_predictit_data()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    print("Converting to DataFrame...")
    df = markets_to_dataframe(data)
    
    # Filter for active markets
    df = df[df['market_status'] == 'Open']
    
    print(f"Total active contracts: {len(df)}")
    
    # Group by market
    markets = df.groupby('market_id')
    
    opportunities = []

    print("Scanning for 'No' arbitrage opportunities...")
    for market_id, group in markets:
        # We need at least 2 contracts to arbitrage
        if len(group) < 2:
            continue
            
        # Extract "No" prices (Best Buy No Cost)
        # We use 'best_buy_no' because we are buying 'No' contracts.
        # If 'best_buy_no' is None (no liquidity), we can't trade.
        
        # Filter out contracts with missing prices
        valid_contracts = group.dropna(subset=['best_buy_no'])
        
        if len(valid_contracts) < 2:
            continue
            
        prices = valid_contracts['best_buy_no'].tolist()
        contract_names = valid_contracts['contract_name'].tolist()
        
        # Run optimizer
        # Note: The algorithm assumes mutually exclusive outcomes where exactly one wins.
        # PredictIt markets are usually "Winner Take All".
        # However, some markets might allow multiple winners? 
        # We assume standard single-winner markets for this strategy.
        
        result = find_no_arbitrage(prices)
        
        if result:
            market_name = group.iloc[0]['market_name']
            print(f"FOUND ARBITRAGE: {market_name}")
            print(f"  ROI: {result['roi_percent']}% | Profit: ${result['guaranteed_profit']}")
            print(f"  Investment: ${result['investment']}")
            
            # Format the trade
            trade_details = []
            for i, qty in enumerate(result['quantities']):
                if qty > 0:
                    trade_details.append({
                        "contract": contract_names[i],
                        "price": prices[i],
                        "quantity": qty,
                        "cost": prices[i] * qty
                    })
            
            opportunities.append({
                "market_id": market_id,
                "market_name": market_name,
                "roi": result['roi_percent'],
                "profit": result['guaranteed_profit'],
                "investment": result['investment'],
                "trades": trade_details
            })

    # Output results
    if opportunities:
        print(f"\nTotal Opportunities Found: {len(opportunities)}")
        # Save to CSV
        rows = []
        for op in opportunities:
            for trade in op['trades']:
                rows.append({
                    "market_name": op['market_name'],
                    "roi_percent": op['roi'],
                    "guaranteed_profit": op['profit'],
                    "total_investment": op['investment'],
                    "contract": trade['contract'],
                    "buy_no_price": trade['price'],
                    "quantity": trade['quantity'],
                    "cost": trade['cost']
                })
        
        res_df = pd.DataFrame(rows)
        res_df.to_csv("arbitrage_opportunities.csv", index=False)
        print("Saved opportunities to 'arbitrage_opportunities.csv'")
    else:
        print("\nNo arbitrage opportunities found at this time.")

    # Also save the raw market data
    df.to_csv("predictit_markets.csv", index=False)
    print("Saved raw market data to 'predictit_markets.csv'")

if __name__ == "__main__":
    main()
