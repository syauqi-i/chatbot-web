import streamlit as st
import os
import json
import markdown
import importlib
import chatbot as chatbot_module
from disaster_data import DISASTER_INFO, get_disaster_names

_particles_lib = open(os.path.join(os.path.dirname(__file__), 'static', 'particles.min.js'), 'r').read()


def get_response(prompt):
    importlib.reload(chatbot_module)
    return chatbot_module.get_response(prompt)

def _inject_particles(config):
    """Inject particles.js inside the iframe."""
    cfg_str = json.dumps(config)
    _html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            html, body {
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                overflow: hidden;
                background: transparent !important;
            }
            #particles-js {
                position: absolute;
                width: 100%;
                height: 100%;
                top: 0;
                left: 0;
                z-index: 1;
            }
        </style>
    </head>
    <body>
        <div id="particles-js"></div>
        <script>
            __PARTICLES_LIB__
        </script>
        <script>
            particlesJS('particles-js', __CONFIG__);
        </script>
    </body>
    </html>
    """.replace("__PARTICLES_LIB__", _particles_lib).replace("__CONFIG__", cfg_str)
    st.components.v1.html(_html, height=0)


st.set_page_config(
    page_title="Edukasi Bencana Alam",
    page_icon="\U0001F30B",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Session State ───────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Beranda"
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "bot",
        "content": "Halo! Saya asisten edukasi bencana alam. Tanyakan apa saja tentang bencana alam, cara mitigasi, atau langkah penyelamatan diri!"
    })
if "disaster_filter" not in st.session_state:
    st.session_state.disaster_filter = None
if "selected_disaster" not in st.session_state:
    st.session_state.selected_disaster = None

# ─── Query Parameters Syncing ──────────────────────────────────
if "page" in st.query_params:
    page_param = st.query_params["page"]
    if page_param in ["Beranda", "Edukasi", "Chatbot", "Tentang"]:
        st.session_state.page = page_param

if "disaster" in st.query_params:
    disaster_param = st.query_params["disaster"]
    if disaster_param in DISASTER_INFO:
        st.session_state.selected_disaster = disaster_param
        st.session_state.page = "Edukasi"
        # Safely remove 'disaster' param so we don't get stuck on it, and set 'page' to Edukasi
        st.query_params["page"] = "Edukasi"
        if "disaster" in st.query_params:
            del st.query_params["disaster"]

# Ensure current state is in URL query parameters
st.query_params["page"] = st.session_state.page

# ─── Track Page Change to Reset Scroll ───────────────────────
if "previous_page" not in st.session_state:
    st.session_state.previous_page = st.session_state.page

if st.session_state.page != st.session_state.previous_page:
    st.session_state.previous_page = st.session_state.page
    import time
    timestamp = int(time.time() * 1000)
    st.components.v1.html(
        f"""
        <script id="scroll-to-top-{timestamp}">
            (function() {{
                try {{
                    // Scroll main window/body
                    window.parent.scrollTo(0, 0);
                    var doc = window.parent.document;
                    // Also find Streamlit's main containers and scroll them
                    var mainEl = doc.querySelector('.main');
                    if (mainEl) {{
                        mainEl.scrollTo({{top: 0, behavior: 'instant'}});
                    }}
                    var stApp = doc.querySelector('.stApp');
                    if (stApp) {{
                        stApp.scrollTo({{top: 0, behavior: 'instant'}});
                    }}
                }} catch(e) {{
                    console.error('Scroll to top error:', e);
                }}
            }})();
        </script>
        """,
        height=0
    )

# ─── CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&display=swap');

    * { font-family: 'Space Grotesk', sans-serif; }

    /* ── Modern Animated Background ── */
    @keyframes gradientAnimation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .stApp {
        background: linear-gradient(-45deg, #0b1a10, #132d20, #0a1f28, #182e2c) !important;
        background-size: 400% 400% !important;
        animation: gradientAnimation 18s ease infinite !important;
        background-attachment: fixed !important;
    }

    .page-bg-image img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .page-bg-image .bg-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            180deg,
            rgba(11, 26, 16, 0.6) 0%,
            rgba(10, 31, 40, 0.7) 50%,
            rgba(19, 45, 32, 0.8) 100%
        );
    }
    .main > .block-container { position: relative; z-index: 10; }
    .nav-container {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 2147483647;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.6rem 4rem;
        background: rgba(10, 32, 21, 0.85);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin: 0;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    .nav-logo {
        font-weight: 800;
        font-size: 1.4rem;
        color: #FFFDF7 !important;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .nav-logo span {
        color: #FFD166;
    }
    .nav-links { display: flex; gap: 0.5rem; flex-wrap: wrap; }

    /* ── Nav Link HTML Styling ── */
    .nav-link {
        background: transparent !important;
        border: 1.5px solid transparent !important;
        color: rgba(255,253,247,0.6) !important;
        font-size: 0.9rem !important;
        text-transform: uppercase !important;
        font-weight: 600 !important;
        padding: 0.4rem 1.2rem !important;
        border-radius: 12px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        letter-spacing: 0.5px !important;
        text-decoration: none !important;
        display: inline-block !important;
    }
    .nav-link:hover {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #FFFDF7 !important;
        text-decoration: none !important;
    }
    .nav-link.active {
        background: linear-gradient(135deg, rgba(255,209,102,0.2), rgba(255,107,53,0.15)) !important;
        border: 1.5px solid rgba(255,209,102,0.5) !important;
        color: #FFD166 !important;
        font-weight: 700 !important;
        box-shadow: 0 0 20px rgba(255,209,102,0.15) !important;
        text-decoration: none !important;
    }

    /* ── Streamlit Button Styling ── */
    .stButton > button {
        background: #FFFDF7 !important;
        border: 3px solid #000 !important;
        color: #000 !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        padding: 0.5rem 1.2rem !important;
        cursor: pointer !important;
        box-shadow: 4px 4px 0 #000 !important;
        transition: all 0.08s linear !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        border-radius: 0 !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        transform: translate(-2px, -2px) !important;
        box-shadow: 6px 6px 0 #000 !important;
        background: #FFFDF7 !important;
        color: #000 !important;
        border-color: #000 !important;
    }
    .stButton > button:focus {
        box-shadow: 4px 4px 0 #000 !important;
        border-color: #000 !important;
        color: #000 !important;
    }
    .stButton > button:active {
        transform: translate(2px, 2px) !important;
        box-shadow: 0px 0px 0 #000 !important;
    }

    /* ── Background Video ── */
    .bg-video {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        object-fit: cover;
        z-index: -2 !important;
        pointer-events: none;
    }
    .bg-video-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: linear-gradient(
            180deg,
            rgba(0, 0, 0, 0.45) 0%,
            rgba(0, 0, 0, 0.75) 100%
        );
        z-index: -1 !important;
        pointer-events: none;
    }

    /* ── Hero Section ── */
    .hero-section {
        position: relative;
        min-height: calc(100vh - 120px);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin-top: 0;
        padding: 4rem 1rem 1rem 1rem;
        box-sizing: border-box;
        z-index: 2;
    }
    .hero-content {
        position: relative;
        z-index: 2;
        text-align: center;
        max-width: 900px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    .hero-content h1 {
        font-size: 4rem;
        font-weight: 800;
        color: #FFFDF7;
        margin: 0 0 1rem;
        line-height: 1.15;
        text-transform: uppercase;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.6);
        letter-spacing: -1px;
    }
    .hero-content .highlight {
        display: inline-block;
        background: #FFD166;
        padding: 0.2rem 1rem;
        border: 4px solid #000;
        color: #000;
        box-shadow: 6px 6px 0 rgba(0,0,0,1);
    }
    .hero-content p {
        font-size: 1.4rem;
        color: rgba(255,253,247,0.9);
        max-width: 700px;
        margin: 1.5rem auto 1rem;
        font-weight: 500;
        line-height: 1.6;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    }

    /* ── Centered HTML Hero Actions ── */
    .hero-actions {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1.5rem;
        margin-top: 2rem;
        animation: fadeInUp 0.8s ease 0.4s both;
    }
    .hero-btn {
        text-decoration: none !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        padding: 0.8rem 2rem !important;
        border-radius: 12px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    }
    .hero-btn.primary {
        background: linear-gradient(135deg, #FF6B35, #FF8E53) !important;
        color: #000000 !important;
        border: 2px solid #FF6B35 !important;
    }
    .hero-btn.primary:hover {
        transform: translateY(-4px) scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(255, 107, 53, 0.4) !important;
        background: linear-gradient(135deg, #FFD166, #FF9F43) !important;
    }
    .hero-btn.secondary {
        background: rgba(255, 253, 247, 0.08) !important;
        color: #FFFDF7 !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        backdrop-filter: blur(8px) !important;
    }
    .hero-btn.secondary:hover {
        background: rgba(255, 253, 247, 0.15) !important;
        color: #FFFDF7 !important;
        transform: translateY(-4px) scale(1.02) !important;
        border-color: #FFD166 !important;
        box-shadow: 0 8px 25px rgba(255, 209, 102, 0.2) !important;
    }

    /* ── Stats Overhaul (Glassmorphism) ── */
    .stat-box {
        background: rgba(255, 253, 247, 0.05) !important;
        border: 1.5px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 1.5rem 2rem;
        text-align: center;
        min-width: 160px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        backdrop-filter: blur(8px);
    }
    .stat-box:hover {
        transform: translateY(-5px) !important;
        border-color: rgba(255, 209, 102, 0.4) !important;
        box-shadow: 0 8px 30px rgba(0,0,0,0.3), 0 0 15px rgba(255, 209, 102, 0.08) !important;
    }
    .stat-box .num {
        font-size: 2.5rem;
        font-weight: 800;
        line-height: 1;
    }
    .stat-box .label {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.5rem;
        color: rgba(255, 253, 247, 0.6) !important;
    }

    /* ── Cards Section ── */
    .section-title {
        font-size: 2rem;
        font-weight: 800;
        text-transform: uppercase;
        margin: 2.5rem 0 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(255, 255, 255, 0.1);
        display: inline-block;
        color: #FFFDF7 !important;
    }
    .section-title, .section-title * {
        color: #FFFDF7 !important;
    }

    /* ── Premium Glowing Disaster Cards ── */
    .disaster-card {
        background: rgba(255, 253, 247, 0.04) !important;
        border: 2px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 24px !important;
        padding: 2rem 1.8rem !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        text-align: left !important;
        text-decoration: none !important;
        position: relative !important;
        overflow: hidden !important;
        backdrop-filter: blur(10px) !important;
    }
    .disaster-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: transparent;
        transition: all 0.3s ease;
    }
    .disaster-card:hover {
        transform: translateY(-8px) !important;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.5) !important;
        background: rgba(255, 253, 247, 0.08) !important;
    }
    .disaster-card .card-icon { font-size: 2.8rem; margin-bottom: 1rem; }
    .disaster-card h3 {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        margin: 0 0 0.8rem 0 !important;
        padding: 0 0.2rem !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        -webkit-text-fill-color: initial !important;
    }
    .disaster-card p {
        font-size: 0.9rem !important;
        color: rgba(255, 253, 247, 0.7) !important;
        margin: 0 0 1.2rem 0 !important;
        padding: 0 0.2rem !important;
        line-height: 1.7 !important;
    }
    .disaster-card .learn-more-text {
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        color: #FFD166 !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.25rem !important;
        margin-top: auto !important;
    }

    /* Glow variants */
    .card-gempa::before,
    .card-tsunami::before,
    .card-banjir::before,
    .card-gunung::before,
    .card-angin::before,
    .card-longsor::before,
    .card-kebakaran::before,
    .card-kekeringan::before { background: #FFD166; }
    .card-gempa:hover,
    .card-tsunami:hover,
    .card-banjir:hover,
    .card-gunung:hover,
    .card-angin:hover,
    .card-longsor:hover,
    .card-kebakaran:hover,
    .card-kekeringan:hover { border-color: rgba(255, 209, 102, 0.4) !important; box-shadow: 0 15px 40px rgba(255, 209, 102, 0.15) !important; }
    .card-gempa h3,
    .card-tsunami h3,
    .card-banjir h3,
    .card-gunung h3,
    .card-angin h3,
    .card-longsor h3,
    .card-kebakaran h3,
    .card-kekeringan h3 { color: #FFD166 !important; }

    /* ── Detail page (Dark Glassmorphic) ── */
    .detail-section {
        background: rgba(255, 253, 247, 0.04) !important;
        border: 2px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 24px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important;
        padding: 2.2rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        animation: fadeInUp 0.5s ease backwards;
    }
    .detail-section:hover {
        border-color: rgba(255, 209, 102, 0.3) !important;
        transform: translateY(-4px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.4) !important;
    }
    .detail-section h2 {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0 0 0.5rem;
        color: #FFFDF7 !important;
        background: none;
        -webkit-text-fill-color: #FFFDF7 !important;
    }
    .detail-section .subtitle {
        font-size: 0.9rem;
        color: rgba(255, 253, 247, 0.5) !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        margin-bottom: 1.5rem;
    }
    .detail-section p {
        color: rgba(255, 253, 247, 0.8) !important;
        line-height: 1.7;
    }
    .detail-section ul {
        list-style: none;
        padding: 0;
    }
    .detail-section ul li {
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        font-size: 0.9rem;
        color: rgba(255, 253, 247, 0.8) !important;
    }
    .detail-section ul li::before {
        content: "▸";
        font-weight: 700;
        margin-right: 0.5rem;
        color: #FF6B35;
    }
    .detail-section ul li strong {
        color: #FFD166 !important;
    }
    /* Accent variants for detail sections */
    .detail-section.accent-yellow {
        border-left: 4px solid #FFD166 !important;
        background: linear-gradient(135deg, rgba(255, 209, 102, 0.06), rgba(255, 253, 247, 0.03)) !important;
    }
    .detail-section.accent-yellow h2 {
        color: #FFD166 !important;
        -webkit-text-fill-color: #FFD166 !important;
    }
    .detail-section.accent-blue-solid {
        border-left: 4px solid #118AB2 !important;
        background: linear-gradient(135deg, rgba(17, 138, 178, 0.08), rgba(255, 253, 247, 0.03)) !important;
    }
    .detail-section.accent-blue-solid h2 {
        color: #118AB2 !important;
        -webkit-text-fill-color: #118AB2 !important;
    }
    .detail-section.accent-blue-solid .subtitle {
        color: rgba(255, 253, 247, 0.6) !important;
    }
    .detail-section.accent-blue-solid ul li {
        color: rgba(255, 253, 247, 0.9) !important;
    }
    .detail-section.accent-green-solid {
        border-left: 4px solid #06D6A0 !important;
        background: linear-gradient(135deg, rgba(6, 214, 160, 0.06), rgba(255, 253, 247, 0.03)) !important;
    }
    .detail-section.accent-green-solid h2 {
        color: #06D6A0 !important;
        -webkit-text-fill-color: #06D6A0 !important;
    }
        /* ── Brutal CTA Cards ── */
    .brutal-card {
        border-radius: 20px !important;
        padding: 1.8rem 2rem !important;
        box-shadow: 0 10px 30px rgba(255,255,255,0.15) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .brutal-card:hover {
        transform: translateY(-6px) !important;
        box-shadow: 0 15px 40px rgba(255,255,255,0.25) !important;
    }
    .brutal-card h3 {
        margin: 0 0 0.6rem !important;
        font-size: 1.3rem !important;
        font-weight: 800 !important;
    }
    .brutal-card p {
        margin: 0 !important;
        line-height: 1.6 !important;
    }
    
    /* ── Misc ── */
    .footer {
        text-align: center;
        padding: 2rem;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        margin-top: 3rem;
        font-size: 0.8rem;
        color: rgba(255, 253, 247, 0.4);
        font-weight: 500;
    }
    .stTextInput input {
        border: 1.5px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        box-shadow: none !important;
        background: rgba(255,255,255,0.06) !important;
        color: #FFFDF7 !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }
    section[data-testid="stSidebar"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stApp > header { display: none; }
    .block-container { padding-top: 90px !important; max-width: 1200px; }
    .stExpander {
        border: 1.5px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2) !important;
        border-radius: 16px !important;
        background: rgba(255, 253, 247, 0.04) !important;
        backdrop-filter: blur(8px) !important;
    }
    .stExpander > details > summary {
        color: #FFFDF7 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }
    .stExpander * {
        color: rgba(255, 253, 247, 0.85) !important;
    }

    /* Feature grid */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1.5rem;
        margin: 1.5rem 0;
    }

    /* Tag badges */
    .tag-badge {
        display: inline-block;
        background: #FF6B35;
        border: 2px solid #000;
        padding: 0.2rem 0.6rem;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-top: 0.5rem;
        box-shadow: 2px 2px 0 #000;
    }
    .tag-badge.green { background: #06D6A0; }
    .tag-badge.yellow { background: #FFD166; }
    .tag-badge.blue { background: #118AB2; color: #fff; }
    .tag-badge.pink { background: #EF476F; color: #fff; }

    /* ═══════════════════════════════════════════════
       EDUKASI PAGE — Colorful Animated Cards
    ═══════════════════════════════════════════════ */

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-40px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(40px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 20px rgba(255,209,102,0.3); }
        50% { box-shadow: 0 0 40px rgba(255,209,102,0.6); }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    @keyframes borderPulse {
        0%, 100% { border-color: rgba(255,209,102,0.4); }
        50% { border-color: rgba(255,107,53,0.8); }
    }
    @keyframes iconBounce {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.15); }
    }
    @keyframes rotateIn {
        from { opacity: 0; transform: rotate(-5deg) scale(0.95); }
        to { opacity: 1; transform: rotate(0) scale(1); }
    }

    .edu-page-header {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem;
        animation: fadeInUp 0.8s ease;
    }
    .edu-page-header h1 {
        font-size: 2.8rem;
        font-weight: 800;
        color: #FFFDF7;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: -0.5px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .edu-page-header h1 .accent {
        background: linear-gradient(135deg, #FFD166, #FF6B35);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .edu-page-header p {
        color: rgba(255,253,247,0.7);
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }

    /* Disaster selector cards */
    .disaster-select-card {
        background: rgba(255,253,247,0.06);
        border: 2px solid rgba(255,255,255,0.1);
        border-radius: 22px;
        padding: 1.3rem 1.1rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.6s ease backwards;
        backdrop-filter: blur(8px);
        position: relative;
        overflow: hidden;
    }
    .disaster-select-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(135deg, transparent 0%, rgba(255,209,102,0.05) 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
        border-radius: 22px;
    }
    .disaster-select-card:hover::before { opacity: 1; }
    .disaster-select-card:hover {
        border-color: rgba(255,209,102,0.5);
        transform: translateY(-6px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.3), 0 0 20px rgba(255,209,102,0.1);
    }
    .disaster-select-card.active {
        border-color: #FFD166;
        background: rgba(255,209,102,0.12);
        box-shadow: 0 8px 32px rgba(255,209,102,0.2);
        animation: pulseGlow 2.5s infinite;
    }
    .disaster-select-card .card-emoji {
        font-size: 2.2rem;
        display: block;
        margin-bottom: 0.5rem;
        animation: float 3s ease-in-out infinite;
    }
    .disaster-select-card .card-name {
        font-size: 0.82rem;
        font-weight: 700;
        color: #FFFDF7;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .disaster-select-card.active .card-name {
        color: #FFD166;
    }

    /* Detail panel */
    .edu-detail-panel {
        background: rgba(255,253,247,0.04);
        border: 2px solid rgba(255,255,255,0.1);
        border-radius: 24px;
        padding: 2.5rem;
        margin-top: 1.5rem;
        backdrop-filter: blur(12px);
        animation: fadeInUp 0.5s ease;
        position: relative;
        overflow: hidden;
    }
    .edu-detail-panel::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 30% 40%, rgba(255,209,102,0.03) 0%, transparent 50%);
        pointer-events: none;
    }
    .edu-detail-title {
        font-size: 2rem;
        font-weight: 800;
        color: #FFFDF7;
        margin: 0 0 0.3rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        animation: slideInLeft 0.6s ease;
    }
    .edu-detail-title .title-emoji {
        font-size: 2.4rem;
        animation: iconBounce 2s ease-in-out infinite;
    }
    .edu-detail-subtitle {
        color: rgba(255,253,247,0.5);
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin-bottom: 1.5rem;
        animation: slideInLeft 0.6s ease 0.1s backwards;
    }
    .edu-definition {
        font-size: 1.05rem;
        line-height: 1.7;
        color: rgba(255,253,247,0.85);
        padding: 1.2rem 1.5rem;
        background: rgba(255,255,255,0.05);
        border-left: 4px solid #FFD166;
        border-radius: 0 12px 12px 0;
        margin-bottom: 1.5rem;
        animation: slideInLeft 0.6s ease 0.2s backwards;
    }

    /* Info section blocks */
    .edu-info-block {
        background: rgba(255,255,255,0.04);
        border: 1.5px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 1.6rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        animation: fadeInUp 0.5s ease backwards;
    }
    .edu-info-block:hover {
        border-color: rgba(255,209,102,0.3);
        background: rgba(255,255,255,0.06);
        transform: translateX(4px);
    }
    .edu-info-block .block-title {
        font-size: 1rem;
        font-weight: 700;
        color: #FFD166;
        margin: 0 0 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .edu-info-block .block-title .block-icon {
        font-size: 1.3rem;
    }
    .edu-info-block ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .edu-info-block ul li {
        padding: 0.45rem 0;
        color: rgba(255,253,247,0.8);
        font-size: 0.88rem;
        line-height: 1.55;
        border-bottom: 1px solid rgba(255,255,255,0.04);
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
    }
    .edu-info-block ul li:last-child { border-bottom: none; }
    .edu-info-block ul li .li-marker {
        color: #FF6B35;
        font-weight: 700;
        flex-shrink: 0;
        margin-top: 2px;
    }

    /* Fact cards */
    .fact-card {
        background: linear-gradient(135deg, rgba(255,209,102,0.08), rgba(255,107,53,0.06));
        border: 1.5px solid rgba(255,209,102,0.2);
        border-radius: 18px;
        padding: 1.4rem 1.5rem;
        margin-bottom: 0.8rem;
        transition: all 0.3s ease;
        animation: rotateIn 0.6s ease backwards;
        position: relative;
        overflow: hidden;
    }
    .fact-card::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 200%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent);
        animation: shimmer 4s ease-in-out infinite;
    }
    .fact-card:hover {
        border-color: rgba(255,209,102,0.5);
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    }
    .fact-card .fact-label {
        font-size: 0.65rem;
        font-weight: 700;
        color: #FFD166;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 0.4rem;
    }
    .fact-card .fact-text {
        font-size: 0.88rem;
        color: rgba(255,253,247,0.85);
        line-height: 1.55;
    }

    /* Color accents for different disaster types - Overhauled with borders, gradients and glows */
    .accent-red {
        border-left: 5px solid #EF476F !important;
        background: linear-gradient(135deg, rgba(239, 71, 111, 0.08), rgba(255, 255, 255, 0.02)) !important;
        box-shadow: 0 4px 20px rgba(239, 71, 111, 0.05) !important;
    }
    .accent-red .block-title { color: #EF476F !important; }
    .accent-red:hover {
        border-color: #EF476F !important;
        box-shadow: 0 4px 25px rgba(239, 71, 111, 0.15) !important;
    }

    .accent-blue {
        border-left: 5px solid #118AB2 !important;
        background: linear-gradient(135deg, rgba(17, 138, 178, 0.08), rgba(255, 255, 255, 0.02)) !important;
        box-shadow: 0 4px 20px rgba(17, 138, 178, 0.05) !important;
    }
    .accent-blue .block-title { color: #118AB2 !important; }
    .accent-blue:hover {
        border-color: #118AB2 !important;
        box-shadow: 0 4px 25px rgba(17, 138, 178, 0.15) !important;
    }

    .accent-green {
        border-left: 5px solid #06D6A0 !important;
        background: linear-gradient(135deg, rgba(6, 214, 160, 0.08), rgba(255, 255, 255, 0.02)) !important;
        box-shadow: 0 4px 20px rgba(6, 214, 160, 0.05) !important;
    }
    .accent-green .block-title { color: #06D6A0 !important; }
    .accent-green:hover {
        border-color: #06D6A0 !important;
        box-shadow: 0 4px 25px rgba(6, 214, 160, 0.15) !important;
    }

    .accent-orange {
        border-left: 5px solid #FF6B35 !important;
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.08), rgba(255, 255, 255, 0.02)) !important;
        box-shadow: 0 4px 20px rgba(255, 107, 53, 0.05) !important;
    }
    .accent-orange .block-title { color: #FF6B35 !important; }
    .accent-orange:hover {
        border-color: #FF6B35 !important;
        box-shadow: 0 4px 25px rgba(255, 107, 53, 0.15) !important;
    }

    .accent-purple {
        border-left: 5px solid #B07FFF !important;
        background: linear-gradient(135deg, rgba(176, 127, 255, 0.08), rgba(255, 255, 255, 0.02)) !important;
        box-shadow: 0 4px 20px rgba(176, 127, 255, 0.05) !important;
    }
    .accent-purple .block-title { color: #B07FFF !important; }
    .accent-purple:hover {
        border-color: #B07FFF !important;
        box-shadow: 0 4px 25px rgba(176, 127, 255, 0.15) !important;
    }

    .accent-pink {
        border-left: 5px solid #FF6B9D !important;
        background: linear-gradient(135deg, rgba(255, 107, 157, 0.08), rgba(255, 255, 255, 0.02)) !important;
        box-shadow: 0 4px 20px rgba(255, 107, 157, 0.05) !important;
    }
    .accent-pink .block-title { color: #FF6B9D !important; }
    .accent-pink:hover {
        border-color: #FF6B9D !important;
        box-shadow: 0 4px 25px rgba(255, 107, 157, 0.15) !important;
    }

    /* ═══════════════════════════════════════════════
       CHATBOT PAGE — Modern Glassmorphism
    ═══════════════════════════════════════════════ */

    @keyframes typing {
        0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
        30% { opacity: 1; transform: translateY(-4px); }
    }
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 4px 8px;
        min-height: 20px;
    }
    .typing-dot {
        width: 8px;
        height: 8px;
        background-color: rgba(255, 253, 247, 0.7);
        border-radius: 50%;
        animation: typing 1.4s infinite ease-in-out;
    }
    .typing-dot:nth-child(1) { animation-delay: 0ms; }
    .typing-dot:nth-child(2) { animation-delay: 200ms; }
    .typing-dot:nth-child(3) { animation-delay: 400ms; }
    @keyframes bubbleAppear {
        from { opacity: 0; transform: translateY(20px) scale(0.95); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    @keyframes chatGlow {
        0%, 100% { box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 0 20px rgba(255, 255, 255, 0.02); }
        50% { box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5), 0 0 30px rgba(255, 209, 102, 0.08); }
    }

    .chat-page-header {
        text-align: center;
        padding: 2rem 1rem 1rem;
        animation: fadeInUp 0.6s ease;
    }
    .chat-page-header h1 {
        font-size: 2.4rem;
        font-weight: 800;
        color: #FFFDF7;
        margin: 0;
        text-transform: uppercase;
    }
    .chat-page-header h1 .chat-accent {
        background: linear-gradient(135deg, #06D6A0, #118AB2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .chat-page-header p {
        color: rgba(255,253,247,0.6);
        font-size: 1rem;
        margin-top: 0.3rem;
    }

    /* Chat container modern glassmorphism */
    .chat-modern {
        background: rgba(10, 30, 20, 0.4) !important;
        border: 2px solid rgba(255, 209, 102, 0.15) !important;
        border-radius: 24px !important;
        padding: 1.5rem;
        min-height: 420px;
        max-height: 520px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        backdrop-filter: blur(12px);
        animation: chatGlow 5s ease infinite;
        scrollbar-width: thin;
        scrollbar-color: rgba(255,255,255,0.15) transparent;
    }
    .chat-modern::-webkit-scrollbar {
        width: 6px;
    }
    .chat-modern::-webkit-scrollbar-track {
        background: transparent;
    }
    .chat-modern::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.15);
        border-radius: 3px;
    }

    .chat-bubble {
        max-width: 78%;
        padding: 0.9rem 1.2rem;
        font-size: 0.92rem;
        line-height: 1.6;
        font-weight: 500;
        animation: bubbleAppear 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) both;
        position: relative;
    }
    .chat-bubble.user-bubble {
        align-self: flex-end;
        margin-left: auto;
        background: linear-gradient(135deg, #FFD166, #FF9F43);
        color: #000 !important;
        border-radius: 18px 18px 4px 18px;
        box-shadow: 0 4px 15px rgba(255,209,102,0.25);
    }
    .chat-bubble.user-bubble * { color: #000 !important; }
    .chat-bubble.bot-bubble {
        align-self: flex-start;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.12);
        color: rgba(255,253,247,0.9) !important;
        border-radius: 18px 18px 18px 4px;
        backdrop-filter: blur(6px);
    }
    .chat-bubble.bot-bubble * { color: rgba(255,253,247,0.9) !important; }

    .chat-sender {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.3rem;
        opacity: 0.6;
    }

    /* Quick action pills */
    .quick-pill {
        display: inline-block;
        background: rgba(255,255,255,0.06);
        border: 1.5px solid rgba(255,255,255,0.12);
        border-radius: 25px;
        padding: 0.5rem 1rem;
        font-size: 0.8rem;
        font-weight: 600;
        color: rgba(255,253,247,0.7);
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 0.3rem;
    }
    .quick-pill:hover {
        background: rgba(255,209,102,0.12);
        border-color: rgba(255,209,102,0.4);
        color: #FFD166;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }

    /* Tips sidebar card */
    .tips-card {
        background: rgba(255,255,255,0.04);
        border: 1.5px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(8px);
        transition: all 0.3s ease;
        animation: fadeInUp 0.5s ease backwards;
    }
    .tips-card:hover {
        border-color: rgba(255,209,102,0.3);
    }
    .tips-card h3 {
        font-size: 0.95rem;
        font-weight: 700;
        color: #FFD166 !important;
        margin: 0 0 0.5rem;
        -webkit-text-fill-color: #FFD166 !important;
    }
    .tips-card p {
        font-size: 0.78rem;
        color: rgba(255,253,247,0.5) !important;
        margin: 0;
        line-height: 1.5;
    }

    .emergency-card {
        background: linear-gradient(135deg, rgba(239,71,111,0.12), rgba(255,107,53,0.08));
        border: 1.5px solid rgba(239,71,111,0.3);
        border-radius: 20px;
        padding: 1.5rem;
        margin-top: 1rem;
        animation: fadeInUp 0.5s ease 0.3s backwards;
        transition: all 0.3s ease;
    }
    .emergency-card:hover {
        border-color: rgba(239,71,111,0.6);
        box-shadow: 0 0 20px rgba(239,71,111,0.15);
    }
    .emergency-card h3 {
        font-size: 0.95rem;
        font-weight: 700;
        color: #EF476F !important;
        margin: 0 0 0.5rem;
        -webkit-text-fill-color: #EF476F !important;
    }
    .emergency-card .e-line {
        font-size: 0.82rem;
        color: rgba(255,253,247,0.75) !important;
        font-weight: 600;
        margin: 0.2rem 0;
    }

    /* Chatbot buttons override */
    .chat-actions .stButton > button {
        background: #FFFDF7 !important;
        border: 3px solid #000 !important;
        color: #000 !important;
        font-weight: 700 !important;
        font-size: 0.75rem !important;
        padding: 0.5rem 0.6rem !important;
        cursor: pointer !important;
        box-shadow: 4px 4px 0 #000 !important;
        transition: all 0.08s linear !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        border-radius: 0 !important;
        width: 100% !important;
        text-align: left !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        white-space: nowrap !important;
        overflow: hidden !important;
    }
    .chat-actions .stButton > button div,
    .chat-actions .stButton > button p {
        text-align: left !important;
        justify-content: flex-start !important;
        align-items: center !important;
        display: flex !important;
        width: 100% !important;
        margin: 0 !important;
        gap: 0.5rem !important;
    }
    .chat-actions .stButton > button:hover {
        transform: translate(-2px, -2px) !important;
        box-shadow: 6px 6px 0 #000 !important;
        background: #FFFDF7 !important;
        color: #000 !important;
        border-color: #000 !important;
    }
    .chat-actions .stButton > button:active {
        transform: translate(2px, 2px) !important;
        box-shadow: 0px 0px 0 #000 !important;
    }
    .clear-btn .stButton > button {
        background: rgba(239,71,111,0.08) !important;
        border: 1.5px solid rgba(239,71,111,0.2) !important;
        color: rgba(239,71,111,0.8) !important;
        border-radius: 14px !important;
        box-shadow: none !important;
        font-size: 0.82rem !important;
        text-transform: none !important;
        transition: all 0.3s ease !important;
    }
    .clear-btn .stButton > button:hover {
        background: rgba(239,71,111,0.15) !important;
        border-color: rgba(239,71,111,0.5) !important;
        color: #EF476F !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(239,71,111,0.2) !important;
    }

    /* Modern chat input override */
    .stChatInput, div[data-testid="stChatInput"] {
        background: rgba(255,255,255,0.06) !important;
        border: 1.5px solid rgba(255,255,255,0.12) !important;
        border-radius: 18px !important;
        padding: 4px 8px !important;
        transition: all 0.3s ease !important;
    }
    .stChatInput textarea, div[data-testid="stChatInput"] textarea {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #FFFDF7 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 0.92rem !important;
        overflow: hidden !important;
        resize: none !important;
        padding: 0.8rem 1.2rem !important;
    }
    .stChatInput:focus-within, div[data-testid="stChatInput"]:focus-within {
        border-color: rgba(255, 209, 102, 0.4) !important;
        box-shadow: 0 0 20px rgba(255,209,102,0.1) !important;
    }

    /* Edu page button overrides */
    .edu-btn .stButton > button {
        background: linear-gradient(135deg, rgba(255,209,102,0.15), rgba(255,107,53,0.1)) !important;
        border: 1.5px solid rgba(255,209,102,0.3) !important;
        color: #FFD166 !important;
        border-radius: 14px !important;
        box-shadow: none !important;
        font-size: 0.85rem !important;
        text-transform: none !important;
        transition: all 0.3s ease !important;
    }
    .edu-btn .stButton > button:hover {
        background: linear-gradient(135deg, rgba(255,209,102,0.25), rgba(255,107,53,0.18)) !important;
        border-color: rgba(255,209,102,0.6) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 24px rgba(255,209,102,0.15) !important;
    }

    /* ── Particles.js Background ── */
    iframe[srcdoc*="particles-js"] {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        z-index: 1 !important;
        pointer-events: none !important;
        border: none !important;
        background: transparent !important;
    }
    
    /* Style all element containers and columns to stack in front of particles */
    .element-container, div[data-testid="column"] {
        position: relative !important;
        z-index: 2 !important;
    }
    
    /* Target the element-container that wraps the particles iframe and set its z-index lower */
    .element-container:has(iframe[srcdoc*="particles-js"]) {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        z-index: 1 !important;
        pointer-events: none !important;
    }

    /* ── Ensure navbar always on top of everything ── */
    .nav-container {
        z-index: 2147483647 !important;
    }

</style>
""", unsafe_allow_html=True)

