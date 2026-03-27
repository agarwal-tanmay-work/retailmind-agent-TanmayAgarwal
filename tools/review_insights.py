"""
Tool 4: get_review_insights
==============================
Uses LangChain and an LLM to summarise customer reviews for a given product.
Returns: average rating, total reviews, a 2-sentence sentiment summary,
and top 2 recurring themes (positive and negative).

Filters reviews CSV by product_id, concatenates review texts, and passes
to the LLM for summarisation. Caches results to avoid repeat API calls.
"""

import os
import json
import streamlit as st
from data.loader import get_products_df, get_reviews_df
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

# Cache for review insights to avoid repeated LLM calls
_review_cache = {}


def get_review_insights(product_id: str) -> dict:
    """
    Get LLM-generated review insights for a specific product using LangChain.
    
    Args:
        product_id: The product ID (e.g., 'SC001')
    
    Returns:
        Dict with keys: product_id, product_name, avg_rating, total_reviews,
        sentiment_summary, positive_themes, negative_themes
    """
    product_id = product_id.upper()
    
    # Check cache first
    if product_id in _review_cache:
        return _review_cache[product_id]
    
    products_df = get_products_df()
    reviews_df = get_reviews_df()
    
    product = products_df[products_df['product_id'] == product_id]
    if product.empty:
        return {"error": f"Product {product_id} not found"}
    
    product_name = product.iloc[0]['product_name']
    product_reviews = reviews_df[reviews_df['product_id'] == product_id]
    
    if product_reviews.empty:
        result = {
            "product_id": product_id,
            "product_name": product_name,
            "avg_rating": float(product.iloc[0]['avg_rating']),
            "total_reviews": 0,
            "sentiment_summary": "No customer reviews available for this product yet.",
            "positive_themes": [],
            "negative_themes": []
        }
        _review_cache[product_id] = result
        return result
    
    # Calculate average rating from reviews
    avg_rating = round(product_reviews['rating'].mean(), 2)
    total_reviews = len(product_reviews)
    
    # Concatenate all review texts for LLM analysis
    review_texts = []
    for _, rev in product_reviews.iterrows():
        review_texts.append(
            f"Rating: {rev['rating']}/5 | Title: {rev['review_title']} | "
            f"Review: {rev['review_text']} | Verified: {rev['verified_purchase']}"
        )
    
    all_reviews_text = "\n".join(review_texts)
    
    # Call LLM for sentiment analysis and theme extraction
    try:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,  # Low temperature for consistent, factual analysis
            max_tokens=300,   # Sufficient for structured JSON response
            model_kwargs={"top_p": 0.9}, # Slightly restricted for focused output
            max_retries=0,
            timeout=15
        )
        
        system_content = (
            "You are a product review analyst. Analyze the following customer reviews "
            "and provide a JSON response with exactly this structure:\n"
            '{"sentiment_summary": "<2-sentence summary of overall sentiment>", '
            '"positive_themes": ["<theme 1>", "<theme 2>"], '
            '"negative_themes": ["<theme 1>", "<theme 2>"]}\n'
            "Keep themes concise (3-5 words each). Be specific and data-driven. "
            "Return ONLY valid JSON, no other text."
        )
        
        user_content = (
            f"Product: {product_name} (ID: {product_id})\n"
            f"Average Rating: {avg_rating}/5 from {total_reviews} reviews\n\n"
            f"Reviews:\n{all_reviews_text}"
        )
        
        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=user_content)
        ]
        
        # Use LangChain to invoke the LLM
        response = llm.invoke(messages)
        llm_output = response.content.strip()
        
        # Parse JSON response from LLM
        # Handle potential markdown code fences
        if llm_output.startswith("```"):
            llm_output = llm_output.split("```")[1]
            if llm_output.startswith("json"):
                llm_output = llm_output[4:]
        
        parsed = json.loads(llm_output)
        
        result = {
            "product_id": product_id,
            "product_name": product_name,
            "avg_rating": avg_rating,
            "total_reviews": total_reviews,
            "sentiment_summary": parsed.get("sentiment_summary", "Analysis unavailable."),
            "positive_themes": parsed.get("positive_themes", []),
            "negative_themes": parsed.get("negative_themes", [])
        }
        
    except Exception as e:
        # Fallback if LLM call fails - provide basic analysis
        result = {
            "product_id": product_id,
            "product_name": product_name,
            "avg_rating": avg_rating,
            "total_reviews": total_reviews,
            "sentiment_summary": f"Product has an average rating of {avg_rating}/5 from {total_reviews} reviews. LLM analysis temporarily unavailable.",
            "positive_themes": ["Unable to analyze"],
            "negative_themes": ["Unable to analyze"],
            "error_detail": str(e)
        }
    
    # Cache the result
    _review_cache[product_id] = result
    return result
