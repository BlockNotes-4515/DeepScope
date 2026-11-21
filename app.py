import html
import math
import re
import time
import streamlit as st
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="RESEARCHMIND // Autonomous Multi-Agent System",
    page_icon="■",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------
# Square Brutalist Black Theme + Green Animated Lighting CSS
# --------------------------------------------------
st.markdown(
"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Silkscreen:wght@400;700&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --bg: #000000;
    --panel: #050806;
    --panel-2: #0A0F0C;
    --ink: #F4F4F5;
    --ink-dim: #A1A1AA;
    --green: #00FF88;
    --green-soft: rgba(0, 255, 136, 0.14);
    --green-glow: rgba(0, 255, 136, 0.42);
    --pink: #F472B6;
    --blue: #3B82F6;
    --amber: #F59E0B;
    --purple: #A78BFA;
    --border: rgba(255, 255, 255, 0.16);
}

html {
    scroll-behavior: smooth;
}

html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: var(--bg) !important;
    background-image:
        radial-gradient(ellipse 70% 35% at 50% 0%, rgba(0, 255, 136, 0.11), transparent),
        linear-gradient(rgba(0, 255, 136, 0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 255, 136, 0.025) 1px, transparent 1px) !important;
    background-size: 100% 100%, 42px 42px, 42px 42px !important;
    color: var(--ink) !important;
    font-family: "Space Grotesk", -apple-system, sans-serif !important;
}

header[data-testid="stHeader"] {
    display: none !important;
}

.block-container {
    padding-top: 0.75rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1360px !important;
}

/* Force High-Contrast Text Visibility */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] td,
[data-testid="stMarkdownContainer"] th,
label, .stCaption {
    color: #E4E4E7 !important;
}

[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stMarkdownContainer"] strong {
    color: #FFFFFF !important;
}

[data-testid="stMarkdownContainer"] a {
    color: var(--green);
}

/* ---------------- Keyframe Animations & Green Lighting ---------------- */
@keyframes greenBorderPulse {
    0%, 100% { box-shadow: 0 0 0 1px rgba(0,255,136,0.22), 0 0 16px rgba(0,255,136,0.08); }
    50% { box-shadow: 0 0 0 1px rgba(0,255,136,0.72), 0 0 28px rgba(0,255,136,0.26); }
}

