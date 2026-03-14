"""
AutoResearch Agent
==================
An autonomous AI research agent that searches the web and produces
professional PDF research reports on any topic.

Author: M. Umer Farooq
GitHub: https://github.com/umerfarooq
Built with: Groq (LLaMA 3.3 70B) + Tavily Search API
"""

import os
import sys
import hashlib
import json
from datetime import datetime
from dotenv import load_dotenv
from tavily import TavilyClient
from groq import Groq
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 HRFlowable, Table, TableStyle,
                                 PageBreak, BaseDocTemplate, Frame,
                                 PageTemplate)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT

load_dotenv()


# --- Error handling for API keys ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if not GROQ_API_KEY:
    print("[ERROR] GROQ_API_KEY not found in environment. Please set it in your .env file.")
    sys.exit(1)
if not TAVILY_API_KEY:
    print("[ERROR] TAVILY_API_KEY not found in environment. Please set it in your .env file.")
    sys.exit(1)

groq_client = Groq(api_key=GROQ_API_KEY)
tavily = TavilyClient(api_key=TAVILY_API_KEY)
MODEL = "llama-3.3-70b-versatile"

# Brand colors
DARK_BLUE    = HexColor('#0f172a')
ACCENT_BLUE  = HexColor('#2563eb')
LIGHT_BLUE   = HexColor('#dbeafe')
TEAL         = HexColor('#0891b2')
GRAY         = HexColor('#6b7280')
LIGHT_GRAY   = HexColor('#f1f5f9')
DARK_GRAY    = HexColor('#1e293b')
WHITE        = HexColor('#ffffff')
GOLD         = HexColor('#f59e0b')


def ask_groq(prompt, system="You are a helpful research assistant."):
    try:
        response = groq_client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[ERROR] Groq API call failed: {e}")
        return "[Error: Unable to get response from Groq API.]"

def generate_sub_questions(topic):
    print(f"\n🧠 Breaking down topic: {topic}")
    prompt = f"""Break this research topic into 5 specific sub-questions that together would cover it comprehensively:
Topic: {topic}
Return ONLY a numbered list of 5 questions, nothing else."""
    result = ask_groq(prompt)
    questions = [line.strip() for line in result.strip().split('\n')
                 if line.strip() and line[0].isdigit()]
    for q in questions:
        print(f"  {q}")
    return questions


def estimate_credibility(source):
    # Simple heuristic: .gov/.edu > .org > .com > others
    url = source.get('url', '').lower()
    if ".gov" in url or ".edu" in url:
        return 5
    if ".org" in url:
        return 4
    if ".com" in url:
        return 3
    return 2

def extract_evidence_snippet(content):
    # Return the first 200 chars as a snippet (could be improved)
    return content[:200] + ("..." if len(content) > 200 else "")

