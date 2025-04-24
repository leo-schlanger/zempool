import discord
import logging
from core.apr import simulate_apr_apy, format_small_number
from core.chart_builder import generate_range_chart
from core.chart_density import get_range_coverage_ratio

logger = logging.getLogger("renderer")

async def send_analysis_result(interaction, info, network, pair, apr_value, price_range, closes, candles):
    if info["liquidity_usd"] < 5000:
        await interaction.followup.send("❌ Pool below minimum liquidity requirement ($5,000).")
        return

    earnings = simulate_apr_apy(apr_value, info["volume_usd"], info["liquidity_usd"])
    if not earnings:
        await interaction.followup.send("❌ Could not calculate APR.")
        return

    daily_usd = earnings['realistic_based_on_vol_liq']['daily']
    weekly_usd = earnings['realistic_based_on_vol_liq']['weekly']
    yearly_usd = earnings['realistic_based_on_vol_liq']['yearly']

    if candles:
        chart_path = f"range_{pair.replace('/', '_')}.png"
        chart_result = generate_range_chart(candles, price_range['lower'], price_range['upper'], chart_path)
    else:
        chart_result = None

    coverage = get_range_coverage_ratio(closes, price_range["lower"], price_range["upper"])
    apr_value = round(apr_value * coverage, 2)

    embed = discord.Embed(
        title="🧘 ZenPool Analysis",
        description=(
            f"**Pair:** `{info['pair']}`\n"
            f"**Network:** `{info['network']}`\n"
            f"**DEX:** `{info['dex']} (Fee: {round(info.get('fee_rate', 0.003) * 100, 2)}%)`"
        ),
        color=0x6e57e0
    )

    embed.add_field(name="Price", value=f"$ {format_small_number(info['price_usd'])}", inline=True)
    embed.add_field(name="Volume", value=f"$ {info['volume_usd']:,.2f}", inline=True)
    embed.add_field(name="Liquidity", value=f"$ {info['liquidity_usd']:,.2f}", inline=True)

    embed.add_field(name="APR", value=f"{apr_value}%", inline=False)
    embed.add_field(name="APR (Daily)", value=f"{round(apr_value / 365, 4)}%", inline=True)
    embed.add_field(name="APR (Weekly)", value=f"{round(apr_value / 52, 4)}%", inline=True)
    embed.add_field(
        name="Range",
        value=f"$ {format_small_number(price_range['lower'])} - $ {format_small_number(price_range['upper'])}\n*{price_range.get('confidence', '')}*",
        inline=False
    )

    embed.add_field(
        name="Earnings Est. ($1000)",
        value=f"• Daily: `$ {daily_usd}`\n• Weekly: `$ {weekly_usd}`\n• Yearly: `$ {yearly_usd}`",
        inline=False
    )

    embed.set_footer(text="Note: Gas fees and IL (Impermanent Loss) not included.")

    await interaction.followup.send(
        embed=embed,
        file=discord.File(chart_result) if chart_result else None,
    )