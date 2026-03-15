# ==========================================
# 🎨 PALETTE DE COULEURS (DESIGN SYSTEM)
# ==========================================
BG_MAIN = "#121212"       # Fond principal (Charbon)
BG_SURFACE = "#1F2937"    # Fond des listes et menus
BG_HOVER = "#374151"      # Fond au survol
BG_CAULDRON = "#1A1A24"   # Fond sombre de la zone magique

TEXT_MAIN = "#E2E8F0"     # Texte clair lisible
TEXT_MUTED = "#9CA3AF"    # Texte grisé (sous-titres)

ACCENT_GOLD = "#D4AF37"   # Or vieilli (Titres, bordures)
ACCENT_CYAN = "#22D3EE"   # Bleu magique (Boutons)
ACCENT_PURPLE = "#8B5CF6" # Violet (Chaudron)
BORDER_DARK = "#4A5568"   # Bordure discrète

# ==========================================
# 🧩 MODULES DE STYLE (Découpés par composants)
# ==========================================

STYLE_BASE = f"""
    QMainWindow, QDialog {{ background-color: {BG_MAIN}; color: {TEXT_MAIN}; }}
    QLabel {{ color: {ACCENT_GOLD}; font-weight: bold; }}
"""

STYLE_ONGLETS = f"""
    QTabWidget::pane {{ border: 1px solid {ACCENT_GOLD}; background: {BG_MAIN}; }}
    QTabBar::tab {{ background: {BG_SURFACE}; color: {TEXT_MAIN}; padding: 10px; border: 1px solid {BORDER_DARK}; }}
    QTabBar::tab:selected {{ background: {ACCENT_GOLD}; color: {BG_MAIN}; font-weight: bold; }}
"""

STYLE_INPUTS_BOUTONS = f"""
    QLineEdit, QTextEdit {{ 
        background-color: {BG_SURFACE}; color: {TEXT_MAIN}; 
        border: 1px solid {ACCENT_GOLD}; border-radius: 3px; padding: 5px; 
    }}
    QPushButton {{ 
        background-color: {BG_SURFACE}; color: {ACCENT_CYAN}; 
        border: 1px solid {ACCENT_CYAN}; padding: 10px; 
        border-radius: 5px; font-weight: bold; 
    }}
    QPushButton:hover {{ background-color: {ACCENT_CYAN}; color: {BG_MAIN}; }}
"""

STYLE_LISTES = f"""
    QListWidget {{ 
        background-color: {BG_SURFACE}; 
        color: {TEXT_MAIN}; 
        border: 1px solid {ACCENT_GOLD}; 
        border-radius: 5px; 
        padding: 10px; 
        font-size: 14px; 
        outline: 0; 
    }}
"""

STYLE_CARTES_INVENTAIRE = f"""
    /* On rend l'élément natif de Qt 100% invisible pour laisser notre ItemCard briller */
    QListWidget#inventory_list::item {{
        background: transparent; 
        border: none;
        color: transparent; 
    }}
    QListWidget#inventory_list::item:hover {{
        background: transparent; 
    }}
    QListWidget#inventory_list::item:selected {{
        background: transparent; 
        border: none;
        color: transparent;
        outline: none; 
    }}
"""

STYLE_CHAUDRON = f"""
    QListWidget#cauldron {{
        border: 2px dashed {ACCENT_PURPLE}; 
        background-color: {BG_CAULDRON};
        padding: 10px;
    }}
    QListWidget#cauldron::item {{
        color: {TEXT_MAIN}; 
        background-color: {BG_SURFACE};
        padding: 8px;
        border-radius: 4px;
        margin-bottom: 5px;
    }}
"""



# ==========================================
# 🔗 ASSEMBLAGE FINAL
# ==========================================
# On concatène toutes nos variables en une seule grosse chaîne pour main.py
GLOBAL_STYLE = STYLE_BASE + STYLE_ONGLETS + STYLE_INPUTS_BOUTONS + STYLE_LISTES + STYLE_CARTES_INVENTAIRE + STYLE_CHAUDRON