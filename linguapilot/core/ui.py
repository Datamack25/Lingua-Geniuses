"""Thème visuel et composants d'interface réutilisables."""
from __future__ import annotations
import html
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');
:root{--navy:#14213D;--teal:#0E7490;--gold:#C9A227;--ink:#1F2937;--muted:#6B7280;--card:#FFFFFF;--line:#E7E5DF;--bg:#F8F7F2;}
html, body, [class*="css"], .stMarkdown, .stButton button, input, textarea { font-family:'Plus Jakarta Sans', system-ui, sans-serif !important; }
.stApp { background: var(--bg); }
.block-container { padding-top: 1.6rem; max-width: 1250px; }
h1, h2, h3 { font-family:'Fraunces', Georgia, serif !important; color: var(--navy); letter-spacing:-.01em; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg,#14213D 0%,#1B2E52 100%); }
section[data-testid="stSidebar"] * { color:#EEF2FF !important; }
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div { background:rgba(255,255,255,.08); border-color:rgba(255,255,255,.2); }
section[data-testid="stSidebar"] [role="radiogroup"] label { padding:6px 10px; border-radius:10px; margin-bottom:2px; }
section[data-testid="stSidebar"] [role="radiogroup"] label:hover { background:rgba(255,255,255,.08); }
.stButton > button { border-radius: 999px; font-weight: 700; border: 1px solid var(--line); padding:.45rem 1.1rem; }
.stButton > button[kind="primary"] { background: var(--teal); border-color: var(--teal); }
.stButton > button[kind="primary"]:hover { background:#0B5E75; border-color:#0B5E75; }
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] { background:#fff; border:1px solid var(--line); border-radius:999px; padding:6px 16px; height:auto; }
.stTabs [aria-selected="true"] { background: var(--navy) !important; color:#fff !important; }
div[data-testid="stMetric"] { background:#fff; border:1px solid var(--line); border-radius:16px; padding:14px 16px; }
.hero { background: radial-gradient(1200px 300px at 10% -20%, rgba(201,162,39,.35), transparent),
        linear-gradient(135deg,#14213D 0%,#0E7490 100%); color:#fff; border-radius:22px; padding:28px 32px; margin-bottom:18px; }
.hero h1 { color:#fff; margin:0 0 6px; font-size:2.1rem; }
.hero p { color:#E0F2FE; margin:0; font-size:1.02rem; }
.card { background:var(--card); border:1px solid var(--line); border-radius:18px; padding:18px 20px; height:100%;
        box-shadow: 0 1px 2px rgba(20,33,61,.04); }
.card h4 { margin:0 0 6px; font-family:'Fraunces',serif; color:var(--navy); font-size:1.15rem; }
.card p { color: var(--muted); margin: 0; font-size:.93rem; }
.agent { border-top: 5px solid var(--c); }
.agent .em { font-size: 1.9rem; }
.tag { display:inline-block; padding:3px 10px; border-radius:999px; font-size:.75rem; font-weight:700; margin:2px 4px 2px 0;
       background:#EEF2FF; color:#3730A3; }
.tag.gold { background:#FEF3C7; color:#92400E; } .tag.teal { background:#CFFAFE; color:#155E75; }
.tag.green { background:#D1FAE5; color:#065F46; } .tag.pink { background:#FCE7F3; color:#9D174D; }
.lvl { display:inline-flex; align-items:center; justify-content:center; width:74px; height:74px; border-radius:50%;
       background:var(--navy); color:#fff; font-weight:800; font-size:1.6rem; border:5px solid var(--gold); }
.qcard { background:#fff; border:1px solid var(--line); border-radius:20px; padding:22px 26px; margin:8px 0 14px; }
.qcard .q { font-size:1.25rem; font-weight:700; color:var(--navy); }
.feedback-ok { background:#ECFDF5; border:1px solid #A7F3D0; color:#065F46; padding:12px 16px; border-radius:14px; }
.feedback-ko { background:#FFF7ED; border:1px solid #FED7AA; color:#9A3412; padding:12px 16px; border-radius:14px; }
.res { display:flex; gap:10px; align-items:flex-start; padding:10px 0; border-bottom:1px dashed var(--line); }
.res a { font-weight:700; color:var(--teal); text-decoration:none; } .res a:hover { text-decoration:underline; }
.res small { color: var(--muted); }
.quest { display:flex; justify-content:space-between; align-items:center; padding:9px 12px; border-radius:12px; background:#fff;
         border:1px solid var(--line); margin-bottom:6px; }
.quest.done { background:#ECFDF5; border-color:#A7F3D0; }
.notif { background:#fff; border:1px solid var(--line); border-left:5px solid var(--gold); border-radius:12px; padding:12px 16px; margin-bottom:8px; }
.notif.read { opacity:.6; border-left-color: var(--line); }
.badge { text-align:center; background:#fff; border:1px solid var(--line); border-radius:16px; padding:14px 6px; }
.badge .i { font-size:2rem; } .badge.off { filter: grayscale(1); opacity:.35; }
.xpbar { height:8px; background:rgba(255,255,255,.18); border-radius:8px; overflow:hidden; }
.xpbar i { display:block; height:100%; background: var(--gold); }
.small { color:var(--muted); font-size:.85rem; }
footer { visibility: hidden; }
</style>
"""


def inject():
    st.markdown(CSS, unsafe_allow_html=True)


def esc(s) -> str:
    return html.escape(str(s))


def hero(title: str, subtitle: str):
    st.markdown(f'<div class="hero"><h1>{esc(title)}</h1><p>{esc(subtitle)}</p></div>', unsafe_allow_html=True)


def card(title: str, body: str, extra: str = ""):
    st.markdown(f'<div class="card"><h4>{esc(title)}</h4><p>{esc(body)}</p>{extra}</div>', unsafe_allow_html=True)


def agent_card(a):
    tags = "".join(f'<span class="tag">{esc(s)}</span>' for s in (a.skills or [a.title]))
    st.markdown(f'<div class="card agent" style="--c:{a.color}"><div class="em">{a.emoji}</div>'
                f'<h4>{esc(a.name)} · <span style="font-family:Plus Jakarta Sans;font-size:.9rem;color:{a.color}">{esc(a.title)}</span></h4>'
                f'<p>{esc(a.mission)}</p><div style="margin-top:8px">{tags}</div></div>', unsafe_allow_html=True)


def agent_banner(a, text: str):
    st.markdown(f'<div class="card agent" style="--c:{a.color};margin-bottom:14px"><span class="em">{a.emoji}</span> '
                f'<b style="color:{a.color}">{esc(a.name)}</b> — <span class="small">{esc(a.title)}</span>'
                f'<p style="margin-top:6px">{esc(text)}</p></div>', unsafe_allow_html=True)


def resource_list(df):
    icons = {"vidéo": "🎬", "audio": "🎧", "site": "🌐", "guide": "📘", "discours": "🎤", "outil": "🛠️",
             "dictionnaire": "📖", "lecture": "📰", "cours": "🎓", "archives": "🗄️", "annuaire": "🗂️"}
    out = ""
    for _, r in df.iterrows():
        out += (f'<div class="res"><span style="font-size:1.3rem">{icons.get(r.type, "🔗")}</span><div>'
                f'<a href="{esc(r.url)}" target="_blank">{esc(r.titre)}</a><br>'
                f'<small>{esc(r.description)} · dès {esc(r.level_min)} · {esc(r.skill)}</small></div></div>')
    st.markdown(out or '<p class="small">Aucune ressource.</p>', unsafe_allow_html=True)


def level_badge(level: str, label: str, usage: str):
    st.markdown(f'<div style="display:flex;gap:16px;align-items:center"><div class="lvl">{esc(level)}</div>'
                f'<div><div style="font-weight:800;font-size:1.15rem;color:#14213D">{esc(label)}</div>'
                f'<div class="small">{esc(usage)}</div></div></div>', unsafe_allow_html=True)