def search_web(query, max_results=4, cache_dir=".cache"):
    print(f"\n🔍 Searching: {query[:65]} (max_results={max_results})...")
    # --- Caching logic ---
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    cache_key = hashlib.md5(f"{query}|{max_results}".encode()).hexdigest()
    cache_path = os.path.join(cache_dir, f"{cache_key}.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cached = json.load(f)
            print("[CACHE] Using cached search results.")
            return cached
        except Exception:
            pass
    try:
        results = tavily.search(query=query, max_results=max_results, search_depth="advanced")
    except Exception as e:
        print(f"[ERROR] Tavily API call failed: {e}")
        return []
    sources = []
    for r in results.get('results', []):
        credibility = estimate_credibility(r)
        snippet = extract_evidence_snippet(r.get('content', ''))
        sources.append({
            'title': r.get('title', ''),
            'url':   r.get('url', ''),
            'content': r.get('content', '')[:1000],
            'credibility': credibility,
            'snippet': snippet
        })
    if not sources:
        print("[WARNING] No sources found for this query.")
    # Save to cache
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(sources, f)
    except Exception:
        pass
    return sources

def synthesize_findings(topic, all_sources):
    print(f"\n✍️  Synthesizing {len(all_sources)} sources into report...")
    sources_text = ""
    for i, s in enumerate(all_sources, 1):
        sources_text += f"\nSource {i}: {s['title']}\nURL: {s['url']}\nContent: {s['content']}\n"

    prompt = f"""You are a senior research analyst at a top consulting firm. 
Write a thorough, professional research report on: "{topic}"

Use EXACTLY this structure and be very detailed in each section:

## Executive Summary
Write 5-6 detailed sentences covering the most important findings, current state, and implications.

## Background & Context
Write 4-5 sentences providing context, history, and why this topic matters today.

## Key Findings

### Finding 1: [Descriptive Theme Title]
Write 2 sentences introducing this theme.
- Specific finding with data or evidence
- Specific finding with data or evidence  
- Specific finding with data or evidence
- Specific finding with data or evidence

### Finding 2: [Descriptive Theme Title]
Write 2 sentences introducing this theme.
- Specific finding with data or evidence
- Specific finding with data or evidence
- Specific finding with data or evidence
- Specific finding with data or evidence

### Finding 3: [Descriptive Theme Title]
Write 2 sentences introducing this theme.
- Specific finding with data or evidence
- Specific finding with data or evidence
- Specific finding with data or evidence
- Specific finding with data or evidence

### Finding 4: [Descriptive Theme Title]
Write 2 sentences introducing this theme.
- Specific finding with data or evidence
- Specific finding with data or evidence
- Specific finding with data or evidence

## Areas of Consensus
Write 5-6 sentences about what experts and sources broadly agree on regarding this topic.

## Debates and Controversies
Write 5-6 sentences describing the main disagreements, opposing viewpoints, and contested claims.

## Challenges and Barriers
Write 4-5 sentences about the main obstacles, risks, or challenges in this area.

## What Remains Unknown
Write 4-5 sentences about knowledge gaps, unanswered questions, and areas needing more research.

## Future Outlook
Write 4-5 sentences about trends, predictions, and what to expect in the coming years.

## Conclusion
Write 5-6 sentences synthesizing the report, key takeaways, and final recommendations.

SOURCES TO USE:
{sources_text}

Write the complete detailed report now. Be thorough, specific, and analytical:"""

    return ask_groq(prompt, system="You are a senior research analyst who writes detailed, evidence-based, professional reports for executives and academics.")

class ProfessionalDoc(BaseDocTemplate):
    def __init__(self, filename, topic, num_sources, **kwargs):
        super().__init__(filename, **kwargs)
        self.topic = topic
        self.num_sources = num_sources
        frame = Frame(
            self.leftMargin, self.bottomMargin + 0.6*inch,
            self.width, self.height - 1.4*inch, id='main'
        )
        template = PageTemplate(id='main', frames=frame,
                                onPage=self.add_header_footer)
        self.addPageTemplates([template])

    def add_header_footer(self, c, doc):
        c.saveState()
        w, h = letter

        # Header
        c.setFillColor(DARK_BLUE)
        c.rect(0, h - 0.75*inch, w, 0.75*inch, fill=1, stroke=0)
        c.setFillColor(ACCENT_BLUE)
        c.rect(0, h - 0.75*inch, 0.08*inch, 0.75*inch, fill=1, stroke=0)

        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(0.25*inch, h - 0.32*inch, "AUTORESEARCH AGENT")
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor('#93c5fd'))
        c.drawString(0.25*inch, h - 0.52*inch, "Powered by LLaMA 3.3 70B + Tavily Search | Built by M. Umer Farooq")

        topic_short = self.topic[:55] + "..." if len(self.topic) > 55 else self.topic
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 9)
        c.drawRightString(w - 0.3*inch, h - 0.42*inch, topic_short)

        # Footer
        c.setFillColor(LIGHT_GRAY)
        c.rect(0, 0, w, 0.55*inch, fill=1, stroke=0)
        c.setStrokeColor(ACCENT_BLUE)
        c.setLineWidth(2)
        c.line(0, 0.55*inch, w, 0.55*inch)

        c.setFillColor(GRAY)
        c.setFont("Helvetica", 8)
        c.drawString(0.3*inch, 0.22*inch,
                     f"© {datetime.now().year} M. Umer Farooq  |  AutoResearch Agent  |  Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        c.setFillColor(ACCENT_BLUE)
        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(w - 0.3*inch, 0.22*inch,
                          f"Sources: {self.num_sources}  |  Page {doc.page}")
        c.restoreState()

def build_cover_page(topic, num_sources, styles):
    story = []
    story.append(Spacer(1, 0.4*inch))

    # Badge
    badge_style = ParagraphStyle(
        'Badge', fontSize=9, fontName='Helvetica-Bold',
        textColor=ACCENT_BLUE, spaceAfter=16,
        borderColor=ACCENT_BLUE, borderWidth=1,
        borderPad=6, backColor=LIGHT_BLUE,
        alignment=TA_LEFT
    )
    story.append(Paragraph("🤖  AI-GENERATED RESEARCH REPORT", badge_style))
    story.append(Spacer(1, 0.1*inch))

    # Main title
    title_style = ParagraphStyle(
        'CoverTitle', fontSize=28, fontName='Helvetica-Bold',
        textColor=DARK_BLUE, spaceAfter=12, leading=34
    )
    story.append(Paragraph("Research Report", title_style))

    topic_style = ParagraphStyle(
        'CoverTopic', fontSize=17, fontName='Helvetica',
        textColor=ACCENT_BLUE, spaceAfter=24, leading=24
    )
    story.append(Paragraph(topic, topic_style))

    story.append(HRFlowable(width="100%", thickness=2.5,
                            color=ACCENT_BLUE, spaceAfter=20))

    # Meta table
    meta = [
        ['📅  Date', datetime.now().strftime('%B %d, %Y')],
        ['👨‍💻  Author', 'M. Umer Farooq'],
        ['🤖  AI Model', 'LLaMA 3.3 70B (Groq Ultra-Fast Inference)'],
        ['🔍  Search', 'Tavily Advanced Web Search'],
        ['📚  Sources', f'{num_sources} web sources analyzed'],
        ['⚡  Generated in', '< 60 seconds'],
    ]
    t = Table(meta, colWidths=[1.8*inch, 4.8*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), LIGHT_BLUE),
        ('BACKGROUND', (1,0), (1,-1), WHITE),
        ('TEXTCOLOR', (0,0), (0,-1), DARK_BLUE),
        ('TEXTCOLOR', (1,0), (1,-1), DARK_GRAY),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('PADDING', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, HexColor('#e2e8f0')),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*inch))

    # Disclaimer
    disc_style = ParagraphStyle(
        'Disclaimer', fontSize=8, fontName='Helvetica',
        textColor=GRAY, spaceAfter=0, leading=12,
        borderColor=LIGHT_GRAY, borderWidth=1,
        borderPad=8, backColor=LIGHT_GRAY
    )
    story.append(Paragraph(
        "⚠️  This report was autonomously generated by AutoResearch Agent. "
        "All findings are synthesized from publicly available web sources. "
        "Verify critical information independently before making decisions.",
        disc_style
    ))
    story.append(PageBreak())
    return story

