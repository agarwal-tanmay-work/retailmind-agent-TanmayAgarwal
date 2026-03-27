"""
Tool 2: get_inventory_health
==============================
Returns inventory status for a product: current stock, average daily sales,
estimated days to stockout, and a status flag.

Status flags:
  - Critical: < 7 days to stockout
  - Low: 7-14 days to stockout
  - Healthy: > 14 days to stockout
"""

from data.loader import get_products_df


def get_inventory_health(product_id: str) -> dict:
    """
    Get inventory health status for a specific product.
    
    Args:
        product_id: The product ID (e.g., 'SC001')
    
    Returns:
        Dict with keys: product_id, product_name, stock_quantity, avg_daily_sales,
        days_to_stockout, status, reorder_level, needs_reorder
    """
    df = get_products_df()
    product = df[df['product_id'] == product_id.upper()]
    
    if product.empty:
        return {"error": f"Product {product_id} not found"}
    
    row = product.iloc[0]
    stock = int(row['stock_quantity'])
    avg_sales = float(row['avg_daily_sales'])
    reorder_level = int(row['reorder_level'])
    
    # Compute days to stockout (handle division by zero)
    if avg_sales > 0:
        days_to_stockout = round(stock / avg_sales, 1)
    else:
        days_to_stockout = float('inf')  # No sales means no stockout risk
    
    # Determine status flag
    if days_to_stockout == float('inf'):
        status = "Healthy"
    elif days_to_stockout < 7:
        status = "Critical"
    elif days_to_stockout <= 14:
        status = "Low"
    else:
        status = "Healthy"
    
    return {
        "product_id": row['product_id'],
        "product_name": row['product_name'],
        "category": row['category'],
        "stock_quantity": stock,
        "avg_daily_sales": avg_sales,
        "days_to_stockout": days_to_stockout if days_to_stockout != float('inf') else "N/A (no sales)",
        "status": status,
        "reorder_level": reorder_level,
        "needs_reorder": stock <= reorder_level,
        "price": float(row['price'])
    }
