"""
RetailMind AI Agent — Streamlit Application (Premium Edition)
================================================================
Main Streamlit UI for the Product Intelligence Agent.

Features:
  - Sidebar with category filter & quick action buttons
  - Auto-generated Daily Briefing on startup
  - Chat interface with multi-turn conversation memory
  - Always-visible Catalog Summary panel with animated cards
  - Interactive Analytics Dashboard with Plotly charts
  - Premium glassmorphic dark-themed design with CSS animations
  - Robust error handling throughout
  - Export capabilities

Author: RetailMind Analytics
Framework: Streamlit + LangChain + Groq LLM + Plotly
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STARTUP VALIDATION — Graceful error handling
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def validate_environment():
    """Validate all required files and environment variables exist."""
    errors = []
    
    # Check CSV files
    project_root = os.path.dirname(os.path.abspath(__file__))
    products_csv = os.path.join(project_root, "retailmind_products.csv")
    reviews_csv = os.path.join(project_root, "retailmind_reviews.csv")
    
    if not os.path.exists(products_csv):
        errors.append("❌ `retailmind_products.csv` not found in project root.")
    if not os.path.exists(reviews_csv):
        errors.append("❌ `retailmind_reviews.csv` not found in project root.")
    
    # Check API key
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key or api_key == "your_groq_api_key_here":
        errors.append("❌ `GROQ_API_KEY` not set. Create a `.env` file with `GROQ_API_KEY=gsk_your_key`")
    
    return errors

# Run validation
startup_errors = validate_environment()

from data.loader import get_products_df, get_all_categories, get_reviews_df
from agent.router import route_query
from agent.memory import ConversationMemory
from agent.briefing import generate_daily_briefing


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="RetailMind AI — Product Intelligence",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CUSTOM CSS — PREMIUM DARK GLASSMORPHIC THEME
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }
    
    /* Animations */
    @keyframes gradientShift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes pulse { 0%,100% { box-shadow: 0 0 15px rgba(102,126,234,0.3); } 50% { box-shadow: 0 0 25px rgba(118,75,162,0.5); } }
    @keyframes slideInLeft { from { opacity: 0; transform: translateX(-20px); } to { opacity: 1; transform: translateX(0); } }
    @keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }
    
    /* Header */
    .main-header {
        background: linear-gradient(270deg, #667eea, #764ba2, #f093fb, #667eea);
        background-size: 600% 600%;
        animation: gradientShift 8s ease infinite, fadeInUp 0.8s ease-out;
        padding: 1.8rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.2rem;
        color: white;
        position: relative;
        overflow: hidden;
    }
    .main-header h1 { margin: 0; font-size: 1.8rem; font-weight: 800; letter-spacing: -0.5px; }
    .main-header p { margin: 0.3rem 0 0 0; opacity: 0.9; font-size: 0.9rem; font-weight: 300; }
    .tech-badges { margin-top: 0.6rem; }
    .tech-badge {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(10px);
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.7rem;
        margin-right: 0.4rem;
        font-weight: 500;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Metric Cards */
    .metric-card {
        background: rgba(255,255,255,0.06);
        backdrop-filter: blur(20px);
        padding: 1rem 0.8rem;
        border-radius: 14px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        animation: fadeInUp 0.6s ease-out, pulse 4s ease-in-out infinite;
        transition: transform 0.3s ease;
    }
    .metric-card:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(102,126,234,0.3); }
    .metric-card .icon { font-size: 1.3rem; margin-bottom: 0.2rem; }
    .metric-card h3 {
        margin: 0; font-size: 1.6rem; font-weight: 800;
        background: linear-gradient(135deg, #667eea, #f093fb);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .metric-card p { margin: 0.2rem 0 0 0; font-size: 0.72rem; color: rgba(255,255,255,0.55); font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-card-critical h3 { background: linear-gradient(135deg, #ff6b6b, #ee5a24); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
    .metric-card-healthy h3 { background: linear-gradient(135deg, #00b894, #55efc4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0a0a1a 0%, #1a1a3e 50%, #0d0d2b 100%) !important; }
    [data-testid="stSidebar"] * { color: #c8c8e8 !important; }
    .sidebar-logo { text-align: center; padding: 1.2rem 0; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 0.8rem; }
    .sidebar-logo h2 { margin: 0.4rem 0 0 0; font-size: 1.3rem; font-weight: 800; background: linear-gradient(135deg, #667eea, #f093fb); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
    .sidebar-logo p { font-size: 0.7rem; opacity: 0.4; margin: 0; }
    
    .status-indicator { display: inline-flex; align-items: center; gap: 0.3rem; padding: 0.15rem 0.5rem; border-radius: 20px; font-size: 0.68rem; font-weight: 600; }
    .status-online { background: rgba(0,184,148,0.15); color: #00b894; border: 1px solid rgba(0,184,148,0.3); }
    .blink-dot { width: 5px; height: 5px; border-radius: 50%; background: #00b894; display: inline-block; animation: blink 1.5s ease-in-out infinite; }
    
    .capability-item { display: flex; align-items: center; padding: 0.4rem 0.6rem; margin: 0.2rem 0; border-radius: 8px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.04); transition: all 0.3s ease; }
    .capability-item:hover { background: rgba(102,126,234,0.1); transform: translateX(3px); }
    .capability-icon { font-size: 1rem; margin-right: 0.5rem; }
    .capability-text { font-size: 0.78rem; font-weight: 500; }
    .capability-desc { font-size: 0.65rem; opacity: 0.45; }
    
    .section-divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(102,126,234,0.3), transparent); margin: 1rem 0; }
    
    /* Buttons */
    .stButton > button {
        border-radius: 10px; font-weight: 600;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white !important; border: none; transition: all 0.3s ease;
        font-size: 0.78rem;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102,126,234,0.4); }
    
    /* Chat */
    .stChatMessage { border-radius: 14px !important; animation: fadeInUp 0.4s ease-out; }
    [data-testid="stChatMessageContent"] { color: #e0e0f0 !important; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.05); border-radius: 8px; color: #a0a0c0;
        border: 1px solid rgba(255,255,255,0.08); font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea33, #764ba233); color: white !important;
        border-color: #667eea;
    }

    /* Quick action buttons */
    .quick-btn {
        display: inline-block; padding: 0.35rem 0.7rem; margin: 0.2rem;
        background: rgba(102,126,234,0.12); border: 1px solid rgba(102,126,234,0.25);
        border-radius: 20px; font-size: 0.72rem; color: #a78bfa; cursor: pointer;
        transition: all 0.2s ease; font-weight: 500;
    }
    .quick-btn:hover { background: rgba(102,126,234,0.25); transform: scale(1.03); }
</style>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SESSION STATE
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
    st.markdown("""
    <div class="sidebar-logo">
        <div style="font-size: 2.2rem;">🛍️</div>
        <h2>RetailMind AI</h2>
        <p>Product Intelligence Agent v2.0</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align:center; margin-bottom: 0.8rem;">
        <span class="status-indicator status-online"><span class="blink-dot"></span> Agent Online</span>
    </div>
    """, unsafe_allow_html=True)
    
    categories = ["All Categories"] + get_all_categories()
    selected_category = st.selectbox("📂 CATEGORY FILTER", categories, index=0,
        help="Filter the agent's context to a specific product category")
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    if st.button("🔄 Clear Chat & Refresh Briefing", use_container_width=True):
        st.session_state.memory.clear()
        st.session_state.messages = []
        st.session_state.briefing_generated = False
        st.session_state.daily_briefing = ""
        st.rerun()
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Quick action buttons
    st.markdown("#### ⚡ Quick Actions")
    quick_actions = [
        "🔴 Critical stock alerts",
        "📊 Best performing category",
        "💲 Low margin products",
        "⭐ Worst rated product",
        "📦 Full inventory report",
    ]
    for action in quick_actions:
        if st.button(action, use_container_width=True, key=f"qa_{action}"):
            st.session_state.quick_action = action
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    st.markdown("#### 🤖 Capabilities")
    capabilities = [
        ("📦", "Inventory Health", "Stockout prediction"),
        ("💲", "Pricing Analysis", "Margin & positioning"),
        ("⭐", "Review Insights", "LLM sentiment"),
        ("📊", "Catalog Search", "NLP discovery"),
        ("🏷️", "Category Metrics", "Aggregated KPIs"),
        ("🔔", "Restock Alerts", "Revenue at risk"),
    ]
    for icon, name, desc in capabilities:
        st.markdown(f'<div class="capability-item"><span class="capability-icon">{icon}</span><div><div class="capability-text">{name}</div><div class="capability-desc">{desc}</div></div></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; padding: 0.8rem 0;">
        <div style="display: flex; justify-content: center; gap: 0.4rem; flex-wrap: wrap;">
            <span style="background: rgba(255,255,255,0.06); padding: 0.15rem 0.5rem; border-radius: 6px; font-size: 0.65rem; font-weight: 600;">🦜 LangChain</span>
            <span style="background: rgba(255,255,255,0.06); padding: 0.15rem 0.5rem; border-radius: 6px; font-size: 0.65rem; font-weight: 600;">⚡ Groq</span>
            <span style="background: rgba(255,255,255,0.06); padding: 0.15rem 0.5rem; border-radius: 6px; font-size: 0.65rem; font-weight: 600;">🎈 Streamlit</span>
            <span style="background: rgba(255,255,255,0.06); padding: 0.15rem 0.5rem; border-radius: 6px; font-size: 0.65rem; font-weight: 600;">📊 Plotly</span>
        </div>
        <div style="font-size: 0.55rem; opacity: 0.2; margin-top: 0.6rem;">RetailMind Analytics © 2026</div>
    </div>
    """, unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ERROR DISPLAY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if startup_errors:
    for err in startup_errors:
        st.error(err)
    st.stop()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HEADER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<div class="main-header">
    <h1>🛍️ RetailMind Product Intelligence Agent</h1>
    <p>AI-powered catalog analytics for StyleCraft — powered by LangChain + Groq</p>
    <div class="tech-badges">
        <span class="tech-badge">🦜 LangChain</span>
        <span class="tech-badge">⚡ Groq Llama 3.3 70B</span>
        <span class="tech-badge">📊 30 SKUs · 5 Categories</span>
        <span class="tech-badge">🔧 6 AI Tools</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CATALOG SUMMARY PANEL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