@keyframes scanSweep {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

@keyframes revealSlide {
    0% { opacity: 0; transform: translateY(16px); }
    100% { opacity: 1; transform: translateY(0); }
}

@keyframes maskUp {
    0% { opacity: 0; transform: translateY(115%); }
    100% { opacity: 1; transform: translateY(0%); }
}

@keyframes sqFillIn {
    0% { opacity: 0; transform: scale(0.25); filter: brightness(2.2); }
    65% { opacity: 1; transform: scale(1.12); box-shadow: 0 0 12px var(--green); }
    100% { opacity: 1; transform: scale(1); }
}

@keyframes ledBlink {
    0%, 100% { opacity: 1; box-shadow: 0 0 10px var(--green); }
    50% { opacity: 0.35; box-shadow: 0 0 2px var(--green); }
}

/* ---------------- 1. Proper Square Raster Header ---------------- */
.rm-sq-header {
    position: sticky;
    top: 0.45rem;
    z-index: 999;
    background: rgba(0, 0, 0, 0.92);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(0, 255, 136, 0.45);
    border-radius: 0px;
    padding: 0.72rem 1.2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
    animation: greenBorderPulse 3.6s ease-in-out infinite;
    margin-bottom: 0.5rem;
}

.rm-pixel-logo {
    font-family: "Silkscreen", monospace !important;
    font-size: 1.55rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: #FFFFFF;
    text-decoration: none !important;
    display: flex;
    align-items: center;
    gap: 0.65rem;
}

.rm-pixel-logo span {
    color: var(--green);
}

.rm-nav-links {
    display: flex;
    align-items: center;
    gap: 1.1rem;
    flex-wrap: wrap;
}

.rm-nav-link {
    font-family: "JetBrains Mono", monospace;
    font-size: 0.80rem;
    color: #D4D4D8 !important;
    text-decoration: none !important;
    padding: 0.25rem 0.4rem;
    border: 1px solid transparent;
    transition: all 0.2s ease;
}

.rm-nav-link:hover {
    color: var(--green) !important;
    border-color: rgba(0, 255, 136, 0.5);
    background: rgba(0, 255, 136, 0.08);
    transform: translateY(-2px);
}

.rm-hdr-right {
    display: flex;
    align-items: center;
    gap: 0.85rem;
}

.rm-motion-tag {
    font-family: "JetBrains Mono", monospace;
    font-size: 0.76rem;
    color: var(--green);
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

.green-led {
    width: 8px;
    height: 8px;
    background: var(--green);
    display: inline-block;
    animation: ledBlink 1.3s ease-in-out infinite;
}

.rm-sq-cta {
    background: var(--green) !important;
    color: #000000 !important;
    font-weight: 700;
    font-size: 0.82rem;
    padding: 0.48rem 0.95rem;
    border: 1px solid var(--green);
    border-radius: 0px;
    text-decoration: none !important;
    transition: all 0.2s ease;
}

.rm-sq-cta:hover {
    background: #000000 !important;
    color: var(--green) !important;
    box-shadow: 0 0 18px rgba(0, 255, 136, 0.45);
}

/* Sub-header Green Scanline Bar */
.rm-scan-bar {
    height: 2px;
    width: 100%;
    background: linear-gradient(90deg, transparent, var(--green), #38BDF8, var(--green), transparent);
    background-size: 200% 100%;
    animation: scanSweep 3.5s linear infinite;
    margin-bottom: 1.5rem;
}

/* ---------------- Hero Editorial Text ---------------- */
.rm-hero-kicker {
    font-family: "JetBrains Mono", monospace;
    font-size: 0.78rem;
    color: var(--green);
    margin-bottom: 0.55rem;
    letter-spacing: 0.05em;
}

.rm-hero-title {
    font-size: clamp(2.15rem, 4vw, 3.35rem);
    font-weight: 700;
    line-height: 1.05;
    letter-spacing: -0.035em;
    color: #FFFFFF;
    margin-bottom: 0.95rem;
}

.rm-mask { display: block; overflow: hidden; }
.rm-slide { display: inline-block; animation: maskUp 0.85s cubic-bezier(0.16, 1, 0.3, 1) both; }
.rm-d1 { animation-delay: 0.05s; }
.rm-d2 { animation-delay: 0.16s; color: var(--green); text-shadow: 0 0 24px rgba(0,255,136,0.35); }

/* ---------------- Sharp Square Boxes & Pattern Cards ---------------- */
.sq-box {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 0px;
    padding: 1.15rem 1.25rem;
    transition: all 0.26s cubic-bezier(0.16, 1, 0.3, 1);
    animation: revealSlide 0.6s ease both;
}

.sq-box:hover {
    border-color: var(--green);
    box-shadow: 0 0 24px rgba(0, 255, 136, 0.16);
    transform: translateY(-3px);
}

/* 4 Pattern Agent Cards (Reference Image 1 Style) */
.track-card {
    border: 1px solid rgba(255,255,255,0.22);
    border-radius: 0px;
    overflow: hidden;
    background: #050806;
    transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1);
    cursor: pointer;
}

.track-card:hover {
    border-color: var(--green);
    box-shadow: 0 0 28px rgba(0, 255, 136, 0.28);
    transform: translateY(-5px);
}

.track-pattern {
    width: 100%;
    height: 155px;
    display: block;
}

.track-foot {
    padding: 0.85rem 1rem;
    border-top: 1px solid rgba(255,255,255,0.14);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.track-name {
    font-size: 1.2rem;
    font-weight: 700;
    color: #FFFFFF;
}

.track-meta {
    font-family: "JetBrains Mono", monospace;
    font-size: 0.72rem;
    color: var(--green);
}

/* ---------------- 2. Dynamic Box Matrix with Hover Info ---------------- */
.matrix-grid {
    display: grid;
    grid-template-columns: repeat(22, minmax(0, 1fr));
    gap: 5px;
    padding: 0.9rem 0;
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
}

.mx-cell {
    position: relative;
    aspect-ratio: 1 / 1;
    border-radius: 0px;
    animation: sqFillIn 0.45s ease both;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.mx-cell:hover {
    transform: scale(1.45);
    z-index: 20;
    box-shadow: 0 0 14px var(--green);
    outline: 1px solid #FFFFFF;
}

.mx-tip {
    visibility: hidden;
    opacity: 0;
    position: absolute;
    bottom: 130%;
    left: 50%;
    transform: translateX(-50%);
    background: #000000;
    border: 1px solid var(--green);
    color: #FFFFFF;
    padding: 0.42rem 0.62rem;
    font-family: "JetBrains Mono", monospace;
    font-size: 0.68rem;
    white-space: nowrap;
    z-index: 99;
    pointer-events: none;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.85);
    transition: opacity 0.15s ease;
}

.mx-cell:hover .mx-tip {
    visibility: visible;
    opacity: 1;
}

/* ---------------- Square Search Bar & Boxed Buttons ---------------- */
div[data-testid="stForm"] {
    background: #040705 !important;
    border: 1px solid rgba(0, 255, 136, 0.45) !important;
    border-radius: 0px !important;
    padding: 0.45rem 0.6rem !important;
    box-shadow: 0 0 24px rgba(0, 255, 136, 0.10);
    transition: all 0.25s ease;
}

div[data-testid="stForm"]:focus-within,
div[data-testid="stForm"]:hover {
    border-color: var(--green) !important;
    box-shadow: 0 0 32px rgba(0, 255, 136, 0.26);
}

div[data-testid="stForm"] input {
    background: transparent !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 0px !important;
    font-family: "JetBrains Mono", monospace !important;
    font-size: 0.94rem !important;
}

div[data-testid="stForm"] input::placeholder {
    color: #71717A !important;
}

.stButton > button,
.stDownloadButton > button,
div[data-testid="stForm"] button[kind="primaryFormSubmit"] {
    border-radius: 0px !important;
    font-family: "JetBrains Mono", monospace !important;
    font-size: 0.80rem !important;
    font-weight: 700 !important;
    background: #070B09 !important;
    color: #F4F4F5 !important;
    border: 1px solid rgba(255, 255, 255, 0.24) !important;
    transition: all 0.22s ease !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color: var(--green) !important;
    color: var(--green) !important;
    background: rgba(0, 255, 136, 0.08) !important;
    box-shadow: 0 0 18px rgba(0, 255, 136, 0.25) !important;
    transform: translateY(-2px) !important;
}

div[data-testid="stForm"] button[kind="primaryFormSubmit"] {
    background: #16A34A !important;
    color: #000000 !important;
    border: 1px solid #16A34A !important;
}

div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover {
    background: #000000 !important;
    color: var(--green) !important;
}

/* Segmented Radio -> Sharp Square Boxes */
div[data-testid="stRadio"] > div[role="radiogroup"] {
    gap: 0 !important;
    display: inline-flex;
    border: 1px solid rgba(0, 255, 136, 0.45);
    border-radius: 0px;
}

div[data-testid="stRadio"] label {
    background: #050806 !important;
    border-radius: 0px !important;
    padding: 0.34rem 0.9rem !important;
    margin: 0 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.16);
}

div[data-testid="stRadio"] label:last-child { border-right: none; }
div[data-testid="stRadio"] label:has(input:checked) { background: var(--green) !important; }
div[data-testid="stRadio"] label:has(input:checked) p { color: #000000 !important; font-weight: 700 !important; }
div[data-testid="stRadio"] input { display: none !important; }

/* Native Bordered Containers -> Square Green-Hover Boxes */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #050806 !important;
    border: 1px solid rgba(255, 255, 255, 0.16) !important;
    border-radius: 0px !important;
    padding: 1.15rem !important;
    transition: all 0.25s ease !important;
}

[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: var(--green) !important;
    box-shadow: 0 0 24px rgba(0, 255, 136, 0.14) !important;
}

/* ---------------- Interactive Hover SVG Charts ---------------- */
.svg-chart-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
}

.pie-node .pie-tip {
    opacity: 0;
    transition: opacity 0.2s ease;
    pointer-events: none;
}

.pie-node:hover .pie-tip {
    opacity: 1;
}

.pie-node circle.slice-ring {
    transition: stroke-width 0.25s ease, filter 0.25s ease;
    cursor: pointer;
}

.pie-node:hover circle.slice-ring {
    stroke-width: 66px !important;
    filter: brightness(1.25) drop-shadow(0 0 12px rgba(0,255,136,0.45));
}

.pt-node .pt-tip {
    opacity: 0;
    transform: translateY(6px);
    transition: all 0.2s ease;
    pointer-events: none;
}

.pt-node:hover .pt-tip {
    opacity: 1;
    transform: translateY(0px);
}

.pt-node .pt-dot {
    transition: r 0.2s ease, fill 0.2s ease;
    cursor: pointer;
}

.pt-node:hover .pt-dot {
    r: 9;
    fill: #FFFFFF;
}

/* ---------------- Raster 3-Column Table & Data Table ---------------- */
.raster-grid-3 {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.35rem;
    margin-top: 0.75rem;
}

@media (max-width: 900px) {
    .raster-grid-3 { grid-template-columns: 1fr; }
}

.raster-cell {
    border-top: 1px solid rgba(255, 255, 255, 0.26);
    border-bottom: 1px solid rgba(255, 255, 255, 0.14);
    padding: 0.85rem 0.35rem;
    transition: all 0.22s ease;
}

.raster-cell:hover {
    border-top-color: var(--green);
    background: rgba(0, 255, 136, 0.05);
    padding-left: 0.75rem;
}

.r-time {
    font-family: "JetBrains Mono", monospace;
    font-size: 0.76rem;
    color: #A1A1AA;
    margin-bottom: 0.25rem;
}

.r-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 0.35rem;
}

