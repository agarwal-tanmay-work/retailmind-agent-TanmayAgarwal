"""
Tool 6: generate_restock_alert
================================
Scans all products and returns a list of products at risk of stockout
within the specified number of days, sorted by urgency (fewest days remaining first).
Also includes estimated revenue at risk.

Revenue at risk = price × (remaining stock + avg_daily_sales × threshold_days)
"""

from data.loader import get_products_df


def generate_restock_alert(threshold_days: int = 7) -> list[dict]:
    """
    Generate restock alerts for products at risk of stockout.
    
    Args:
        threshold_days: Number of days to use as stockout threshold (default: 7)
    
    Returns:
        List of dicts sorted by urgency (fewest days first), each with:
        product_id, product_name, category, stock_quantity, avg_daily_sales,
        days_to_stockout, status, revenue_at_risk
    """
    df = get_products_df()
    
    alerts = []
    for _, row in df.iterrows():
        stock = int(row['stock_quantity'])
        avg_sales = float(row['avg_daily_sales'])
        price = float(row['price'])
        
        # Compute days to stockout
        if avg_sales > 0:
            days_to_stockout = round(stock / avg_sales, 1)
        else:
            continue  # Skip products with zero sales (no stockout risk)
        
        # Only include products at risk within threshold
        if days_to_stockout <= threshold_days:
            # Revenue at risk formula from requirements
            revenue_at_risk = round(price * (stock + avg_sales * threshold_days), 2)
            
            # Determine status
            if days_to_stockout < 7:
                status = "🔴 Critical"
            else:
                status = "🟡 Low"
            
            alerts.append({
                "product_id": row['product_id'],
                "product_name": row['product_name'],
                "category": row['category'],
                "stock_quantity": stock,
                "avg_daily_sales": avg_sales,
                "days_to_stockout": days_to_stockout,
                "status": status,
                "revenue_at_risk": revenue_at_risk,
                "reorder_level": int(row['reorder_level']),
                "price": price
            })
    
    # Sort by urgency (fewest days remaining first)
    alerts.sort(key=lambda x: x['days_to_stockout'])
    
    return alerts
