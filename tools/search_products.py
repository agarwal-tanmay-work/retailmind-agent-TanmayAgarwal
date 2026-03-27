"""
Tool 1: search_products
========================
Searches and returns matching products from the CSV based on a text query
and optional category filter. Returns product ID, name, category, price,
stock, rating for the top 5 matches.

Uses simple string matching on product_name and category fields.
"""

from data.loader import get_products_df


def search_products(query: str, category: str = None) -> list[dict]:
    """
    Search products by text query with optional category filter.
    
    Args:
        query: Search text to match against product names (case-insensitive)
        category: Optional category filter (Tops/Dresses/Bottoms/Outerwear/Accessories)
    
    Returns:
        List of up to 5 matching product dicts with keys:
        product_id, product_name, category, price, stock_quantity, avg_rating
    """
    df = get_products_df()
    
    # Apply category filter if provided
    if category and category.lower() != "all categories":
        df = df[df['category'].str.lower() == category.lower()]
    
    # String matching on product_name (case-insensitive)
    # Split query into words and check if any word matches
    query_lower = query.lower()
    query_words = query_lower.split()
    
    # Score each product by how many query words match in the product name or category
    def match_score(row):
        name_lower = row['product_name'].lower()
        cat_lower = row['category'].lower()
        score = 0
        for word in query_words:
            if word in name_lower:
                score += 2  # Higher weight for name matches
            if word in cat_lower:
                score += 1
        return score
    
    df = df.copy()
    df['_score'] = df.apply(match_score, axis=1)
    
    # Filter to products with at least some match, or return top by rating if no matches
    matched = df[df['_score'] > 0].sort_values('_score', ascending=False)
    
    if matched.empty:
        # If no string matches, return top 5 products by rating as fallback
        matched = df.sort_values('avg_rating', ascending=False)
    
    # Return top 5 results
    results = []
    for _, row in matched.head(5).iterrows():
        results.append({
            "product_id": row['product_id'],
            "product_name": row['product_name'],
            "category": row['category'],
            "price": float(row['price']),
            "stock_quantity": int(row['stock_quantity']),
            "avg_rating": float(row['avg_rating']),
            "avg_daily_sales": float(row['avg_daily_sales']),
            "review_count": int(row['review_count'])
        })
    
    return results