def save_pdf(topic, report_text, all_sources, logo_path=None):
    filename = topic.lower().replace(' ', '-')[:40] + '-report.pdf'
    doc = ProfessionalDoc(
        filename, topic=topic, num_sources=len(all_sources),
        pagesize=letter,
        rightMargin=0.75*inch, leftMargin=0.75*inch,
        topMargin=1.0*inch, bottomMargin=0.9*inch
    )

    styles = getSampleStyleSheet()

    # Define styles
    h2_style = ParagraphStyle(
        'H2', fontSize=13, fontName='Helvetica-Bold',
        textColor=WHITE, spaceBefore=18, spaceAfter=10,
        leading=18, leftIndent=-6, rightIndent=-6,
        borderPad=9, backColor=DARK_BLUE
    )
    h3_style = ParagraphStyle(
        'H3', fontSize=11, fontName='Helvetica-Bold',
        textColor=ACCENT_BLUE, spaceBefore=12, spaceAfter=5, leading=15
    )
    body_style = ParagraphStyle(
        'Body', fontSize=10, fontName='Helvetica',
        textColor=DARK_GRAY, spaceAfter=6, leading=16,
        alignment=TA_JUSTIFY
    )
    bullet_style = ParagraphStyle(
        'Bullet', fontSize=10, fontName='Helvetica',
        textColor=DARK_GRAY, spaceAfter=5, leading=15,
        leftIndent=20, bulletIndent=6
    )
    citation_style = ParagraphStyle(
        'Citation', fontSize=9, fontName='Helvetica-Bold',
        textColor=DARK_GRAY, spaceAfter=3, leading=13, leftIndent=16
    )
    url_style = ParagraphStyle(
        'URL', fontSize=8, fontName='Helvetica',
        textColor=TEAL, spaceAfter=10, leading=11, leftIndent=16
    )

    story = []


    # Cover page with optional logo
    if logo_path and os.path.exists(logo_path):
        from reportlab.platypus import Image
        story.append(Image(logo_path, width=1.5*inch, height=1.5*inch))
        story.append(Spacer(1, 0.1*inch))
    story.extend(build_cover_page(topic, len(all_sources), styles))

    # --- Summary table of sources ---
    if all_sources:
        print("[DEBUG] ParagraphStyle type:", type(ParagraphStyle), ParagraphStyle)
        if ParagraphStyle is None or not callable(ParagraphStyle):
            raise RuntimeError("ParagraphStyle is not callable or not imported correctly!")
        cell_style = ParagraphStyle('cell', fontSize=7, leading=9, textColor=DARK_GRAY)
        header_style = ParagraphStyle('header', fontSize=7, leading=9, textColor=DARK_BLUE, fontName='Helvetica-Bold')

        table_data = [[
            Paragraph('#', header_style),
            Paragraph('Title', header_style),
            Paragraph('Cred.', header_style),
            Paragraph('Evidence Snippet', header_style),
            Paragraph('URL', header_style),
        ]]
        for i, s in enumerate(all_sources, 1):
            table_data.append([
                Paragraph(str(i), cell_style),
                Paragraph(s.get('title', '')[:40], cell_style),
                Paragraph(str(s.get('credibility', '')), cell_style),
                Paragraph(s.get('snippet', '')[:120], cell_style),
                Paragraph(s.get('url', '')[:60], cell_style),
            ])

        t = Table(table_data, colWidths=[0.3*inch, 1.5*inch, 0.6*inch, 2.5*inch, 2.2*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), LIGHT_BLUE),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 7),
            ('GRID', (0,0), (-1,-1), 0.5, HexColor('#e2e8f0')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Summary of Sources", styles['Heading3']))
        story.append(t)
        story.append(Spacer(1, 0.2*inch))

    # Report content
    for line in report_text.split('\n'):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 4))
        elif line.startswith('## '):
            story.append(Spacer(1, 6))
            story.append(Paragraph(f"   {line[3:].upper()}", h2_style))
        elif line.startswith('### '):
            story.append(Paragraph(line[4:], h3_style))
        elif line.startswith('- ') or line.startswith('* '):
            story.append(Paragraph(f"▸   {line[2:]}", bullet_style))
        else:
            story.append(Paragraph(line, body_style))

    # Sources
    story.append(Spacer(1, 0.2*inch))
    story.append(HRFlowable(width="100%", thickness=1.5,
                            color=ACCENT_BLUE, spaceAfter=8))
    story.append(Paragraph("   SOURCES & CITATIONS", h2_style))
    story.append(Spacer(1, 8))
    for i, s in enumerate(all_sources, 1):
        story.append(Paragraph(f"[{i}]  {s['title']}", citation_style))
        story.append(Paragraph(s['url'], url_style))

    # Back cover note
    story.append(Spacer(1, 0.3*inch))
    back_style = ParagraphStyle(
        'Back', fontSize=9, fontName='Helvetica',
        textColor=GRAY, alignment=TA_CENTER, leading=14
    )
    story.append(HRFlowable(width="100%", thickness=0.5,
                            color=LIGHT_GRAY, spaceAfter=10))
    story.append(Paragraph(
        f"Report generated by AutoResearch Agent  |  Built by M. Umer Farooq  |  "
        f"{datetime.now().strftime('%Y')}",
        back_style
    ))

    doc.build(story)
    return filename


