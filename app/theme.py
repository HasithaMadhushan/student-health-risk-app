from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemePalette:
    primary: str
    on_primary: str
    accent: str
    background: str
    foreground: str
    surface: str
    muted_surface: str
    border: str
    destructive: str


LIGHT_THEME = ThemePalette(
    primary="#187C72",
    on_primary="#FFFFFF",
    accent="#4F8F79",
    background="#F7F8F4",
    foreground="#17324D",
    surface="#FFFFFF",
    muted_surface="#EAF3EE",
    border="#D8E2DC",
    destructive="#B42318",
)

DARK_THEME = ThemePalette(
    primary="#22D3EE",
    on_primary="#082F49",
    accent="#34D399",
    background="#081F29",
    foreground="#F0FDFF",
    surface="#102F3B",
    muted_surface="#163E4A",
    border="#155E75",
    destructive="#F87171",
)


def _relative_luminance(hex_colour: str) -> float:
    raw = hex_colour.removeprefix("#")
    if len(raw) != 6:
        raise ValueError("Colour must use six-digit hexadecimal notation")
    channels = tuple(int(raw[index : index + 2], 16) / 255 for index in (0, 2, 4))
    linear = tuple(
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    )
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(foreground: str, background: str) -> float:
    lighter, darker = sorted(
        (_relative_luminance(foreground), _relative_luminance(background)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def _properties(palette: ThemePalette) -> str:
    return f"""
    --app-primary: {palette.primary};
    --app-on-primary: {palette.on_primary};
    --app-accent: {palette.accent};
    --app-background: {palette.background};
    --app-foreground: {palette.foreground};
    --app-surface: {palette.surface};
    --app-muted-surface: {palette.muted_surface};
    --app-border: {palette.border};
    --app-destructive: {palette.destructive};
    """


def build_theme_css(theme_override: str | None = None) -> str:
    if theme_override not in (None, "light", "dark"):
        raise ValueError("Theme override must be light, dark or None")
    forced_properties = (
        _properties(DARK_THEME if theme_override == "dark" else LIGHT_THEME)
        if theme_override is not None
        else ""
    )
    return f"""
<style>
:root {{
{_properties(LIGHT_THEME)}
    --app-alert-surface: #FFF7E8;
    --app-alert-foreground: #62440E;
    --app-muted-text: #5F6F7A;
    --app-focus: #D97706;
}}

@media (prefers-color-scheme: dark) {{
    :root {{
{_properties(DARK_THEME)}
        --app-alert-surface: #0C4A6E;
        --app-alert-foreground: #E0F2FE;
        --app-focus: #FBBF24;
    }}
}}

{f":root {{{forced_properties}}}" if forced_properties else ""}

html,
body,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"] {{
    background-color: var(--app-background) !important;
    color: var(--app-foreground) !important;
}}

[data-testid="stAppViewContainer"] {{
    background-image:
        radial-gradient(circle at top right, color-mix(in srgb, var(--app-primary) 7%, transparent), transparent 28rem);
}}

[data-testid="stMainBlockContainer"] {{
    max-width: 52rem;
    padding-top: 2rem;
    padding-bottom: 3rem;
}}

[data-testid="stMainBlockContainer"] h1 {{
    font-size: clamp(2.25rem, 6vw, 3.4rem);
    line-height: 1.05;
    letter-spacing: -0.035em;
    margin-bottom: 0.55rem;
}}

[data-testid="stMainBlockContainer"] h2,
[data-testid="stMainBlockContainer"] h3 {{
    letter-spacing: -0.018em;
}}

[data-testid="stMainBlockContainer"] h1,
[data-testid="stMainBlockContainer"] h2,
[data-testid="stMainBlockContainer"] h3,
[data-testid="stMainBlockContainer"] h4,
[data-testid="stMainBlockContainer"] p,
[data-testid="stMainBlockContainer"] label,
[data-testid="stMainBlockContainer"] li,
[data-testid="stMainBlockContainer"] small {{
    color: var(--app-foreground) !important;
}}

[data-testid="stMainBlockContainer"] p,
[data-testid="stMainBlockContainer"] label,
[data-testid="stMainBlockContainer"] li {{
    font-size: 1rem;
    line-height: 1.55;
}}

[data-testid="stCaptionContainer"] p {{
    color: var(--app-muted-text) !important;
    opacity: 1;
}}

[data-testid="stAlert"] {{
    background: var(--app-alert-surface) !important;
    border: 1px solid var(--app-border) !important;
    border-radius: 1rem;
    padding: 0.15rem 0.25rem;
}}

[data-testid="stAlert"] p,
[data-testid="stAlert"] div,
[data-testid="stAlert"] svg {{
    color: var(--app-alert-foreground) !important;
    fill: currentColor;
}}

[data-testid="stVerticalBlockBorderWrapper"] {{
    background: var(--app-surface) !important;
    border: 1px solid var(--app-border) !important;
    border-radius: 1rem;
    box-shadow: 0 10px 30px rgba(23, 50, 77, 0.06);
}}

[data-testid="stExpander"] details,
[data-testid="stExpander"] summary {{
    background: var(--app-surface) !important;
    color: var(--app-foreground) !important;
    border-color: var(--app-border) !important;
    border-radius: 0.75rem;
}}

[data-testid="stNumberInput"] input,
[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
[role="listbox"],
[role="option"] {{
    background: var(--app-surface) !important;
    color: var(--app-foreground) !important;
    border-color: var(--app-border) !important;
    min-height: 46px;
}}

[data-testid="stNumberInput"] button {{
    background: var(--app-muted-surface) !important;
    color: var(--app-foreground) !important;
    border-color: var(--app-border) !important;
}}

[data-testid="stCodeBlock"],
[data-testid="stCodeBlock"] pre {{
    overflow-wrap: anywhere;
    white-space: pre-wrap;
}}

code {{
    overflow-wrap: anywhere;
}}

.stButton > button,
[data-testid="stButtonGroup"] button,
[data-testid="stSegmentedControl"] button {{
    min-height: 44px;
    border-radius: 0.875rem;
    font-weight: 650;
    background: var(--app-surface) !important;
    border-color: var(--app-border) !important;
    color: var(--app-foreground) !important;
    cursor: pointer;
    transition: background-color 180ms ease, border-color 180ms ease, color 180ms ease;
}}

[data-testid="stButtonGroup"] button[aria-checked="true"],
[data-testid="stSegmentedControl"] button[aria-checked="true"] {{
    background: var(--app-primary) !important;
    border-color: var(--app-primary) !important;
    color: var(--app-on-primary) !important;
}}

.stButton > button p,
[data-testid="stButtonGroup"] button p,
[data-testid="stSegmentedControl"] button p {{
    color: inherit !important;
}}

.stButton > button[kind="primary"] {{
    background: var(--app-primary) !important;
    border-color: var(--app-primary) !important;
    color: var(--app-on-primary) !important;
    box-shadow: 0 8px 18px rgba(24, 124, 114, 0.18);
}}

.stButton > button[kind="primary"]:hover {{
    background: #12685F !important;
    border-color: #12685F !important;
}}

.stButton > button:not([kind="primary"]) {{
    background: var(--app-surface) !important;
    border-color: var(--app-border) !important;
    color: var(--app-foreground) !important;
}}

.stButton > button:disabled,
input:disabled,
[aria-disabled="true"] {{
    opacity: 0.5;
    cursor: not-allowed;
}}

button:focus-visible,
input:focus-visible,
[role="combobox"]:focus-visible,
summary:focus-visible {{
    outline: 3px solid var(--app-focus) !important;
    outline-offset: 2px;
}}

[data-testid="stProgressBarTrack"] > div {{
    background-color: var(--app-accent) !important;
}}

[data-testid="stProgressBarTrack"] {{
    background-color: var(--app-muted-surface) !important;
}}

[data-testid="stDataFrame"] {{
    border: 1px solid var(--app-border);
    border-radius: 0.75rem;
    overflow: hidden;
}}

[data-testid="stTable"] {{
    border: 1px solid var(--app-border);
    border-radius: 0.75rem;
    overflow: hidden;
}}

[data-testid="stTable"] table,
[data-testid="stTable"] th,
[data-testid="stTable"] td {{
    background: var(--app-surface) !important;
    color: var(--app-foreground) !important;
    border-color: var(--app-border) !important;
}}

#MainMenu {{
    visibility: hidden;
}}

@media (min-width: 1024px) {{
    [data-guide-grid="true"] {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 1rem;
    }}
}}

@media (max-width: 640px) {{
    [data-testid="stMainBlockContainer"] {{
        padding: 1.25rem 1rem 3rem;
    }}

    h1 {{
        font-size: 2rem !important;
        line-height: 1.15 !important;
    }}

    .stButton > button {{
        width: 100%;
    }}
}}

@media (prefers-reduced-motion: reduce) {{
    *,
    *::before,
    *::after {{
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        scroll-behavior: auto !important;
        transition-duration: 0.01ms !important;
    }}
}}
</style>
"""
