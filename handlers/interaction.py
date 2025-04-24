import logging
import discord
from core.chart_builder import fetch_closing_prices
from core.price_density import get_range_by_density_dexscreener
from core.fallback import fetch_candles_fallback
from services.fetch_pool_data import fetch_pool_data
from handlers.response import send_analysis_result

logger = logging.getLogger("ZenPool")

async def analyze_pair(interaction: discord.Interaction, network: str, pair: str):
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
        fee_rate = info.get("fee_rate", 0.003)
        apr_value = round((info["volume_usd"] / info["liquidity_usd"]) * fee_rate * 365 * 100 * 0.75, 2) if info["volume_usd"] > 0 and info["liquidity_usd"] > 0 else 0
        logger.info(f"[APR] Calculated: {apr_value}%")

        logger.info("[Chart] Fetching closing prices")
        closes = fetch_closing_prices(info["pair"].split("/")[0].lower())
        logger.debug(f"[Chart] First prices: {closes[:5]}")

        logger.info("[Range] Fetching density-based range")
        range_auto = get_range_by_density_dexscreener(network, pair)
        logger.debug(f"[Range] Result: {range_auto}")

        if range_auto:
            price_now = info["price_usd"]
            range_width = range_auto[1] - range_auto[0]
            if (range_width / price_now) < 0.02:
                logger.warning("[RANGE] Too narrow (<2%) - fallback")
                range_auto = None

        if range_auto:
            price_range = {
                "lower": range_auto[0],
                "upper": range_auto[1],
                "confidence": "Dense range based on 90d (4h candles)"
            }
            candles = fetch_candles_fallback(network, pair)
        else:
            price = info["price_usd"]
            price_range = {
                "lower": round(price * 0.995, 4),
                "upper": round(price * 1.005, 4),
                "confidence": "Fallback ±0.5% range applied"
            }
            candles = fetch_candles_fallback(network, pair)

        logger.info(f"[Result] Sending analysis with APR: {apr_value}, Range: {price_range}, Closing prices: {len(closes)}")
        await send_analysis_result(interaction, info, network, pair, apr_value, price_range, closes, candles)
        logger.debug("[EXIT] analyze_pair - result sent")

    except Exception as e:
        logger.error(f"[ERROR] analyze_pair failed: {e}")
        await interaction.followup.send("❌ Unexpected error occurred.")
