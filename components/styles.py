import streamlit as st

_CSS = """
<link rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"
      crossorigin="anonymous" referrerpolicy="no-referrer"/>
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #2d5a8e);
        border-radius: 12px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .metric-card .card-icon  { font-size: 1.6rem; opacity: 0.9; margin-bottom: 6px; }
    .metric-card .card-label { font-size: 0.8rem; opacity: 0.75; letter-spacing: 0.05em; text-transform: uppercase; }
    .metric-card .card-value { font-size: 1.5rem; font-weight: 700; margin-top: 4px; }
    .metric-card .card-delta { font-size: 0.75rem; margin-top: 6px; font-weight: 600; }
    .metric-card .delta-up   { color: #a8f5c2; }
    .metric-card .delta-down { color: #ffb3b3; }
    .metric-card .delta-neu  { color: rgba(255,255,255,0.5); }

    .insight-card {
        background: #f0f4ff;
        border-left: 4px solid #2d5a8e;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 6px 0;
        color: #1a1a2e;
    }
    .insight-card i { color: #2d5a8e; margin-right: 8px; }

    .alert-card {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 6px 0;
        color: #856404;
    }
    .alert-card i { color: #856404; margin-right: 8px; }

    .alert-danger {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 6px 0;
        color: #721c24;
    }
    .alert-danger i { color: #dc3545; margin-right: 8px; }

    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1e3a5f;
        margin: 24px 0 12px 0;
        border-bottom: 2px solid #2d5a8e;
        padding-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-title i { color: #2d5a8e; font-size: 1.1rem; }
</style>
"""


def inject_styles() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def sec(icon: str, label: str) -> str:
    return f'<div class="section-title"><i class="fa-solid fa-{icon}"></i>{label}</div>'