# ─── Navigasi ──────────────────────────────────────────────────
active_beranda = "active" if st.session_state.page == "Beranda" else ""
active_edukasi = "active" if st.session_state.page == "Edukasi" else ""
active_chatbot = "active" if st.session_state.page == "Chatbot" else ""
active_tentang = "active" if st.session_state.page == "Tentang" else ""

# Inject navbar via JavaScript into the parent Streamlit document
# This avoids stacking-context issues that break position:fixed inside st.markdown
_nav_inject_js = f"""
<script>
(function() {{
    try {{
        var doc = window.parent.document;
        // Remove any old navbar first
        var old = doc.getElementById('custom-navbar');
        if (old) old.remove();

        // Create navbar element
        var nav = doc.createElement('div');
        nav.id = 'custom-navbar';
        nav.innerHTML = `
            <div style="
                position: fixed;
                top: 0; left: 0; right: 0;
                z-index: 2147483647;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0.6rem 4rem;
                background: rgba(10, 32, 21, 0.88);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border-bottom: 1px solid rgba(255, 255, 255, 0.12);
                font-family: 'Space Grotesk', sans-serif;
                flex-wrap: wrap;
                gap: 0.5rem;
                box-sizing: border-box;
            ">
                <div style="
                    font-weight: 800;
                    font-size: 1.4rem;
                    color: #FFFDF7;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                "><span style="color:#FFD166;">🌋</span> EDUKASI BENCANA</div>
                <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
                    <a href="?page=Beranda" class="{'active' if '{active_beranda}' == 'active' else ''}"
                       style="
                        background: {'linear-gradient(135deg, rgba(255,209,102,0.2), rgba(255,107,53,0.15))' if '{active_beranda}' == 'active' else 'transparent'};
                        border: 1.5px solid {'rgba(255,209,102,0.5)' if '{active_beranda}' == 'active' else 'transparent'};
                        color: {'#FFD166' if '{active_beranda}' == 'active' else 'rgba(255,253,247,0.6)'};
                        font-size: 0.9rem;
                        text-transform: uppercase;
                        font-weight: {'700' if '{active_beranda}' == 'active' else '600'};
                        padding: 0.4rem 1.2rem;
                        border-radius: 12px;
                        letter-spacing: 0.5px;
                        text-decoration: none;
                        display: inline-block;
                        transition: all 0.3s ease;
                        font-family: 'Space Grotesk', sans-serif;
                        {'box-shadow: 0 0 20px rgba(255,209,102,0.15);' if '{active_beranda}' == 'active' else ''}
                    ">Beranda</a>
                    <a href="?page=Edukasi"
                       style="
                        background: {'linear-gradient(135deg, rgba(255,209,102,0.2), rgba(255,107,53,0.15))' if '{active_edukasi}' == 'active' else 'transparent'};
                        border: 1.5px solid {'rgba(255,209,102,0.5)' if '{active_edukasi}' == 'active' else 'transparent'};
                        color: {'#FFD166' if '{active_edukasi}' == 'active' else 'rgba(255,253,247,0.6)'};
                        font-size: 0.9rem;
                        text-transform: uppercase;
                        font-weight: {'700' if '{active_edukasi}' == 'active' else '600'};
                        padding: 0.4rem 1.2rem;
                        border-radius: 12px;
                        letter-spacing: 0.5px;
                        text-decoration: none;
                        display: inline-block;
                        transition: all 0.3s ease;
                        font-family: 'Space Grotesk', sans-serif;
                        {'box-shadow: 0 0 20px rgba(255,209,102,0.15);' if '{active_edukasi}' == 'active' else ''}
                    ">Edukasi</a>
                    <a href="?page=Chatbot"
                       style="
                        background: {'linear-gradient(135deg, rgba(255,209,102,0.2), rgba(255,107,53,0.15))' if '{active_chatbot}' == 'active' else 'transparent'};
                        border: 1.5px solid {'rgba(255,209,102,0.5)' if '{active_chatbot}' == 'active' else 'transparent'};
                        color: {'#FFD166' if '{active_chatbot}' == 'active' else 'rgba(255,253,247,0.6)'};
                        font-size: 0.9rem;
                        text-transform: uppercase;
                        font-weight: {'700' if '{active_chatbot}' == 'active' else '600'};
                        padding: 0.4rem 1.2rem;
                        border-radius: 12px;
                        letter-spacing: 0.5px;
                        text-decoration: none;
                        display: inline-block;
                        transition: all 0.3s ease;
                        font-family: 'Space Grotesk', sans-serif;
                        {'box-shadow: 0 0 20px rgba(255,209,102,0.15);' if '{active_chatbot}' == 'active' else ''}
                    ">Chatbot</a>
                    <a href="?page=Tentang"
                       style="
                        background: {'linear-gradient(135deg, rgba(255,209,102,0.2), rgba(255,107,53,0.15))' if '{active_tentang}' == 'active' else 'transparent'};
                        border: 1.5px solid {'rgba(255,209,102,0.5)' if '{active_tentang}' == 'active' else 'transparent'};
                        color: {'#FFD166' if '{active_tentang}' == 'active' else 'rgba(255,253,247,0.6)'};
                        font-size: 0.9rem;
                        text-transform: uppercase;
                        font-weight: {'700' if '{active_tentang}' == 'active' else '600'};
                        padding: 0.4rem 1.2rem;
                        border-radius: 12px;
                        letter-spacing: 0.5px;
                        text-decoration: none;
                        display: inline-block;
                        transition: all 0.3s ease;
                        font-family: 'Space Grotesk', sans-serif;
                        {'box-shadow: 0 0 20px rgba(255,209,102,0.15);' if '{active_tentang}' == 'active' else ''}
                    ">Tentang</a>
                </div>
            </div>
        `;
        doc.body.insertBefore(nav, doc.body.firstChild);

        // Add hover effects via JS
        var links = nav.querySelectorAll('a');
        links.forEach(function(a) {{
            a.addEventListener('mouseenter', function() {{
                if (!this.classList.contains('active')) {{
                    this.style.background = 'rgba(255, 255, 255, 0.08)';
                    this.style.color = '#FFFDF7';
                }}
            }});
            a.addEventListener('mouseleave', function() {{
                if (!this.classList.contains('active')) {{
                    this.style.background = 'transparent';
                    this.style.color = 'rgba(255,253,247,0.6)';
                }}
            }});
        }});
    }} catch(e) {{
        console.error('Navbar injection error:', e);
    }}
}})();
</script>
"""
st.components.v1.html(_nav_inject_js, height=0)

