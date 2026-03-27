"""
RetailMind Analytics — Professional Streamlit Application
================================================================
Main Streamlit UI for the Product Intelligence Platform.
Enterprise-grade design: minimalist, clean, and data-focused.

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
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    products_csv = os.path.join(project_root, "retailmind_products.csv")
    reviews_csv = os.path.join(project_root, "retailmind_reviews.csv")
    
    if not os.path.exists(products_csv):
        errors.append("Error: `retailmind_products.csv` not found in project root.")
    if not os.path.exists(reviews_csv):
        errors.append("Error: `retailmind_reviews.csv` not found in project root.")
    
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key or api_key == "your_groq_api_key_here":
        errors.append("Error: `GROQ_API_KEY` not set. Create a `.env` file with `GROQ_API_KEY=gsk_your_key`")
    
    return errors

startup_errors = validate_environment()

from data.loader import get_products_df, get_all_categories, get_reviews_df
from agent.router import route_query
from agent.memory import ConversationMemory
from agent.briefing import generate_daily_briefing


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="RetailMind Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CUSTOM CSS — ENTERPRISE MINIMALIST THEME
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
    }
    
    .stApp { 
        background-color: #0E1117;
    }
    
    /* Header */
    .main-header {
        padding: 1.5rem 0;
        border-bottom: 1px solid #262730;
        margin-bottom: 2rem;
    }
    .main-header h1 { 
        margin: 0; 
        font-size: 1.5rem; 
        font-weight: 500; 
        color: #F8FAFC;
        letter-spacing: -0.5px;
    }
    .main-header p { 
        margin: 0.3rem 0 0 0; 
        color: #CBD5E1; 
        font-size: 0.9rem; 
        font-weight: 400; 
    }
    .tech-badges { margin-top: 1rem; }
    .tech-badge {
        display: inline-block;
        background-color: transparent;
        color: #94A3B8;
        padding: 0.1rem 0.6rem;
        border-radius: 4px;
        font-size: 0.7rem;
        margin-right: 0.5rem;
        border: 1px solid #475569;
    }
    
    /* Metric Cards */
    .metric-card {
        background-color: #161B22;
        padding: 1.2rem;
        border-radius: 6px;
        border: 1px solid #30363D;
        border-left: 3px solid #3B82F6;
    }
    .metric-card-critical { border-left-color: #EF4444; }
    .metric-card-healthy { border-left-color: #10B981; }
    .metric-card-warning { border-left-color: #F59E0B; }
    
    .metric-card h3 {
        margin: 0; 
        font-size: 1.6rem; 
        font-weight: 600;
        color: #E2E8F0;
    }
    .metric-card p { 
        margin: 0.2rem 0 0 0; 
        font-size: 0.7rem; 
        color: #CBD5E1; 
        font-weight: 600; 
        text-transform: uppercase; 
        letter-spacing: 0.5px; 
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] { 
        background-color: #0D1117 !important; 
        border-right: 1px solid #30363D;
    }
    .sidebar-logo { 
        padding: 1rem 0; 
        border-bottom: 1px solid #30363D; 
        margin-bottom: 1.5rem; 
    }
    .sidebar-logo h2 { 
        margin: 0; 
        font-size: 1.2rem; 
        font-weight: 500; 
        color: #E2E8F0; 
    }
    .sidebar-logo p { 
        font-size: 0.75rem; 
        color: #CBD5E1; 
        margin: 0.2rem 0 0 0; 
    }
    
    .status-indicator { 
        display: inline-flex; 
        align-items: center; 
        gap: 0.4rem; 
        font-size: 0.75rem; 
        color: #CBD5E1;
        margin-bottom: 1rem;
    }
    .status-dot { 
        width: 6px; 
        height: 6px; 
        border-radius: 50%; 
        background-color: #238636; 
    }
    
    .section-divider { 
        height: 1px; 
        background-color: #30363D; 
        margin: 1.5rem 0; 
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 4px;
        font-weight: 500;
        font-size: 0.8rem;
        background-color: #238636;
        color: white !important;
        border: none;
        transition: background-color 0.2s;
    }
    .stButton > button:hover {
        background-color: #2EA043;
    }
    
    .secondary-btn > button {
        background-color: transparent !important;
        border: 1px solid #30363D !important;
        color: #C9D1D9 !important;
    }
    .secondary-btn > button:hover {
        background-color: #1F2428 !important;
        border-color: #8B949E !important;
    }
    
    /* Chat window */
    .stChatMessage { 
        background-color: transparent !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { 
        border-bottom: 1px solid #30363D;
        gap: 1.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 1rem;
        padding-bottom: 1rem;
        color: #CBD5E1;
        background: transparent;
        border: none !important;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        color: #E2E8F0 !important;
        border-bottom: 2px solid #58A6FF !important;
    }
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
        <h2>RetailMind Analytics</h2>
        <p>Product Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="status-indicator">
        <div class="status-dot"></div> System Online & Connected
    </div>
    """, unsafe_allow_html=True)
    
    categories = ["All Categories"] + get_all_categories()
    selected_category = st.selectbox("Category Filter", categories, index=0)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    st.markdown("<p style='font-size: 0.8rem; color: #8B949E; font-weight: 500; margin-bottom: 0.5rem;'>Quick Diagnostics</p>", unsafe_allow_html=True)
    
    # Use standard streamlit buttons styled via CSS class logic using columns
    diagnostics = [
        "Critical stock alerts",
        "Best performing category",
        "Low margin products",
        "Worst rated product",
        "Full inventory report",
    ]
    for action in diagnostics:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button(action, use_container_width=True, key=f"qa_{action}"):
            st.session_state.quick_action = action
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.memory.clear()
        st.session_state.messages = []
        st.session_state.briefing_generated = False
        st.session_state.daily_briefing = ""
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align:left; padding: 1rem 0; margin-top: 2rem;">
        <div style="font-size: 0.7rem; color: #8B949E; margin-bottom: 0.4rem;">Infrastructure Core</div>
        <div style="display: flex; gap: 0.4rem; flex-wrap: wrap;">
            <span class="tech-badge">LangChain</span>
            <span class="tech-badge">Groq</span>
            <span class="tech-badge">Plotly</span>
        </div>
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
    <h1>Product Intelligence Dashboard</h1>
    <p>Comprehensive catalog analytics, real-time inventory tracking, and consumer sentiment insights.</p>
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