.r-tag {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.12rem 0.45rem;
    margin-left: 0.4rem;
    color: #000000;
}

.sq-table {
    width: 100%;
    border-collapse: collapse;
    font-family: "JetBrains Mono", monospace;
    font-size: 0.82rem;
}

.sq-table th {
    text-align: left;
    padding: 0.7rem 0.8rem;
    background: #0A110D;
    color: var(--green);
    border: 1px solid rgba(0, 255, 136, 0.3);
    text-transform: uppercase;
    font-size: 0.72rem;
}

.sq-table td {
    padding: 0.7rem 0.8rem;
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #F4F4F5;
    transition: background 0.18s ease;
}

.sq-table tr:hover td {
    background: rgba(0, 255, 136, 0.09);
}

/* ---------------- Section Header & Quotes ---------------- */
.sec-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid rgba(0, 255, 136, 0.4);
    border-bottom: 1px solid rgba(255, 255, 255, 0.16);
    padding: 0.65rem 0.9rem;
    background: #050907;
    margin: 2rem 0 1rem 0;
}

.sec-bar-title {
    font-family: "Silkscreen", monospace;
    font-size: 1rem;
    color: #FFFFFF;
}

.sec-bar-code {
    font-family: "JetBrains Mono", monospace;
    font-size: 0.75rem;
    color: var(--green);
}

.quote-box {
    border: 1px solid rgba(0, 255, 136, 0.4);
    border-left: 5px solid var(--green);
    background: #040806;
    padding: 1.35rem 1.5rem;
    margin: 2rem 0 1.5rem 0;
    transition: box-shadow 0.25s ease;
}

.quote-box:hover {
    box-shadow: 0 0 28px rgba(0, 255, 136, 0.18);
}

.quote-text {
    font-size: 1.18rem;
    font-weight: 500;
    line-height: 1.5;
    color: #FFFFFF;
}

.quote-sub {
    margin-top: 0.55rem;
    font-family: "JetBrains Mono", monospace;
    font-size: 0.78rem;
    color: var(--green);
}

/* ---------------- Proper Square Footer (Image 2 Style) ---------------- */
.rm-sq-footer {
    margin-top: 2.5rem;
    border: 1px solid rgba(0, 255, 136, 0.45);
    background: #030504;
    padding: 2rem 1.6rem 1.4rem 1.6rem;
    animation: greenBorderPulse 4.5s ease-in-out infinite;
}

.rm-f-top {
    display: grid;
    grid-template-columns: 1.15fr 1.85fr;
    gap: 2.2rem;
    align-items: start;
}

@media (max-width: 900px) {
    .rm-f-top { grid-template-columns: 1fr; }
}

.rm-f-big-title {
    font-family: "Silkscreen", monospace;
    font-size: clamp(1.9rem, 3.2vw, 2.7rem);
    color: #FFFFFF;
    line-height: 1.05;
    margin-bottom: 0.8rem;
}

.rm-f-big-title span { color: var(--green); }

.rm-f-quote {
    font-size: 0.94rem;
    line-height: 1.6;
    color: #D4D4D8;
    border-left: 3px solid var(--green);
    padding-left: 0.85rem;
    margin-bottom: 1rem;
}

