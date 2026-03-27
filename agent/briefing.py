"""
Daily Briefing Module
=======================
Generates an automatic Daily Briefing when the agent starts up.
The briefing includes:
  1. Top 3 most critically low-stock products with days-to-stockout and revenue at risk
  2. Worst-rated product with a one-line summary of customer unhappiness
  3. One pricing flag — product with lowest gross margin (if < 25%)
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv
from data.loader import get_products_df, get_reviews_df
from tools.restock_alert import generate_restock_alert
from tools.pricing_analysis import get_pricing_analysis
from tools.review_insights import get_review_insights

load_dotenv()


def generate_daily_briefing() -> str:
    """
    Generate an automatic Daily Briefing with critical alerts.
    Called on app startup before any user interaction.
    
    Returns:
        Formatted markdown string with the daily briefing content
    """
    products_df = get_products_df()
    
    briefing_parts = []
    briefing_parts.append("## Daily Intelligence Briefing — StyleCraft Catalog\n")
    briefing_parts.append("*Auto-generated on startup • Powered by RetailMind Analytics*\n")
    briefing_parts.append("---\n")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 1: Top 3 Critically Low-Stock Products
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    briefing_parts.append("### Critical Inventory Alerts\n")
    
    restock_alerts = generate_restock_alert(threshold_days=14)  # Broader scan
    
    if restock_alerts:
        # Take top 3 most urgent
        top_3 = restock_alerts[:3]
        for i, alert in enumerate(top_3, 1):
            days = alert['days_to_stockout']
            revenue = alert['revenue_at_risk']
            briefing_parts.append(
                f"**{i}. {alert['product_name']}** (`{alert['product_id']}`) — "
                f"*{alert['category']}*\n"
                f"   - [Urgent] **{days} days** to stockout | "
                f"Stock: {alert['stock_quantity']} units | "
                f"Daily sales: {alert['avg_daily_sales']} units/day\n"
                f"   - [Risk] Revenue at risk: **₹{revenue:,.0f}**\n"
            )
        
        briefing_parts.append("")
    else:
        briefing_parts.append("[OK] No critical inventory alerts. All products have healthy stock levels.\n")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 2: Worst-Rated Product
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    briefing_parts.append("### Lowest Rated Product Alert\n")
    
    worst_product = products_df.loc[products_df['avg_rating'].idxmin()]
    worst_id = worst_product['product_id']
    worst_name = worst_product['product_name']
    worst_rating = worst_product['avg_rating']
    
    # Get review insights for worst product (uses LLM)
    try:
        review_data = get_review_insights(worst_id)
        sentiment = review_data.get("sentiment_summary", "Review analysis unavailable.")
        negative_themes = review_data.get("negative_themes", [])
    except Exception:
        sentiment = "Review analysis temporarily unavailable."
        negative_themes = []
    
    briefing_parts.append(
        f"**{worst_name}** (`{worst_id}`) — Rating: **{worst_rating}/5.0**\n"
        f"- [Sentiment] {sentiment}\n"
    )
    if negative_themes:
        briefing_parts.append(f"- [Themes] Key issues: {', '.join(negative_themes)}\n")
    briefing_parts.append("")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 3: Pricing Flag (Lowest Margin Product)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    briefing_parts.append("### Margin/Pricing Flag\n")
    
    # Find product with lowest gross margin
    products_with_margin = products_df.copy()
    products_with_margin['gross_margin_pct'] = (
        (products_with_margin['price'] - products_with_margin['cost']) 
        / products_with_margin['price'] * 100
    )
    
    lowest_margin_product = products_with_margin.loc[products_with_margin['gross_margin_pct'].idxmin()]
    lowest_margin_pct = round(lowest_margin_product['gross_margin_pct'], 2)
    
    if lowest_margin_pct < 25:
        pricing_data = get_pricing_analysis(lowest_margin_product['product_id'])
        briefing_parts.append(
            f"**{lowest_margin_product['product_name']}** (`{lowest_margin_product['product_id']}`) — "
            f"*{lowest_margin_product['category']}*\n"
            f"- [Flag] Gross margin: **{lowest_margin_pct}%** (below 25% priority target)\n"
            f"- Price: ₹{lowest_margin_product['price']:,.0f} | Cost: ₹{lowest_margin_product['cost']:,.0f}\n"
        )
        if pricing_data.get("suggested_action"):
            briefing_parts.append(f"- [Action] {pricing_data['suggested_action']}\n")
    else:
        briefing_parts.append(
            f"[OK] All products have margins above 25%. "
            f"Lowest: {lowest_margin_product['product_name']} at {lowest_margin_pct}%.\n"
        )
    
    briefing_parts.append("\n---\n")
    briefing_parts.append("*Ask me anything about your catalog! Try: \"Which products need restocking?\" or \"What's the margin on SC018?\"*")
    
    return "\n".join(briefing_parts)