def save_word(topic, report_text, all_sources, logo_path=None):
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    filename = topic.lower().replace(" ", "-")[:40] + "-report.docx"
    doc = Document()

    # Page margins
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Title and optional logo
    if logo_path and os.path.exists(logo_path):
        from docx.shared import Inches
        doc.add_picture(logo_path, width=Inches(1.5))
    title = doc.add_heading("Research Report", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = title.runs[0]
    run.font.color.rgb = RGBColor(0x0f, 0x17, 0x2a)
    run.font.size = Pt(26)

    # --- Summary table of sources ---
    if all_sources:
        doc.add_heading("Summary of Sources", level=2)
        table = doc.add_table(rows=len(all_sources)+1, cols=5)
        table.style = "Table Grid"
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "#"
        hdr_cells[1].text = "Title"
        hdr_cells[2].text = "Credibility"
        hdr_cells[3].text = "Evidence Snippet"
        hdr_cells[4].text = "URL"
        for i, s in enumerate(all_sources, 1):
            row = table.rows[i].cells
            row[0].text = str(i)
            row[1].text = s.get('title', '')[:30]
            row[2].text = str(s.get('credibility', ''))
            row[3].text = s.get('snippet', '')[:60]
            row[4].text = s.get('url', '')[:40]
        doc.add_paragraph()

    # Topic
    topic_para = doc.add_paragraph()
    topic_run = topic_para.add_run(topic)
    topic_run.font.size = Pt(16)
    topic_run.font.color.rgb = RGBColor(0x25, 0x63, 0xeb)
    topic_para.paragraph_format.space_after = Pt(6)

    # Meta info
    doc.add_paragraph()
    meta = [
        ("Date Generated", datetime.now().strftime("%B %d, %Y")),
        ("Author", "M. Umer Farooq"),
        ("AI Model", "LLaMA 3.3 70B (Groq)"),
        ("Search Engine", "Tavily Web Search"),
        ("Sources Analyzed", str(len(all_sources))),
    ]
    table = doc.add_table(rows=len(meta), cols=2)
    table.style = "Table Grid"
    for i, (key, val) in enumerate(meta):
        row = table.rows[i]
        row.cells[0].text = key
        row.cells[1].text = val
        row.cells[0].paragraphs[0].runs[0].font.bold = True
        row.cells[0].paragraphs[0].runs[0].font.color.rgb = RGBColor(0x0f, 0x17, 0x2a)

    doc.add_paragraph()
    disclaimer = doc.add_paragraph()
    disc_run = disclaimer.add_run(
        "⚠️ This report was autonomously generated by AutoResearch Agent. "
        "All findings are synthesized from publicly available web sources. "
        "Verify critical information independently before making decisions."
    )
    disc_run.font.size = Pt(9)
    disc_run.font.color.rgb = RGBColor(0x6b, 0x72, 0x80)
    doc.add_page_break()

    # Report content
    for line in report_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        elif line.startswith("## "):
            h = doc.add_heading(line[3:], level=1)
            h.runs[0].font.color.rgb = RGBColor(0x0f, 0x17, 0x2a)
        elif line.startswith("### "):
            h = doc.add_heading(line[4:], level=2)
            h.runs[0].font.color.rgb = RGBColor(0x25, 0x63, 0xeb)
        elif line.startswith("#### "):
            h = doc.add_heading(line[5:], level=3)
        elif line.startswith("- ") or line.startswith("* "):
            p = doc.add_paragraph(line[2:], style="List Bullet")
            p.paragraph_format.space_after = Pt(3)
        else:
            p = doc.add_paragraph(line)
            p.paragraph_format.space_after = Pt(4)
            p.runs[0].font.size = Pt(10) if p.runs else None

    # Sources
    doc.add_page_break()
    doc.add_heading("Sources & Citations", level=1)
    for i, s in enumerate(all_sources, 1):
        p = doc.add_paragraph()
        run = p.add_run(f"[{i}]  {s['title']}")
        run.font.bold = True
        run.font.size = Pt(9)
        url_p = doc.add_paragraph()
        url_run = url_p.add_run(s["url"])
        url_run.font.size = Pt(8)
        url_run.font.color.rgb = RGBColor(0x25, 0x63, 0xeb)

    # Footer note
    doc.add_paragraph()
    footer_p = doc.add_paragraph()
    footer_run = footer_p.add_run(
        f"Report generated by AutoResearch Agent  |  Built by M. Umer Farooq  |  {datetime.now().strftime('%Y')}"
    )
    footer_run.font.size = Pt(8)
    footer_run.font.color.rgb = RGBColor(0x6b, 0x72, 0x80)
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.save(filename)
    return filename

# --- HTML and Markdown output support ---
def save_html(topic, report_text, all_sources, logo_path=None):
    filename = topic.lower().replace(' ', '-')[:40] + '-report.html'
    html = ["<html><head><meta charset='utf-8'><title>Research Report</title></head><body>"]
    if logo_path and os.path.exists(logo_path):
        html.append(f"<img src='{logo_path}' alt='Logo' style='width:120px;height:120px;'/><br>")
    html.append(f"<h1>Research Report</h1><h2>{topic}</h2>")
    # --- Summary table of sources ---
    if all_sources:
        html.append("<h3>Summary of Sources</h3><table border='1' cellpadding='4' style='border-collapse:collapse;font-size:0.95em;'>")
        html.append("<tr><th>#</th><th>Title</th><th>Credibility</th><th>Evidence Snippet</th><th>URL</th></tr>")
        for i, s in enumerate(all_sources, 1):
            html.append(f"<tr><td>{i}</td><td>{s.get('title','')[:30]}</td><td>{s.get('credibility','')}</td><td>{s.get('snippet','')[:60]}</td><td><a href='{s.get('url','')}'>{s.get('url','')[:40]}</a></td></tr>")
        html.append("</table><br>")
    html.append("<h3>Sources & Citations</h3><ul>")
    for i, s in enumerate(all_sources, 1):
        html.append(f"<li><b>[{i}] {s['title']}</b><br><a href='{s['url']}'>{s['url']}</a></li>")
    html.append("</ul><hr>")
    html.append("<pre style='font-size:1em;'>" + report_text + "</pre>")
    html.append("</body></html>")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html))
    return filename

