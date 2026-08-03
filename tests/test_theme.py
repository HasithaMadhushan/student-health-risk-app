from app.theme import (
    DARK_THEME,
    LIGHT_THEME,
    build_theme_css,
    contrast_ratio,
)


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


def test_primary_button_text_meets_wcag_aa():
    assert LIGHT_THEME.primary == "#005EB8"
    assert contrast_ratio(
        LIGHT_THEME.on_primary,
        LIGHT_THEME.primary,
    ) >= 4.5


def test_public_service_health_palette_is_used():
    assert LIGHT_THEME.background == "#F0F4F5"
    assert LIGHT_THEME.foreground == "#212B32"
    assert LIGHT_THEME.primary == "#005EB8"
    assert LIGHT_THEME.accent == "#007F3B"
    assert LIGHT_THEME.surface == "#FFFFFF"
    assert LIGHT_THEME.muted_surface == "#E8EDEE"
    assert LIGHT_THEME.border == "#D8DDE0"
    assert LIGHT_THEME.secondary_text == "#4C6272"
    assert LIGHT_THEME.input_border == "#4C6272"
    assert LIGHT_THEME.alert_surface == "#FFF9C4"
    assert LIGHT_THEME.alert_foreground == "#212B32"
    assert LIGHT_THEME.focus == "#FFEB3B"
    assert LIGHT_THEME.destructive == "#D5281B"
    assert contrast_ratio(
        LIGHT_THEME.foreground,
        LIGHT_THEME.background,
    ) >= 4.5
    assert contrast_ratio(
        LIGHT_THEME.on_primary,
        LIGHT_THEME.primary,
    ) >= 4.5


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
