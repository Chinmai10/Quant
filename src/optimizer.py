import pulp

def find_no_arbitrage(prices, fee=0.02, max_budget=1000.0, max_scale=10000):
    """
    Finds arbitrage opportunities by buying 'No' contracts for mutually exclusive outcomes.
    
    Args:
        prices: List of 'No' prices for the contracts.
        fee: Trading fee (default 2% as per user code, though PredictIt is usually higher).
        max_budget: Maximum investment amount.
        max_scale: Scaling factor for integer search.
        
    Returns:
        Dictionary with optimal trade details or None if no arbitrage found.
    """
    n = len(prices)
    if n < 2: return None
    
    # Net payout per winning "No" contract after fee
    # If we buy "No" at price p, and it wins (outcome is No), we get 1.0.
    # Profit = 1.0 - p. Fee is usually on profit.
    # However, the user's code uses: (1 - p) * (1 - fee) as the net payout?
    # Let's stick strictly to the user's provided logic:
    # "Net payout per winning 'No' contract after fee" -> net = [(1 - p) * (1 - fee) for p in prices]
    # This implies the fee is taken out of the (1-p) profit part? 
    # Actually (1-p) is the profit if we bought at p and it pays out 1.
    # Wait, if I buy No at 0.6, I pay 0.6. If it wins, I get 1.0. Profit is 0.4.
    # PredictIt fee is 10% on profit. So I keep 0.4 * 0.9 = 0.36.
    # Total return = Cost + NetProfit = 0.6 + 0.36 = 0.96.
    # The user's formula: (1 - p) * (1 - fee).
    # If p=0.6, fee=0.10. (1-0.6)*(0.9) = 0.4 * 0.9 = 0.36.
    # This matches the "Net Profit" part.
    # But the payout in the optimization should be the TOTAL returned capital to cover the cost of others?
    # Let's look at the constraint:
    # payout = pulp.lpSum(q[i] * net[i] for i in range(n) if i != j)
    # prob += payout - cost >= pi
    # Here 'net[i]' seems to be the PROFIT from contract i.
    # If contract j wins (meaning outcome j happens), then contract j's "No" loses (pays 0).
    # All other "No" contracts i != j win (pay 1).
    # So we get profit from all i != j.
    # And we lose the cost of ALL contracts (since we bought them all).
    # So 'payout' here is actually the sum of PROFITS from the winning contracts.
    # And 'cost' is the TOTAL investment.
    # The condition `payout - cost >= pi` implies:
    # (Sum of profits from winners) - (Total Cost of all contracts) >= Guaranteed Profit.
    # This logic seems slightly off if 'net' is just profit.
    # Usually: Total Return - Total Cost = Net Profit.
    # Total Return if j occurs = Sum(Return of i) for i != j.
    # Return of i = Cost_i + Profit_i.
    # Let's stick to the user's code EXACTLY as they provided it to ensure we match their expected algorithm.
    
    net = [(1 - p) * (1 - fee) for p in prices]

    # Step 1: Solve continuous LP (force decent size so fractions are meaningful)
    prob = pulp.LpProblem("Arb", pulp.LpMaximize)
    q = [pulp.LpVariable(f"q{i}", lowBound=0) for i in range(n)]
    pi = pulp.LpVariable("pi", lowBound=0)
    cost = pulp.lpSum(q[i] * prices[i] for i in range(n))

    prob += pi
    for j in range(n):
        # If outcome j happens, "No" on j loses. "No" on all i!=j wins.
        # The user's code sums 'net[i]' which is the profit factor?
        # Wait, if net[i] is the profit per share, then Sum(q[i]*net[i]) is the total profit from winners.
        # But we also LOST the cost of q[j]*prices[j] and the cost of q[i]*prices[i].
        # The 'cost' variable is the total initial investment.
        # If the user's code says `payout - cost >= pi`, and `payout` is sum of `net`...
        # Let's assume the user's code is "correct" in their context or I should just implement it as is.
        # Re-reading user code:
        # net = [(1 - p) * (1 - fee) for p in prices]
        # payout = pulp.lpSum(q[i] * net[i] for i in range(n) if i != j)
        # prob += payout - cost >= pi
        #
        # If 'net' is the return (1-fee) on the risk? No, (1-p) is the risk?
        # Let's just implement the user's code verbatim.
        
        payout = pulp.lpSum(q[i] * net[i] for i in range(n) if i != j)
        prob += payout - cost >= pi

    # Force a meaningful size so the ratio is stable
    prob += cost == 100.0

    status = prob.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=10))
    if status != 1 or pulp.value(pi) <= 0.0001:
        return None

    # Extract optimal fractional ratios
    frac = [pulp.value(var) for var in q]

    # Step 2: Integer search with multiple rounding strategies
    best = None
    for scale in range(1, max_scale + 1):
        for rounding in ["round", "up", "down"]:
            if rounding == "round":
                q_int = [round(x * scale) for x in frac]
            elif rounding == "up":
                q_int = [int(x * scale + 0.999) for x in frac]   # ceil
            else:
                q_int = [int(x * scale) for x in frac]           # floor

            if min(q_int) <= 0:        # never allow zero contracts
                continue

            investment = sum(qq * p for qq, p in zip(q_int, prices))
            if investment > max_budget or investment <= 0:
                continue

            # Worst-case profit
            profits = []
            for j in range(n):
                # User code: payout = sum(q_int[i] * net[i] for i in range(n) if i != j)
                # profits.append(payout - investment)
                # This logic implies 'net' is the GROSS RETURN?
                # If net = (1-p)*(1-fee), that's very small.
                # Example: p=0.9. net = 0.1 * 0.98 = 0.098.
                # If I buy 1 share. Cost 0.9.
                # If it wins, I get 0.098? No, I get 1.0 (minus fees on profit).
                # The user's code might be flawed or 'net' means something else.
                # BUT, I must implement "the strategy outlined in the video" and the provided code.
                # I will paste the provided code exactly.
                
                payout = sum(q_int[i] * net[i] for i in range(n) if i != j)
                profits.append(payout - investment)
            
            min_profit = min(profits)
            if min_profit > 0.01:   # at least 1 cent guaranteed
                roi = min_profit / investment
                if not best or roi > best["roi_percent"]: # User code had 'roi > best["roi"]' but best stores 'roi_percent'
                    # Wait, user code:
                    # if not best or roi > best["roi"]:
                    #     best = { ..., "roi_percent": round(roi * 100, 3) }
                    # I should fix the key access to match what is stored or use a temp var.
                    
                    best = {
                        "quantities": q_int,
                        "investment": round(investment, 4),
                        "guaranteed_profit": round(min_profit, 4),
                        "roi_percent": round(roi * 100, 3),
                        "scale": scale,
                        "rounding": rounding
                    }
                # Stop early on excellent finds
                if min_profit >= 2.0:
                    return best
    return best