def save_markdown(topic, report_text, all_sources, logo_path=None):
    filename = topic.lower().replace(' ', '-')[:40] + '-report.md'
    md = [f"# Research Report\n\n## {topic}\n"]
    if logo_path and os.path.exists(logo_path):
        md.append(f"![Logo]({logo_path})\n")
    # --- Summary table of sources ---
    if all_sources:
        md.append("## Summary of Sources\n| # | Title | Credibility | Evidence Snippet | URL |\n|---|-------|-------------|------------------|-----|")
        for i, s in enumerate(all_sources, 1):
            md.append(f"| {i} | {s.get('title','')[:30]} | {s.get('credibility','')} | {s.get('snippet','')[:60]} | {s.get('url','')[:40]} |")
        md.append("")
    md.append("## Sources & Citations\n")
    for i, s in enumerate(all_sources, 1):
        md.append(f"[{i}] {s['title']}\n{s['url']}\n")
    md.append("---\n")
    md.append(report_text)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
    return filename



# --- Modularized main research workflow ---
def collect_sources_for_topic(topic, plugin_hooks=None):
    questions = generate_sub_questions(topic)
    all_sources = []
    # Allow user to set number of sources per query via env var or default
    try:
        max_sources = int(os.getenv("MAX_SOURCES_PER_QUERY", "4"))
    except Exception:
        max_sources = 4
    for q in questions:
        sources = search_web(q, max_results=max_sources)
        if plugin_hooks and 'on_sources_fetched' in plugin_hooks:
            sources = plugin_hooks['on_sources_fetched'](q, sources)
        all_sources.extend(sources)
    return all_sources

