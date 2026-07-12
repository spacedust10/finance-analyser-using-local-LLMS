"""The Private Ledger — design system.

Two palettes (ink-dark, paper-light) selected at render time from
st.context.theme.type. Fraunces (serif display) for the masthead,
IBM Plex Sans for body, IBM Plex Mono with tabular numerals for money.
"""

PALETTES = {
    "dark": dict(
        ink="#0D1210", card="#151C18", paper="#F4EFE6", muted="#8A948C",
        emerald="#4FCE8B", mint="#7ADFA9", amber="#E0A458", rose="#E2606B",
        hairline="rgba(244,239,230,0.14)", grain="rgba(244,239,230,0.025)",
    ),
    "light": dict(
        ink="#F7F3EA", card="#FFFDF8", paper="#1C231F", muted="#6B746D",
        emerald="#1F9D5B", mint="#177A46", amber="#B97F2A", rose="#C43D49",
        hairline="rgba(28,35,31,0.16)", grain="rgba(28,35,31,0.03)",
    ),
}

class AppStyles:

    @staticmethod
    def palette(theme: str) -> dict:
        return PALETTES[theme if theme in PALETTES else "dark"]

    @staticmethod
    def _vars(c: dict) -> str:
        return (f"--card: {c['card']}; --paper: {c['paper']}; --muted: {c['muted']}; "
                f"--emerald: {c['emerald']}; --mint: {c['mint']}; --amber: {c['amber']}; "
                f"--rose: {c['rose']}; --hairline: {c['hairline']};")

    @staticmethod
    def css(theme: str) -> str:
        c = AppStyles.palette(theme)
        return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

    /* server-known theme is the default; the theme-sync observer flips the
       data attribute instantly when the user switches via the app menu */
    :root {{ {AppStyles._vars(c)} }}
    html[data-ledger-theme="dark"] {{ {AppStyles._vars(PALETTES['dark'])} }}
    html[data-ledger-theme="light"] {{ {AppStyles._vars(PALETTES['light'])} }}

    /* hidden rerun trigger for the theme-sync observer */
    .st-key-theme_refresh {{ display: none; }}

    html, body, [class*="css"], .stMarkdown, p, li {{
        font-family: 'IBM Plex Sans', sans-serif;
    }}

    /* faint paper grain */
    .stApp {{
        background-image: radial-gradient({c['grain']} 1px, transparent 1px);
        background-size: 22px 22px;
    }}

    h1, h2, h3 {{ font-family: 'Fraunces', Georgia, serif; letter-spacing: 0.01em; }}

    /* ── masthead ── */
    .ledger-masthead {{
        border-top: 3px double var(--hairline);
        border-bottom: 1px solid var(--hairline);
        padding: 1.4rem 0 1.1rem 0;
        margin-bottom: 1rem;
        text-align: center;
    }}
    .ledger-masthead .kicker {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.32em;
        text-transform: uppercase;
        color: var(--emerald);
        margin-bottom: 0.5rem;
    }}
    .ledger-masthead h1 {{
        font-family: 'Fraunces', Georgia, serif;
        font-weight: 600;
        font-size: 2.7rem;
        line-height: 1.05;
        margin: 0;
        color: var(--paper);
    }}
    .ledger-masthead .tagline {{
        font-size: 0.95rem;
        color: var(--muted);
        margin-top: 0.5rem;
        font-style: italic;
        font-family: 'Fraunces', Georgia, serif;
    }}

    /* ── ledger metric cards ── */
    .ledger-card {{
        background: var(--card);
        border: 1px solid var(--hairline);
        border-top: 2px solid var(--accent, var(--emerald));
        border-radius: 4px;
        padding: 1.05rem 1.15rem 0.95rem;
        margin: 0.25rem 0;
    }}
    .ledger-card .label {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--muted);
        margin-bottom: 0.45rem;
    }}
    .ledger-card .value {{
        font-family: 'IBM Plex Mono', monospace;
        font-variant-numeric: tabular-nums;
        font-size: 1.75rem;
        font-weight: 500;
        color: var(--accent, var(--paper));
        line-height: 1.1;
    }}
    .ledger-card .delta {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        color: var(--muted);
        margin-top: 0.35rem;
    }}

    /* ── empty state ── */
    .ledger-empty {{
        border: 1px dashed var(--hairline);
        border-radius: 6px;
        padding: 3.2rem 2rem;
        text-align: center;
        margin: 2rem 0;
    }}
    .ledger-empty h2 {{
        font-family: 'Fraunces', Georgia, serif;
        color: var(--paper);
        margin-bottom: 0.4rem;
    }}
    .ledger-empty p {{ color: var(--muted); margin: 0; }}

    /* ── status chips ── */
    .ledger-chips {{ margin: 0.2rem 0 0.8rem 0; }}
    .ledger-chip {{
        display: inline-block;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        border: 1px solid var(--hairline);
        border-radius: 999px;
        padding: 0.25rem 0.75rem;
        margin-right: 0.5rem;
        color: var(--muted);
    }}
    .ledger-chip.on {{ color: var(--emerald); border-color: var(--emerald); }}

    /* ── streamlit chrome ── */
    .stButton > button {{
        font-family: 'IBM Plex Mono', monospace;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-size: 0.78rem;
        border: 1px solid var(--hairline);
        border-radius: 4px;
        transition: border-color 0.15s ease, color 0.15s ease;
    }}
    .stButton > button:hover {{
        border-color: var(--emerald);
        color: var(--emerald);
    }}
    /* nav: segmented control reads as chunky buttons */
    [data-testid="stButtonGroup"] button {{
        font-family: 'IBM Plex Mono', monospace;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        font-size: 0.8rem;
        padding: 0.55rem 1.4rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-family: 'IBM Plex Mono', monospace;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        font-size: 0.78rem;
    }}
    [data-testid="stSidebar"] {{
        border-right: 1px solid var(--hairline);
    }}
    [data-testid="stSidebar"] .stMarkdown h3 {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.24em;
        text-transform: uppercase;
        color: var(--muted);
    }}
    [data-testid="stMetricValue"] {{
        font-family: 'IBM Plex Mono', monospace;
        font-variant-numeric: tabular-nums;
    }}
    [data-testid="stChatMessage"] {{
        background: var(--card);
        border: 1px solid var(--hairline);
        border-radius: 6px;
    }}
    </style>
    """
