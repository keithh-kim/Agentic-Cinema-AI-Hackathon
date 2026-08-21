import os
import streamlit as st
import json
from engine import scout_scene

# Page Configuration
st.set_page_config(
    page_title="CineScout — Film Pre-Production Agent",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Film Aesthetics & Dark Glassmorphism
st.markdown("""
<style>
    /* Dark Cinematic Background & Fonts */
    .stApp {
        background-color: #0c0f17;
        color: #e2e8f0;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Glassmorphic Container Cards */
    .glass-card {
        background: rgba(18, 24, 38, 0.75);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    .venue-card {
        background: linear-gradient(135deg, rgba(16, 37, 34, 0.6) 0%, rgba(18, 24, 38, 0.8) 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 14px;
    }

    .permit-card {
        background: linear-gradient(135deg, rgba(39, 32, 16, 0.6) 0%, rgba(18, 24, 38, 0.8) 100%);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 14px;
    }

    .logistics-card {
        background: linear-gradient(135deg, rgba(23, 30, 48, 0.6) 0%, rgba(18, 24, 38, 0.8) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 14px;
    }

    /* Pill Badges */
    .badge-live {
        background-color: rgba(16, 185, 129, 0.2);
        color: #10b981;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }

    .badge-simulated {
        background-color: rgba(99, 102, 241, 0.2);
        color: #818cf8;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(99, 102, 241, 0.4);
    }

    .badge-score {
        background-color: #059669;
        color: #ffffff;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
    }

    /* Headers */
    h1, h2, h3, h4 {
        color: #f8fafc !important;
        font-weight: 700 !important;
    }

    /* Custom Streamlit Button Styling */
    .stButton>button {
        background: linear-gradient(90deg, #ec4899 0%, #8b5cf6 100%);
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(236, 72, 153, 0.4);
    }
</style>
""", unsafe_allow_html=1)

# Pre-loaded Demo Scenes
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

MARA (40s) slides a steaming porcelain mug across the counter to SAM (50s). jukebox in the corner hums a faint funk rhythm.

MARA
You shouldn't have come back here, Sam. The sheriff checks this diner twice every afternoon.

SAM
I only need five minutes, Mara. And a hot coffee.""",

    "Industrial Warehouse": """INT. ABANDONED WAREHOUSE - NIGHT

Shafts of moonlight pierce through shattered skylights, illuminating swirling dust and rusted iron support pillars. High ceiling trusses echo with distant water drips.

LEO (25) crouches behind a stack of wooden crates, holding a flickering tactical flashlight. Freight elevator cables groan softly in the shaft nearby.""",
}

# Sidebar - Key Status & System Info
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/clapperboard.png", width=60)
    st.title("CineScout AI")
    st.caption("Autonomous Film Pre-Production Agent")
    st.markdown("---")
    
    st.subheader("🔑 Environment Keys")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    parallel_key = os.environ.get("PARALLEL_API_KEY")
    
    if gemini_key:
        st.markdown("`GEMINI_API_KEY`: <span class='badge-live'>ACTIVE</span>", unsafe_allow_html=True)
    else:
        st.markdown("`GEMINI_API_KEY`: <span class='badge-simulated'>OFFLINE DEMO</span>", unsafe_allow_html=True)

    if parallel_key:
        st.markdown("`PARALLEL_API_KEY`: <span class='badge-live'>ACTIVE</span>", unsafe_allow_html=True)
    else:
        st.markdown("`PARALLEL_API_KEY`: <span class='badge-simulated'>OFFLINE DEMO</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("⚙️ Agent Architecture")
    st.markdown("""
    - **LLM Engine:** Gemini 1.5 Flash (`google-genai`)
    - **Search SDK:** Parallel Search (`parallel-web`)
    - **Execution Mode:** `parallel.beta.search`
    """)
    st.markdown("---")
    st.caption("Built for Agentic Cinema Hackathon")

# Main Application Layout
st.title("🎬 CineScout: Autonomous Location & Permit Agent")
st.markdown("Transform screenplay excerpts into live, verified film production location dossiers and municipal regulatory filings.")

# Initialize session state for dossier
if "dossier" not in st.session_state:
    st.session_state.dossier = None

col_left, col_right = st.columns([1, 1.2], gap="large")

# LEFT COLUMN - Input Controls
with col_left:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("🎯 1. Select Target City & Scene Preset")
    
    city_option = st.selectbox(
        "Target Filming Location / City:",
        ["Nairobi, Kenya", "Los Angeles, CA", "London, UK", "Tokyo, Japan", "Cape Town, South Africa", "Custom City"]
    )
    
    if city_option == "Custom City":
        target_city = st.text_input("Enter Custom City/Region:", "Nairobi, Kenya")
    else:
        target_city = city_option

    preset_choice = st.selectbox(
        "Quick-Select Demo Scene Preset:",
        ["Custom Script", "Nairobi Cyberpunk Rooftop", "Vintage 1970s Diner", "Industrial Warehouse"]
    )
    
    default_text = PRESET_SCENES.get(preset_choice, "") if preset_choice != "Custom Script" else "EXT. ROOFTOP - NIGHT\n\nRain falls across the city skyline..."
    
    screenplay_input = st.text_area(
        "Screenplay Scene Excerpt:",
        value=default_text,
        height=260,
        help="Paste a raw screenplay excerpt containing scene heading, description, and dialogue."
    )
    
    scout_button = st.button("🚀 Scout Scene & Search Locations", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if scout_button:
        if not screenplay_input.strip():
            st.error("Please enter or select a screenplay excerpt before scouting.")
        else:
            with st.spinner(f"🔍 Agent scouting live locations & municipal permits in {target_city}..."):
                st.session_state.dossier = scout_scene(screenplay_input, target_city)
            st.success("Dossier Generated Successfully!")

# RIGHT COLUMN - Production Dossier Dashboard
with col_right:
    dossier = st.session_state.dossier
    
    if not dossier:
        st.info("👈 Select a demo scene on the left and click **🚀 Scout Scene** to generate your live Production Dossier.")
    else:
        meta = dossier.get("execution_meta", {})
        gemini_status = "Gemini 1.5 Live" if meta.get("gemini_live") else "Synthesized Dossier"
        parallel_status = "Parallel Search Live" if meta.get("parallel_live") else "Simulated Web Search"
        
        st.markdown(f"""
        <div style='display: flex; gap: 10px; align-items: center; margin-bottom: 12px;'>
            <h3>📋 Production Dossier</h3>
            <span class='badge-live'>{parallel_status}</span>
            <span class='badge-simulated'>{gemini_status}</span>
        </div>
        """, unsafe_allow_html=True)

        # Tabbed Dashboard View
        tab_venues, tab_permits, tab_logistics, tab_raw = st.tabs([
            "📍 Verified Venues", 
            "📜 Municipal Permits", 
            "⚠️ Logistics & Safety", 
            "🔎 Raw Queries & Sources"
        ])

        # TAB 1: VERIFIED VENUES
        with tab_venues:
            venues = dossier.get("venues", [])
            st.markdown(f"**Found {len(venues)} location matches in {meta.get('target_city', 'Target Region')}:**")
            for v in venues:
                st.markdown(f"""
                <div class='venue-card'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <h4 style='margin:0;'>{v.get('name')}</h4>
                        <span class='badge-score'>Match: {v.get('suitability_score', '90%')}</span>
                    </div>
                    <p style='color:#94a3b8; font-size:0.9rem; margin-top:4px;'>📍 {v.get('address', 'Location Area')}</p>
                    <p>{v.get('description')}</p>
                    <div>
                        <strong>Key Features:</strong>
                        <ul style='margin-top:4px;'>
                            {''.join([f"<li>{f}</li>" for f in v.get('key_features', [])])}
                        </ul>
                    </div>
                    <a href="{v.get('url', '#')}" target="_blank" style="color: #10b981; font-weight:600; text-decoration:none;">🔗 View Booking / Location Source →</a>
                </div>
                """, unsafe_allow_html=True)

        # TAB 2: MUNICIPAL PERMITS
        with tab_permits:
            permits = dossier.get("permits", [])
            st.markdown(f"**Required Municipal Approvals & Bylaws:**")
            for p in permits:
                st.markdown(f"""
                <div class='permit-card'>
                    <h4 style='margin:0;'>📜 {p.get('permit_name')}</h4>
                    <p style='color:#cbd5e1; margin-top:4px;'><strong>Authority:</strong> {p.get('authority')}</p>
                    <div style='display:flex; gap:20px; margin: 8px 0;'>
                        <span>⏳ <strong>Lead Time:</strong> {p.get('lead_time', 'N/A')}</span>
                        <span>💵 <strong>Est. Fee:</strong> {p.get('estimated_fee', 'N/A')}</span>
                    </div>
                    <div>
                        <strong>Mandatory Requirements:</strong>
                        <ul style='margin-top:4px;'>
                            {''.join([f"<li>{req}</li>" for req in p.get('key_requirements', [])])}
                        </ul>
                    </div>
                    <a href="{p.get('application_url', '#')}" target="_blank" style="color: #f59e0b; font-weight:600; text-decoration:none;">🔗 Official Permit Portal →</a>
                </div>
                """, unsafe_allow_html=True)

        # TAB 3: LOGISTICS & SAFETY
        with tab_logistics:
            summary = dossier.get("scene_summary", {})
            st.markdown(f"**Aesthetic Profile:** {summary.get('aesthetic_vibes', '')}")
            
            st.subheader("Technical & Safety Advisories")
            for log in dossier.get("logistics", []):
                st.markdown(f"""
                <div class='logistics-card'>
                    <h4 style='margin:0;'>{log.get('category')}</h4>
                    <p style='color:#f87171; margin-top:6px;'><strong>Advisory:</strong> {log.get('advisory')}</p>
                    <p style='color:#4ade80; margin-top:4px;'><strong>Mitigation Strategy:</strong> {log.get('mitigation_strategy')}</p>
                </div>
                """, unsafe_allow_html=True)

        # TAB 4: RAW QUERIES & CITATIONS
        with tab_raw:
            st.subheader("Formulated Search Queries")
            for q in dossier.get("raw_search_queries", []):
                st.code(q, language="text")
            
            st.subheader("Source Citations & Live References")
            for cite in dossier.get("citations", []):
                st.markdown(f"- [{cite}]({cite})")

        # EXPORT FEATURE
        st.markdown("---")
        
        # Build clean Markdown string for download
        md_content = f"# CineScout Production Dossier\n"
        md_content += f"**Target Location:** {meta.get('target_city', 'Target Region')}\n\n"
        md_content += f"## Scene Summary\n{summary.get('aesthetic_vibes', '')}\n\n"
        md_content += f"## Verified Venues\n"
        for v in dossier.get("venues", []):
            md_content += f"### {v.get('name')} (Match: {v.get('suitability_score')})\n"
            md_content += f"- **Address:** {v.get('address')}\n"
            md_content += f"- **Description:** {v.get('description')}\n"
            md_content += f"- **Source URL:** {v.get('url')}\n\n"
            
        md_content += f"## Municipal Permits\n"
        for p in dossier.get("permits", []):
            md_content += f"### {p.get('permit_name')}\n"
            md_content += f"- **Authority:** {p.get('authority')}\n"
            md_content += f"- **Lead Time:** {p.get('lead_time')}\n"
            md_content += f"- **Estimated Fee:** {p.get('estimated_fee')}\n"
            md_content += f"- **Application URL:** {p.get('application_url')}\n\n"

        st.download_button(
            label="📥 Download Dossier as Markdown (.md)",
            data=md_content,
            file_name=f"cinescout_dossier_{target_city.lower().replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )
