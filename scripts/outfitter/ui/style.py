"""A single, self-contained dark stylesheet for the browser window.

Returns a QSS string applied to the ``ClothingBrowser`` instance only (set on the
window, not the QApplication), so it styles the tool without bleeding into Maya's
other UI. No external image assets — all chrome is drawn by Qt from these rules.

Conventions used by the widgets:
  * a primary action button sets ``button.setProperty("accent", True)``,
  * the type badge label uses ``objectName == "typeBadge"``,
  * section/heading labels use ``objectName in {"assetName", "sectionHeading"}``.
"""
from __future__ import annotations


# Palette — tuned to sit comfortably next to Maya 2026's dark theme.
_BG = "#2b2b2b"          # window background
_SURFACE = "#323335"     # panels / inputs at rest
_SURFACE_HI = "#3c3d40"  # hover / raised
_BORDER = "#1d1d1f"      # separators / input borders
_TEXT = "#dcdcdc"
_MUTED = "#9a9a9a"


def stylesheet(accent: str = "#4a90d9") -> str:
    """Full QSS for the window, themed around ``accent`` (a hex colour)."""
    accent_hi = _lighten(accent, 0.15)
    accent_dim = _darken(accent, 0.18)
    return f"""
    QWidget {{
        background: {_BG};
        color: {_TEXT};
        font-size: 12px;
    }}
    QLabel {{ background: transparent; }}

    /* Branded app header: 'Outfitter' wordmark + version (font set in code) */
    QWidget#appHeader {{
        background: {_SURFACE};
        border-bottom: 1px solid {_BORDER};
    }}
    QLabel#appName {{
        color: #ff6d7a;  /* salmon — matches the shirt body in the shelf icon */
        font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", "Roboto", Arial;
        font-size: 32px;
        font-weight: 900;
    }}
    QLabel#appVersion {{
        color: #fff0a6;  /* yellow — matches the flowers in the shelf icon */
        font-size: 13px; font-weight: 600; padding-bottom: 6px;
    }}

    QLabel#assetName {{ font-size: 17px; font-weight: 600; color: #ffffff; }}
    /* Section headings: pass the caption already upper-cased — Qt's QSS engine
       implements neither text-transform nor letter-spacing, so they're set in code. */
    QLabel#sectionHeading {{
        font-size: 11px; font-weight: 600; color: {_MUTED};
    }}
    QLabel#fieldLabel {{ color: {_MUTED}; }}
    QLabel#muted {{ color: {_MUTED}; }}
    QLabel#description {{ color: #c4c4c4; }}

    /* Publish tab — numbered step cards down the right column */
    QFrame#stepCard {{
        background: {_SURFACE};
        border: 1px solid {_BORDER};
        border-radius: 8px;
    }}
    QLabel#stepNumber {{
        color: {accent};
        font-size: 24px;
        font-weight: 800;
    }}
    QLabel#stepTitle {{ font-size: 14px; font-weight: 700; color: #ffffff; }}
    QLabel#stepInstruction {{ color: {_MUTED}; }}
    QLabel#stepDest {{ color: {_MUTED}; }}
    QLabel#stepDest[warn="true"] {{ color: #e0b057; font-weight: 600; }}
    QScrollArea#stepsScroll {{ background: transparent; border: none; }}
    QScrollArea#stepsScroll > QWidget > QWidget {{ background: transparent; }}

    /* Type badge — a rounded accent chip */
    QLabel#typeBadge {{
        background: {accent_dim};
        color: #ffffff;
        border-radius: 9px;
        padding: 2px 10px;
        font-size: 11px;
        font-weight: 600;
    }}

    /* Preview image frame */
    QLabel#previewImage {{
        background: #232325;
        border: 1px solid {_BORDER};
        border-radius: 8px;
    }}

    /* Publish log — a console-style read-out of each action's result */
    QPlainTextEdit#logView {{
        background: #1f1f21;
        border: 1px solid {_BORDER};
        border-radius: 6px;
        padding: 6px 8px;
        color: {_TEXT};
    }}

    QTabWidget::pane {{ border: 1px solid {_BORDER}; border-radius: 6px; top: -1px; }}
    QTabBar::tab {{
        background: transparent; color: {_MUTED};
        padding: 7px 18px; margin-right: 2px;
        border-top-left-radius: 6px; border-top-right-radius: 6px;
    }}
    QTabBar::tab:selected {{ background: {_SURFACE}; color: {_TEXT}; }}
    QTabBar::tab:hover:!selected {{ color: {_TEXT}; }}

    QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QPlainTextEdit, QTextEdit {{
        background: {_SURFACE};
        border: 1px solid {_BORDER};
        border-radius: 5px;
        padding: 5px 8px;
        selection-background-color: {accent};
    }}
    QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus,
    QSpinBox:focus, QPlainTextEdit:focus, QTextEdit:focus {{
        border: 1px solid {accent};
    }}
    QComboBox::drop-down {{ border: none; width: 18px; }}
    QComboBox QAbstractItemView {{
        background: {_SURFACE}; border: 1px solid {_BORDER};
        selection-background-color: {accent};
    }}

    QPushButton {{
        background: {_SURFACE};
        border: 1px solid {_BORDER};
        border-radius: 5px;
        padding: 6px 14px;
        color: {_TEXT};
    }}
    QPushButton:hover {{ background: {_SURFACE_HI}; }}
    QPushButton:pressed {{ background: {_BORDER}; }}
    QPushButton:disabled {{ color: #6a6a6a; background: #2e2e30; }}
    QPushButton[accent="true"] {{
        background: {accent}; border: 1px solid {accent}; color: #ffffff;
        font-weight: 600;
    }}
    QPushButton[accent="true"]:hover {{ background: {accent_hi}; }}
    QPushButton[accent="true"]:pressed {{ background: {accent_dim}; }}
    QPushButton[positive="true"] {{
        background: #3a9d5d; border: 1px solid #3a9d5d; color: #ffffff;
        font-weight: 600;
    }}
    QPushButton[positive="true"]:hover {{ background: #49b06d; }}
    QPushButton[positive="true"]:pressed {{ background: #2f8550; }}

    QListWidget {{
        background: #262628;
        border: 1px solid {_BORDER};
        border-radius: 6px;
        padding: 6px;
        outline: none;
    }}
    QListWidget::item {{
        background: {_SURFACE};
        border: 1px solid transparent;
        border-radius: 6px;
        margin: 4px;
        padding: 6px;
        color: {_TEXT};
    }}
    QListWidget::item:hover {{ background: {_SURFACE_HI}; }}
    QListWidget::item:selected {{
        background: {_SURFACE_HI};
        border: 1px solid {accent};
        color: #ffffff;
    }}

    QGroupBox {{
        border: 1px solid {_BORDER}; border-radius: 6px;
        margin-top: 10px; padding-top: 8px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin; left: 10px; padding: 0 4px;
        color: {_MUTED};
    }}

    QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
    QScrollBar::handle:vertical {{
        background: #4a4a4d; border-radius: 5px; min-height: 24px;
    }}
    QScrollBar::handle:vertical:hover {{ background: #5a5a5d; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}

    QSplitter::handle {{ background: {_BORDER}; }}
    QToolTip {{
        background: #1b1b1d; color: {_TEXT};
        border: 1px solid {accent}; padding: 4px;
    }}
    """


# --- tiny hex helpers (no external colour lib needed) ------------------------
def _clamp(v: int) -> int:
    return max(0, min(255, v))


def _scale(hex_color: str, factor: float, toward: int) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    r = _clamp(int(r + (toward - r) * factor))
    g = _clamp(int(g + (toward - g) * factor))
    b = _clamp(int(b + (toward - b) * factor))
    return f"#{r:02x}{g:02x}{b:02x}"


def _lighten(hex_color: str, factor: float) -> str:
    return _scale(hex_color, factor, 255)


def _darken(hex_color: str, factor: float) -> str:
    return _scale(hex_color, factor, 0)
