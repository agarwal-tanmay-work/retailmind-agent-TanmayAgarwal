"""
Router Agent Module
=====================
LLM-powered Router that classifies each incoming user query and dispatches
it to the correct downstream handler. Uses LLM-based intent classification
(NOT keyword/regex matching) as required by the exam specification.

Powered by **LangChain** and **Groq**.

Routes:
  - INVENTORY: stock levels, stockout risk, restock needs
  - PRICING: margins, pricing tiers, profitability
  - REVIEWS: customer feedback, ratings, sentiment
  - CATALOG: product search, category overviews
  - GENERAL: greetings, meta questions, general knowledge
"""

import os
import json
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from tools.search_products import search_products
from tools.inventory_health import get_inventory_health
from tools.pricing_analysis import get_pricing_analysis
from tools.review_insights import get_review_insights
from tools.category_performance import get_category_performance
from tools.restock_alert import generate_restock_alert

load_dotenv()


# System prompt for the router - carefully engineered for accurate classification
ROUTER_SYSTEM_PROMPT = """You are an intent classification router for a retail product intelligence system.
Your job is to classify the user's query into exactly ONE of these intents and extract relevant parameters.

INTENTS:
1. INVENTORY - Questions about stock levels, stockout risk, restock needs, how long inventory will last, which products need restocking.
2. PRICING - Questions about margins, pricing tiers, profitability, cost efficiency, pricing vs competitors, gross margin.
3. REVIEWS - Questions about customer feedback, ratings, complaints, what customers are saying, sentiment analysis.
4. CATALOG - Questions about product search, category overviews, top performers, broad catalog discovery, finding specific products.
5. GENERAL - Greetings, meta questions about the agent, general retail knowledge not in the data, thanks, help requests.

RULES:
- If the query mentions "stock", "inventory", "restock", "stockout", "running out", "how long will X last" → INVENTORY
- If the query mentions "margin", "profit", "price", "pricing", "cost", "expensive", "cheap" → PRICING
- If the query mentions "review", "customer", "feedback", "rating", "complaint", "sentiment", "happy", "unhappy" → REVIEWS
- If the query mentions "show me", "find", "search", "list", "category", "performance", "top products", "best selling" → CATALOG
- If none of the above clearly apply → GENERAL

OUTPUT FORMAT (JSON only, no other text):
{
  "intent": "INVENTORY|PRICING|REVIEWS|CATALOG|GENERAL",
  "product_id": "SC001 or null if not mentioned",
  "category": "category name or null",
  "threshold_days": 7,
  "search_query": "search terms if applicable or null"
}

IMPORTANT: Return ONLY valid JSON. No explanation. No markdown."""


# System prompt for generating natural language responses from tool outputs
RESPONSE_SYSTEM_PROMPT = """You are the RetailMind Analytics Copilot, an enterprise-grade product intelligence engine.
Your function is to provide product managers with high-fidelity, actionable catalog data.

GUIDELINES:
- Maintain a strictly professional, analytical, and data-driven B2B SaaS tone.
- Be concise but thorough. Use bullet points for clear data presentation.
- Always lead with specific quantitative metrics from the tool results.
- For inventory issues, emphasize operational urgency using exact days-to-stockout calculations.
- For pricing analysis, report precise margin percentages and strategic positioning.
- For consumer sentiment, highlight statistically significant positive and negative themes.
- Provide clear, operational recommendations based on the data.
- NEVER use emojis, exclamation marks, or colloquial language.
- Format currency in INR (₹) with standard grouping.
"""


def classify_intent(query: str, conversation_context: str = "") -> dict:
    """
    Use LangChain ChatGroq to classify user query intent. NOT keyword matching.
    
    Args:
        query: The user's natural language query
        conversation_context: Recent conversation history for context
    
    Returns:
        Dict with intent classification and extracted parameters
    """
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.1,  # Very low temperature for consistent classification
        max_tokens=150,   # Classification output is small
        model_kwargs={"top_p": 0.95},
        max_retries=0,
        timeout=15
    )
    
    user_message = f"Conversation context:\n{conversation_context}\n\nClassify this query: {query}"
    
    messages = [
        SystemMessage(content=ROUTER_SYSTEM_PROMPT),
        HumanMessage(content=user_message)
    ]
    
    response = llm.invoke(messages)
    output = response.content.strip()
    
    # Parse JSON (handle potential markdown fences)
    if output.startswith("```"):
        output = output.split("```")[1]
        if output.startswith("json"):
            output = output[4:]
    
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        # Fallback: try to extract intent from text
        output_upper = output.upper()
        for intent in ["INVENTORY", "PRICING", "REVIEWS", "CATALOG"]:
            if intent in output_upper:
                return {"intent": intent, "product_id": None, "category": None, "search_query": None}
        return {"intent": "GENERAL", "product_id": None, "category": None, "search_query": None}


