import logging
logger = logging.getLogger("apr")
logger.setLevel(logging.DEBUG)
def simulate_apr_apy(apr, volume, liquidity, capital=1000):
    try:
        # Conversão segura para float
        apr = float(apr)
        volume = float(volume)
        liquidity = float(liquidity)

        # Checagens de sanidade
        if apr <= 0 or volume <= 0 or liquidity <= 0:
            return None

        # Cálculo do retorno diário em % e em $ sobre capital fornecido (default: $1000)
        daily_return_rate = apr / 365 / 100
        daily_earn = round(capital * daily_return_rate, 2)
        weekly_earn = round(daily_earn * 7, 2)
        yearly_earn = round(capital * apr / 100, 2)

        # Estimativa realista baseada em volume e liquidez (rendimento sobre proporção do volume)
        proportion = volume / liquidity
        realistic_daily_usd = round(proportion * 0.5 * capital * 0.003, 2)  # assume 0.3% fee share, split 50/50
        realistic_weekly_usd = round(realistic_daily_usd * 7, 2)
        realistic_yearly_usd = round(realistic_daily_usd * 365, 2)

        # APY composto
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
        return None


def format_small_number(n):
    try:
        n = float(n)
        return f"{n:.8f}" if n < 0.01 else f"{n:.4f}"
    except:
        return "0.0000"
