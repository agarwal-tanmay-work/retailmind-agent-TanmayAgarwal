import sys
import os
import pandas as pd
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def test_data_loading():
    print("Test 1: Data Loading...", end="")
    from data.loader import get_products_df, get_reviews_df
    products = get_products_df()
    reviews = get_reviews_df()
    assert len(products) == 30, f"Expected 30 products, got {len(products)}"
    assert len(reviews) == 40, f"Expected 40 reviews, got {len(reviews)}"
    print(" [PASSED]")

def test_inventory_tool():
    print("Test 2: Inventory Health Tool...", end="")
    from tools.inventory_health import get_inventory_health
    res = get_inventory_health("SC001")
    assert "stock_quantity" in res
    print(" [PASSED]")

def test_restock_tool():
    print("Test 3: Restock Alert Tool...", end="")
    from tools.restock_alert import generate_restock_alert
    res = generate_restock_alert(threshold_days=7)
    assert isinstance(res, list)
    print(" [PASSED]")

def test_pricing_tool():
    print("Test 4: Pricing Analysis Tool...", end="")
    from tools.pricing_analysis import get_pricing_analysis
    res = get_pricing_analysis("SC005")
    assert "gross_margin_pct" in res
    print(" [PASSED]")

def test_router_classification():
    print("Test 5: LLM Router classification...", end="")
    from agent.router import classify_intent
    res = classify_intent("Show me low stock items")
    assert res['intent'] == 'INVENTORY'
    print(" [PASSED]")

if __name__ == "__main__":
    try:
        test_data_loading()
        test_inventory_tool()
        test_restock_tool()
        test_pricing_tool()
        test_router_classification()
        print("\nAll Core Tests Passed! Ready for Submission.")
    except Exception as e:
        print(f"\n [FAILED] {str(e)}")
        sys.exit(1)