def execute_tools(classification: dict, query: str, selected_category: str = None) -> str:
    """
    Execute the appropriate tool(s) based on intent classification.
    
    Args:
        classification: The intent classification dict from classify_intent()
        query: Original user query
        selected_category: Category filter from sidebar (if any)
    
    Returns:
        String representation of tool results
    """
    intent = classification.get("intent", "GENERAL").upper()
    product_id = classification.get("product_id")
    category = classification.get("category") or selected_category
    search_query = classification.get("search_query") or query
    threshold = classification.get("threshold_days", 7)
    
    results = {}
    
    if intent == "INVENTORY":
        if product_id:
            results["inventory_health"] = get_inventory_health(product_id)
        # Also get restock alerts for broader inventory questions
        results["restock_alerts"] = generate_restock_alert(threshold_days=threshold)
        
    elif intent == "PRICING":
        if product_id:
            results["pricing_analysis"] = get_pricing_analysis(product_id)
        else:
            # If no specific product, search for relevant products first
            found = search_products(search_query, category)
            if found:
                results["pricing_analysis"] = get_pricing_analysis(found[0]["product_id"])
                results["search_results"] = found
            
    elif intent == "REVIEWS":
        if product_id:
            results["review_insights"] = get_review_insights(product_id)
        else:
            # Search for the product first
            found = search_products(search_query, category)
            if found:
                results["review_insights"] = get_review_insights(found[0]["product_id"])
                results["search_results"] = found
    
    elif intent == "CATALOG":
        if category and category.lower() != "all categories":
            results["category_performance"] = get_category_performance(category)
        
        # Also search for products
        results["search_results"] = search_products(search_query, category)
        
    else:  # GENERAL
        results["general"] = True
    
    return json.dumps(results, indent=2, default=str)


def generate_response(query: str, tool_results: str, conversation_history: list, intent: str) -> str:
    """
    Generate a natural language response using LangChain ChatGroq with tool results.
    
    Args:
        query: Original user query
        tool_results: JSON string of tool execution results
        conversation_history: List of previous messages
        intent: The classified intent
    
    Returns:
        Natural language response string
    """
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.5,  # Moderate temperature for natural but accurate responses
        max_tokens=800,   # Allow detailed responses
        model_kwargs={"top_p": 0.9},
        max_retries=0,
        timeout=25
    )
    
    messages = [SystemMessage(content=RESPONSE_SYSTEM_PROMPT)]
    
    # Add conversation history for multi-turn context (last 6 messages)
    for msg in conversation_history[-6:]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    
    if intent.upper() == "GENERAL":
        # For general queries, respond directly without tool data
        messages.append(HumanMessage(content=query))
    else:
        # Include tool results in the prompt
        content = (
            f"User asked: {query}\n\n"
            f"Intent classified as: {intent}\n\n"
            f"Tool results:\n{tool_results}\n\n"
            f"Please provide a clear, actionable response based on this data. "
            f"Include specific numbers and recommendations."
        )
        messages.append(HumanMessage(content=content))
    
    response = llm.invoke(messages)
    return response.content.strip()


def route_query(query: str, conversation_history: list = None, selected_category: str = None) -> str:
    """
    Main entry point: Route a user query through classification → tool execution → response.
    
    This is the primary function called by the Streamlit UI.
    
    Args:
        query: The user's natural language query
        conversation_history: List of previous message dicts
        selected_category: Category filter from sidebar
    
    Returns:
        Natural language response string
    """
    if conversation_history is None:
        conversation_history = []
    
    # Build conversation context string for the classifier
    context = "\n".join([
        f"{'User' if m['role'] == 'user' else 'Agent'}: {m['content'][:150]}"
        for m in conversation_history[-6:]
    ]) if conversation_history else "No prior conversation."
    
    # Step 1: Classify intent using LLM
    classification = classify_intent(query, context)
    intent = classification.get("intent", "GENERAL")
    
    # Step 2: Execute appropriate tools
    tool_results = execute_tools(classification, query, selected_category)
    
    # Step 3: Generate natural language response
    response = generate_response(query, tool_results, conversation_history, intent)
    
    return response
