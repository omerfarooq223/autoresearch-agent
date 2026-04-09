# 🤖 AutoResearch Agent

An autonomous AI research agent that takes any topic, breaks it into targeted sub-questions, searches the live web in parallel, verifies its own claims, and produces a professional research report — typically in 1-2 minutes.

> Built with LLaMA 3.3 70B (Groq) + Tavily Search API

![AutoResearch Agent UI](sample-images/ui-screenshot.png)

---

## Why not just use Perplexity or ChatGPT?

- **Multi-step research pipeline** — breaks a topic into sub-questions and synthesizes across them automatically
- **Downloadable, branded reports** — ready-to-share PDF/Word outputs with structured sections
- **Designed for handoff** — source tables, citations, and organized insights instead of raw chat output
- **Self-verifying** — agent audits its own claims against retrieved sources and flags anything it can't back up

---

## ✨ Features

- 🧠 Breaks any topic into 5 targeted sub-questions automatically
- 🔍 Searches all sub-questions **in parallel** for ~4x faster results
- 📊 Synthesizes findings from 12+ sources
- 🔁 **Self-critique loop** — flags unsupported or partially supported claims
- ⚠️ **Low Confidence Claims** section in every report for full transparency
- 🏆 Multi-factor source credibility scoring (TLD tier + trusted domain whitelist + content quality)
- 📄 Generates professional branded PDF, Word, HTML, or Markdown reports
- 🏷️ Custom branding/logo support
- 🗂️ Summary table of all sources with metadata
- ⚡ Typically 60-120 seconds (includes self-verification loop)
- 💾 Caching for faster repeated queries
- 🔧 Modular, extensible, and plugin-ready

---

## 🌐 Live Demo
👉 [Try it here](https://autoresearch-agent.streamlit.app) — no installation needed

---

## 🔁 How It Works
```
Topic
  └─► Generate 5 sub-questions
        └─► Search all in parallel (Tavily)
              └─► Synthesize report (LLaMA 3.3 70B)
                    └─► Self-critique: audit claims vs sources
                          └─► Re-search unsupported claims
                                └─► Patch report + flag low confidence
                                      └─► Export (PDF / Word / HTML / Markdown)
```

---

# 📁 Project Structure

```
autoresearch-agent/
├── app.py                  # Streamlit web UI
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── .env                    # API keys (not committed)
├── sample-images/          # Screenshots for README
│   ├── ui-screenshot.png
│   └── pdf-screenshot.png
├── skills/                 # Main agent logic and skill docs
│   ├── agent.py
│   └── SKILL.md
└── .cache/                 # Search result cache (auto-generated)
```

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/omerfarooq223/autoresearch-agent.git
cd autoresearch-agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up API keys
Create a `.env` file:
```
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
```

### 4. Run via CLI
```bash
python skills/agent.py research "Impact of AI on healthcare in 2025"
```

### 5. Output Formats
```bash
python skills/agent.py research "AI in medicine" --format pdf
python skills/agent.py research "AI in medicine" --format word
python skills/agent.py research "AI in medicine" --format html
python skills/agent.py research "AI in medicine" --format md
```

### 6. Custom Branding
```bash
python skills/agent.py research "AI in medicine" --logo path/to/logo.png
```

### 7. Control Number of Sources
```bash
python skills/agent.py research "AI in medicine" --max-sources 6
```

---

## 🖥️ Streamlit Web UI
```bash
streamlit run app.py
```

- **Research Tab** — Enter a topic, select output format, optionally upload a logo, click Generate
- **Competitor Analysis Tab** — Enter company names (comma-separated) for a competitive intelligence report
- UI shows whether all claims were verified or flags low-confidence statements before download

---

## 🔑 API Keys (Both Free)

- **Groq**: https://console.groq.com
- **Tavily**: https://app.tavily.com

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| LLM | LLaMA 3.3 70B via Groq |
| Search | Tavily Advanced Web Search |
| Parallelism | Python ThreadPoolExecutor |
| PDF | ReportLab |
| UI | Streamlit |
| Language | Python 3.x |

---

## 📄 Report Structure

Every generated report includes:

- Cover page with metadata
- Executive Summary
- Key Findings (organized by theme)
- Areas of Consensus
- Debates & Controversies
- Challenges & Barriers
- What Remains Unknown
- Future Outlook
- Conclusion
- ⚠️ Low Confidence Claims (auto-flagged by self-critique loop)
- Full Citations
- Summary Table of Sources (with credibility scores and evidence snippets)

---

## 🏆 Source Credibility Scoring

Sources are scored 1–5 across three signals:

| Signal | What it checks |
|---|---|
| TLD tier | `.gov/.edu/.mil` score highest |
| Trusted whitelist | Reuters, arXiv, BBC, Nature, etc. get a bonus |
| Content quality | Length, presence of data/stats, descriptive title |

---

## 🆘 Troubleshooting

| Issue | Fix |
|---|---|
| API Key Error | Ensure `.env` has valid `GROQ_API_KEY` and `TAVILY_API_KEY` |
| No Results | Try a broader topic or increase `--max-sources` |
| Slow Performance | Cached results reused automatically; parallel search active by default |
| Custom Logo Not Showing | Check path and use PNG/JPG format |
| Other Issues | Delete `.cache/` and retry |


---

## 🖼️ Screenshots

![App UI](sample-images/ui-screenshot.png)

![PDF Report](sample-images/pdf-screenshot.png)

---

## 👨‍💻 Author

**M. Umer Farooq**  
BS Artificial Intelligence — UMT Lahore  
GitHub: [omerfarooq223](https://github.com/omerfarooq223)