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


def test_design_system_candidate_is_not_used_for_white_button_text():
    assert contrast_ratio("#FFFFFF", "#0891B2") < 4.5
    assert LIGHT_THEME.primary == "#187C72"
    assert contrast_ratio(
        LIGHT_THEME.on_primary,
        LIGHT_THEME.primary,
    ) >= 4.5


def test_calm_wellness_light_palette_is_used():
    assert LIGHT_THEME.background == "#F7F8F4"
    assert LIGHT_THEME.foreground == "#17324D"
    assert LIGHT_THEME.primary == "#187C72"
    assert LIGHT_THEME.surface == "#FFFFFF"
    assert LIGHT_THEME.muted_surface == "#EAF3EE"
    assert LIGHT_THEME.border == "#D8E2DC"
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
