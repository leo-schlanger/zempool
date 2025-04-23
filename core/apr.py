
def simulate_apr_apy(apr, volume, liquidity):
    try:
        apr = float(apr)
        daily_return = apr / 365 / 100
        usd_daily = round(100 * daily_return, 2)
        usd_monthly = round(usd_daily * 30, 2)
        usd_yearly = round(usd_daily * 365, 2)
        apy = (1 + daily_return) ** 365 - 1
        return {
            "apr_return_usd": {
                "daily": usd_daily,
                "monthly": usd_monthly,
                "yearly": usd_yearly
            },
            "apy_percent": {
                "daily": round(daily_return * 100, 4),
                "monthly": round(((1 + daily_return) ** 30 - 1) * 100, 4),
                "yearly": round(apy * 100, 4)
            }
        }
    except:
        return None

def format_small_number(n):
    return f"{n:.8f}" if n < 0.01 else f"{n:.4f}"
