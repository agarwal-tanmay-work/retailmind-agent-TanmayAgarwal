"""
Tool 5: get_category_performance
==================================
Returns aggregated category-level metrics:
  - Total SKUs
  - Average rating
  - Average margin %
  - Total stock units
  - Number of low/critical stock items
  - Top 3 revenue-generating products (price × avg_daily_sales)
"""

from data.loader import get_products_df


def get_category_performance(category: str) -> dict:
    """
    Get aggregated performance metrics for a product category.
    
    Args:
        category: Category name (Tops/Dresses/Bottoms/Outerwear/Accessories)
    
    Returns:
        Dict with keys: category, total_skus, avg_rating, avg_margin_pct,
        total_stock, critical_stock_items, low_stock_items, top_3_revenue_products
    """
    df = get_products_df()
    
    cat_df = df[df['category'].str.lower() == category.lower()]
    
    if cat_df.empty:
        return {"error": f"Category '{category}' not found. Available: {df['category'].unique().tolist()}"}
    
    # Compute margins
    cat_df = cat_df.copy()
    cat_df['gross_margin_pct'] = (cat_df['price'] - cat_df['cost']) / cat_df['price'] * 100
    cat_df['daily_revenue'] = cat_df['price'] * cat_df['avg_daily_sales']
    
    # Compute days to stockout for stock health analysis
    cat_df['days_to_stockout'] = cat_df.apply(
        lambda r: r['stock_quantity'] / r['avg_daily_sales'] if r['avg_daily_sales'] > 0 else float('inf'),
        axis=1
    )
    
    # Count critical and low stock items
    critical_items = cat_df[cat_df['days_to_stockout'] < 7]
    low_items = cat_df[(cat_df['days_to_stockout'] >= 7) & (cat_df['days_to_stockout'] <= 14)]
    
    # Top 3 revenue generating products
    top_revenue = cat_df.nlargest(3, 'daily_revenue')
    top_3 = []
    for _, row in top_revenue.iterrows():
        top_3.append({
            "product_id": row['product_id'],
            "product_name": row['product_name'],
            "daily_revenue": round(float(row['daily_revenue']), 2),
            "price": float(row['price']),
            "avg_daily_sales": float(row['avg_daily_sales'])
        })
    
    # Low margin products in category
    low_margin_products = cat_df[cat_df['gross_margin_pct'] < 20]
    low_margin_list = []
    for _, row in low_margin_products.iterrows():
        low_margin_list.append({
            "product_id": row['product_id'],
            "product_name": row['product_name'],
            "margin_pct": round(float(row['gross_margin_pct']), 2)
        })
    
    return {
        "category": category,
        "total_skus": len(cat_df),
        "avg_rating": round(float(cat_df['avg_rating'].mean()), 2),
        "avg_margin_pct": round(float(cat_df['gross_margin_pct'].mean()), 2),
        "total_stock_units": int(cat_df['stock_quantity'].sum()),
        "total_daily_revenue": round(float(cat_df['daily_revenue'].sum()), 2),
        "critical_stock_items": len(critical_items),
        "low_stock_items": len(low_items),
        "healthy_stock_items": len(cat_df) - len(critical_items) - len(low_items),
        "top_3_revenue_products": top_3,
        "low_margin_products": low_margin_list
    }
