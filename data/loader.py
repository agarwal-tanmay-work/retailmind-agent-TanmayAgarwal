"""
Data Loader Module
==================
Loads and caches the RetailMind product and review datasets from CSV files.
Uses Streamlit's caching to avoid re-reading files on every interaction.
"""

import pandas as pd
import streamlit as st
import os

# Get the project root directory (where CSVs are located)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PRODUCTS_CSV = os.path.join(PROJECT_ROOT, "retailmind_products.csv")
REVIEWS_CSV = os.path.join(PROJECT_ROOT, "retailmind_reviews.csv")


@st.cache_data
def get_products_df() -> pd.DataFrame:
    """
    Load the products CSV into a pandas DataFrame.
    Cached to avoid re-reading on every Streamlit rerun.
    
    Returns:
        pd.DataFrame with columns: product_id, product_name, category, price, cost,
        stock_quantity, avg_daily_sales, return_rate, avg_rating, review_count,
        launch_date, reorder_level
    """
    df = pd.read_csv(PRODUCTS_CSV)
    # Ensure correct data types
    df['price'] = df['price'].astype(float)
    df['cost'] = df['cost'].astype(float)
    df['stock_quantity'] = df['stock_quantity'].astype(int)
    df['avg_daily_sales'] = df['avg_daily_sales'].astype(float)
    df['return_rate'] = df['return_rate'].astype(float)
    df['avg_rating'] = df['avg_rating'].astype(float)
    df['review_count'] = df['review_count'].astype(int)
    df['reorder_level'] = df['reorder_level'].astype(int)
    df['launch_date'] = pd.to_datetime(df['launch_date'])
    return df


@st.cache_data
def get_reviews_df() -> pd.DataFrame:
    """
    Load the reviews CSV into a pandas DataFrame.
    Cached to avoid re-reading on every Streamlit rerun.
    
    Returns:
        pd.DataFrame with columns: review_id, product_id, reviewer_name, rating,
        review_title, review_text, verified_purchase, helpful_votes, review_date
    """
    df = pd.read_csv(REVIEWS_CSV)
    df['rating'] = df['rating'].astype(int)
    df['helpful_votes'] = df['helpful_votes'].astype(int)
    df['verified_purchase'] = df['verified_purchase'].astype(bool)
    df['review_date'] = pd.to_datetime(df['review_date'])
    return df


def get_all_categories() -> list:
    """Return a sorted list of all unique product categories."""
    df = get_products_df()
    return sorted(df['category'].unique().tolist())
