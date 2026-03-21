import streamlit as st
import tempfile
import os
import io
import contextlib

st.set_page_config(page_title="AutoResearch Agent", layout="centered")

# Sidebar — must come before keys check
with st.sidebar:
    st.markdown("### 🔑 API Keys")
    st.markdown("Both are free to get:")
    groq_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    tavily_key = st.text_input("Tavily API Key", type="password", placeholder="tvly-...")
    st.markdown("[Get Groq key](https://console.groq.com) | [Get Tavily key](https://app.tavily.com)")

# Keys check
if not groq_key or not tavily_key:
    st.info("👈 Enter your API keys in the sidebar to get started.")
    st.stop()

os.environ["GROQ_API_KEY"] = groq_key
os.environ["TAVILY_API_KEY"] = tavily_key

from skills.agent import run_agent, run_competitor_agent

# --- Custom CSS for header and footer ---
st.markdown(
    """
    <style>
    .navy-header {
        background: #0f172a;
        color: #fff;
        padding: 1.5rem 0 1.2rem 0;
        text-align: center;
        font-size: 2.1rem;
        font-weight: 700;
        letter-spacing: 1px;
        border-radius: 0 0 18px 18px;
        margin-bottom: 1.5rem;
        border-bottom: 3px solid #2563eb;
    }
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
    }
    .stTabs [aria-selected="true"] {
        color: #2563eb !important;
        border-bottom-color: #2563eb !important;
    }
    .footer {
        color: #6b7280;
        font-size: 0.95rem;
        text-align: center;
        margin-top: 2.5rem;
        margin-bottom: 0.5rem;
    }
    </style>
    <div class="navy-header">🤖 AutoResearch Agent</div>
    """,
    unsafe_allow_html=True,
)

tabs = st.tabs(["Research", "Competitor Analysis"])


# --- Research Tab ---
with tabs[0]:
    st.subheader("Research Report Generator")
    topic = st.text_input("Enter research topic:", "")
    format_map = {"PDF": "pdf", "Word": "word", "HTML": "html", "Markdown": "md"}
    output_format = st.selectbox("Output format:", list(format_map.keys()), index=0)
    logo_file = st.file_uploader("Optional logo (PNG/JPG)", type=["png", "jpg", "jpeg"], key="logo1")
    generate = st.button("Generate Report", key="gen1")
    output_file = None
    stdout_buffer = io.StringIO()
    if generate and topic.strip():
        with st.spinner("Generating research report..."):
            try:
                # Save logo to temp file if provided
                logo_path = None
                if logo_file:
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                    tmp.write(logo_file.read())
                    tmp.flush()
                    logo_path = tmp.name
                # Capture stdout
                with contextlib.redirect_stdout(stdout_buffer):
                    run_agent(topic, output_format=format_map[output_format], logo_path=logo_path)
                # Find output file
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
                st.error(f"Error: {e}")
        st.code(stdout_buffer.getvalue(), language="text")

        # Show critique summary in UI
        stdout_text = stdout_buffer.getvalue()
        if "Low Confidence Claims" in stdout_text or "unsupported claims" in stdout_text.lower():
            st.warning("⚠️ Some claims could not be fully verified. See 'Low Confidence Claims' section in your report.")
        else:
            st.success("✅ All claims verified against sources.")
    
        if output_file:
            with open(output_file, "rb") as f:
                st.download_button(
                    label=f"Download {output_format} report",
                    data=f,
                    file_name=os.path.basename(output_file),
                    mime="application/octet-stream"
                )

# --- Competitor Analysis Tab ---
with tabs[1]:
    st.subheader("Competitor Analysis Generator")
    companies = st.text_input("Enter company names (comma-separated):", "", placeholder="e.g. OpenAI, Anthropic, Google")
    output_format2 = st.selectbox("Output format:", list(format_map.keys()), index=0, key="fmt2")
    generate2 = st.button("Generate Report", key="gen2")
    output_file2 = None
    stdout_buffer2 = io.StringIO()
    if generate2 and companies.strip():
        with st.spinner("Generating competitor analysis report..."):
            try:
                with contextlib.redirect_stdout(stdout_buffer2):
                    run_competitor_agent(companies, fmt=format_map[output_format2])
                base = "competitive-analysis-" + "-".join([c.strip().lower().replace(' ','-')[:10] for c in companies.split(",")[:3]])
                ext = format_map[output_format2]
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
                st.error(f"Error: {e}")
        st.code(stdout_buffer2.getvalue(), language="text")
        if output_file2:
            with open(output_file2, "rb") as f:
                st.download_button(
                    label=f"Download {output_format2} report",
                    data=f,
                    file_name=os.path.basename(output_file2),
                    mime="application/octet-stream"
                )

# --- Footer ---
st.markdown('<div class="footer">Built by Muhammad Umar Farooq</div>', unsafe_allow_html=True)
