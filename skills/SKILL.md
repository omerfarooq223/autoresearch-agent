# AutoResearch Agent Skill

## Overview
This skill provides autonomous research and competitive analysis capabilities using the `agent.py` module. It leverages LLMs and live web search to generate professional research reports and competitive intelligence documents in multiple formats.

## Features
- Research mode: Generates a detailed research report on any topic, including sub-question breakdown, web search, synthesis, and PDF/Word/HTML/Markdown output.
- Competitor mode: Produces a competitive analysis report for a comma-separated list of companies.
- Source credibility scoring (TLD tier + trusted domain whitelist + content quality signals) and evidence snippets.
- Custom branding/logo support.
- Caching for repeated queries.
- Modular and extensible for plugins.


## Usage
- **Web UI:**
	- Launch the Streamlit app with `streamlit run app.py` for a user-friendly browser interface.
	- Use the Research or Competitor Analysis tabs to generate reports and download files directly.
- **Python API:**
	- Import and call `run_agent(topic, output_format, logo_path)` for research reports.
	- Import and call `run_competitor_agent(companies_input, fmt)` for competitor analysis.
- All output files are saved to the current directory and progress is printed to stdout or shown in the UI.

## Requirements
- Python 3.x
- API keys for Groq and Tavily (set in `.env`)
- Required packages: see `requirements.txt`

## Example
```python
from agent import run_agent, run_competitor_agent
run_agent("Impact of AI on healthcare in 2025", output_format="pdf", logo_path=None)
run_competitor_agent("OpenAI, Anthropic, Google", fmt="pdf")
```
