from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemePalette:
    primary: str
    primary_hover: str
    on_primary: str
    accent: str
    background: str
    foreground: str
    surface: str
    muted_surface: str
    border: str
    secondary_text: str
    input_border: str
    alert_surface: str
    alert_foreground: str
    focus: str
    destructive: str


LIGHT_THEME = ThemePalette(
    primary="#0F766E",
    primary_hover="#115E59",
    on_primary="#FFFFFF",
    accent="#0D9488",
    background="#F8FAFC",
    foreground="#0F172A",
    surface="#FFFFFF",
    muted_surface="#F1F5F9",
    border="#CBD5E1",
    secondary_text="#475569",
    input_border="#64748B",
    alert_surface="#FEF2F2",
    alert_foreground="#991B1B",
    focus="#0D9488",
    destructive="#B91C1C",
)

DARK_THEME = ThemePalette(
    primary="#5EEAD4",
    primary_hover="#99F6E4",
    on_primary="#042F2E",
    accent="#2DD4BF",
    background="#020617",
    foreground="#F8FAFC",
    surface="#0F172A",
    muted_surface="#1E293B",
    border="#475569",
    secondary_text="#CBD5E1",
    input_border="#94A3B8",
    alert_surface="#450A0A",
    alert_foreground="#FECACA",
    focus="#2DD4BF",
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
    --app-primary-hover: {palette.primary_hover};
    --app-on-primary: {palette.on_primary};
    --app-accent: {palette.accent};
    --app-background: {palette.background};
    --app-foreground: {palette.foreground};
    --app-surface: {palette.surface};
    --app-muted-surface: {palette.muted_surface};
    --app-border: {palette.border};
    --app-secondary-text: {palette.secondary_text};
    --app-input-border: {palette.input_border};
    --app-alert-surface: {palette.alert_surface};
    --app-alert-foreground: {palette.alert_foreground};
    --app-focus: {palette.focus};
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
}}

@media (prefers-color-scheme: dark) {{
    :root {{
{_properties(DARK_THEME)}
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

[data-testid="stMainBlockContainer"] {{
    max-width: 56.25rem;
    padding: 2.5rem 1.5rem 3rem;
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
    color: var(--app-secondary-text) !important;
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
    box-shadow: 0 6px 20px rgba(15, 23, 42, 0.07);
}}

[data-testid="stExpander"] details {{
    background: var(--app-surface) !important;
    color: var(--app-foreground) !important;
    border-color: var(--app-input-border) !important;
    border-radius: 1rem;
}}

[data-testid="stExpander"] summary {{
    background: var(--app-surface) !important;
    color: var(--app-foreground) !important;
    border-color: var(--app-input-border) !important;
    border-radius: 0.875rem;
}}

[role="listbox"],
[role="option"] {{
    background: var(--app-surface) !important;
    color: var(--app-foreground) !important;
    border-color: var(--app-border) !important;
    min-height: 44px;
}}

[data-testid="stNumberInputContainer"],
[data-testid="stSelectbox"] [role="group"] {{
    background: var(--app-surface) !important;
    border: 1.5px solid var(--app-input-border) !important;
    border-radius: 0.875rem !important;
    color: var(--app-foreground) !important;
    min-height: 48px;
    overflow: hidden;
    transition: border-color 180ms ease, box-shadow 180ms ease;
}}

[data-testid="stNumberInputContainer"]:focus-within,
[data-testid="stSelectbox"] [role="group"]:focus-within {{
    border-color: var(--app-primary) !important;
    box-shadow: 0 0 0 3px var(--app-focus) !important;
}}

[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] input,
[data-testid="stSelectbox"] svg {{
    color: var(--app-foreground) !important;
    fill: currentColor !important;
}}

[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] input {{
    background: var(--app-surface) !important;
    border: 0 !important;
    font-size: 1rem !important;
    font-variant-numeric: tabular-nums;
    min-height: 48px;
    padding-inline: 0.875rem !important;
}}

[data-testid="stNumberInput"] input::placeholder,
[data-testid="stSelectbox"] input::placeholder {{
    color: var(--app-secondary-text) !important;
    opacity: 1 !important;
}}

[data-testid="stNumberInput"] button {{
    display: none !important;
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
    box-shadow: none;
}}

.stButton > button[kind="primary"]:hover {{
    background: var(--app-primary-hover) !important;
    border-color: var(--app-primary-hover) !important;
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
    border: 1px solid var(--app-border);
    min-height: 0.5rem;
    overflow: hidden;
}}

[data-testid="stDataFrame"] {{
    border: 1px solid var(--app-border);
    border-radius: 1rem;
    overflow: hidden;
}}

[data-testid="stTable"] {{
    border: 1px solid var(--app-border);
    border-radius: 1rem;
    overflow: hidden;
}}

[data-testid="stTable"] table,
[data-testid="stTable"] th,
[data-testid="stTable"] td {{
    background: var(--app-surface) !important;
    color: var(--app-foreground) !important;
    border-color: var(--app-border) !important;
}}

.app-footer {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem 1.5rem;
    margin-top: 2.5rem;
    padding-top: 1rem;
    border-top: 1px solid var(--app-border);
    color: var(--app-secondary-text);
    font-size: 0.8125rem;
    line-height: 1.5;
}}

.medical-disclaimer {{
    margin: 0.75rem 0 0;
    color: var(--app-secondary-text) !important;
    font-size: 0.8125rem;
    line-height: 1.5;
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

    .app-footer {{
        align-items: flex-start;
        flex-direction: column;
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
