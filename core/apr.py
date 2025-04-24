import logging

logger = logging.getLogger("apr")
logger.setLevel(logging.DEBUG)

def simulate_apr_apy(apr_value, volume_usd, liquidity_usd, fee_rate=None, capital=1000):
    try:
        apr = float(apr_value)
        volume = float(volume_usd)
        liquidity = float(liquidity_usd)

        if apr <= 0 or volume <= 0 or liquidity <= 0:
            logger.warning("[APR] Invalid inputs - apr, volume, or liquidity are non-positive.")
            return None

        daily_return_rate = apr / 365 / 100
        daily_earn = round(capital * daily_return_rate, 2)
        weekly_earn = round(daily_earn * 7, 2)
        yearly_earn = round(capital * apr / 100, 2)

        fee = fee_rate if fee_rate is not None else 0.003

        proportion = volume / liquidity
        realistic_daily_usd = round(proportion * 0.5 * capital * fee, 2)
        realistic_weekly_usd = round(realistic_daily_usd * 7, 2)
        realistic_yearly_usd = round(realistic_daily_usd * 365, 2)

        apy = (1 + daily_return_rate) ** 365 - 1

        return {
            "apr_return_usd": {
                "daily": daily_earn,
                "weekly": weekly_earn,
                "yearly": yearly_earn
            },
            "realistic_based_on_vol_liq": {
                "daily": realistic_daily_usd,
                "weekly": realistic_weekly_usd,
                "yearly": realistic_yearly_usd
            },
            "apy_percent": {
                "daily": round(daily_return_rate * 100, 4),
                "weekly": round(((1 + daily_return_rate) ** 7 - 1) * 100, 4),
                "yearly": round(apy * 100, 4)
            }
        }

    except Exception as e:
        logger.error(f"[APR] Failed to calculate APR/APY: {e}")
        return None


def format_small_number(n):
    try:
        n = float(n)
        return f"{n:.8f}" if n < 0.01 else f"{n:.4f}"
    except Exception as e:
        logger.warning(f"[APR] format_small_number failed: {e}")
        return "0.0000"
