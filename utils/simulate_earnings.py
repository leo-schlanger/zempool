def format_small_number(value: float, min_sig_digits: int = 2) -> str:
    str_val = f"{value:.20f}".rstrip("0")
    integer, decimal = str_val.split(".")
    sig_digits = 0
    result = "0."
    for digit in decimal:
        result += digit
        if digit != "0":
            sig_digits += 1
        if sig_digits >= min_sig_digits:
            break
    return result

def estimate_passive_apr(volume_24h, liquidity_usd, fee_rate=0.003):
    if not volume_24h or not liquidity_usd or liquidity_usd == 0:
        return None
    try:
        daily_fees = float(volume_24h) * fee_rate
        estimated_apr = (daily_fees * 365) / float(liquidity_usd)
        return estimated_apr * 100  # % APR
    except:
        return None

def simulate_apr_apy(apr_percentage, volume_24h=None, liquidity_usd=None, initial_amount=100):
    try:
        if apr_percentage in [None, "N/A"] and volume_24h and liquidity_usd:
            apr_percentage = estimate_passive_apr(volume_24h, liquidity_usd)

        if apr_percentage in [None, "N/A"]:
            return None

        if isinstance(apr_percentage, str):
            apr = float(apr_percentage.strip('%'))
        else:
            apr = float(apr_percentage)

        apr_decimal = apr / 100
    except:
        return None

    earnings_apr_dollars = {
        "daily": round(initial_amount * apr_decimal / 365, 4),
        "monthly": round(initial_amount * apr_decimal / 12, 4),
        "yearly": round(initial_amount * apr_decimal, 4),
    }

    apy_percentage = {
        "daily": round((1 + apr_decimal / 365 - 1) * 100, 4),
        "monthly": round(((1 + apr_decimal / 365) ** 30 - 1) * 100, 4),
        "yearly": round(((1 + apr_decimal / 365) ** 365 - 1) * 100, 4),
    }

    return {
        "apr_return_usd": earnings_apr_dollars,
        "apy_percent": apy_percentage,
        "apr_percent": format_small_number(apr)
    }
