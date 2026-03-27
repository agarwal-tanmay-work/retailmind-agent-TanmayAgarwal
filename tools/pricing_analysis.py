"""
Tool 3: get_pricing_analysis
==============================
Returns pricing intelligence for a product:
  - Gross margin % = (price - cost) / price * 100
  - Price positioning: Premium / Mid-Range / Budget (based on category averages)
  - Flag if margin is below 20%
"""

from data.loader import get_products_df


def get_pricing_analysis(product_id: str) -> dict:
    """
    Get pricing analysis for a specific product.
    
    Args:
        product_id: The product ID (e.g., 'SC001')
    
    Returns:
        Dict with keys: product_id, product_name, price, cost, gross_margin_pct,
        price_positioning, category_avg_price, low_margin_flag, suggested_action
    """
    df = get_products_df()
    product = df[df['product_id'] == product_id.upper()]
    
    if product.empty:
        return {"error": f"Product {product_id} not found"}
    
    row = product.iloc[0]
    price = float(row['price'])
    cost = float(row['cost'])
    category = row['category']
    
    # Compute gross margin percentage
    gross_margin_pct = round((price - cost) / price * 100, 2)
    
    # Calculate category average price for positioning
    category_products = df[df['category'] == category]
    category_avg_price = round(category_products['price'].mean(), 2)
    category_min_price = float(category_products['price'].min())
    category_max_price = float(category_products['price'].max())
    
    # Determine price positioning based on category comparison
    price_range = category_max_price - category_min_price
    if price_range > 0:
        relative_position = (price - category_min_price) / price_range
        if relative_position >= 0.66:
            positioning = "Premium"
        elif relative_position >= 0.33:
            positioning = "Mid-Range"
        else:
            positioning = "Budget"
    else:
        positioning = "Mid-Range"
    
    # Low margin flag and suggested action
    low_margin_flag = gross_margin_pct < 20
    suggested_action = None
    if gross_margin_pct < 20:
        suggested_action = f"⚠️ Margin critically low at {gross_margin_pct}%. Consider: (1) Renegotiate supplier cost, (2) Increase selling price by ₹{int((0.30 * cost / (1-0.30)) - price + price)}, or (3) Discontinue if sales volume doesn't justify."
    elif gross_margin_pct < 25:
        suggested_action = f"Margin below target (25%). Consider a modest price increase or cost optimization."
    
    # Compute category-level margin stats
    category_products = category_products.copy()
    category_products['margin'] = (category_products['price'] - category_products['cost']) / category_products['price'] * 100
    category_avg_margin = round(category_products['margin'].mean(), 2)
    
    return {
        "product_id": row['product_id'],
        "product_name": row['product_name'],
        "category": category,
        "price": price,
        "cost": cost,
        "gross_margin_pct": gross_margin_pct,
        "price_positioning": positioning,
        "category_avg_price": category_avg_price,
        "category_avg_margin_pct": category_avg_margin,
        "low_margin_flag": low_margin_flag,
        "suggested_action": suggested_action
    }
