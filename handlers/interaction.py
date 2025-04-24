import logging
import discord
from services.fetch_pool_data import fetch_pool_data
from utils.renderer import send_analysis_result

logger = logging.getLogger("ZenPool")

async def analyze_pair(interaction: discord.Interaction, network: str, pair: str):
    closes = []  # placeholder since closing prices are no longer used
    logger.debug(f"[ENTRY] analyze_pair(network={network}, pair={pair})")
    try:
        logger.info(f"[fetch_pool_data] Fetching pool for network={network}, pair={pair}")
        info = fetch_pool_data(network, pair)
        logger.info(f"[fetch_pool_data] Result: {info}")

        if isinstance(info, str):
            await interaction.followup.send(info)
            logger.debug(f"[EXIT] analyze_pair - error message sent to user")
            return

        logger.info(f"[APR] fee_rate: {info.get('fee_rate', 0.003)}")
        fee_rate = float(info.get("fee_rate", 0.003))
        apr_value = round((info["volume_usd"] / info["liquidity_usd"]) * fee_rate * 365 * 100 * 0.75, 2) if info["volume_usd"] > 0 and info["liquidity_usd"] > 0 else 0
        logger.info(f"[APR] Calculated: {apr_value}%")

        logger.info("[Chart] Fetching closing prices")
        logger.debug(f"[Chart] First prices: {closes[:5]}")

        logger.info("[Range] Fetching density-based range")
        range_auto = None  # disabled chart call (fallback will be applied based on volume)
        logger.debug(f"[Range] Result: {range_auto}")

        
        # Fallback volume-based range simulation (replaces density-based chart analysis)
        spread_pct = 0.01 if info["volume_usd"] > 100_000 else 0.02 if info["volume_usd"] > 10_000 else 0.03
        token0_price = float(info.get("token0_price", 0))
        token1_price = float(info.get("token1_price", 1)) or 1  # fallback para evitar divisão por zero
        price = token0_price / token1_price
        price_range = {
            "lower": round(price * (1 - spread_pct), 4),
            "upper": round(price * (1 + spread_pct), 4),
            "confidence": f"Simulated ±{int(spread_pct * 100)}% range based on volume"
        }
        candles = []  # Not used due to lack of historical candles in public API


        logger.info(f"[Result] Sending analysis with APR: {apr_value}, Range: {price_range}, Closing prices: {len(closes)}")
        await send_analysis_result(interaction, info, network, pair, apr_value, price_range, closes, candles)
        logger.debug("[EXIT] analyze_pair - result sent")

    except Exception as e:
        logger.error(f"[ERROR] analyze_pair failed: {e}")
        await interaction.followup.send("❌ Unexpected error occurred.")
