from app.theme import (
    DARK_THEME,
    LIGHT_THEME,
    build_theme_css,
    contrast_ratio,
)


def _css_declarations(css: str, selector: str) -> str:
    marker = f"{selector} {{"
    marker_index = css.find(marker)
    if marker_index < 0:
        return ""
    start = marker_index + len(marker)
    return css[start : css.index("}", start)]


def test_normal_text_pairs_meet_wcag_aa():
    pairs = (
        (LIGHT_THEME.foreground, LIGHT_THEME.background),
        (LIGHT_THEME.foreground, LIGHT_THEME.surface),
        (LIGHT_THEME.on_primary, LIGHT_THEME.primary),
        (DARK_THEME.foreground, DARK_THEME.background),
        (DARK_THEME.foreground, DARK_THEME.surface),
        (DARK_THEME.on_primary, DARK_THEME.primary),
    )
    assert all(
        contrast_ratio(foreground, background) >= 4.5
        for foreground, background in pairs
    )


def test_generated_css_contains_paired_theme_and_accessibility_rules():
    css = build_theme_css()
    assert LIGHT_THEME.background in css
    assert DARK_THEME.background in css
    assert "@media (prefers-color-scheme: dark)" in css
    assert "@media (prefers-reduced-motion: reduce)" in css
    assert "min-height: 44px" in css
    assert "focus-visible" in css
    assert '[data-testid="stAlert"]' in css
    assert '[data-testid="stSelectbox"] [role="group"]' in css


def test_clean_numeric_input_css_contract():
    css = build_theme_css("light")
    assert '[data-testid="stNumberInput"] button' in css
    assert "display: none !important" in css
    assert '[data-testid="stNumberInputContainer"]' in css
    assert "min-height: 48px" in css
    assert "border: 1.5px solid var(--app-input-border)" in css
    assert "border-radius: 0.875rem" in css
    assert "font-variant-numeric: tabular-nums" in css
    assert "::placeholder" in css
    assert "color: var(--app-secondary-text) !important" in css


def test_primary_button_text_meets_wcag_aa():
    assert LIGHT_THEME.primary == "#0F766E"
    for palette in (LIGHT_THEME, DARK_THEME):
        assert hasattr(palette, "primary_hover")
        assert contrast_ratio(palette.on_primary, palette.primary) >= 4.5
        assert contrast_ratio(palette.on_primary, palette.primary_hover) >= 4.5

    css = build_theme_css()
    hover = _css_declarations(css, '.stButton > button[kind="primary"]:hover')
    assert "background: var(--app-primary-hover)" in hover
    assert "border-color: var(--app-primary-hover)" in hover


def test_professional_health_palette_is_used():
    assert LIGHT_THEME.primary == "#0F766E"
    assert LIGHT_THEME.on_primary == "#FFFFFF"
    assert LIGHT_THEME.background == "#F8FAFC"
    assert LIGHT_THEME.foreground == "#0F172A"
    assert LIGHT_THEME.surface == "#FFFFFF"
    assert LIGHT_THEME.muted_surface == "#F1F5F9"
    assert LIGHT_THEME.border == "#CBD5E1"
    assert LIGHT_THEME.secondary_text == "#475569"
    assert LIGHT_THEME.focus == "#0D9488"
    assert contrast_ratio(
        LIGHT_THEME.foreground,
        LIGHT_THEME.background,
    ) >= 4.5


def test_professional_layout_is_centered_restrained_and_responsive():
    css = build_theme_css("light")
    assert "max-width: 56.25rem" in css
    assert "radial-gradient" not in css
    assert "linear-gradient" not in css
    assert "box-shadow: 0 6px 20px" in css
    assert "border-radius: 0.875rem" in css
    assert ".app-footer" in css
    assert ".medical-disclaimer" in css
    assert "@media (max-width: 640px)" in css
    assert "min-height: 48px" in css
    assert "prefers-reduced-motion" in css
    assert contrast_ratio(
        LIGHT_THEME.on_primary,
        LIGHT_THEME.primary,
    ) >= 4.5


def test_component_radii_distinguish_controls_from_card_surfaces():
    css = build_theme_css("light")
    assert "border-radius: 0.875rem" in _css_declarations(
        css,
        '[data-testid="stExpander"] summary',
    )
    assert "border-radius: 1rem" in _css_declarations(
        css,
        '[data-testid="stExpander"] details',
    )
    assert "border-radius: 1rem" in _css_declarations(
        css,
        '[data-testid="stDataFrame"]',
    )
    assert "border-radius: 1rem" in _css_declarations(
        css,
        '[data-testid="stTable"]',
    )


def test_streamlit_selected_theme_is_not_overridden_by_system_palette():
    css = build_theme_css()
    assert "color-scheme: light" not in css
    dark_css = build_theme_css("dark")
    assert dark_css.rfind(DARK_THEME.background) > dark_css.find(
        "@media (prefers-color-scheme: dark)"
    )
    light_css = build_theme_css("light")
    assert light_css.rfind(LIGHT_THEME.alert_surface) > light_css.find(
        "@media (prefers-color-scheme: dark)"
    )
