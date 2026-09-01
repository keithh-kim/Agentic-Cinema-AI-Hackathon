import os
from dotenv import load_dotenv
from engine import scout_scene
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="CineScout — Production Coordinator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()

# ============================================================
# DESIGN SYSTEM — "Continuity Binder"
# ============================================================
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Courier+Prime:wght@400;700&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

    :root{
        --paper:#EFEAE0;
        --card:#FBF9F4;
        --ink:#1C1A17;
        --ink-soft:#6b6459;
        --rule:#D9D2C2;
        --red:#A8382C;
        --red-bg:#F6E9E6;
        --green:#2F6F4E;
        --green-bg:#E7EFE7;
        --blue:#33506C;
        --blue-bg:#E7ECEF;
    }

    /* ---------- Base canvas ---------- */
    .stApp{
        background-color:var(--paper);
        background-image:
            repeating-linear-gradient(0deg, rgba(28,26,23,0.025) 0px, rgba(28,26,23,0.025) 1px, transparent 1px, transparent 3px);
        color:var(--ink);
        font-family:'IBM Plex Sans', sans-serif;
    }
    h1,h2,h3,h4,h5{
        font-family:'Bebas Neue', sans-serif !important;
        letter-spacing:.03em !important;
        color:var(--ink) !important;
        font-weight:400 !important;
    }
    code, .stCode, pre, .mono{
        font-family:'Courier Prime', monospace !important;
    }

    /* Body copy Streamlit renders as markdown paragraphs, captions, etc.
       Scoped to the main content block only — never the whole DOM — so it
       can't fight with button/badge/select rules that need other colors. */
    [data-testid="stAppViewContainer"] p,
    [data-testid="stAppViewContainer"] li,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stCaptionContainer"]{
        color:var(--ink);
    }

    /* ---------- Widget labels (the question text above every input) ----------
       This is the actual cause of the invisible-label bug: Streamlit's own
       theme colors these independently of body text, so they need their
       own explicit rule rather than relying on a blanket div/span override. */
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label,
    [data-testid="stWidgetLabel"]{
        color:var(--ink-soft) !important;
        font-family:'Courier Prime', monospace !important;
        font-size:.82rem !important;
        opacity:1 !important;
    }

    /* ---------- Slate header ---------- */
    .clapper-bar{
        height:16px;
        background:repeating-linear-gradient(-45deg, var(--ink) 0 22px, #f2efe7 22px 44px);
        margin:0 0 22px 0;
        border:1px solid var(--ink);
    }
    .slate-title{
        font-family:'Bebas Neue', sans-serif;
        font-size:3.4rem;
        line-height:1;
        letter-spacing:.04em;
        margin:0 0 4px 0;
        color:var(--ink);
    }
    .slate-meta{
        font-family:'Courier Prime', monospace;
        font-size:.85rem;
        color:var(--ink-soft);
        border-top:1px dashed var(--rule);
        padding-top:8px;
        margin-top:6px;
        display:flex;
        gap:28px;
        flex-wrap:wrap;
    }
    .slate-meta b{ color:var(--ink); }

    /* ---------- Sidebar: binder spine ---------- */
    [data-testid="stSidebar"]{
        background-color:#E3DCC9;
        border-right:2px solid var(--ink);
        background-image: radial-gradient(circle, rgba(28,26,23,0.35) 2.5px, transparent 2.6px);
        background-size: 100% 46px;
        background-position: 14px 10px;
    }
    [data-testid="stSidebar"] > div{ padding-left:14px; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3{
        font-family:'Bebas Neue', sans-serif !important;
        letter-spacing:.05em;
        color:var(--ink) !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"]{
        color:var(--ink) !important;
    }
    [data-testid="stSidebar"] hr{ border-color:var(--ink); opacity:.25; }

    /* ---------- Rubber-stamp badges ---------- */
    .stamp{
        display:inline-block;
        font-family:'Courier Prime', monospace;
        font-weight:700;
        font-size:.72rem;
        letter-spacing:.08em;
        text-transform:uppercase;
        padding:3px 10px;
        border:2px solid currentColor;
        border-radius:3px;
        transform:rotate(-2deg);
        background:transparent;
    }
    .stamp-live{ color:var(--green); }
    .stamp-offline{ color:var(--red); }
    .stamp-score{
        font-family:'Courier Prime', monospace;
        font-weight:700;
        font-size:.72rem;
        letter-spacing:.04em;
        padding:3px 9px;
        background:var(--ink);
        color:var(--card);
        border-radius:2px;
        transform:rotate(1deg);
        display:inline-block;
    }

    /* ---------- Index cards ---------- */
    .sheet{
        background:var(--card);
        border:1px solid var(--ink);
        border-radius:2px;
        padding:22px 22px 18px 22px;
        margin-bottom:18px;
        position:relative;
        box-shadow:3px 3px 0 rgba(28,26,23,0.08);
        color:var(--ink);
    }
    .sheet::before{
        content:attr(data-tab);
        position:absolute;
        top:-13px; left:18px;
        font-family:'Courier Prime', monospace;
        font-size:.68rem;
        letter-spacing:.1em;
        text-transform:uppercase;
        background:var(--ink);
        color:var(--card);
        padding:3px 10px;
        border-radius:2px;
    }
    .sheet--venue{ border-left:5px solid var(--green); }
    .sheet--venue::before{ background:var(--green); }
    .sheet--permit{ border-left:5px solid var(--red); }
    .sheet--permit::before{ background:var(--red); }
    .sheet--logistics{ border-left:5px solid var(--blue); }
    .sheet--logistics::before{ background:var(--blue); }

    .sheet-num{
        font-family:'Courier Prime', monospace;
        font-weight:700;
        color:var(--ink-soft);
        font-size:.85rem;
        margin-right:8px;
    }
    .sheet h4{
        font-family:'IBM Plex Sans', sans-serif !important;
        font-weight:700 !important;
        font-size:1.05rem !important;
        letter-spacing:0 !important;
        margin:2px 0 6px 0 !important;
        display:inline;
        color:var(--ink) !important;
    }
    .sheet .addr{
        font-family:'Courier Prime', monospace;
        font-size:.82rem;
        color:var(--ink-soft);
        margin:2px 0 10px 0;
    }
    .sheet .feat-label{
        font-family:'Courier Prime', monospace;
        font-size:.72rem;
        text-transform:uppercase;
        letter-spacing:.08em;
        color:var(--ink-soft);
        margin-top:10px;
        border-top:1px dashed var(--rule);
        padding-top:8px;
    }
    .sheet ul{ margin:6px 0 4px 0; padding-left:18px; }
    .sheet li{ font-size:.9rem; margin-bottom:2px; color:var(--ink); }
    .sheet a.src-link{
        display:inline-block;
        margin-top:10px;
        font-family:'Courier Prime', monospace;
        font-size:.8rem;
        font-weight:700;
        text-decoration:none;
        border-bottom:2px solid currentColor;
        padding-bottom:1px;
    }
    .sheet--venue a.src-link{ color:var(--green); }
    .sheet--permit a.src-link{ color:var(--red); }

    .permit-meta{
        display:flex; gap:24px; margin:8px 0 4px 0;
        font-family:'Courier Prime', monospace; font-size:.82rem;
        color:var(--ink);
    }
    .permit-meta b{ display:block; font-size:.68rem; text-transform:uppercase; letter-spacing:.06em; color:var(--ink-soft); font-weight:700; }

    .advisory{ color:var(--red); font-weight:600; margin-top:6px; }
    .mitigation{ color:var(--green); font-weight:600; margin-top:4px; }

    /* ---------- Text area ---------- */
    .stTextArea textarea{
        background:var(--card) !important;
        border:1px solid var(--ink) !important;
        border-radius:2px !important;
        color:var(--ink) !important;
        font-family:'Courier Prime', monospace !important;
    }
    .stTextArea textarea:focus{
        box-shadow:0 0 0 2px var(--ink) !important;
    }

    /* ---------- Text input (custom city box) ---------- */
    .stTextInput input{
        background:var(--card) !important;
        border:1px solid var(--ink) !important;
        border-radius:2px !important;
        color:var(--ink) !important;
    }
    .stTextInput input::placeholder{ color:var(--ink-soft) !important; opacity:1 !important; }

    /* ---------- Select box: closed control ----------
       Streamlit/BaseWeb renders the visible closed dropdown as nested divs
       under [data-baseweb="select"] — background AND text/icon color both
       need to be forced here, or Streamlit's dark-theme default shows through. */
    div[data-baseweb="select"] > div{
        background-color:var(--card) !important;
        border:1px solid var(--ink) !important;
        border-radius:2px !important;
        color:var(--ink) !important;
    }
    div[data-baseweb="select"] span{
        color:var(--ink) !important;
        font-family:'Courier Prime', monospace !important;
    }
    div[data-baseweb="select"] svg{
        fill:var(--ink) !important;
    }

    /* ---------- Select box: open dropdown menu ---------- */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] ul,
    div[data-baseweb="menu"]{
        background-color:var(--card) !important;
        border:1px solid var(--ink) !important;
        border-radius:2px !important;
    }
    div[data-baseweb="popover"] li{
        background-color:var(--card) !important;
        color:var(--ink) !important;
        font-family:'Courier Prime', monospace !important;
    }
    div[data-baseweb="popover"] li:hover{
        background-color:var(--rule) !important;
    }

    /* ---------- Buttons ---------- */
    .stButton>button{
        background-color:var(--ink) !important;
        border:2px solid var(--ink) !important;
        border-radius:2px !important;
        padding:12px 24px !important;
        box-shadow:3px 3px 0 rgba(28,26,23,0.35) !important;
        transition:transform .1s ease, box-shadow .1s ease !important;
    }
    .stButton>button p, .stButton>button span, .stButton>button div{
        color:var(--card) !important;
        font-family:'Courier Prime', monospace !important;
        font-weight:700 !important;
        letter-spacing:.08em !important;
        text-transform:uppercase;
        font-size:.85rem !important;
    }
    .stButton>button:hover{
        transform:translate(2px,2px) !important;
        box-shadow:1px 1px 0 rgba(28,26,23,0.35) !important;
    }

    .stDownloadButton>button{
        background-color:var(--card) !important;
        color:var(--ink) !important;
        font-family:'Courier Prime', monospace !important;
        font-weight:700 !important;
        letter-spacing:.06em !important;
        border:2px solid var(--ink) !important;
        border-radius:2px !important;
        box-shadow:3px 3px 0 rgba(28,26,23,0.2) !important;
    }
    .stDownloadButton>button p, .stDownloadButton>button span{
        color:var(--ink) !important;
    }

    /* ---------- Tabs ---------- */
    .stTabs [data-baseweb="tab-list"]{
        gap:4px;
        border-bottom:2px solid var(--ink);
    }
    .stTabs [data-baseweb="tab"]{
        border-radius:3px 3px 0 0;
        padding:9px 16px;
        background:var(--rule);
        border:1px solid var(--ink);
        border-bottom:none;
    }
    .stTabs [data-baseweb="tab"] p{
        font-family:'Courier Prime', monospace !important;
        font-size:.82rem !important;
        letter-spacing:.04em !important;
        text-transform:uppercase !important;
        color:var(--ink-soft) !important;
    }
    .stTabs [aria-selected="true"]{
        background:var(--ink) !important;
    }
    .stTabs [aria-selected="true"] p{
        color:var(--card) !important;
    }

    /* ---------- Alerts (error / success) ---------- */
    [data-testid="stAlert"] p{
        color:var(--ink) !important;
    }

    /* ---------- Section rule ---------- */
    .rule{ border:none; border-top:1px dashed var(--rule); margin:26px 0; }
</style>
""",
    unsafe_allow_html=True,
)

# Demo Scenes
PRESET_SCENES = {
    "Nairobi Cyberpunk Rooftop": """EXT. ROOFTOP - NIGHT

Heavy rain slickens the concrete deck. Giant holographic advertisements cast violent neon pink and cyan light across KIKO (30s), wearing a high-collared techwear trench coat.

Kiko checks his arm-mounted comms deck. Rain drops hit the lens. Down below, the Nairobi skyline buzzes with high-altitude drone deliveries.

KIKO
(into comms)
I'm on the roof. Perimeter is clear, but security sweep starts in six minutes. Get the rig ready.

A low-frequency rumble vibrates through the deck as an un-marked VTOL craft cuts through the cloud line overhead.""",
    "Vintage 1970s Diner": """INT. RETRO DINER - DAY

Sunlight filters through venetian blinds, cutting golden slashes across red vinyl booths and chrome counter stools.

MARA (40s) slides a steaming porcelain mug across the counter to SAM (50s). The jukebox in the corner hums a faint funk rhythm.

MARA
You shouldn't have come back here, Sam. The sheriff checks this diner twice every afternoon.

SAM
I only need five minutes, Mara. And a hot coffee.""",
    "Industrial Warehouse": """INT. ABANDONED WAREHOUSE - NIGHT

Shafts of moonlight pierce through shattered skylights, illuminating swirling dust and rusted iron support pillars. High ceiling trusses echo with distant water drips.

LEO (25) crouches behind a stack of wooden crates, holding a flickering tactical flashlight. Freight elevator cables groan softly in the shaft nearby.""",
}

# Sidebar
with st.sidebar:
  st.markdown("### CINESCOUT")
  st.caption("PRODUCTION COORDINATOR — BINDER 01")
  st.markdown("---")

  st.markdown("**ENV. KEYS**")
  gemini_key = os.environ.get("GEMINI_API_KEY")
  parallel_key = os.environ.get("PARALLEL_API_KEY")

  st.markdown(
      "`GEMINI_API_KEY`<br>"
      + (
          "<span class='stamp stamp-live'>Active</span>"
          if gemini_key
          else "<span class='stamp stamp-offline'>Offline Demo</span>"
      ),
      unsafe_allow_html=True,
  )
  st.write("")
  st.markdown(
      "`PARALLEL_API_KEY`<br>"
      + (
          "<span class='stamp stamp-live'>Active</span>"
          if parallel_key
          else "<span class='stamp stamp-offline'>Offline Demo</span>"
      ),
      unsafe_allow_html=True,
  )

  st.markdown("---")
  st.markdown("**AGENT SPEC**")
  st.markdown(
      """
        <div style="font-family:'Courier Prime',monospace; font-size:.78rem; line-height:1.9; color:var(--ink);">
        LLM ····· Gemini 3.7 Flash<br>
        SEARCH ··· parallel-web SDK<br>
        MODE ····· Fast Spatial Extraction
        </div>
        """,
      unsafe_allow_html=True,
  )
  st.markdown("---")
  st.caption("Built for the Agentic Cinema Hackathon")

# Clapper Header
st.markdown('<div class="clapper-bar"></div>', unsafe_allow_html=True)
st.markdown('<div class="slate-title">CineScout</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="slate-meta">
        <span><b>PROD.</b> Autonomous Location &amp; Permit Agent</span>
        <span><b>DEPT.</b> Pre-Production</span>
        <span><b>UNIT</b> Scouting + Compliance</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")
st.markdown(
    "Paste a screenplay excerpt. The agent breaks the scene down, searches live"
    " municipal and venue sources, and returns a verified scouting dossier with"
    " citations."
)
st.write("")

if "dossier" not in st.session_state:
  st.session_state.dossier = None

col_left, col_right = st.columns([1, 1.2], gap="large")

# Left Column (Intake)
with col_left:
  st.markdown(
      '<div class="sheet" data-tab="Sheet 01 — Scene Intake">',
      unsafe_allow_html=True,
  )
  st.markdown("#### Target &amp; Scene", unsafe_allow_html=True)

  city_option = st.selectbox(
      "Target filming location / city",
      [
          "Nairobi, Kenya",
          "Los Angeles, CA",
          "Dodoma, Tanzania",
          "London, UK",
          "Tokyo, Japan",
          "Cape Town, South Africa",
          "Custom City",
      ],
  )

  # Antigravity Fix 4B: Blank Custom City fallback
  if city_option == "Custom City":
    custom_val = st.text_input("Enter custom city/region", "Nairobi, Kenya")
    target_city = custom_val.strip() or "Nairobi, Kenya"
  else:
    target_city = city_option

  preset_choice = st.selectbox(
      "Quick-select demo scene",
      ["Custom Script"] + list(PRESET_SCENES.keys()),
      index=1,
  )

  default_text = (
      PRESET_SCENES.get(preset_choice, "")
      if preset_choice != "Custom Script"
      else "EXT. ROOFTOP - NIGHT\n\nRain falls across the city skyline..."
  )

  # Antigravity Fix 1A: Dynamic key bound to preset_choice to resolve widget lock
  screenplay_input = st.text_area(
      "Screenplay scene excerpt",
      value=default_text,
      key=f"scene_input_{preset_choice}",
      height=260,
      help=(
          "Paste a raw screenplay excerpt containing scene heading,"
          " description, and dialogue."
      ),
  )

  scout_button = st.button("▸ Scout Scene", use_container_width=True)
  st.markdown("</div>", unsafe_allow_html=True)

  if scout_button:
    if not screenplay_input.strip():
      st.error(
          "No scene text yet — paste an excerpt or pick a demo scene before"
          " scouting."
      )
    else:
      with st.spinner(
          f"Agent scouting live locations & municipal permits in {target_city}"
          " ..."
      ):
        st.session_state.dossier = scout_scene(screenplay_input, target_city)
      st.success("Dossier generated.")

# Right Column (Dossier Output)
with col_right:
  dossier = st.session_state.dossier

  if not dossier:
    st.markdown(
        """
            <div class="sheet" data-tab="Sheet 02 — Dossier" style="text-align:center; padding:48px 22px;">
                <p style="color:var(--ink-soft); font-family:'Courier Prime',monospace;">
                Empty binder. Select a scene on the left and click <b>Scout Scene</b><br>to generate a verified production dossier.
                </p>
            </div>
            """,
        unsafe_allow_html=True,
    )
  else:
    # Antigravity Fix 2B: NoneType safe dictionary retrievals
    meta = dossier.get("execution_meta") or {}
    summary = dossier.get("scene_summary") or {}
    gemini_status = "Gemini Live" if meta.get("gemini_live") else "Synthesized"
    parallel_status = (
        "Parallel Live" if meta.get("parallel_live") else "Simulated Search"
    )

    st.markdown(
        f"""
            <div style='display:flex; gap:10px; align-items:center; margin-bottom:14px; flex-wrap:wrap;'>
                <h3 style="margin:0;">Production Dossier</h3>
                <span class='stamp {"stamp-live" if meta.get("parallel_live") else "stamp-offline"}'>{parallel_status}</span>
                <span class='stamp {"stamp-live" if meta.get("gemini_live") else "stamp-offline"}'>{gemini_status}</span>
            </div>
            """,
        unsafe_allow_html=True,
    )

    tab_venues, tab_permits, tab_logistics, tab_raw = st.tabs(
        ["Venues", "Permits", "Logistics", "Sources"]
    )

    # TAB 1: VENUES
    with tab_venues:
      venues = dossier.get("venues") or []
      st.markdown(
          f"**{len(venues)} location match(es) in"
          f" {meta.get('target_city', target_city)}**"
      )
      for i, v in enumerate(venues, start=1):
        # Antigravity Fix 2A: NoneType safe feature iteration
        feats_list = v.get("key_features") or []
        feats_html = "".join([f"<li>{f}</li>" for f in feats_list])

        st.markdown(
            f"""
                <div class='sheet sheet--venue' data-tab="Venue">
                    <span class="sheet-num">{i:02d}</span><h4>{v.get('name', 'Venue')}</h4>
                    <span class="stamp-score" style="float:right;">MATCH {v.get('suitability_score', '90%')}</span>
                    <div class="addr">{v.get('address', 'Location area')}</div>
                    <p>{v.get('description', '')}</p>
                    <div class="feat-label">Key features</div>
                    <ul>
                        {feats_html if feats_html else '<li>Standard production access</li>'}
                    </ul>
                    <a class="src-link" href="{v.get('url', '#')}" target="_blank">View booking / source →</a>
                </div>
                """,
            unsafe_allow_html=True,
        )

    # TAB 2: PERMITS
    with tab_permits:
      permits = dossier.get("permits") or []
      st.markdown("**Required municipal approvals &amp; bylaws**")
      for i, p in enumerate(permits, start=1):
        # Antigravity Fix 2A: NoneType safe requirements iteration
        reqs_list = p.get("key_requirements") or []
        reqs_html = "".join([f"<li>{req}</li>" for req in reqs_list])

        st.markdown(
            f"""
                <div class='sheet sheet--permit' data-tab="Permit">
                    <span class="sheet-num">{i:02d}</span><h4>{p.get('permit_name', 'Permit Required')}</h4>
                    <div class="addr">Authority: {p.get('authority', 'Municipal Office')}</div>
                    <div class="permit-meta">
                        <div><b>Lead time</b>{p.get('lead_time', 'N/A')}</div>
                        <div><b>Est. fee</b>{p.get('estimated_fee', 'N/A')}</div>
                    </div>
                    <div class="feat-label">Mandatory requirements</div>
                    <ul>
                        {reqs_html if reqs_html else '<li>Standard filming filing requirements</li>'}
                    </ul>
                    <a class="src-link" href="{p.get('application_url', '#')}" target="_blank">Official permit portal →</a>
                </div>
                """,
            unsafe_allow_html=True,
        )

    # TAB 3: LOGISTICS & SAFETY
    with tab_logistics:
      st.markdown(
          f"**Aesthetic profile:** {summary.get('aesthetic_vibes', '')}"
      )
      challenges = summary.get("technical_challenges") or []
      if challenges:
        st.markdown("**Identified Technical Constraints:**")
        for c in challenges:
          st.markdown(f"- `{c}`")

      st.markdown('<div class="rule"></div>', unsafe_allow_html=True)
      st.markdown(
          "#### Technical &amp; safety advisories", unsafe_allow_html=True
      )
      for log in dossier.get("logistics") or []:
        st.markdown(
            f"""
                <div class='sheet sheet--logistics' data-tab="Logistics">
                    <h4>{log.get('category', 'Logistics')}</h4>
                    <p class="advisory">⚑ {log.get('advisory', '')}</p>
                    <p class="mitigation">✓ {log.get('mitigation_strategy', '')}</p>
                </div>
                """,
            unsafe_allow_html=True,
        )

    # TAB 4: RAW QUERIES & CITATIONS
    with tab_raw:
      st.markdown(
          "#### Formulated search queries", unsafe_allow_html=True
      )
      for q in dossier.get("raw_search_queries") or []:
        st.code(q, language="text")

      st.markdown('<div class="rule"></div>', unsafe_allow_html=True)
      st.markdown("#### Source citations", unsafe_allow_html=True)
      for cite in dossier.get("citations") or []:
        st.markdown(f"- [{cite}]({cite})")

    # Antigravity Fix 3: Full Markdown Export
    st.markdown('<div class="rule"></div>', unsafe_allow_html=True)

    md_content = f"# CineScout Production Dossier\n"
    md_content += (
        f"**Target Location:** {meta.get('target_city', target_city)}\n\n"
    )
    md_content += f"## Scene Summary\n"
    md_content += f"**Setting:** {summary.get('setting', 'N/A')}\n"
    md_content += f"**Aesthetic:** {summary.get('aesthetic_vibes', '')}\n\n"

    if challenges:
      md_content += "### Technical Constraints\n"
      for c in challenges:
        md_content += f"- {c}\n"
      md_content += "\n"

    md_content += "## Verified Venues\n"
    for v in venues:
      md_content += (
          f"### {v.get('name')} (Match: {v.get('suitability_score')})\n"
      )
      md_content += f"- **Address:** {v.get('address')}\n"
      md_content += f"- **Description:** {v.get('description')}\n"
      md_content += f"- **Source URL:** {v.get('url')}\n"
      feats = v.get("key_features") or []
      if feats:
        md_content += f"- **Key Features:** {', '.join(feats)}\n\n"

    md_content += "## Municipal Permits\n"
    for p in permits:
      md_content += f"### {p.get('permit_name')}\n"
      md_content += f"- **Authority:** {p.get('authority')}\n"
      md_content += f"- **Lead Time:** {p.get('lead_time')}\n"
      md_content += f"- **Estimated Fee:** {p.get('estimated_fee')}\n"
      md_content += f"- **Application URL:** {p.get('application_url')}\n\n"

    md_content += "## Technical & Safety Logistics\n"
    for log in dossier.get("logistics") or []:
      md_content += f"### {log.get('category')}\n"
      md_content += f"- **Advisory:** {log.get('advisory')}\n"
      md_content += f"- **Mitigation:** {log.get('mitigation_strategy')}\n\n"

    md_content += "## Sources & Citations\n"
    for cite in dossier.get("citations") or []:
      md_content += f"- {cite}\n"

    st.download_button(
        label="↓ Download Dossier (.md)",
        data=md_content,
        file_name=(
            f"cinescout_dossier_{target_city.lower().replace(' ', '_')}.md"
        ),
        mime="text/markdown",
        use_container_width=True,
    )