# ─── Halaman: Beranda ──────────────────────────────────────────
if st.session_state.page == "Beranda":
    disasters = get_disaster_names()
    icons_map = {
        "gempa_bumi": "\U0001F30D", "banjir": "\U0001F30A", "tsunami": "\U0001F30A",
        "gunung_meletus": "\U0001F30B", "angin_topan": "\U0001F300",
        "tanah_longsor": "\U0001F5FB", "kebakaran_hutan": "\U0001F525", "kekeringan": "\u2600\uFE0F"
    }
    desc_map = {
        "gempa_bumi": "Getaran bumi akibat pelepasan energi dari dalam perut bumi secara tiba-tiba.",
        "banjir": "Genangan air yang merendam daratan akibat curah hujan tinggi atau luapan sungai.",
        "tsunami": "Gelombang laut besar yang dipicu oleh gempa bawah laut atau letusan gunung.",
        "gunung_meletus": "Letusan gunung berapi yang mengeluarkan magma, abu, dan gas panas.",
        "angin_topan": "Pusaran angin kencang dengan kecepatan tinggi yang merusak.",
        "tanah_longsor": "Pergerakan massa tanah atau batuan menuruni lereng secara tiba-tiba.",
        "kebakaran_hutan": "Api yang menyebar tak terkendali di area hutan atau lahan gambut.",
        "kekeringan": "Krisis pasokan air berkepanjangan akibat curah hujan di bawah normal.",
    }

    # Hero Section
    _video_url = "https://res.cloudinary.com/dbf3jpzm0/video/upload/v1780148457/13644081_3840_2160_60fps_cfoirx.mp4"
    st.markdown(f"""
    <style>
        .stApp {{
            background: transparent !important;
        }}
    </style>
    <video class="bg-video" autoplay muted loop playsinline>
        <source src="{_video_url}" type="video/mp4">
    </video>
    <div class="bg-video-overlay"></div>
    <div class="hero-section">
        <div class="hero-content">
            <h1>SIAP <span class="highlight">HADAPI</span><br>BENCANA ALAM</h1>
            <p>Pusat informasi dan edukasi kebencanaan untuk Indonesia. Pelajari, pahami, dan siagakan dirimu.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hero action buttons — centered side-by-side using custom HTML & CSS links
    st.markdown("""
    <div class="hero-actions">
        <a class="hero-btn primary" href="?page=Edukasi" target="_self">📚 Mulai Belajar</a>
        <a class="hero-btn secondary" href="?page=Tentang" target="_self">📊 Lihat Statistik</a>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    st.markdown("")
    stats_cols = st.columns(4)
    stats_data = [
        ("8", "Jenis Bencana", "#FF6B35"),
        ("127", "Gunung Aktif", "#EF476F"),
        ("500K", "Gempa/Tahun", "#118AB2"),
        ("40%", "Zona Rawan", "#06D6A0"),
    ]
    for i, (num, label, color) in enumerate(stats_data):
        with stats_cols[i]:
            st.markdown(
                f'<div class="stat-box"><div class="num" style="color:{color}">{num}</div>'
                f'<div class="label">{label}</div></div>',
                unsafe_allow_html=True
            )

    st.markdown("---")

    # Featured disasters
    st.markdown('<div class="section-title" id="mulai">📚 Jenis Bencana</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:rgba(255, 253, 247, 0.6);font-weight:500;margin-bottom:1.5rem;">Pelajari 8 jenis bencana alam utama di Indonesia</p>', unsafe_allow_html=True)

    card_color_map = {
        "gempa_bumi": "card-gempa",
        "tsunami": "card-tsunami",
        "banjir": "card-banjir",
        "gunung_meletus": "card-gunung",
        "angin_topan": "card-angin",
        "tanah_longsor": "card-longsor",
        "kebakaran_hutan": "card-kebakaran",
        "kekeringan": "card-kekeringan",
    }

    featured = ["gempa_bumi", "tsunami", "banjir", "gunung_meletus"]
    fcols = st.columns(4)
    for i, key in enumerate(featured):
        with fcols[i]:
            info = DISASTER_INFO[key]
            cc = card_color_map.get(key, "")
            st.markdown(
                f"""
                <a href="?disaster={key}" target="_self" style="text-decoration:none;">
                    <div class="disaster-card {cc}">
                        <div class="card-icon">{icons_map.get(key, "⚠️")}</div>
                        <div>
                            <h3>{info["nama"]}</h3>
                            <p>{desc_map.get(key, "")[:100]}...</p>
                        </div>
                        <div class="learn-more-text">Pelajari Selengkapnya →</div>
                    </div>
                </a>
                """,
                unsafe_allow_html=True
            )

    # More disasters
    st.markdown("")
    more = ["angin_topan", "tanah_longsor", "kebakaran_hutan", "kekeringan"]
    mcols = st.columns(4)
    for i, key in enumerate(more):
        with mcols[i]:
            info = DISASTER_INFO[key]
            cc = card_color_map.get(key, "")
            st.markdown(
                f"""
                <a href="?disaster={key}" target="_self" style="text-decoration:none;">
                    <div class="disaster-card {cc}">
                        <div class="card-icon">{icons_map.get(key, "⚠️")}</div>
                        <div>
                            <h3>{info["nama"]}</h3>
                            <p>{desc_map.get(key, "")[:100]}...</p>
                        </div>
                        <div class="learn-more-text">Pelajari Selengkapnya →</div>
                    </div>
                </a>
                """,
                unsafe_allow_html=True
            )

    st.markdown("---")

    # Safety CTA
    cta_cols = st.columns(2)
    with cta_cols[0]:
        st.markdown(
            '<div class="brutal-card" style="background:#FFD166;">'
            '<h3 style="-webkit-text-fill-color:#000;">\U0001F6E1\uFE0F SIAP SIAGA BENCANA</h3>'
            '<p style="color:#000;font-weight:500;">Ketahui langkah-langkah penyelamatan diri untuk setiap jenis bencana. Jangan panik, tetap siap siaga!</p>'
            '</div>',
            unsafe_allow_html=True
        )
        
        if st.button("\U0001F4D6 Lihat Panduan", key="cta_panduan"):
            st.session_state.page = "Edukasi"
            st.query_params["page"] = "Edukasi"
            st.rerun()
    with cta_cols[1]:
        st.markdown(
            '<div class="brutal-card" style="background:#06D6A0;">'
            '<h3 style="-webkit-text-fill-color:#000;">\U0001F916 TANYA CHATBOT</h3>'
            '<p style="color:#000;font-weight:500;">Punya pertanyaan spesifik? Tanyakan langsung pada asisten edukasi bencana alam kami.</p>'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("\U0001F4AC Tanya Sekarang", key="cta_tanya"):
            st.session_state.page = "Chatbot"
            st.query_params["page"] = "Chatbot"
            st.rerun()

# ─── Halaman: Edukasi ─────────────────────────────────────────
elif st.session_state.page == "Edukasi":
    _pc = {"particles":{"number":{"value":35,"density":{"enable":True,"value_area":900}},"color":{"value":["#FFD166","#FF6B35","#EF476F","#06D6A0","#118AB2","#B07FFF"]},"shape":{"type":["circle","triangle","polygon","star","edge"],"stroke":{"width":0,"color":"#000000"},"polygon":{"nb_sides":5}},"opacity":{"value":0.6,"random":True,"anim":{"enable":True,"speed":0.8,"opacity_min":0.2,"sync":False}},"size":{"value":12,"random":True,"anim":{"enable":True,"speed":2,"size_min":4,"sync":False}},"line_linked":{"enable":False},"move":{"enable":True,"speed":0.8,"direction":"none","random":True,"straight":False,"out_mode":"out","bounce":False,"attract":{"enable":False,"rotateX":600,"rotateY":1200}}},"interactivity":{"detect_on":"window","events":{"onhover":{"enable":True,"mode":"bubble"},"onclick":{"enable":True,"mode":"push"},"resize":True},"modes":{"bubble":{"distance":200,"size":16,"duration":2,"opacity":0.8,"speed":3},"push":{"particles_nb":3}}},"retina_detect":True}
    _inject_particles(_pc)
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(
                180deg,
                rgba(11, 26, 16, 0.6) 0%,
                rgba(10, 31, 40, 0.7) 50%,
                rgba(19, 45, 32, 0.8) 100%
            ), url("/app/static/bg_nature.png") no-repeat center center !important;
            background-size: cover !important;
            background-attachment: fixed !important;
        }
    </style>
    """, unsafe_allow_html=True)
    disasters = get_disaster_names()
    icons_map = {
        "gempa_bumi": "\U0001F30D", "banjir": "\U0001F30A", "tsunami": "\U0001F30A",
        "gunung_meletus": "\U0001F30B", "angin_topan": "\U0001F300",
        "tanah_longsor": "\U0001F5FB", "kebakaran_hutan": "\U0001F525", "kekeringan": "\u2600\uFE0F"
    }
    color_map = {
        "gempa_bumi": ("#EF476F", "red"),
        "banjir": ("#118AB2", "blue"),
        "tsunami": ("#06D6A0", "green"),
        "gunung_meletus": ("#FF6B35", "orange"),
        "angin_topan": ("#B07FFF", "purple"),
        "tanah_longsor": ("#FF6B9D", "pink"),
        "kebakaran_hutan": ("#FF6B35", "orange"),
        "kekeringan": ("#FFD166", "yellow"),
    }

    # Animated header
    st.markdown("""
    <div class="edu-page-header">
        <h1>📚 <span class="accent">Edukasi</span> Bencana Alam</h1>
        <p>Pilih jenis bencana di bawah ini untuk mempelajari informasi lengkap</p>
    </div>
    """, unsafe_allow_html=True)

    # Auto-select from filter
    f = st.session_state.disaster_filter
    if f and f in disasters:
        st.session_state.selected_disaster = f
        st.session_state.disaster_filter = None

    # Build disaster selector grid
    all_keys = list(disasters.keys())
    selected = st.session_state.selected_disaster

    # Render as clickable selector cards (4 per row)
    selector_cols = st.columns(4)
    for i, key in enumerate(all_keys):
        info = DISASTER_INFO[key]
        icon = icons_map.get(key, "⚠️")
        is_active = (selected == key)
        active_class = "active" if is_active else ""
        delay = i * 0.08

        with selector_cols[i % 4]:
            st.markdown(
                f'<div class="disaster-select-card {active_class}" style="animation-delay:{delay}s;">'
                f'<span class="card-emoji">{icon}</span>'
                f'<span class="card-name">{info["nama"]}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            if st.button(f"{'✦ ' if is_active else ''}{info['nama']}", key=f"sel_{key}",
                         help=f"Lihat detail {info['nama']}"):
                st.session_state.selected_disaster = key if not is_active else None
                st.rerun()

    # Detail panel for selected disaster
    if selected and selected in DISASTER_INFO:
        info = DISASTER_INFO[selected]
        icon = icons_map.get(selected, "⚠️")
        accent_color, accent_class = color_map.get(selected, ("#FFD166", "yellow"))

        st.markdown(f"""
        <div class="edu-detail-panel">
            <div class="edu-detail-title">
                <span class="title-emoji">{icon}</span>
                {info['nama']}
            </div>
            <div class="edu-detail-subtitle">{info['nama_inggris']}</div>
            <div class="edu-definition">{info['definisi']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Info blocks in columns
        col1, col2 = st.columns(2)

        with col1:
            # Penyebab
            items_html = ""
            for p in info["penyebab"]:
                items_html += f'<li><span class="li-marker">▸</span> {p}</li>'
            st.markdown(f"""
            <div class="edu-info-block accent-{accent_class}" style="animation-delay:0.1s;">
                <div class="block-title"><span class="block-icon">💡</span> Penyebab</div>
                <ul>{items_html}</ul>
            </div>
            """, unsafe_allow_html=True)

            # Tanda-tanda
            items_html = ""
            for t in info["tanda"]:
                items_html += f'<li><span class="li-marker">▸</span> {t}</li>'
            st.markdown(f"""
            <div class="edu-info-block accent-blue" style="animation-delay:0.2s;">
                <div class="block-title"><span class="block-icon">🔍</span> Tanda-tanda</div>
                <ul>{items_html}</ul>
            </div>
            """, unsafe_allow_html=True)

            # Mitigasi
            items_html = ""
            for m in info["mitigasi"]:
                items_html += f'<li><span class="li-marker">▸</span> {m}</li>'
            st.markdown(f"""
            <div class="edu-info-block accent-green" style="animation-delay:0.3s;">
                <div class="block-title"><span class="block-icon">🛡️</span> Mitigasi</div>
                <ul>{items_html}</ul>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # Saat Terjadi
            items_html = ""
            for s in info["saat_terjadi"]:
                items_html += f'<li><span class="li-marker">▸</span> {s}</li>'
            st.markdown(f"""
            <div class="edu-info-block accent-orange" style="animation-delay:0.15s;">
                <div class="block-title"><span class="block-icon">💥</span> Saat Terjadi</div>
                <ul>{items_html}</ul>
            </div>
            """, unsafe_allow_html=True)

            # Setelah Terjadi
            items_html = ""
            for s in info["setelah_terjadi"]:
                items_html += f'<li><span class="li-marker">▸</span> {s}</li>'
            st.markdown(f"""
            <div class="edu-info-block accent-purple" style="animation-delay:0.25s;">
                <div class="block-title"><span class="block-icon">📌</span> Setelah Terjadi</div>
                <ul>{items_html}</ul>
            </div>
            """, unsafe_allow_html=True)

            # Lottie animation
            lottie_map = {
                "gempa_bumi": "https://assets9.lottiefiles.com/packages/lf20_w51pcehl.json",
                "banjir": "https://assets10.lottiefiles.com/packages/lf20_5njp3vgg.json",
                "tsunami": "https://assets4.lottiefiles.com/packages/lf20_b7tq4kqu.json",
                "gunung_meletus": "https://assets5.lottiefiles.com/packages/lf20_h3h37bdf.json",
                "angin_topan": "https://assets10.lottiefiles.com/packages/lf20_tuxc1gip.json",
                "tanah_longsor": "https://assets1.lottiefiles.com/packages/lf20_T3hyg2.json",
                "kebakaran_hutan": "https://assets3.lottiefiles.com/packages/lf20_9i1t48qy.json",
                "kekeringan": "https://assets1.lottiefiles.com/packages/lf20_3nt7snqy.json"
            }
            lottie_url = lottie_map.get(selected)
            if lottie_url:
                html_code = f"""
                <div style="display:flex;justify-content:center;align-items:center;height:200px;margin:0.5rem 0;">
                    <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
                    <lottie-player src="{lottie_url}" background="transparent" speed="1" style="width:180px;height:180px;" loop autoplay></lottie-player>
                </div>
                """
                st.components.v1.html(html_code, height=210)

        # Fakta Menarik
        st.markdown("""
        <div style="margin-top:1rem; margin-bottom:0.5rem;">
            <span style="font-size:1.1rem;font-weight:700;color:#FFD166;text-transform:uppercase;letter-spacing:0.5px;">
                ✨ Fakta Menarik
            </span>
        </div>
        """, unsafe_allow_html=True)

        fact_cols = st.columns(2)
        for i, fact in enumerate(info["fakta"]):
            with fact_cols[i % 2]:
                delay = i * 0.1
                st.markdown(f"""
                <div class="fact-card" style="animation-delay:{delay}s;">
                    <div class="fact-label">Fakta #{i+1}</div>
                    <div class="fact-text">{fact}</div>
                </div>
                """, unsafe_allow_html=True)

        # Ask chatbot button
        st.markdown('<div class="edu-btn" style="max-width:350px;margin-top:1rem;">', unsafe_allow_html=True)
        if st.button(f"🤖 Tanya Chatbot tentang {info['nama']}", key=f"ask_{selected}"):
            st.session_state.messages.append({"role": "user", "content": f"Apa itu {info['nama'].lower()}?"})
            resp = get_response(f"Apa itu {info['nama'].lower()}?")
            st.session_state.messages.append({"role": "bot", "content": resp})
            st.session_state.page = "Chatbot"
            st.query_params["page"] = "Chatbot"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    elif not selected:
        # Show prompt to select
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;animation:fadeInUp 0.6s ease;">
            <div style="font-size:4rem;margin-bottom:1rem;animation:float 3s ease-in-out infinite;">👆</div>
            <p style="color:rgba(255,253,247,0.5);font-size:1.1rem;font-weight:600;">
                Pilih salah satu bencana di atas untuk melihat informasi lengkap
            </p>
        </div>
        """, unsafe_allow_html=True)

# ─── Halaman: Chatbot ──────────────────────────────────────────
elif st.session_state.page == "Chatbot":
    _pc = {"particles":{"number":{"value":35,"density":{"enable":True,"value_area":900}},"color":{"value":["#06D6A0","#118AB2","#FFD166","#FF6B35","#B07FFF","#EF476F"]},"shape":{"type":["circle","triangle","polygon","star","edge"],"stroke":{"width":0,"color":"#000000"},"polygon":{"nb_sides":5}},"opacity":{"value":0.6,"random":True,"anim":{"enable":True,"speed":0.8,"opacity_min":0.2,"sync":False}},"size":{"value":12,"random":True,"anim":{"enable":True,"speed":2,"size_min":4,"sync":False}},"line_linked":{"enable":False},"move":{"enable":True,"speed":0.8,"direction":"none","random":True,"straight":False,"out_mode":"out","bounce":False,"attract":{"enable":False,"rotateX":600,"rotateY":1200}}},"interactivity":{"detect_on":"window","events":{"onhover":{"enable":True,"mode":"bubble"},"onclick":{"enable":True,"mode":"push"},"resize":True},"modes":{"bubble":{"distance":200,"size":16,"duration":2,"opacity":0.8,"speed":3},"push":{"particles_nb":3}}},"retina_detect":True}
    _inject_particles(_pc)
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(
                180deg,
                rgba(11, 26, 16, 0.6) 0%,
                rgba(10, 31, 40, 0.7) 50%,
                rgba(19, 45, 32, 0.8) 100%
            ), url("/app/static/bg_nature.png") no-repeat center center !important;
            background-size: cover !important;
            background-attachment: fixed !important;
        }
    </style>
    """, unsafe_allow_html=True)
    # Modern header
    st.markdown("""
    <div class="chat-page-header">
        <h1>🤖 <span class="chat-accent">Chatbot</span> Edukasi</h1>
        <p>Tanyakan apa pun tentang bencana alam, mitigasi, dan penyelamatan diri</p>
    </div>
    """, unsafe_allow_html=True)

    chat_col, tips_col = st.columns([2.5, 1.5])

    with chat_col:
        # Modern chat messages placeholder
        chat_placeholder = st.empty()
        
        def render_chat(show_thinking=False):
            chat_html = '<div class="chat-modern" id="chat-messages-box">'
            for msg in st.session_state.messages:
                role = msg["role"]
                if role == "user":
                    chat_html += (
                        f'<div class="chat-bubble user-bubble">'
                        f'<div class="chat-sender">Anda</div>'
                        f'{msg["content"]}'
                        f'</div>'
                    )
                else:
                    bot_content = markdown.markdown(msg["content"])
                    chat_html += (
                        f'<div class="chat-bubble bot-bubble">'
                        f'<div class="chat-sender">🤖 Asisten</div>'
                        f'{bot_content}'
                        f'</div>'
                    )
            if show_thinking:
                chat_html += (
                    f'<div class="chat-bubble bot-bubble">'
                    f'<div class="chat-sender">🤖 Asisten</div>'
                    f'<div class="typing-indicator">'
                    f'<div class="typing-dot"></div>'
                    f'<div class="typing-dot"></div>'
                    f'<div class="typing-dot"></div>'
                    f'</div>'
                    f'</div>'
                )
            chat_html += '</div>'
            chat_placeholder.markdown(chat_html, unsafe_allow_html=True)
            # Inject auto-scroll via components.v1.html so JS actually runs
            import time
            timestamp = int(time.time() * 1000)
            st.components.v1.html(
                f"""
                <script id="scroll-{timestamp}">
                (function scroll() {{
                    // Walk up into the parent Streamlit frames to find .chat-modern
                    function tryScroll(win) {{
                        try {{
                            var el = win.document.getElementById('chat-messages-box');
                            if (!el) el = win.document.querySelector('.chat-modern');
                            if (el) {{ el.scrollTop = el.scrollHeight; return true; }}
                        }} catch(e) {{}}
                        return false;
                    }}
                    // Try current window first, then parent chain
                    if (!tryScroll(window)) {{
                        var w = window;
                        for (var i = 0; i < 5; i++) {{
                            try {{ w = w.parent; if (tryScroll(w)) break; }} catch(e) {{ break; }}
                        }}
                    }}
                    // Retry a few times to handle rendering delays
                    setTimeout(function() {{ tryScroll(window); try{{ tryScroll(window.parent); }}catch(e){{}} }}, 100);
                    setTimeout(function() {{ tryScroll(window); try{{ tryScroll(window.parent); }}catch(e){{}} }}, 300);
                    setTimeout(function() {{ tryScroll(window); try{{ tryScroll(window.parent); }}catch(e){{}} }}, 600);
                }})();
                </script>
                """,
                height=0
            )

        # Initial render
        render_chat(show_thinking=False)

        # Chat input
        st.markdown('<div class="chat-input-area">', unsafe_allow_html=True)
        prompt = st.chat_input("Tanya tentang bencana alam...")
        st.markdown('</div>', unsafe_allow_html=True)

        # Clear button
        st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
        clear_clicked = st.button("🧹 Hapus Percakapan", key="clear_chat")
        st.markdown('</div>', unsafe_allow_html=True)

        if clear_clicked:
            st.session_state.messages = []
            st.session_state.messages.append({
                "role": "bot",
                "content": "Halo! Saya asisten edukasi bencana alam. Tanyakan apa saja tentang bencana alam, cara mitigasi, atau langkah penyelamatan diri!"
            })
            st.rerun()

    with tips_col:
        # Quick questions
        st.markdown(
            '<div class="tips-card" style="animation-delay:0.1s;">'
            '<h3>💬 Contoh Pertanyaan</h3>'
            '<p>Klik salah satu untuk langsung bertanya</p>'
            '</div>',
            unsafe_allow_html=True
        )

        examples = [
            ("Apa itu tsunami?", "🌊"),
            ("Penyebab gempa bumi", "🌍"),
            ("Cara menghadapi banjir", "🌧️"),
            ("Tanda-tanda gunung meletus", "🌋"),
            ("Mitigasi tanah longsor", "⛰️"),
            ("Nomor darurat bencana", "📞"),
        ]

        st.markdown('<div class="chat-actions">', unsafe_allow_html=True)
        ex_clicked = None
        for ex_text, ex_icon in examples:
            if st.button(f"{ex_icon} {ex_text}", key=f"ex_{ex_text.replace(' ', '_')}"):
                ex_clicked = ex_text
        st.markdown('</div>', unsafe_allow_html=True)

        # Emergency card
        st.markdown(
            '<div class="emergency-card">'
            '<h3>⚠️ Darurat?</h3>'
            '<p class="e-line">📞 <strong>Darurat Nasional:</strong> 112</p>'
            '<p class="e-line">📞 <strong>BMKG:</strong> 021-6546318</p>'
            '<p class="e-line">📞 <strong>BNPB:</strong> 021-29887300</p>'
            '<p class="e-line">📞 <strong>PMI:</strong> 021-7993006</p>'
            '</div>',
            unsafe_allow_html=True
        )

    # Process prompt or example question click AFTER layout generation is complete
    active_prompt = prompt or ex_clicked
    if active_prompt:
        # 1. Append user prompt and render
        st.session_state.messages.append({"role": "user", "content": active_prompt})
        render_chat(show_thinking=True)
        
        # 2. Add a small artificial sleep of 0.8s for the "thinking" animation effect to feel realistic
        import time
        time.sleep(0.8)
        
        # 3. Get response from LLM / database
        response = get_response(active_prompt)
        st.session_state.messages.append({"role": "bot", "content": response})
        
        # 4. Rerun so it displays the final message and clears st.chat_input
        st.rerun()

# ─── Halaman: Tentang ─────────────────────────────────────────
elif st.session_state.page == "Tentang":
    _pc = {"particles":{"number":{"value":35,"density":{"enable":True,"value_area":900}},"color":{"value":["#118AB2","#B07FFF","#06D6A0","#FFD166","#EF476F","#FF6B35"]},"shape":{"type":["circle","triangle","polygon","star","edge"],"stroke":{"width":0,"color":"#000000"},"polygon":{"nb_sides":5}},"opacity":{"value":0.6,"random":True,"anim":{"enable":True,"speed":0.8,"opacity_min":0.2,"sync":False}},"size":{"value":12,"random":True,"anim":{"enable":True,"speed":2,"size_min":4,"sync":False}},"line_linked":{"enable":False},"move":{"enable":True,"speed":0.8,"direction":"none","random":True,"straight":False,"out_mode":"out","bounce":False,"attract":{"enable":False,"rotateX":600,"rotateY":1200}}},"interactivity":{"detect_on":"window","events":{"onhover":{"enable":True,"mode":"bubble"},"onclick":{"enable":True,"mode":"push"},"resize":True},"modes":{"bubble":{"distance":200,"size":16,"duration":2,"opacity":0.8,"speed":3},"push":{"particles_nb":3}}},"retina_detect":True}
    _inject_particles(_pc)
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(
                180deg,
                rgba(11, 26, 16, 0.6) 0%,
                rgba(10, 31, 40, 0.7) 50%,
                rgba(19, 45, 32, 0.8) 100%
            ), url("/app/static/bg_nature.png") no-repeat center center !important;
            background-size: cover !important;
            background-attachment: fixed !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Animated page header
    st.markdown("""
    <div class="edu-page-header">
        <h1>ℹ️ <span class="accent">Tentang</span> Platform</h1>
        <p>Informasi lengkap tentang platform edukasi bencana alam ini</p>
    </div>
    """, unsafe_allow_html=True)

    acerca, sumber = st.columns(2)

    with acerca:
        st.markdown(
            '<div class="detail-section" style="animation-delay:0.1s;">'
            '<h2>🌏 Tentang Platform Ini</h2>'
            '<div class="subtitle">Edukasi &amp; Kesiapsiagaan Bencana</div>'
            '<p>'
            "Platform ini bertujuan untuk memberikan edukasi dan informasi kebencanaan kepada masyarakat Indonesia. "
            "Dengan memahami jenis-jenis bencana alam, penyebab, tanda-tanda, serta langkah mitigasi dan penyelamatan diri, "
            "diharapkan masyarakat dapat lebih siap dan tanggap dalam menghadapi situasi darurat bencana alam."
            '</p>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="detail-section" style="animation-delay:0.2s;">'
            '<h2>✨ Fitur</h2>'
            '<div class="subtitle">Apa yang bisa kamu lakukan</div>'
            '<ul>'
            '<li>Mempelajari <strong>8 jenis bencana alam</strong> utama di Indonesia</li>'
            '<li>Informasi lengkap: definisi, penyebab, tanda, mitigasi, langkah evakuasi</li>'
            '<li>Fakta-fakta menarik dan unik tentang bencana alam</li>'
            '<li>Chatbot interaktif untuk tanya-jawab cepat</li>'
            '<li>Kontak darurat resmi (BMKG, BNPB, dll)</li>'
            '</ul>'
            '</div>',
            unsafe_allow_html=True
        )

    with sumber:
        st.markdown(
            '<div class="detail-section accent-yellow" style="animation-delay:0.15s;">'
            '<h2>📚 Sumber Data</h2>'
            '<div class="subtitle">Informasi dari lembaga resmi</div>'
            '<ul>'
            '<li><strong>BMKG</strong> (Badan Meteorologi, Klimatologi, dan Geofisika)</li>'
            '<li><strong>BNPB</strong> (Badan Nasional Penanggulangan Bencana)</li>'
            '<li><strong>PVMBG</strong> (Pusat Vulkanologi dan Mitigasi Bencana Geologi)</li>'
            '<li><strong>PMI</strong> (Palang Merah Indonesia)</li>'
            '<li><strong>UNESCO</strong> — Pendidikan kebencanaan global</li>'
            '</ul>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="detail-section accent-blue-solid" style="animation-delay:0.25s;">'
            '<h2>📞 Kontak Darurat</h2>'
            '<div class="subtitle">Simpan nomor ini!</div>'
            '<ul>'
            '<li>\U0001F4DE <strong>Call Center Darurat Nasional:</strong> 112</li>'
            '<li>\U0001F4DE <strong>BMKG (Info Gempa):</strong> 021-6546318</li>'
            '<li>\U0001F4DE <strong>BNPB:</strong> 021-29887300</li>'
            '<li>\U0001F4DE <strong>PMI:</strong> 021-7993006</li>'
            '<li>\U0001F4DE <strong>PVMBG:</strong> 022-7271723</li>'
            '</ul>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="detail-section accent-green-solid" style="animation-delay:0.3s;">'
            '<h2>⚙️ Tech Stack</h2>'
            '<div class="subtitle">Dibuat dengan</div>'
            '<ul>'
            "<li><strong>Python</strong> \u2014 Backend & logika chatbot</li>"
            "<li><strong>Streamlit</strong> \u2014 Frontend web</li>"
            "<li><strong>Dark Glassmorphism</strong> \u2014 Desain UI</li>"
            '</ul>'
            '</div>',
            unsafe_allow_html=True
        )

# ─── Footer ────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">'
    '\U0001F30B Edukasi Bencana Alam &mdash; Siaga untuk Selamat &mdash;'
    '<br>Data bersumber dari BMKG, BNPB, dan PVMBG'
    '</div>',
    unsafe_allow_html=True
)