.rm-f-bottom {
    margin-top: 1.5rem;
    padding-top: 0.9rem;
    border-top: 1px solid rgba(255, 255, 255, 0.16);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.75rem;
    font-family: "JetBrains Mono", monospace;
    font-size: 0.76rem;
    color: #A1A1AA;
}
</style>
""",
unsafe_allow_html=True,
)


# --------------------------------------------------
# Session State
# --------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "current_result" not in st.session_state:
    st.session_state.current_result = None

if "active_stage" not in st.session_state:
    st.session_state.active_stage = 0

if "selected_agent_view" not in st.session_state:
    st.session_state.selected_agent_view = "All Outputs"


# --------------------------------------------------
# Helpers & Real Metrics
# --------------------------------------------------
def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text or ""))


def extract_urls(text: str) -> list:
    raw = re.findall(r"https?://[^\s\)\]>\"']+", text or "")
    seen = []
    for u in raw:
        clean = u.rstrip(".,;:")
        if clean not in seen:
            seen.append(clean)
    return seen


def slugify(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", text.strip().lower()).strip("_") or "researchmind_report"


def compute_quality_score(metrics: dict, report: str, feedback: str) -> tuple[int, str]:
    """Extracts critic numeric score if present, otherwise computes a transparent quality index."""
    m = re.search(r"(\d{1,3})\s*/\s*(100|10)", feedback or "")
    if m:
        raw_val = int(m.group(1))
        scale = int(m.group(2))
        score = raw_val * 10 if scale == 10 else raw_val
        return min(max(score, 10), 100), "Critic Audited"

    pts = 55
    if metrics["writer_words"] >= 350:
        pts += 15
    elif metrics["writer_words"] >= 150:
        pts += 8
    if len(metrics["urls"]) >= 3:
        pts += 12
    elif len(metrics["urls"]) >= 1:
        pts += 6
    if len(re.findall(r"^#{1,3}\s+", report or "", flags=re.M)) >= 3:
        pts += 10
    if metrics["critic_words"] >= 40:
        pts += 8
    return min(pts, 98), "Composite Index"


def split_report_sections(report_md: str) -> list[tuple[str, str]]:
    lines = (report_md or "").splitlines()
    sections = []
    curr_title = "Executive Summary"
    curr_buf = []
    for line in lines:
        m = re.match(r"^(#{1,3})\s+(.+)$", line.strip())
        if m and len(m.group(1)) <= 2:
            if curr_buf and "\n".join(curr_buf).strip():
                sections.append((curr_title, "\n".join(curr_buf).strip()))
            curr_title = m.group(2).strip()
            curr_buf = []
        else:
            curr_buf.append(line)
    if curr_buf and "\n".join(curr_buf).strip():
        sections.append((curr_title, "\n".join(curr_buf).strip()))
    return sections or [("Complete Report", report_md or "")]


def render_square_header(active_stage: int, current_res: dict | None):
    motion_txt = f"Stage 0{active_stage} LIVE" if active_stage > 0 else "Motion: on"
    cta_href = "#sec-report" if current_res else "#sec-search"
    cta_text = "View Report" if current_res else "Start Search"

    st.markdown(
        '<div id="sec-top"></div>'
        '<div class="rm-sq-header">'
        '<a class="rm-pixel-logo" href="#sec-top">RESEARCH<span>MIND</span></a>'
        '<div class="rm-nav-links">'
        '<a class="rm-nav-link" href="#sec-agents">(Agents)</a>'
        '<a class="rm-nav-link" href="#sec-matrix">(Matrix)</a>'
        '<a class="rm-nav-link" href="#sec-search">(Search)</a>'
        '<a class="rm-nav-link" href="#sec-analytics">(Analytics)</a>'
        '<a class="rm-nav-link" href="#sec-report">(Report)</a>'
        '<a class="rm-nav-link" href="#sec-footer">(About)</a>'
        '</div>'
        '<div class="rm-hdr-right">'
        f'<div class="rm-motion-tag"><span class="green-led"></span>({motion_txt})</div>'
        f'<a class="rm-sq-cta" href="{cta_href}">{cta_text}</a>'
        '</div>'
        '</div>'
        '<div class="rm-scan-bar"></div>',
        unsafe_allow_html=True,
    )


def build_pattern_cards_html(metrics: dict) -> str:
    """4 square geometric pattern cards modeled directly after Reference Image 1."""
    t = metrics["timings"]
    cards = [
        {
            "name": "01 · Search",
            "sub": f"{metrics['search_words']}w · {t.get('Search', 0)}s",
            "bg": "#F9A8D4",
            "fg": "#EA580C",
            "svg": (
                '<defs><pattern id="p1" width="40" height="40" patternUnits="userSpaceOnUse">'
                '<rect width="40" height="40" fill="#F5B7F5"/>'
                '<path d="M16 6h8v10h10v8H24v10h-8V24H6v-8h10z" fill="#EA580C"/>'
                '</pattern></defs><rect width="100%" height="100%" fill="url(#p1)"/>'
            ),
        },
        {
            "name": "02 · Reader",
            "sub": f"{metrics['reader_words']}w · {t.get('Reader', 0)}s",
            "bg": "#2563EB",
            "fg": "#10B981",
            "svg": (
                '<defs><pattern id="p2" width="36" height="36" patternUnits="userSpaceOnUse">'
                '<rect width="36" height="36" fill="#2563EB"/>'
                '<rect x="4" y="4" width="28" height="28" fill="#10B981"/>'
                '</pattern></defs><rect width="100%" height="100%" fill="url(#p2)"/>'
            ),
        },
        {
            "name": "03 · Writer",
            "sub": f"{metrics['writer_words']}w · {t.get('Writer', 0)}s",
            "bg": "#FACC15",
            "fg": "#DC2626",
            "svg": (
                '<defs><pattern id="p3" width="36" height="36" patternUnits="userSpaceOnUse">'
                '<rect width="36" height="36" fill="#FACC15"/>'
                '<path d="M0 12h24v24h-8V20H0z M18 0h8v18h10v8H18z" fill="#EA580C"/>'
                '</pattern></defs><rect width="100%" height="100%" fill="url(#p3)"/>'
            ),
        },
        {
            "name": "04 · Critic",
            "sub": f"{metrics['critic_words']}w · {t.get('Critic', 0)}s",
            "bg": "#3B82F6",
            "fg": "#C084FC",
            "svg": (
                '<defs><pattern id="p4" width="32" height="32" patternUnits="userSpaceOnUse">'
                '<rect width="32" height="32" fill="#3B82F6"/>'
                '<rect x="0" y="0" width="16" height="16" fill="#A78BFA"/>'
                '<rect x="16" y="16" width="16" height="16" fill="#A78BFA"/>'
                '</pattern></defs><rect width="100%" height="100%" fill="url(#p4)"/>'
            ),
        },
    ]

    html_cards = '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;">'
    for c in cards:
        html_cards += (
            f'<div class="track-card">'
            f'<svg class="track-pattern" viewBox="0 0 240 155" preserveAspectRatio="none">{c["svg"]}</svg>'
            f'<div class="track-foot">'
            f'<span class="track-name">{c["name"]}</span>'
            f'<span class="track-meta">{c["sub"]}</span>'
            f'</div></div>'
        )
    html_cards += "</div>"
    return html_cards


def build_dynamic_matrix(metrics: dict, selected_filter: str) -> str:
    timings = metrics["timings"]
    stages = [
        ("Search", metrics["search_words"], timings.get("Search", 0), "#00FF88", "Web Search"),
        ("Reader", metrics["reader_words"], timings.get("Reader", 0), "#38BDF8", "HTML Scrape"),
        ("Writer", metrics["writer_words"], timings.get("Writer", 0), "#F59E0B", "Report Draft"),
        ("Critic", metrics["critic_words"], timings.get("Critic", 0), "#F472B6", "Quality Audit"),
    ]
    total_w = sum(s[1] for s in stages) or 1
    unit = max(15, math.ceil(total_w / 198))

    cells = ""
    idx = 0
    for name, words, secs, color, role in stages:
        count = max(2, round(words / unit)) if words > 0 else 0
        dimmed = selected_filter != "All" and selected_filter != name
        op = "0.14" if dimmed else "1"
        pct = round((words / total_w) * 100, 1)
        for sq_i in range(count):
            delay = min(idx * 0.004, 0.55)
            cells += (
                f'<div class="mx-cell" style="background:{color};opacity:{op};animation-delay:{delay:.3f}s;">'
                f'<div class="mx-tip">'
                f'<strong style="color:{color};">{name} Agent</strong> · {role}<br>'
                f'Block #{sq_i + 1} (~{unit} words) · Total: {words}w ({pct}%) · {secs}s'
                f'</div></div>'
            )
            idx += 1

    return (
        f'<div class="matrix-grid">{cells}</div>'
        f'<div class="fig-caption">'
        f'<span>HOVER ANY SQUARE FOR LIVE AGENT TELEMETRY · 1 SQUARE ≈ {unit} WORDS</span>'
        f'<span>'
        f'<span style="color:#00FF88;">■</span> Search &nbsp;'
        f'<span style="color:#38BDF8;">■</span> Reader &nbsp;'
        f'<span style="color:#F59E0B;">■</span> Writer &nbsp;'
        f'<span style="color:#F472B6;">■</span> Critic'
        f'</span></div>'
    )


def build_hover_pie_svg(rows: list[dict], metric_key: str, unit_lbl: str) -> str:
    cx, cy, r = 210, 210, 130
    circ = 2 * math.pi * r
    total = sum(row[metric_key] for row in rows) or 1

    slices = ""
    offset = 0.0
    for row in rows:
        val = row[metric_key]
        seg = (val / total) * circ
        pct = round((val / total) * 100, 1)
        slices += (
            f'<g class="pie-node">'
            f'<circle class="slice-ring" cx="{cx}" cy="{cy}" r="{r}" fill="none" '
            f'stroke="{row["color"]}" stroke-width="54" '
            f'stroke-dasharray="{seg:.2f} {circ:.2f}" '
            f'stroke-dashoffset="{-offset:.2f}" '
            f'transform="rotate(-90 {cx} {cy})"></circle>'
            f'<g class="pie-tip">'
            f'<rect x="115" y="168" width="190" height="84" fill="#000000" stroke="#00FF88" stroke-width="1.5"></rect>'
            f'<text x="210" y="194" text-anchor="middle" fill="{row["color"]}" font-size="13" font-weight="700">{row["stage"]}</text>'
            f'<text x="210" y="217" text-anchor="middle" fill="#FFFFFF" font-size="18" font-weight="700">{val} {unit_lbl}</text>'
            f'<text x="210" y="238" text-anchor="middle" fill="#00FF88" font-size="12">{pct}% SHARE · {row["seconds"]}s</text>'
            f'</g></g>'
        )
        offset += seg

    tot_str = f"{total:,}" if isinstance(total, int) else f"{total:.1f}"
    return (
        '<div class="svg-chart-wrap">'
        '<svg viewBox="0 0 420 420" style="width:100%;max-width:340px;height:auto;overflow:visible;">'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="54"></circle>'
        f'<text x="{cx}" y="{cy - 4}" text-anchor="middle" fill="#FFFFFF" font-size="30" font-weight="700">{tot_str}</text>'
        f'<text x="{cx}" y="{cy + 20}" text-anchor="middle" fill="#00FF88" font-size="11" letter-spacing="2">{unit_lbl} (HOVER SLICE)</text>'
        f'{slices}'
        '</svg></div>'
    )


def build_hover_line_svg(rows: list[dict], metric_key: str, unit_lbl: str) -> str:
    w, h = 580, 290
    pad_l, pad_r, pad_t, pad_b = 56, 45, 48, 48
    plot_w = w - pad_l - pad_r
    plot_h = h - pad_t - pad_b
    max_v = max(r[metric_key] for r in rows) or 1

    pts = []
    for i, r in enumerate(rows):
        x = pad_l + (i / max(len(rows) - 1, 1)) * plot_w
        y = pad_t + plot_h - (r[metric_key] / max_v) * plot_h
        pts.append((x, y, r))

    poly_str = " ".join(f"{x:.1f},{y:.1f}" for x, y, _ in pts)
    area_str = f"{pts[0][0]:.1f},{pad_t + plot_h:.1f} {poly_str} {pts[-1][0]:.1f},{pad_t + plot_h:.1f}"

    grid_lines = ""
    for g in range(5):
        gy = pad_t + (g / 4) * plot_h
        gval = round(max_v * (1 - g / 4), 1)
        grid_lines += (
            f'<line x1="{pad_l}" y1="{gy:.1f}" x2="{w - pad_r}" y2="{gy:.1f}" stroke="rgba(255,255,255,0.09)" stroke-dasharray="3 3"></line>'
            f'<text x="{pad_l - 8}" y="{gy + 4:.1f}" text-anchor="end" fill="#71717A" font-size="10">{gval}</text>'
        )

    nodes = ""
    for x, y, r in pts:
        tx = min(max(x - 68, 8), w - 144)
        ty = max(y - 64, 6)
        nodes += (
            f'<g class="pt-node">'
            f'<text x="{x:.1f}" y="{h - 16}" text-anchor="middle" fill="#D4D4D8" font-size="11" font-weight="600">{r["short"]}</text>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="22" fill="transparent"></circle>'
            f'<circle class="pt-dot" cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{r["color"]}" stroke="#000000" stroke-width="2"></circle>'
            f'<g class="pt-tip">'
            f'<rect x="{tx:.1f}" y="{ty:.1f}" width="136" height="46" fill="#000000" stroke="#00FF88" stroke-width="1.3"></rect>'
            f'<text x="{tx + 68:.1f}" y="{ty + 18:.1f}" text-anchor="middle" fill="{r["color"]}" font-size="11" font-weight="700">{r["stage"]}</text>'
            f'<text x="{tx + 68:.1f}" y="{ty + 36:.1f}" text-anchor="middle" fill="#FFFFFF" font-size="11">{r[metric_key]} {unit_lbl} · {r["seconds"]}s</text>'
            f'</g></g>'
        )

    return (
        '<div class="svg-chart-wrap">'
        f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:auto;overflow:visible;">'
        '<defs><linearGradient id="greenArea" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#00FF88" stop-opacity="0.32"/>'
        '<stop offset="100%" stop-color="#00FF88" stop-opacity="0.01"/>'
        '</linearGradient></defs>'
        f'{grid_lines}'
        f'<polygon points="{area_str}" fill="url(#greenArea)"></polygon>'
        f'<polyline points="{poly_str}" fill="none" stroke="#00FF88" stroke-width="3"></polyline>'
        f'{nodes}'
        '</svg></div>'
    )


def execute_pipeline(topic: str, header_slot) -> dict:
    timings = {}
    t_total = time.time()

    with st.status(f"RESEARCHMIND // Executing 4-agent pipeline for: **{topic}**", expanded=True) as status:
        # Stage 1
        st.session_state.active_stage = 1
        with header_slot.container():
            render_square_header(1, st.session_state.current_result)
        st.write("■ **[01] Search Agent** — Querying live sources...")
        t0 = time.time()
        search_agent = build_search_agent()
        search_result = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
        })
        search_text = search_result["messages"][-1].text
        timings["Search"] = round(time.time() - t0, 2)
        st.write(f"✓ Done in `{timings['Search']}s` · `{word_count(search_text)} words`")

        # Stage 2
        st.session_state.active_stage = 2
        with header_slot.container():
            render_square_header(2, st.session_state.current_result)
        st.write("■ **[02] Reader Agent** — Scraping top HTML URLs...")
        t0 = time.time()
        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke({
            "messages": [(
                "user",
                f"Based on the following search results about '{topic}', "
                f"pick ONLY the top 1 or 2 most relevant HTML article URLs (skip any .pdf links), "
                f"scrape them once, and summarize the key facts cleanly.\n\n"
                f"Search Results:\n{search_text[:3000]}"
            )]
        })
        scraped_text = reader_result["messages"][-1].text
        timings["Reader"] = round(time.time() - t0, 2)
        st.write(f"✓ Done in `{timings['Reader']}s` · `{word_count(scraped_text)} words`")

        # Stage 3
        st.session_state.active_stage = 3
        with header_slot.container():
            render_square_header(3, st.session_state.current_result)
        st.write("■ **[03] Writer Chain** — Drafting structured report...")
        t0 = time.time()
        research_combined = (
            f"SEARCH RESULTS:\n{search_text}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{scraped_text}"
        )
        report_text = writer_chain.invoke({
            "topic": topic,
            "research": research_combined,
        })
        timings["Writer"] = round(time.time() - t0, 2)
        st.write(f"✓ Done in `{timings['Writer']}s` · `{word_count(report_text)} words`")

        # Stage 4
        st.session_state.active_stage = 4
        with header_slot.container():
            render_square_header(4, st.session_state.current_result)
        st.write("■ **[04] Critic Chain** — Evaluating accuracy & score...")
        t0 = time.time()
        feedback_text = critic_chain.invoke({"report": report_text})
        timings["Critic"] = round(time.time() - t0, 2)
        st.write(f"✓ Done in `{timings['Critic']}s` · `{word_count(feedback_text)} words`")

        total_elapsed = round(time.time() - t_total, 2)
        st.session_state.active_stage = 0
        status.update(label=f"RESEARCHMIND // Completed in {total_elapsed}s", state="complete", expanded=False)

    metrics = {
        "search_words": word_count(search_text),
        "reader_words": word_count(scraped_text),
        "writer_words": word_count(report_text),
        "critic_words": word_count(feedback_text),
        "timings": timings,
        "total_time": total_elapsed,
        "urls": extract_urls(search_text),
    }
    score, score_src = compute_quality_score(metrics, report_text, feedback_text)
    metrics["score"] = score
    metrics["score_source"] = score_src

    return {
        "topic": topic,
        "search_results": search_text,
        "scraped_content": scraped_text,
        "report": report_text,
        "feedback": feedback_text,
        "timestamp": time.strftime("%H:%M:%S"),
        "metrics": metrics,
    }


# --------------------------------------------------
# 1. Square Header
# --------------------------------------------------
header_slot = st.empty()
with header_slot.container():
    render_square_header(st.session_state.active_stage, st.session_state.current_result)

current = st.session_state.current_result
active_metrics = (
    current["metrics"]
    if current
    else {
        "search_words": 460,
        "reader_words": 640,
        "writer_words": 980,
        "critic_words": 290,
        "timings": {"Search": 4.1, "Reader": 6.3, "Writer": 5.6, "Critic": 2.9},
        "total_time": 18.9,
        "urls": [],
        "score": 94,
        "score_source": "Blueprint Preview",
    }
)

# --------------------------------------------------
# Hero + 4 Geometric Square Agent Cards
# --------------------------------------------------
st.markdown(
    '<div id="sec-agents"></div>'
    '<div class="rm-hero-kicker">(01 — MULTI-AGENT ARCHITECTURE)</div>'
    '<div class="rm-hero-title">'
    '<span class="rm-mask"><span class="rm-slide rm-d1">Four agents. Pick one,</span></span>'
    '<span class="rm-mask"><span class="rm-slide rm-d2">or track the full pipeline.</span></span>'
    '</div>',
    unsafe_allow_html=True,
)
st.markdown(build_pattern_cards_html(active_metrics), unsafe_allow_html=True)

# --------------------------------------------------
# 2. Search Engine Bar + Boxed Quick Prompts
# --------------------------------------------------
st.markdown(
    '<div id="sec-search" class="sec-bar">'
    '<div class="sec-bar-title">02 // RESEARCH ENGINE TERMINAL</div>'
    '<div class="sec-bar-code">SEARCH → READER → WRITER → CRITIC</div>'
    '</div>',
    unsafe_allow_html=True,
)

with st.form("rm_search_bar", clear_on_submit=True):
    s_in, s_btn = st.columns([5.3, 1.3])
    with s_in:
        query_input = st.text_input(
            "Search Query",
            placeholder="> Enter research topic (e.g., Agentic AI Workflows in 2026)...",
            label_visibility="collapsed",
        )
    with s_btn:
        run_clicked = st.form_submit_button("RUN PIPELINE →", use_container_width=True, type="primary")

q_cols = st.columns(4)
quick_topics = [
    "Agentic AI in 2026",
    "Solid-State Batteries",
    "Quantum Error Correction",
    "Autonomous Robotics",
]
clicked_quick = None
for i, qt in enumerate(quick_topics):
    if q_cols[i].button(f"[+] {qt}", use_container_width=True):
        clicked_quick = qt

target_topic = clicked_quick or (query_input if run_clicked else None)
if target_topic and target_topic.strip():
    cleaned_topic = target_topic.strip()
    try:
        res = execute_pipeline(cleaned_topic, header_slot)
        st.session_state.current_result = res
        st.session_state.history.append(res)
        st.session_state.selected_agent_view = "All Outputs"
        st.rerun()
    except Exception as e:
        st.session_state.active_stage = 0
        st.error(f"Pipeline execution error: {e}")
        with st.expander("Inspect Error Traceback"):
            st.exception(e)


# --------------------------------------------------
# 3. Dynamic Box Matrix (Fills on Search + Hover Info)
# --------------------------------------------------
st.markdown(
    '<div id="sec-matrix" class="sec-bar">'
    '<div class="sec-bar-title">03 // DYNAMIC AGENT MATRIX</div>'
    f'<div class="sec-bar-code">{"LIVE EXECUTION DATA" if current else "SAMPLE BLUEPRINT"}</div>'
    '</div>',
    unsafe_allow_html=True,
)

matrix_filter = st.radio(
    "Filter Matrix Stage",
    ["All", "Search", "Reader", "Writer", "Critic"],
    horizontal=True,
    label_visibility="collapsed",
)
st.markdown(
    f'<div class="sq-box">{build_dynamic_matrix(active_metrics, matrix_filter)}</div>',
    unsafe_allow_html=True,
)


# --------------------------------------------------
# 4. Data Analytics: Hoverable Pie Chart + Line Chart + Data Table
# --------------------------------------------------
st.markdown(
    '<div id="sec-analytics" class="sec-bar">'
    '<div class="sec-bar-title">04 // DATA ANALYTICS & TELEMETRY</div>'
    '<div class="sec-bar-code">INTERACTIVE PIE · LINE · DATA TABLE</div>'
    '</div>',
    unsafe_allow_html=True,
)

t_map = active_metrics["timings"]
rows_data = [
    {"stage": "Search Agent", "short": "01 Search", "role": "Web Discovery", "words": active_metrics["search_words"], "seconds": t_map.get("Search", 0), "color": "#00FF88"},
    {"stage": "Reader Agent", "short": "02 Reader", "role": "HTML Scraping", "words": active_metrics["reader_words"], "seconds": t_map.get("Reader", 0), "color": "#38BDF8"},
    {"stage": "Writer Chain", "short": "03 Writer", "role": "Report Draft", "words": active_metrics["writer_words"], "seconds": t_map.get("Writer", 0), "color": "#F59E0B"},
    {"stage": "Critic Chain", "short": "04 Critic", "role": "Quality Audit", "words": active_metrics["critic_words"], "seconds": t_map.get("Critic", 0), "color": "#F472B6"},
]

analytic_metric = st.radio(
    "Analytics Metric",
    ["Output Words", "Execution Time (s)"],
    horizontal=True,
    label_visibility="collapsed",
)
m_key, m_unit = ("words", "WORDS") if analytic_metric == "Output Words" else ("seconds", "SEC")

ch_pie, ch_line = st.columns(2, gap="large")
with ch_pie:
    st.markdown(
        f'<div class="sq-box">'
        f'<div style="font-family:JetBrains Mono,monospace;font-size:0.76rem;color:#00FF88;margin-bottom:0.4rem;">FIG. 02 // PIE DISTRIBUTION ({analytic_metric.upper()})</div>'
        f'{build_hover_pie_svg(rows_data, m_key, m_unit)}'
        f'</div>',
        unsafe_allow_html=True,
    )

with ch_line:
    st.markdown(
        f'<div class="sq-box">'
        f'<div style="font-family:JetBrains Mono,monospace;font-size:0.76rem;color:#00FF88;margin-bottom:0.4rem;">FIG. 03 // STAGE LINE TRAJECTORY (HOVER NODES)</div>'
        f'{build_hover_line_svg(rows_data, m_key, m_unit)}'
        f'</div>',
        unsafe_allow_html=True,
    )

# Square Data Table + Raster 3-Column Agent Overview (Reference Image 2 Style)
tot_words = sum(r["words"] for r in rows_data) or 1
tot_secs = sum(r["seconds"] for r in rows_data) or 1
tr_rows = ""
for r in rows_data:
    w_pct = round((r["words"] / tot_words) * 100, 1)
    s_pct = round((r["seconds"] / tot_secs) * 100, 1)
    rate = round(r["words"] / max(r["seconds"], 0.1), 1)
    tr_rows += (
        f'<tr>'
        f'<td><span style="display:inline-block;width:10px;height:10px;background:{r["color"]};margin-right:8px;"></span><strong>{r["stage"]}</strong></td>'
        f'<td>{r["role"]}</td>'
        f'<td>{r["words"]:,} ({w_pct}%)</td>'
        f'<td>{r["seconds"]}s ({s_pct}%)</td>'
        f'<td>{rate} w/s</td>'
        f'</tr>'
    )

st.markdown(
    f'<div class="sq-box" style="margin-top:1rem;">'
    f'<div style="font-family:JetBrains Mono,monospace;font-size:0.76rem;color:#00FF88;margin-bottom:0.6rem;">FIG. 04 // COMPLETE PIPELINE DATA TABLE</div>'
    f'<table class="sq-table">'
    f'<thead><tr><th>Agent</th><th>Function</th><th>Words Generated</th><th>Latency</th><th>Throughput</th></tr></thead>'
    f'<tbody>{tr_rows}</tbody>'
    f'</table>'
    f'</div>',
    unsafe_allow_html=True,
)


# --------------------------------------------------
# 5. Complete Sectioned Report + Score + Clickable Agent Boxed Buttons + Download
# --------------------------------------------------
st.markdown(
    '<div id="sec-report" class="sec-bar">'
    '<div class="sec-bar-title">05 // COMPLETE REPORT & AGENT INSPECTOR</div>'
    f'<div class="sec-bar-code">SCORE: {active_metrics["score"]}/100 ({active_metrics["score_source"]})</div>'
    '</div>',
    unsafe_allow_html=True,
)

if current:
    # Score + KPI Banner + Download
    sc1, sc2, sc3, sc4 = st.columns([1.1, 1.1, 1.1, 1.2])
    sc1.markdown(f'<div class="sq-box"><div style="font-size:0.72rem;color:#A1A1AA;">QUALITY SCORE</div><div style="font-size:1.9rem;font-weight:700;color:#00FF88;">{active_metrics["score"]}/100</div></div>', unsafe_allow_html=True)
    sc2.markdown(f'<div class="sq-box"><div style="font-size:0.72rem;color:#A1A1AA;">TOTAL LATENCY</div><div style="font-size:1.9rem;font-weight:700;color:#FFFFFF;">{active_metrics["total_time"]}s</div></div>', unsafe_allow_html=True)
    sc3.markdown(f'<div class="sq-box"><div style="font-size:0.72rem;color:#A1A1AA;">SOURCES FOUND</div><div style="font-size:1.9rem;font-weight:700;color:#38BDF8;">{len(active_metrics["urls"])} URLs</div></div>', unsafe_allow_html=True)
    with sc4:
        full_md = (
            f"# {current['topic']}\n"
            f"**Quality Score:** {active_metrics['score']}/100 ({active_metrics['score_source']})\n\n"
            f"## Final Report\n\n{current['report']}\n\n"
            f"---\n\n## Critic Feedback\n\n{current['feedback']}\n\n"
            f"---\n\n## Reader Synthesis\n\n{current['scraped_content']}\n"
        )
        st.download_button(
            "↓ DOWNLOAD REPORT (.MD)",
            data=full_md,
            file_name=f"{slugify(current['topic'])}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Boxed Buttons on Report to Click Any Agent & Inspect Its Info
    btn_labels = [
        ("All Outputs", "[■ ALL OUTPUTS]"),
        ("Writer Chain", "[03 WRITER REPORT]"),
        ("Critic Chain", "[04 CRITIC SCORE & AUDIT]"),
        ("Reader Agent", "[02 READER SCRAPE]"),
        ("Search Agent", "[01 SEARCH & URLS]"),
    ]
    b_cols = st.columns(len(btn_labels))
    for i, (key, lbl) in enumerate(btn_labels):
        if b_cols[i].button(lbl, key=f"ag_btn_{i}", use_container_width=True):
            st.session_state.selected_agent_view = key

    view = st.session_state.selected_agent_view

    if view in ("All Outputs", "Writer Chain"):
        st.markdown(f'<div style="font-family:JetBrains Mono,monospace;color:#00FF88;margin:0.8rem 0 0.4rem 0;">[03 // WRITER CHAIN — COMPLETE REPORT · {active_metrics["writer_words"]} WORDS · {t_map.get("Writer", 0)}s]</div>', unsafe_allow_html=True)
        for idx, (sec_t, sec_b) in enumerate(split_report_sections(current["report"]), start=1):
            with st.container(border=True):
                st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:0.86rem;color:#00FF88;margin-bottom:0.4rem;">SEC {idx:02d} // {html.escape(sec_t)}</div>', unsafe_allow_html=True)
                st.markdown(sec_b)

    if view in ("All Outputs", "Critic Chain"):
        st.markdown(f'<div style="font-family:JetBrains Mono,monospace;color:#F472B6;margin:1rem 0 0.4rem 0;">[04 // CRITIC CHAIN — AUDIT & SCORE ({active_metrics["score"]}/100) · {t_map.get("Critic", 0)}s]</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(current["feedback"])

    if view in ("All Outputs", "Reader Agent"):
        st.markdown(f'<div style="font-family:JetBrains Mono,monospace;color:#38BDF8;margin:1rem 0 0.4rem 0;">[02 // READER AGENT — SCRAPED ARTICLE FACTS · {active_metrics["reader_words"]} WORDS · {t_map.get("Reader", 0)}s]</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(current["scraped_content"])

    if view in ("All Outputs", "Search Agent"):
        st.markdown(f'<div style="font-family:JetBrains Mono,monospace;color:#00FF88;margin:1rem 0 0.4rem 0;">[01 // SEARCH AGENT — SOURCES & RESULTS · {len(active_metrics["urls"])} URLS · {t_map.get("Search", 0)}s]</div>', unsafe_allow_html=True)
        with st.container(border=True):
            if active_metrics["urls"]:
                st.markdown("**Verified URLs Discovered:**")
                for u in active_metrics["urls"]:
                    st.markdown(f"- [{u}]({u})")
                st.divider()
            st.markdown(current["search_results"])

    if len(st.session_state.history) > 1:
        st.markdown('<div style="font-family:JetBrains Mono,monospace;color:#00FF88;margin:1.2rem 0 0.5rem 0;">[SAVED SESSION RUNS]</div>', unsafe_allow_html=True)
        for idx, item in enumerate(reversed(st.session_state.history)):
            hc1, hc2 = st.columns([4.5, 1])
            hc1.markdown(f"**{item['topic']}** · Score `{item['metrics']['score']}/100` · `{item['metrics']['total_time']}s` · *{item['timestamp']}*")
            if hc2.button("LOAD", key=f"load_run_{idx}", use_container_width=True):
                st.session_state.current_result = item
                st.rerun()
else:
    with st.container(border=True):
        st.markdown("Run any topic in **Section 02** above to generate a complete sectioned report, quality score, agent breakdown, and `.md` export.")


# --------------------------------------------------
# 6. Project Quotes + Proper Square Footer (Image 2 Style)
# --------------------------------------------------
st.markdown(
    '<div class="quote-box">'
    '<div class="quote-text">“Four specialized autonomous agents—searching live sources, scraping primary articles, drafting structured synthesis, and auditing every claim—united inside one real-time telemetry workspace.”</div>'
    '<div class="quote-sub">// WHAT WE BUILT IN RESEARCHMIND · SEARCH → READER → WRITER → CRITIC</div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div id="sec-footer" class="rm-sq-footer">'
    '<div class="rm-f-top">'
    '<div>'
    '<div class="rm-f-big-title">RESEARCH<span>MIND</span></div>'
    '<div class="rm-f-quote">'
    '“Turning raw web noise into verified, sectioned intelligence—measured line by line, second by second.”'
    '</div>'
    '<a class="rm-sq-cta" href="#sec-top">(↑ Top)</a>'
    '</div>'
    '<div class="raster-grid-3">'
    '<div class="raster-cell">'
    '<div class="r-time">STAGE 01 · WEB</div>'
    '<div class="r-title">Search Agent <span class="r-tag" style="background:#00FF88;">Search</span></div>'
    '<a class="rm-nav-link" href="#sec-search">(Launch Query)</a>'
    '</div>'
    '<div class="raster-cell">'
    '<div class="r-time">STAGE 02 · HTML</div>'
    '<div class="r-title">Reader Agent <span class="r-tag" style="background:#38BDF8;">Reader</span></div>'
    '<a class="rm-nav-link" href="#sec-matrix">(Inspect Matrix)</a>'
    '</div>'
    '<div class="raster-cell">'
    '<div class="r-time">STAGE 03 · SYNTHESIS</div>'
    '<div class="r-title">Writer Chain <span class="r-tag" style="background:#F59E0B;">Writer</span></div>'
    '<a class="rm-nav-link" href="#sec-report">(Read Report)</a>'
    '</div>'
    '<div class="raster-cell">'
    '<div class="r-time">STAGE 04 · AUDIT</div>'
    '<div class="r-title">Critic Chain <span class="r-tag" style="background:#F472B6;">Critic</span></div>'
    '<a class="rm-nav-link" href="#sec-analytics">(View Score)</a>'
    '</div>'
    '<div class="raster-cell">'
    '<div class="r-time">ANALYTICS · SVG</div>'
    '<div class="r-title">Pie &amp; Line Telemetry <span class="r-tag" style="background:#A78BFA;">Charts</span></div>'
    '<a class="rm-nav-link" href="#sec-analytics">(Open Graphs)</a>'
    '</div>'
    '<div class="raster-cell">'
    '<div class="r-time">ENGINE · PYTHON</div>'
    f'<div class="r-title">Session Runs: {len(st.session_state.history)} <span class="r-tag" style="background:#00FF88;">Live</span></div>'
    '<a class="rm-nav-link" href="#sec-top">(Back to Header)</a>'
    '</div>'
    '</div>'
    '</div>'
    '<div class="rm-f-bottom">'
    '<span>RESEARCHMIND // MULTI-AGENT AUTONOMOUS RESEARCH SYSTEM</span>'
    f'<span>(FULL PIPELINE) · BUILT WITH STREAMLIT &amp; LANGCHAIN · {time.strftime("%Y")}</span>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)