def generate_report_for_topic(topic, all_sources, plugin_hooks=None):
    if plugin_hooks and 'pre_synthesis' in plugin_hooks:
        all_sources = plugin_hooks['pre_synthesis'](all_sources)
    report = synthesize_findings(topic, all_sources)
    if plugin_hooks and 'post_synthesis' in plugin_hooks:
        report = plugin_hooks['post_synthesis'](report)
    return report

def run_agent(topic, output_format="pdf", logo_path=None, plugin_hooks=None):
    print(f"\n{'='*60}")
    print(f"🤖 AutoResearch Agent v2.0")
    print(f"👨‍💻 Built by M. Umer Farooq")
    print(f"📌 Topic: {topic}")
    print(f"{'='*60}")

    all_sources = collect_sources_for_topic(topic, plugin_hooks=plugin_hooks)
    print(f"\n📚 Total sources collected: {len(all_sources)}")
    report = generate_report_for_topic(topic, all_sources, plugin_hooks=plugin_hooks)

    if output_format == "pdf":
        pdf_file = save_pdf(topic, report, all_sources, logo_path=logo_path)
        print(f"📄 PDF saved: {pdf_file}")
    elif output_format == "word":
        word_file = save_word(topic, report, all_sources, logo_path=logo_path)
        print(f"📝 Word saved: {word_file}")
    elif output_format == "html":
        html_file = save_html(topic, report, all_sources, logo_path=logo_path)
        print(f"🌐 HTML saved: {html_file}")
    elif output_format == "md":
        md_file = save_markdown(topic, report, all_sources, logo_path=logo_path)
        print(f"📝 Markdown saved: {md_file}")

    print(f"\n{'='*60}")
    print(f"✅ Research Complete!")
    print(f"📊 Sources analyzed: {len(all_sources)}")
    print(f"👨‍💻 Built by M. Umer Farooq")
    print(f"{'='*60}\n")




