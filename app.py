import streamlit as st
import tempfile
import os
import io
import contextlib
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")


def _clean_api_key(value: str) -> str:
    if not value:
        return ""
    return value.strip().strip('"').strip("'")

st.set_page_config(
    page_title="AutoResearch Agent", 
    layout="wide", 
    initial_sidebar_state="expanded",
    menu_items={
        'About': "### AutoResearch Agent\nPowered by LLaMA 3.3 70B + Tavily Search\nBuilt by Muhammad Umer Farooq"
    }
)

# Enhanced Modern CSS with Glassmorphism & Advanced Design
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&family=Sora:wght@400;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    
    * {
        margin: 0;
        padding: 0;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: #f8fafc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    [data-testid="stAppViewContainer"] {
        background: #f8fafc;
    }

    .block-container {
        padding-top: 1.3rem !important;
        padding-bottom: 1.3rem !important;
        max-width: none !important;
        width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', 'Sora', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    /* ============ ANIMATIONS ============ */
    @keyframes floatInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes gradientShift {
        0%, 100% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
    }
    
    @keyframes glow {
        0%, 100% {
            box-shadow: 0 0 20px rgba(37, 99, 235, 0.3), 0 0 40px rgba(37, 99, 235, 0.15);
        }
        50% {
            box-shadow: 0 0 30px rgba(37, 99, 235, 0.5), 0 0 60px rgba(37, 99, 235, 0.25);
        }
    }
    
    @keyframes shimmer {
        0%, 100% {
            text-shadow: 0 0 10px rgba(37, 99, 235, 0.3), 0 0 20px rgba(37, 99, 235, 0.1);
        }
        50% {
            text-shadow: 0 0 20px rgba(37, 99, 235, 0.8), 0 0 40px rgba(59, 130, 246, 0.5), 0 0 60px rgba(37, 99, 235, 0.2);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulseGlow {
        0%, 100% {
            box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.7);
        }
        50% {
            box-shadow: 0 0 0 10px rgba(37, 99, 235, 0);
        }
    }
    
    /* ============ MAIN HEADER ============ */
    .main-header {
        background: linear-gradient(120deg, #0b1f4a 0%, #11284f 40%, #0e5a3a 100%);
        color: white;
        padding: 1.8rem 1.5rem;
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: 0;
        border-radius: 16px;
        margin-bottom: 1.2rem;
        border: 2px solid #2563eb;
        animation: none;
        backdrop-filter: none;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.18);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 30% 50%, rgba(37, 99, 235, 0.18) 0%, transparent 52%);
        animation: none;
    }
    
    .main-header-text {
        position: relative;
        z-index: 1;
        animation: none;
    }
    
    .main-header:hover { transform: none; }
    
    /* ============ SIDEBAR STYLING ============ */
    [data-testid="sidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }
    
    .sidebar-header {
        background: #0f172a;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: 700;
        font-size: 1.05rem;
        box-shadow: none;
        border: 1px solid #1f2937;
        backdrop-filter: none;
    }
    
    /* ============ TABS STYLING ============ */
    .stTabs { margin-top: 0.6rem; }
    
    .stTabs [data-baseweb="tab-list"] {
        justify-content: flex-start;
        gap: 1rem;
        border-bottom: 1px solid #d1d5db !important;
        padding-bottom: 0 !important;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1rem !important;
        font-weight: 500 !important;
        padding: 0.55rem 0.7rem !important;
        border-radius: 0 !important;
        transition: all 0.2s ease !important;
        color: #374151 !important;
        position: relative;
        background: transparent !important;
        border: none !important;
    }

    .stTabs [data-baseweb="tab-list"] button p {
        margin: 0 !important;
        line-height: 1.2 !important;
        text-align: center !important;
        white-space: nowrap !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        right: 0;
        height: 2px;
        background: #2563eb;
        border-radius: 0;
        transform: scaleX(0);
        transition: transform 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab-list"] button:hover { color: #2563eb !important; }
    
    .stTabs [data-baseweb="tab-list"] button:hover::after { transform: scaleX(0.3); }
    
    .stTabs button[aria-selected="true"] {
        color: #2563eb !important;
        font-weight: 700 !important;
    }

    .stTabs button[aria-selected="true"]::after {
        transform: scaleX(1);
    }
    
    /* ============ CARD STYLING ============ */
    .section-card {
        background: transparent;
        border: 0;
        border-radius: 0;
        padding: 0;
        margin-bottom: 0.5rem;
        backdrop-filter: none;
        box-shadow: none;
        transition: none;
    }
    
    .section-card:hover { transform: none; }
    
    /* ============ INPUT STYLING ============ */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stFileUploader > div > div > div {
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
        padding: 0.52rem 0.8rem !important;
        font-size: 1rem !important;
        transition: border-color 0.2s ease !important;
        background: #ffffff !important;
        backdrop-filter: none !important;
    }

    .stSelectbox div[data-baseweb="select"] > div {
        min-height: 40px !important;
        align-items: center !important;
    }

    .stSelectbox div[data-baseweb="select"] span {
        line-height: 1.2 !important;
        color: #1f2937 !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #9ca3af !important;
        font-weight: 500 !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.12) !important;
        background: #ffffff !important;
    }
    
    .stSelectbox > div > div > div:hover {
        border-color: #2563eb !important;
    }
    
    /* ============ BUTTON STYLING ============ */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 50%, #1e40af 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 0.78rem 1.2rem !important;
        border-radius: 10px !important;
        border: 0 !important;
        font-size: 1.02rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.24) !important;
        text-transform: none;
        letter-spacing: 0;
        position: relative;
        overflow: hidden;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        line-height: 1.2 !important;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 10px 20px rgba(37, 99, 235, 0.28) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) !important;
    }
    
    /* ============ DOWNLOAD BUTTON ============ */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 50%, #047857 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 0.75rem 1rem !important;
        border-radius: 10px !important;
        border: 0 !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 6px 16px rgba(16, 185, 129, 0.2) !important;
        text-transform: none;
        letter-spacing: 0;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        line-height: 1.2 !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 10px 20px rgba(16, 185, 129, 0.26) !important;
    }
    
    /* ============ ALERTS & MESSAGES ============ */
    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%) !important;
        border: 2px solid #86efac !important;
        border-radius: 14px !important;
        padding: 1.25rem !important;
        color: #065f46 !important;
        font-weight: 500 !important;
        box-shadow: 0 5px 15px rgba(16, 185, 129, 0.1) !important;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%) !important;
        border: 2px solid #fca5a5 !important;
        border-radius: 14px !important;
        padding: 1.25rem !important;
        color: #7f1d1d !important;
        font-weight: 500 !important;
        box-shadow: 0 5px 15px rgba(239, 68, 68, 0.1) !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%) !important;
        border: 2px solid #fcd34d !important;
        border-radius: 14px !important;
        padding: 1.25rem !important;
        color: #78350f !important;
        font-weight: 500 !important;
        box-shadow: 0 5px 15px rgba(245, 158, 11, 0.1) !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%) !important;
        border: 2px solid #93c5fd !important;
        border-radius: 14px !important;
        padding: 1.25rem !important;
        color: #0c2d6b !important;
        font-weight: 500 !important;
        box-shadow: 0 5px 15px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* ============ SPINNER ============ */
    .stSpinner {
        text-align: center;
    }
    
    .stSpinner > div {
        border-color: rgba(37, 99, 235, 0.3) !important;
        border-top-color: #2563eb !important;
    }
    
    /* ============ EXPANDABLE SECTIONS ============ */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.05) 0%, rgba(37, 99, 235, 0.02) 100%) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        color: #1f2937 !important;
        padding: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(37, 99, 235, 0.05) 100%) !important;
    }
    
    /* ============ CODE BLOCK ============ */
    .stCode {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%) !important;
        border-radius: 14px !important;
        padding: 1.5rem !important;
        margin: 1.5rem 0 !important;
        border: 1px solid #374151 !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* ============ DIVIDER ============ */
    hr {
        border: none !important;
        height: 1px !important;
        background: #e5e7eb !important;
        margin: 1rem 0 !important;
    }
    
    /* ============ FOOTER ============ */
    .footer {
        color: #6b7280;
        font-size: 0.95rem;
        text-align: center;
        margin-top: 1.2rem;
        margin-bottom: 0.5rem;
        padding-top: 0.8rem;
        border-top: 1px solid #e5e7eb;
        font-weight: 500;
        animation: none;
    }
    
    .footer-highlight { color: #2563eb; font-weight: 700; font-size: 1.15rem; }
    
    .footer-subtext {
        color: #9ca3af;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    /* ============ SUBHEADER & MARKDOWN ============ */
    .stSubheader {
        font-size: 1.6rem !important;
        color: #1f2937 !important;
        font-weight: 700 !important;
        margin-bottom: 1.25rem !important;
        letter-spacing: -0.5px;
    }
    
    .stMarkdown {
        color: #4b5563 !important;
        line-height: 1.6;
    }

    /* Dark-mode-only fixes to preserve original light design */
    @media (prefers-color-scheme: dark) {
        html, body, [data-testid="stAppViewContainer"] {
            background: #0b1220 !important;
            color: #e5e7eb !important;
        }

        [data-testid="sidebar"] {
            background: #111827 !important;
            border-right: 1px solid #334155 !important;
        }

        .sidebar-header {
            background: #0b1326 !important;
            border-color: #334155 !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            border-bottom: 1px solid #334155 !important;
        }

        .stTabs [data-baseweb="tab-list"] button {
            color: #94a3b8 !important;
        }

        .stTabs [data-baseweb="tab-list"] button:hover,
        .stTabs button[aria-selected="true"] {
            color: #60a5fa !important;
        }

        .stTabs [data-baseweb="tab-list"] button::after {
            background: #60a5fa !important;
        }

        .stTextInput > div > div > input,
        .stSelectbox > div > div > div,
        .stFileUploader > div > div > div {
            background: #111827 !important;
            border-color: #334155 !important;
            color: #e5e7eb !important;
        }

        .stSelectbox div[data-baseweb="select"] span,
        .stSelectbox div[data-baseweb="select"] input,
        .stSelectbox div[data-baseweb="select"] div,
        .stTextInput > div > div > input,
        .stTextInput > div > div > input::placeholder {
            color: #cbd5e1 !important;
        }

        .stTextInput > div > div > input::placeholder {
            opacity: 1 !important;
        }

        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > div:focus,
        .stSelectbox > div > div > div:hover {
            border-color: #60a5fa !important;
            background: #111827 !important;
        }

        .streamlit-expanderHeader {
            color: #e5e7eb !important;
            border: 1px solid #334155 !important;
        }

        hr {
            background: #334155 !important;
        }

        .stSubheader {
            color: #e5e7eb !important;
        }

        .stMarkdown,
        .footer,
        .footer-subtext {
            color: #94a3b8 !important;
        }

        .footer {
            border-top: 1px solid #334155 !important;
        }

        .footer-highlight {
            color: #60a5fa !important;
        }
    }
    
    /* ============ RESPONSIVE DESIGN ============ */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }

        .main-header {
            font-size: 2.2rem;
            padding: 2rem 1.5rem;
        }
        
        .stTabs [data-baseweb="tab-list"] button {
            padding: 0.875rem 1rem !important;
            font-size: 0.95rem !important;
        }
        
        .section-card {
            padding: 1.5rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar styling with enhanced header
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">🔑 API Configuration</div>
    """, unsafe_allow_html=True)
    
    st.markdown("**Get your free API keys:**")
    env_groq_key = os.getenv("GROQ_API_KEY", "")
    env_tavily_key = os.getenv("TAVILY_API_KEY", "")
    groq_key_input = st.text_input(
        "🧠 Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Get at console.groq.com",
        value=env_groq_key,
    )
    tavily_key_input = st.text_input(
        "🔍 Tavily API Key",
        type="password",
        placeholder="tvly-...",
        help="Get at app.tavily.com",
        value=env_tavily_key,
    )
    groq_key = _clean_api_key(groq_key_input) or _clean_api_key(env_groq_key)
    tavily_key = _clean_api_key(tavily_key_input) or _clean_api_key(env_tavily_key)
    
    st.markdown("""
    <div style="text-align: center; margin-top: 1.5rem; padding-top: 1.5rem; border-top: 2px solid #e5e7eb;">
        <a href="https://console.groq.com" target="_blank" style="color: #2563eb; text-decoration: none; font-weight: 700; margin-right: 1rem; display: inline-block; padding: 0.5rem 1rem; background: rgba(37, 99, 235, 0.1); border-radius: 8px; transition: all 0.3s;">
            📊 Groq Console
        </a>
        <a href="https://app.tavily.com" target="_blank" style="color: #2563eb; text-decoration: none; font-weight: 700; display: inline-block; padding: 0.5rem 1rem; background: rgba(37, 99, 235, 0.1); border-radius: 8px; transition: all 0.3s;">
            🎯 Tavily App
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(8, 145, 178, 0.05) 100%); 
                border-radius: 12px; padding: 1rem; border: 1px solid rgba(37, 99, 235, 0.2); margin-top: 1rem;">
        <p style="font-size: 0.9rem; color: #475569; margin: 0;">
            <strong>💡 Tip:</strong> Use the enhanced report design for professional-looking outputs with star ratings and visual credibility indicators.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Keys check
if not groq_key or not tavily_key:
    st.info("👈 **Configure API keys in sidebar or .env to get started.**")
    st.stop()

os.environ["GROQ_API_KEY"] = groq_key
os.environ["TAVILY_API_KEY"] = tavily_key

from skills.agent import run_agent, run_competitor_agent

# Main header
st.markdown(
    '<div class="main-header"><div class="main-header-text">🤖 AutoResearch Agent</div></div>',
    unsafe_allow_html=True,
)

st.markdown("""
<div style="text-align: center; margin-bottom: 2rem; color: #6b7280;">
    <p style="font-size: 1.1rem; margin: 0; font-weight: 500;">
        ✨ AI-powered research intelligence with verified sources
    </p>
</div>
""", unsafe_allow_html=True)

# Create tabs
tabs = st.tabs(["📊 Research Report", "🏆 Competitor Analysis", "ℹ️ How It Works"])

# --- Research Tab ---
with tabs[0]:
    # Section card with description
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📝 Generate Your Research Report")
        st.markdown("Enter any topic and our AI research agent will create a comprehensive, source-verified report in seconds.")
    
    with col2:
        st.markdown("")
        st.markdown("")
        st.info("🚀 Fast & Accurate", icon="✨")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Input section
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("**🎯 What would you like to research?**")
        topic = st.text_input(
            "Research Topic",
            placeholder="e.g., Quantum Computing, AI Ethics, Climate Policy...",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("**📄 Choose your output format**")
        format_map = {"📄 PDF": "pdf", "📝 Word": "word", "🌐 HTML": "html", "📋 Markdown": "md"}
        output_format = st.selectbox(
            "Output Format",
            list(format_map.keys()),
            index=0,
            label_visibility="collapsed"
        )
    
    st.markdown("**🖼️ Add your branding (optional)**")
    logo_file = st.file_uploader(
        "Upload Logo",
        type=["png", "jpg", "jpeg"],
        key="logo1",
        help="Add a branded header to your report"
    )
    
    st.markdown("---")
    
    # Action button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate = st.button("🚀 Generate Report", key="gen1", use_container_width=True)
    
    output_file = None
    stdout_buffer = io.StringIO()
    
    if generate and topic.strip():
        with st.spinner("🔍 Researching topic and verifying claims..."):
            try:
                logo_path = None
                if logo_file:
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                    tmp.write(logo_file.read())
                    tmp.flush()
                    logo_path = tmp.name
                
                with contextlib.redirect_stdout(stdout_buffer):
                    run_agent(topic, output_format=format_map[output_format], logo_path=logo_path)
                
                base = topic.lower().replace(' ', '-')[:40]
                ext = format_map[output_format]
                if ext == "pdf":
                    fname = f"{base}-report.pdf"
                elif ext == "word":
                    fname = f"{base}-report.docx"
                elif ext == "html":
                    fname = f"{base}-report.html"
                elif ext == "md":
                    fname = f"{base}-report.md"
                else:
                    fname = None
                
                if fname and os.path.exists(fname):
                    output_file = fname
            except Exception as e:
                st.error(f"❌ Error generating report: {e}")
        
        st.markdown("---")
        
        # Processing details
        with st.expander("📋 **Processing Details**", expanded=False):
            st.code(stdout_buffer.getvalue(), language="text")
        
        stdout_text = stdout_buffer.getvalue()
        if "Low Confidence Claims" in stdout_text or "unsupported claims" in stdout_text.lower():
            st.warning(
                "⚠️ **Some claims could not be fully verified** — See 'Low Confidence Claims' section in your report for transparency.",
                icon="⚠️"
            )
        else:
            st.success("✅ All claims verified against sources!", icon="✅")
        
        st.markdown("---")
        
        if output_file:
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                with open(output_file, "rb") as f:
                    st.download_button(
                        label=f"⬇️ Download {output_format.split()[0]}",
                        data=f,
                        file_name=os.path.basename(output_file),
                        mime="application/octet-stream",
                        use_container_width=True
                    )
            
            with col2:
                st.info(f"📊 Report ready for download!", icon="✨")


# --- Competitor Analysis Tab ---
with tabs[1]:
    # Section card
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 🏢 Comprehensive Competitor Analysis")
        st.markdown("Analyze multiple companies and get competitive intelligence reports with market positioning and strategic insights.")
    
    with col2:
        st.markdown("")
        st.markdown("")
        st.info("📊 Market Intelligence", icon="🔍")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("**🏪 Which companies do you want to analyze?**")
        companies = st.text_input(
            "Company Names",
            placeholder="e.g., OpenAI, Anthropic, Google (comma-separated)",
            label_visibility="collapsed",
            help="Enter company names separated by commas"
        )
    
    with col2:
        st.markdown("**📄 Choose your output format**")
        format_map2 = {"📄 PDF": "pdf", "📝 Word": "word", "🌐 HTML": "html", "📋 Markdown": "md"}
        output_format2 = st.selectbox(
            "Output Format",
            list(format_map2.keys()),
            index=0,
            label_visibility="collapsed",
            key="fmt2"
        )
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate2 = st.button("🚀 Analyze Competition", key="gen2", use_container_width=True)
    
    output_file2 = None
    stdout_buffer2 = io.StringIO()
    
    if generate2 and companies.strip():
        with st.spinner("🔍 Analyzing competitive landscape..."):
            try:
                with contextlib.redirect_stdout(stdout_buffer2):
                    run_competitor_agent(companies, fmt=format_map2[output_format2])
                
                base = "competitive-analysis-" + "-".join([c.strip().lower().replace(' ','-')[:10] for c in companies.split(",")[:3]])
                ext = format_map2[output_format2]
                if ext == "pdf":
                    fname2 = f"{base}.pdf"
                elif ext == "word":
                    fname2 = f"{base}.docx"
                elif ext == "html":
                    fname2 = f"{base}.html"
                elif ext == "md":
                    fname2 = f"{base}.md"
                else:
                    fname2 = None
                
                if fname2 and os.path.exists(fname2):
                    output_file2 = fname2
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        st.markdown("---")
        
        with st.expander("📋 **Processing Details**", expanded=False):
            st.code(stdout_buffer2.getvalue(), language="text")
        
        st.success("✅ Competitive analysis complete!", icon="✅")
        
        st.markdown("---")
        
        if output_file2:
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                with open(output_file2, "rb") as f:
                    st.download_button(
                        label=f"⬇️ Download {output_format2.split()[0]}",
                        data=f,
                        file_name=os.path.basename(output_file2),
                        mime="application/octet-stream",
                        use_container_width=True
                    )
            
            with col2:
                st.info(f"📊 Report ready!", icon="✨")


# --- How It Works Tab ---
with tabs[2]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    
    st.markdown("### 🤖 How AutoResearch Agent Works")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🔍 Step 1: Research**
        - Breaks down your topic into 5 sub-questions
        - Searches the web using Tavily API
        - Collects verified sources
        
        **🧠 Step 2: Synthesis**
        - Uses LLaMA 3.3 70B for analysis
        - Generates comprehensive report
        - Organizes findings into sections
        """)
    
    with col2:
        st.markdown("""
        **✅ Step 3: Verification**
        - Fact-checks all claims
        - Identifies unsupported statements
        - Re-searches for missing evidence
        
        **📄 Step 4: Export**
        - Generates professional reports
        - PDF with gradient styling
        - Word, HTML, and Markdown formats
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    
    st.markdown("### 🎨 Report Features")
    
    features = [
        ("⭐ Credibility Ratings", "Star ratings (★★★★★) for source credibility"),
        ("🎯 Verified Claims", "All findings backed by web sources"),
        ("📊 Source Table", "Comprehensive sources summary with evidence snippets"),
        ("📱 Responsive Design", "Beautiful formatting across all formats"),
        ("🔄 Fact-Checking", "Automatic verification loop for accuracy"),
        ("🎨 Professional Styling", "Modern editorial design with gradients and accents"),
    ]
    
    for title, desc in features:
        st.markdown(f"**{title}** — {desc}")
    
    st.markdown('</div>', unsafe_allow_html=True)


# Footer
st.markdown("""
<div class="footer">
    <div class="footer-highlight">
        ✨ Built by Muhammad Umer Farooq
    </div>
    <div class="footer-subtext">
        Powered by LLaMA 3.3 70B (Groq) + Tavily Search API | Enhanced Design Version
    </div>
</div>
""", unsafe_allow_html=True)