col1, col2, col3, col4, col5 = st.columns(5)
metrics = [
    (col1, total_skus, "Active SKUs", ""),
    (col2, critical_stock, "Critical Stock", "metric-card-critical" if critical_stock > 0 else "metric-card-healthy"),
    (col3, f"{avg_margin}%", "Portfolio Margin", ""),
    (col4, avg_rating, "Average Rating", "metric-card-warning" if avg_rating < 4.0 else "metric-card-healthy"),
    (col5, f"₹{total_revenue:,.0f}", "Daily Revenue", ""),
]
for col, value, label, extra_class in metrics:
    with col:
        cls = f"metric-card {extra_class}" if extra_class else "metric-card"
        st.markdown(f'<div class="{cls}"><h3>{value}</h3><p>{label}</p></div>', unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TABS: Chat | Analytics Dashboard
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
tab_chat, tab_analytics = st.tabs(["AI Copilot", "Visual Analytics"])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1: CHAT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_chat:
    if not st.session_state.briefing_generated:
        with st.status("Initializing intelligence briefing...", expanded=True) as status:
            st.write("Aggregating inventory metrics...")
            st.write("Processing consumer sentiment...")
            st.write("Evaluating margin integrity...")
            try:
                briefing = generate_daily_briefing()
                st.session_state.daily_briefing = briefing
                st.session_state.briefing_generated = True
                st.session_state.messages.append({"role": "assistant", "content": briefing})
                status.update(label="System Initialization Complete", state="complete")
            except Exception as e:
                st.session_state.briefing_generated = True
                err_msg = f"System Error: Briefing generation failed. Details: {str(e)}"
                st.session_state.daily_briefing = err_msg
                st.session_state.messages.append({"role": "assistant", "content": err_msg})
                status.update(label="System Initialization Error", state="error")

    if "quick_action" in st.session_state:
        action = st.session_state.pop("quick_action")
        query_map = {
            "Critical stock alerts": "List all products that have reached critical stock status and require immediate purchase orders.",
            "Best performing category": "Analyze category performance and determine the leader by aggregate revenue and average sentiment.",
            "Low margin products": "Identify all active SKUs exhibiting suboptimal profit margins that require pricing strategy review.",
            "Worst rated product": "Determine the lowest rated SKU and summarize the principal negative consumer themes.",
            "Full inventory report": "Generate a comprehensive inventory health assessment across the catalog.",
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
            response = f"System Error: {str(e)}"
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.memory.add_message("assistant", response)
        st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_query := st.chat_input("Enter your query regarding catalog operations, analytics, or sentiment..."):
        if not user_query.strip():
            st.toast("Empty query received. Please input parameters.", icon="⚠️")
        else:
            with st.chat_message("user"):
                st.markdown(user_query)
            
            st.session_state.messages.append({"role": "user", "content": user_query})
            st.session_state.memory.add_message("user", user_query)
            
            with st.chat_message("assistant"):
                with st.status("Processing via LLM layer...", expanded=False) as status:
                    try:
                        response = route_query(
                            query=user_query,
                            conversation_history=st.session_state.memory.get_history(),
                            selected_category=selected_category if selected_category != "All Categories" else None
                        )
                        status.update(label="Analysis complete", state="complete")
                        st.markdown(response)
                    except Exception as e:
                        response = f"System Error executing query: {str(e)}\n\nPlease verify environment configuration or simplify query taxonomy."
                        status.update(label="Execution Error", state="error")
                        st.error(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.memory.add_message("assistant", response)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2: ANALYTICS DASHBOARD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_analytics:
    st.markdown("<h3 style='margin-bottom: 0.5rem; font-weight: 500; font-size: 1.2rem;'>Telemetry Dashboard</h3>", unsafe_allow_html=True)
    
    chart_df = summary_df.copy()
    chart_df['gross_margin_pct'] = ((chart_df['price'] - chart_df['cost']) / chart_df['price'] * 100).round(1)
    chart_df['daily_revenue'] = (chart_df['price'] * chart_df['avg_daily_sales']).round(0)
    chart_df['days_to_stockout'] = chart_df.apply(
        lambda r: round(r['stock_quantity'] / r['avg_daily_sales'], 1) if r['avg_daily_sales'] > 0 else 999, axis=1)
    
    chart_template = "plotly_dark"
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        cat_stats = products_df.groupby('category').agg(
            avg_rating=('avg_rating', 'mean'),
            avg_margin=('price', lambda x: ((x - products_df.loc[x.index, 'cost']) / x * 100).mean()),
            total_skus=('product_id', 'count'),
            total_stock=('stock_quantity', 'sum'),
            daily_revenue=('avg_daily_sales', lambda x: (x * products_df.loc[x.index, 'price']).sum())
        ).reset_index()
        
        fig = px.bar(cat_stats, x='category', y='daily_revenue',
                     color='avg_rating', color_continuous_scale='Blues',
                     title='Revenue Breakdown by Scope',
                     labels={'daily_revenue': 'Daily Revenue (INR)', 'avg_rating': 'Avg Rating', 'category': ''},
                     template=chart_template)
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#8B949E'),
            title_font=dict(size=14, color='#E2E8F0'),
            height=320,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with chart_col2:
        fig2 = px.scatter(chart_df, x='price', y='gross_margin_pct',
                          size='avg_daily_sales', color='category',
                          hover_name='product_name',
                          title='Pricing vs Margin Correlation Matrix',
                          labels={'price': 'MSRP (INR)', 'gross_margin_pct': 'Gross Margin %', 'category': 'Subcategory'},
                          template=chart_template,
                          color_discrete_sequence=px.colors.qualitative.Prism)
        fig2.add_hline(y=25, line_dash="dash", line_color="#EF4444", 
                       annotation_text="Critical 25% Margin Floor", annotation_font_color="#EF4444")
        fig2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#8B949E'),
            title_font=dict(size=14, color='#E2E8F0'),
            height=320,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        inv_df = chart_df.sort_values('days_to_stockout').head(15)
        inv_df['status'] = inv_df['days_to_stockout'].apply(
            lambda d: 'Critical (<7d)' if d < 7 else ('Warning (<14d)' if d <= 14 else 'Nominal (>14d)'))
        
        fig3 = px.bar(inv_df, x='product_id', y='days_to_stockout',
                      color='status',
                      color_discrete_map={'Critical (<7d)': '#EF4444', 'Warning (<14d)': '#F59E0B', 'Nominal (>14d)': '#10B981'},
                      title='Inventory Burn Rate (Top 15 At-Risk SKUs)',
                      labels={'days_to_stockout': 'Days Remaining', 'product_id': 'Identifier'},
                      template=chart_template)
        fig3.add_hline(y=7, line_dash="dash", line_color="#EF4444")
        fig3.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#8B949E'),
            title_font=dict(size=14, color='#E2E8F0'),
            xaxis_tickangle=-45, height=360,
            margin=dict(l=10, r=10, t=40, b=60),
            showlegend=True, legend=dict(orientation="h", y=1.12)
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with chart_col4:
        fig4 = px.histogram(chart_df, x='avg_rating', nbins=10, color='category',
                            title='Consumer Sentiment Distribution',
                            labels={'avg_rating': 'Aggregated Score (out of 5.0)', 'count': 'Frequency', 'category': 'Subcategory'},
                            template=chart_template,
                            color_discrete_sequence=px.colors.qualitative.Prism)
        fig4.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#8B949E'),
            title_font=dict(size=14, color='#E2E8F0'),
            height=360, barmode='stack',
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig4, use_container_width=True)
        
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    col_export1, col_export2, _ = st.columns([1, 1, 3])
    with col_export1:
        export_data = chart_df[['product_id', 'product_name', 'category', 'price', 'cost',
                                'gross_margin_pct', 'stock_quantity', 'avg_daily_sales',
                                'days_to_stockout', 'avg_rating', 'daily_revenue']].to_csv(index=False)
        st.download_button(
            "Export Telemetry (CSV)",
            data=export_data,
            file_name="retailmind_telemetry.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_export2:
        from tools.restock_alert import generate_restock_alert
        alerts = generate_restock_alert(14)
        if alerts:
            alerts_df = pd.DataFrame(alerts)
            alert_csv = alerts_df.to_csv(index=False)
            st.download_button(
                "Export Procurement Orders",  
                data=alert_csv,
                file_name="retailmind_procurement.csv",
                mime="text/csv",
                use_container_width=True
            )