def analyze_competitor(company, all_sources):
    sources_text = ""
    for i, s in enumerate(all_sources, 1):
        sources_text += f"\nSource {i}: {s['title']}\nURL: {s['url']}\nContent: {s['content']}\n"

    prompt = f"""You are a senior competitive intelligence analyst.
Based on the sources below, write a detailed profile for: "{company}"

Use EXACTLY this structure:

### {company}

#### Company Overview
2-3 sentences about what the company does and its market position.

#### Latest News & Developments
- Recent news item 1
- Recent news item 2
- Recent news item 3

#### Products & Services
- Key product/service 1
- Key product/service 2
- Key product/service 3

#### Funding & Financials
- Latest funding round or revenue data
- Valuation if available
- Key investors

#### Strengths
- Strength 1
- Strength 2
- Strength 3

#### Weaknesses & Risks
- Weakness 1
- Weakness 2

SOURCES:
{sources_text}

Write the complete profile now:"""

    return ask_groq(prompt, system="You are a senior competitive intelligence analyst who writes precise, data-driven company profiles.")

def run_competitor_agent(companies_input, fmt='pdf'):
    companies = [c.strip() for c in companies_input.split(',')]

    print(f"\n{'='*60}")
    print(f"🤖 AutoResearch Agent v2.0 — Competitor Intelligence Mode")
    print(f"👨‍💻 Built by M. Umer Farooq")
    print(f"🏢 Companies: {', '.join(companies)}")
    print(f"{'='*60}")

    all_profiles = {}
    all_sources = []

    for company in companies:
        print(f"\n📊 Researching: {company}")
        company_sources = []

        queries = [
            f"{company} latest news 2025",
            f"{company} products funding valuation 2025",
            f"{company} competitive strategy market position"
        ]
        for q in queries:
            sources = search_web(q)
            company_sources.extend(sources)
            all_sources.extend(sources)

        print(f"  📚 Found {len(company_sources)} sources")
        profile = analyze_competitor(company, company_sources)
        all_profiles[company] = profile

    # Generate comparison summary
    print(f"\n✍️  Generating competitive comparison summary...")
    profiles_text = "\n\n".join([f"=== {c} ===\n{p}" for c, p in all_profiles.items()])
    summary_prompt = f"""Based on these company profiles, write a competitive analysis summary:

{profiles_text}

Write:

## Competitive Landscape Overview
4-5 sentences about the overall competitive dynamics.

## Head-to-Head Comparison
Compare all companies on: market position, product strength, funding, growth trajectory.

## Who is Winning and Why
3-4 sentences identifying the leader and why.

## Strategic Recommendations
- Recommendation 1
- Recommendation 2
- Recommendation 3

Write the complete summary now:"""

    summary = ask_groq(summary_prompt, system="You are a senior competitive intelligence analyst.")

    # Save PDF
    topic = f"Competitive Analysis: {', '.join(companies)}"
    full_report = summary + "\n\n## INDIVIDUAL COMPANY PROFILES\n\n" + profiles_text
    if fmt in ["pdf", "both"]:
        pdf_file = save_competitor_pdf(topic, full_report, companies, all_sources)
        print(f"\n📄 PDF saved: {pdf_file}")
    if fmt in ["word", "both"]:
        word_file = save_word(topic, full_report, all_sources)
        print(f"📝 Word saved: {word_file}")
    print(f"\n{'='*60}")
    print(f"✅ Competitive Analysis Complete!")
    print(f"📊 Total sources analyzed: {len(all_sources)}")
    print(f"{'='*60}\n")