products_df = get_products_df()
reviews_df = get_reviews_df()

if selected_category != "All Categories":
    summary_df = products_df[products_df['category'] == selected_category]
else:
    summary_df = products_df

total_skus = len(summary_df)
summary_calc = summary_df.copy()
summary_calc['days_to_stockout'] = summary_calc.apply(
    lambda r: r['stock_quantity'] / r['avg_daily_sales'] if r['avg_daily_sales'] > 0 else float('inf'), axis=1)
critical_stock = len(summary_calc[summary_calc['days_to_stockout'] < 7])
summary_calc['margin'] = (summary_calc['price'] - summary_calc['cost']) / summary_calc['price'] * 100
avg_margin = round(summary_calc['margin'].mean(), 1)
avg_rating = round(summary_df['avg_rating'].mean(), 2)
total_revenue = round((summary_df['price'] * summary_df['avg_daily_sales']).sum(), 0)
total_stock = int(summary_df['stock_quantity'].sum())

col1, col2, col3, col4, col5, col6 = st.columns(6)
metrics = [
    (col1, "📦", total_skus, "Total SKUs", ""),
    (col2, "🔴" if critical_stock > 0 else "🟢", critical_stock, "Critical Stock", "metric-card-critical" if critical_stock > 0 else "metric-card-healthy"),
    (col3, "💰", f"{avg_margin}%", "Avg Margin", ""),
    (col4, "⭐", avg_rating, "Avg Rating", ""),
    (col5, "📈", f"₹{total_revenue:,.0f}", "Daily Revenue", ""),
    (col6, "🏪", f"{total_stock:,}", "Total Stock", ""),
]
for col, icon, value, label, extra_class in metrics:
    with col:
        cls = f"metric-card {extra_class}" if extra_class else "metric-card"
        st.markdown(f'<div class="{cls}"><div class="icon">{icon}</div><h3>{value}</h3><p>{label}</p></div>', unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TABS: Chat | Analytics Dashboard
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
tab_chat, tab_analytics = st.tabs(["💬 AI Chat Agent", "📊 Analytics Dashboard"])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1: CHAT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_chat:
    # Daily Briefing
    if not st.session_state.briefing_generated:
        with st.status("🔄 Generating Daily Briefing...", expanded=True) as status:
            st.write("📡 Scanning inventory for stockout risks...")
            st.write("⭐ Analyzing product ratings...")
            st.write("💲 Checking margin anomalies...")
            try:
                briefing = generate_daily_briefing()
                st.session_state.daily_briefing = briefing
                st.session_state.briefing_generated = True
                st.session_state.messages.append({"role": "assistant", "content": briefing})
                status.update(label="✅ Daily Briefing Ready!", state="complete")
            except Exception as e:
                st.session_state.briefing_generated = True
                err_msg = f"⚠️ Briefing generation error: {str(e)}\n\nPlease check your GROQ_API_KEY."
                st.session_state.daily_briefing = err_msg
                st.session_state.messages.append({"role": "assistant", "content": err_msg})
                status.update(label="⚠️ Briefing Error", state="error")

    # Handle quick actions from sidebar
    if "quick_action" in st.session_state:
        action = st.session_state.pop("quick_action")
        query_map = {
            "🔴 Critical stock alerts": "Which products are critically low on stock and need immediate restocking?",
            "📊 Best performing category": "What is the best performing category by revenue and rating?",
            "💲 Low margin products": "Which products have the lowest margins and need pricing review?",
            "⭐ Worst rated product": "What is the worst rated product and why are customers unhappy?",
            "📦 Full inventory report": "Give me a full inventory health report across all products",
        }
        user_query = query_map.get(action, action)
        st.session_state.messages.append({"role": "user", "content": user_query})
        st.session_state.memory.add_message("user", user_query)
        
        try:
            response = route_query(
                query=user_query,
                conversation_history=st.session_state.memory.get_history(),
                selected_category=selected_category if selected_category != "All Categories" else None
            )
        except Exception as e:
            response = f"⚠️ Error: {str(e)}"
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.memory.add_message("assistant", response)
        st.rerun()

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])

    # Chat input
    if user_query := st.chat_input("💬 Ask about your catalog... e.g. 'Which dresses are low on stock?'"):
        # Input validation
        if not user_query.strip():
            st.toast("⚠️ Please enter a valid question.", icon="⚠️")
        else:
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_query)
            
            st.session_state.messages.append({"role": "user", "content": user_query})
            st.session_state.memory.add_message("user", user_query)
            
            with st.chat_message("assistant", avatar="🤖"):
                with st.status("🧠 Processing with LangChain + Groq...", expanded=False) as status:
                    try:
                        response = route_query(
                            query=user_query,
                            conversation_history=st.session_state.memory.get_history(),
                            selected_category=selected_category if selected_category != "All Categories" else None
                        )
                        status.update(label="✅ Analysis complete", state="complete")
                        st.markdown(response)
                    except Exception as e:
                        response = f"⚠️ Error processing query: {str(e)}\n\nPlease try rephrasing or check your API key."
                        status.update(label="⚠️ Error", state="error")
                        st.error(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.memory.add_message("assistant", response)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2: ANALYTICS DASHBOARD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_analytics:
    st.markdown("### 📊 Visual Analytics Dashboard")
    st.markdown("*Interactive charts powered by Plotly — explore your catalog data visually*")
    st.markdown("")
    
    # Use the filtered dataframe
    chart_df = summary_df.copy()
    chart_df['gross_margin_pct'] = ((chart_df['price'] - chart_df['cost']) / chart_df['price'] * 100).round(1)
    chart_df['daily_revenue'] = (chart_df['price'] * chart_df['avg_daily_sales']).round(0)
    chart_df['days_to_stockout'] = chart_df.apply(
        lambda r: round(r['stock_quantity'] / r['avg_daily_sales'], 1) if r['avg_daily_sales'] > 0 else 999, axis=1)
    
    # Dark theme for all charts
    chart_template = "plotly_dark"
    colors = px.colors.sequential.Purp
    
    # Row 1: Category comparison + Margin distribution
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Category Performance Radar
        cat_stats = products_df.groupby('category').agg(
            avg_rating=('avg_rating', 'mean'),
            avg_margin=('price', lambda x: ((x - products_df.loc[x.index, 'cost']) / x * 100).mean()),
            total_skus=('product_id', 'count'),
            total_stock=('stock_quantity', 'sum'),
            daily_revenue=('avg_daily_sales', lambda x: (x * products_df.loc[x.index, 'price']).sum())
        ).reset_index()
        
        fig = px.bar(cat_stats, x='category', y='daily_revenue',
                     color='avg_rating', color_continuous_scale='Purp',
                     title='Daily Revenue by Category',
                     labels={'daily_revenue': 'Daily Revenue (₹)', 'avg_rating': 'Avg Rating'},
                     template=chart_template)
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#a0a0c0'),
            title_font=dict(size=14, color='#e0e0ff'),
            height=350,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with chart_col2:
        # Margin vs Price Scatter
        fig2 = px.scatter(chart_df, x='price', y='gross_margin_pct',
                          size='avg_daily_sales', color='category',
                          hover_name='product_name',
                          title='Price vs Margin (bubble = daily sales)',
                          labels={'price': 'Price (₹)', 'gross_margin_pct': 'Gross Margin %'},
                          template=chart_template,
                          color_discrete_sequence=px.colors.qualitative.Set2)
        fig2.add_hline(y=25, line_dash="dash", line_color="#ff6b6b", 
                       annotation_text="25% margin threshold", annotation_font_color="#ff6b6b")
        fig2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#a0a0c0'),
            title_font=dict(size=14, color='#e0e0ff'),
            height=350,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Row 2: Inventory health + Ratings
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        # Inventory Health — Days to Stockout
        inv_df = chart_df[chart_df['days_to_stockout'] < 30].sort_values('days_to_stockout')
        inv_df['status_color'] = inv_df['days_to_stockout'].apply(
            lambda d: 'Critical (<7d)' if d < 7 else ('Low (7-14d)' if d <= 14 else 'Healthy (>14d)'))
        
        fig3 = px.bar(inv_df, x='product_name', y='days_to_stockout',
                      color='status_color',
                      color_discrete_map={'Critical (<7d)': '#ff6b6b', 'Low (7-14d)': '#feca57', 'Healthy (>14d)': '#00b894'},
                      title='Days to Stockout by Product',
                      labels={'days_to_stockout': 'Days', 'product_name': ''},
                      template=chart_template)
        fig3.add_hline(y=7, line_dash="dash", line_color="#ff6b6b", annotation_text="Critical threshold")
        fig3.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#a0a0c0'),
            title_font=dict(size=14, color='#e0e0ff'),
            xaxis_tickangle=-45, height=380,
            margin=dict(l=20, r=20, t=40, b=80),
            showlegend=True, legend=dict(orientation="h", y=1.12)
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with chart_col4:
        # Rating Distribution
        fig4 = px.histogram(chart_df, x='avg_rating', nbins=10, color='category',
                            title='Rating Distribution by Category',
                            labels={'avg_rating': 'Average Rating', 'count': 'Products'},
                            template=chart_template,
                            color_discrete_sequence=px.colors.qualitative.Set2)
        fig4.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#a0a0c0'),
            title_font=dict(size=14, color='#e0e0ff'),
            height=380, barmode='stack',
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig4, use_container_width=True)
    
    # Row 3: Revenue Treemap
    st.markdown("")
    fig5 = px.treemap(chart_df, path=['category', 'product_name'], values='daily_revenue',
                      color='gross_margin_pct', color_continuous_scale='RdYlGn',
                      color_continuous_midpoint=40,
                      title='Revenue Treemap — Size = Daily Revenue, Color = Margin %',
                      template=chart_template)
    fig5.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#a0a0c0'),
        title_font=dict(size=14, color='#e0e0ff'),
        height=420,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    st.plotly_chart(fig5, use_container_width=True)
    
    # Export button
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    col_export1, col_export2, _ = st.columns([1, 1, 3])
    with col_export1:
        export_data = chart_df[['product_id', 'product_name', 'category', 'price', 'cost',
                                'gross_margin_pct', 'stock_quantity', 'avg_daily_sales',
                                'days_to_stockout', 'avg_rating', 'daily_revenue']].to_csv(index=False)
        st.download_button(
            "📥 Export Product Analysis CSV",
            data=export_data,
            file_name="retailmind_analysis.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_export2:
        # Inventory alerts export
        from tools.restock_alert import generate_restock_alert
        alerts = generate_restock_alert(14)
        if alerts:
            alerts_df = pd.DataFrame(alerts)
            alert_csv = alerts_df.to_csv(index=False)
            st.download_button(
                "📥 Export Restock Alerts CSV",  
                data=alert_csv,
                file_name="retailmind_restock_alerts.csv",
                mime="text/csv",
                use_container_width=True
            )
