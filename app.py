"""
RetailMind AI Agent — Streamlit Application
=============================================
Main Streamlit UI for the Product Intelligence Agent.
Features:
  - Sidebar with category filter
  - Auto-generated Daily Briefing on startup
  - Chat interface with multi-turn conversation memory
  - Always-visible Catalog Summary panel
  - Clear Chat button with briefing re-trigger
  - Premium glassmorphic dark-themed design with animations

Author: RetailMind Analytics
Framework: Streamlit + LangChain + Groq LLM
"""

import streamlit as st
import pandas as pd
from data.loader import get_products_df, get_all_categories
from agent.router import route_query
from agent.memory import ConversationMemory
from agent.briefing import generate_daily_briefing
import time


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="RetailMind AI — Product Intelligence Agent",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CUSTOM CSS — PREMIUM DARK THEME WITH ANIMATIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global font & dark background */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    /* ---- ANIMATED GRADIENT HEADER ---- */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 15px rgba(102, 126, 234, 0.4); }
        50% { box-shadow: 0 0 30px rgba(118, 75, 162, 0.6); }
    }
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes countUp {
        from { opacity: 0; transform: scale(0.5); }
        to { opacity: 1; transform: scale(1); }
    }
    
    .main-header {
        background: linear-gradient(270deg, #667eea, #764ba2, #f093fb, #667eea);
        background-size: 600% 600%;
        animation: gradientShift 8s ease infinite, fadeInUp 0.8s ease-out;
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        color: white;
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
        animation: gradientShift 12s ease infinite;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        position: relative;
        z-index: 1;
    }
    .main-header p {
        margin: 0.4rem 0 0 0;
        opacity: 0.9;
        font-size: 1rem;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }
    .main-header .tech-badges {
        margin-top: 0.8rem;
        position: relative;
        z-index: 1;
    }
    .main-header .tech-badge {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(10px);
        padding: 0.25rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        margin-right: 0.5rem;
        font-weight: 500;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* ---- GLASSMORPHIC METRIC CARDS ---- */
    .metric-card {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 1.2rem 1rem;
        border-radius: 16px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        animation: fadeInUp 0.6s ease-out, pulse 3s ease-in-out infinite;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    .metric-card h3 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: countUp 0.8s ease-out;
    }
    .metric-card p {
        margin: 0.3rem 0 0 0;
        font-size: 0.78rem;
        color: rgba(255, 255, 255, 0.6);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card .metric-icon {
        font-size: 1.5rem;
        margin-bottom: 0.3rem;
    }
    .metric-card-critical h3 {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .metric-card-healthy h3 {
        background: linear-gradient(135deg, #00b894, #55efc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* ---- BRIEFING CONTAINER ---- */
    .briefing-container {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        animation: slideInLeft 0.6s ease-out;
    }
    
    /* ---- SIDEBAR STYLING ---- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a1a 0%, #1a1a3e 50%, #0d0d2b 100%) !important;
    }
    [data-testid="stSidebar"] * {
        color: #c8c8e8 !important;
    }
    [data-testid="stSidebar"] .stSelectbox label {
        color: #a0aec0 !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 1px;
    }
    
    /* ---- SIDEBAR LOGO SECTION ---- */
    .sidebar-logo {
        text-align: center;
        padding: 1.5rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 1rem;
    }
    .sidebar-logo h2 {
        margin: 0.5rem 0 0 0;
        font-size: 1.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .sidebar-logo p {
        font-size: 0.75rem;
        opacity: 0.5;
        margin: 0;
    }
    
    /* ---- CAPABILITY LIST ---- */
    .capability-item {
        display: flex;
        align-items: center;
        padding: 0.5rem 0.8rem;
        margin: 0.3rem 0;
        border-radius: 10px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.05);
        transition: all 0.3s ease;
        animation: slideInLeft 0.6s ease-out;
    }
    .capability-item:hover {
        background: rgba(102, 126, 234, 0.1);
        border-color: rgba(102, 126, 234, 0.3);
        transform: translateX(4px);
    }
    .capability-icon {
        font-size: 1.2rem;
        margin-right: 0.7rem;
    }
    .capability-text {
        font-size: 0.82rem;
        font-weight: 500;
    }
    .capability-desc {
        font-size: 0.7rem;
        opacity: 0.5;
        margin-top: 0.1rem;
    }
    
    /* ---- CHAT STYLING ---- */
    .stChatMessage {
        border-radius: 16px !important;
        animation: fadeInUp 0.4s ease-out;
    }
    [data-testid="stChatMessageContent"] {
        color: #e0e0f0 !important;
    }
    
    /* ---- BUTTON STYLING ---- */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 0.6rem 1.5rem;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.8rem;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* ---- SECTION DIVIDER ---- */
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.3), transparent);
        margin: 1.5rem 0;
    }
    
    /* ---- CHAT INPUT ---- */
    .stChatInput textarea {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    
    /* ---- STATUS INDICATOR ---- */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    .status-online {
        background: rgba(0, 184, 148, 0.15);
        color: #00b894;
        border: 1px solid rgba(0, 184, 148, 0.3);
    }
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    .blink-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #00b894;
        display: inline-block;
        animation: blink 1.5s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SESSION STATE INITIALIZATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "briefing_generated" not in st.session_state:
    st.session_state.briefing_generated = False

if "daily_briefing" not in st.session_state:
    st.session_state.daily_briefing = ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIDEBAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    # Logo section
    st.markdown("""
    <div class="sidebar-logo">
        <div style="font-size: 2.5rem;">🛍️</div>
        <h2>RetailMind AI</h2>
        <p>Product Intelligence Agent v1.0</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Status
    st.markdown("""
    <div style="text-align:center; margin-bottom: 1rem;">
        <span class="status-indicator status-online">
            <span class="blink-dot"></span> Agent Online
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Category filter
    categories = ["All Categories"] + get_all_categories()
    selected_category = st.selectbox(
        "📂 CATEGORY FILTER",
        categories,
        index=0,
        help="Filter the agent's context to a specific product category"
    )
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Clear Chat button
    if st.button("🔄 Clear Chat & Refresh Briefing", use_container_width=True):
        st.session_state.memory.clear()
        st.session_state.messages = []
        st.session_state.briefing_generated = False
        st.session_state.daily_briefing = ""
        st.rerun()
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Capabilities
    st.markdown("#### 🤖 Agent Capabilities")
    
    capabilities = [
        ("📦", "Inventory Health", "Stock levels & stockout risk"),
        ("💲", "Pricing Analysis", "Margins & price positioning"),
        ("⭐", "Review Insights", "LLM-powered sentiment"),
        ("📊", "Catalog Search", "Natural language discovery"),
        ("🏷️", "Category Metrics", "Aggregated performance"),
        ("🔔", "Restock Alerts", "Urgency-based warnings"),
    ]
    
    for icon, name, desc in capabilities:
        st.markdown(f"""
        <div class="capability-item">
            <span class="capability-icon">{icon}</span>
            <div>
                <div class="capability-text">{name}</div>
                <div class="capability-desc">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Tech stack footer
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0;">
        <div style="font-size: 0.65rem; opacity: 0.35; text-transform: uppercase; letter-spacing: 1px;">Powered by</div>
        <div style="display: flex; justify-content: center; gap: 0.5rem; margin-top: 0.5rem; flex-wrap: wrap;">
            <span style="background: rgba(255,255,255,0.06); padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.68rem; font-weight: 600;">🦜 LangChain</span>
            <span style="background: rgba(255,255,255,0.06); padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.68rem; font-weight: 600;">⚡ Groq</span>
            <span style="background: rgba(255,255,255,0.06); padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.68rem; font-weight: 600;">🎈 Streamlit</span>
        </div>
        <div style="font-size: 0.6rem; opacity: 0.25; margin-top: 0.8rem;">RetailMind Analytics © 2026</div>
    </div>
    """, unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN CONTENT AREA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Animated gradient header
st.markdown("""
<div class="main-header">
    <h1>🛍️ RetailMind Product Intelligence Agent</h1>
    <p>AI-powered catalog analytics for StyleCraft — Ask anything about your products, inventory, pricing, and customer reviews.</p>
    <div class="tech-badges">
        <span class="tech-badge">🦜 LangChain</span>
        <span class="tech-badge">⚡ Groq Llama 3.3</span>
        <span class="tech-badge">📊 30 SKUs · 5 Categories</span>
        <span class="tech-badge">🔧 6 AI Tools</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CATALOG SUMMARY PANEL (Always Visible)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
products_df = get_products_df()

# Apply category filter for summary if a specific category is selected
if selected_category != "All Categories":
    summary_df = products_df[products_df['category'] == selected_category]
else:
    summary_df = products_df

# Calculate summary metrics
total_skus = len(summary_df)
summary_df_with_stockout = summary_df.copy()
summary_df_with_stockout['days_to_stockout'] = summary_df_with_stockout.apply(
    lambda r: r['stock_quantity'] / r['avg_daily_sales'] if r['avg_daily_sales'] > 0 else float('inf'),
    axis=1
)
critical_stock = len(summary_df_with_stockout[summary_df_with_stockout['days_to_stockout'] < 7])
summary_df_with_margin = summary_df.copy()
summary_df_with_margin['margin'] = (summary_df_with_margin['price'] - summary_df_with_margin['cost']) / summary_df_with_margin['price'] * 100
avg_margin = round(summary_df_with_margin['margin'].mean(), 1)
avg_rating = round(summary_df['avg_rating'].mean(), 2)

# Display metrics in glassmorphic cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">📦</div>
        <h3>{total_skus}</h3>
        <p>Total SKUs</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    card_class = "metric-card metric-card-critical" if critical_stock > 0 else "metric-card metric-card-healthy"
    st.markdown(f"""
    <div class="{card_class}">
        <div class="metric-icon">{'🔴' if critical_stock > 0 else '🟢'}</div>
        <h3>{critical_stock}</h3>
        <p>Critical Stock</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">💰</div>
        <h3>{avg_margin}%</h3>
        <p>Avg Margin</p>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">⭐</div>
        <h3>{avg_rating}</h3>
        <p>Avg Rating</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DAILY BRIEFING (Auto-generated on startup)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if not st.session_state.briefing_generated:
    with st.spinner("🔄 Generating Daily Briefing — Scanning catalog for critical issues..."):
        try:
            briefing = generate_daily_briefing()
            st.session_state.daily_briefing = briefing
            st.session_state.briefing_generated = True
            
            # Add briefing as first assistant message
            st.session_state.messages.append({
                "role": "assistant",
                "content": briefing
            })
        except Exception as e:
            st.error(f"⚠️ Error generating daily briefing: {str(e)}")
            st.session_state.briefing_generated = True
            st.session_state.daily_briefing = "Daily briefing generation failed. Please check your API key in .env file."
            st.session_state.messages.append({
                "role": "assistant",
                "content": st.session_state.daily_briefing
            })

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHAT INTERFACE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# Chat input
if user_query := st.chat_input("💬 Ask about your catalog... e.g. 'Which dresses are low on stock?'"):
    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_query)
    
    # Add to session state
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.session_state.memory.add_message("user", user_query)
    
    # Generate response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🧠 Analyzing with LangChain + Groq..."):
            try:
                response = route_query(
                    query=user_query,
                    conversation_history=st.session_state.memory.get_history(),
                    selected_category=selected_category if selected_category != "All Categories" else None
                )
                st.markdown(response)
            except Exception as e:
                response = f"⚠️ I encountered an error processing your query: {str(e)}\n\nPlease ensure your GROQ_API_KEY is set correctly in the .env file."
                st.error(response)
    
    # Add response to history
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.memory.add_message("assistant", response)