def save_competitor_pdf(topic, report_text, companies, all_sources):
    filename = "competitor-analysis-" + "-".join([c.lower().replace(' ','-')[:10] for c in companies[:3]]) + ".pdf"

    doc = ProfessionalDoc(
        filename, topic=topic, num_sources=len(all_sources),
        pagesize=letter,
        rightMargin=0.75*inch, leftMargin=0.75*inch,
        topMargin=1.0*inch, bottomMargin=0.9*inch
    )

    styles = getSampleStyleSheet()

    h2_style = ParagraphStyle(
        'H2', fontSize=13, fontName='Helvetica-Bold',
        textColor=white, spaceBefore=18, spaceAfter=10,
        leading=18, leftIndent=-6, rightIndent=-6,
        borderPad=9, backColor=DARK_BLUE
    )
    h3_style = ParagraphStyle(
        'H3', fontSize=12, fontName='Helvetica-Bold',
        textColor=DARK_BLUE, spaceBefore=16, spaceAfter=6,
        leading=16, borderPad=6, backColor=LIGHT_BLUE,
        leftIndent=-4, rightIndent=-4
    )
    h4_style = ParagraphStyle(
        'H4', fontSize=10, fontName='Helvetica-Bold',
        textColor=ACCENT_BLUE, spaceBefore=10, spaceAfter=4, leading=14
    )
    body_style = ParagraphStyle(
        'Body', fontSize=10, fontName='Helvetica',
        textColor=DARK_GRAY, spaceAfter=6, leading=16,
        alignment=TA_JUSTIFY
    )
    bullet_style = ParagraphStyle(
        'Bullet', fontSize=10, fontName='Helvetica',
        textColor=DARK_GRAY, spaceAfter=5, leading=15,
        leftIndent=20
    )
    citation_style = ParagraphStyle(
        'Citation', fontSize=9, fontName='Helvetica-Bold',
        textColor=DARK_GRAY, spaceAfter=3, leading=13, leftIndent=16
    )
    url_style = ParagraphStyle(
        'URL', fontSize=8, fontName='Helvetica',
        textColor=TEAL, spaceAfter=10, leading=11, leftIndent=16
    )

    story = []
    story.extend(build_cover_page(topic, len(all_sources), styles))

    for line in report_text.split('\n'):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 4))
        elif line.startswith('## '):
            story.append(Spacer(1, 6))
            story.append(Paragraph(f"   {line[3:].upper()}", h2_style))
        elif line.startswith('### '):
            story.append(Paragraph(f"  {line[4:].upper()}  ", h3_style))
        elif line.startswith('#### '):
            story.append(Paragraph(line[5:], h4_style))
        elif line.startswith('- ') or line.startswith('* '):
            story.append(Paragraph(f"▸   {line[2:]}", bullet_style))
        else:
            story.append(Paragraph(line, body_style))

    # Sources
    story.append(Spacer(1, 0.2*inch))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT_BLUE, spaceAfter=8))
    story.append(Paragraph("   SOURCES & CITATIONS", h2_style))
    story.append(Spacer(1, 8))
    for i, s in enumerate(all_sources, 1):
        story.append(Paragraph(f"[{i}]  {s['title']}", citation_style))
        story.append(Paragraph(s['url'], url_style))

    story.append(Spacer(1, 0.3*inch))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GRAY, spaceAfter=10))
    back_style = ParagraphStyle('Back', fontSize=9, fontName='Helvetica',
                                textColor=GRAY, alignment=TA_CENTER, leading=14)
    story.append(Paragraph(
        f"Report generated by AutoResearch Agent  |  Built by M. Umer Farooq  |  {datetime.now().strftime('%Y')}",
        back_style
    ))

    doc.build(story)
    return filename


# Update main block

# Override the __main__ block
import sys as _sys
import argparse as _argparse

if __name__ == "__main__":
    parser = _argparse.ArgumentParser(
        description="🤖 AutoResearch Agent — Built by M. Umer Farooq"
    )
    parser.add_argument("mode", choices=["research", "compete"],
                        help="Mode: research or compete")
    parser.add_argument("input", nargs="+",
                        help="Topic or comma-separated company names")
    parser.add_argument("--format", choices=["pdf", "word", "both", "html", "md"],
                        default="pdf",
                        help="Output format: pdf, word, html, md, or both (default: pdf)")
    parser.add_argument("--logo", type=str, default=None, help="Path to custom logo image (optional)")
    parser.add_argument("--max-sources", type=int, default=None, help="Number of sources per sub-question (overrides env)")
    args = parser.parse_args()
    input_text = " ".join(args.input)

    if args.mode == "research":
        if args.max_sources:
            os.environ["MAX_SOURCES_PER_QUERY"] = str(args.max_sources)
        run_agent(input_text, output_format=args.format, logo_path=args.logo)
    elif args.mode == "compete":
        run_competitor_agent(input_text, fmt=args.format)
