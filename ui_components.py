from PyQt6.QtWidgets import QListWidget, QWidget, QVBoxLayout, QLabel, QListWidgetItem
from PyQt6.QtCore import Qt
import re

# --- DICTIONNAIRE DES COULEURS DES TAGS ---
TAG_COLORS = {
    'feu': '#EF4444',      
    'eau': '#3B82F6',      
    'plante': '#10B981',   
    'terre': '#D97706',    
    'air': '#6EE7B7',      
    'foudre': '#FBBF24',   
    'glace': '#7DD3FC',    
    'lumiere': '#FEF08A',  
    'ombre': '#7C3AED',    
    'magie': '#D946EF',     
    'minerai': '#A1A1AA'
}

# --- CLASSE : LE CHAUDRON INTELLIGENT ---
class CauldronWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("cauldron")

    def dragEnterEvent(self, event):
        if event.source():
            event.accept()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.source():
            event.accept()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        source = event.source()
        if source and source != self:
            item_glisse = source.currentItem()
            if item_glisse:
                nom_ingredient = item_glisse.data(Qt.ItemDataRole.UserRole)
                if nom_ingredient:
                    nouvel_item = QListWidgetItem(nom_ingredient)
                    nouvel_item.setForeground(Qt.GlobalColor.white) 
                    self.addItem(nouvel_item)
            event.accept()
        else:
            super().dropEvent(event)

class ItemCard(QWidget):
    def __init__(self, nom, provenance, type_item, tags, quantite, ingredients=None):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.type_item_exact = type_item 
        self.provenance_exact = provenance
        self.tags_exact = tags

        if ingredients is None:
            ingredients = []
            
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2) 
        main_layout.setSpacing(0)

        self.inner_widget = QWidget()
        self.inner_widget.setStyleSheet("background-color: #2D3748; border-radius: 4px;")
        inner_layout = QVBoxLayout(self.inner_widget)
        inner_layout.setContentsMargins(10, 8, 10, 8)
        inner_layout.setSpacing(4)

        # Titre
        self.lbl_nom = QLabel(nom)
        self.lbl_nom.setStyleSheet("font-weight: bold; color: #D4AF37; font-size: 14px; background: transparent;")

        # 👇 NOUVEAU VISUEL : On nettoie les crochets des tags et on utilise un tableau HTML
        tags_clean = str(tags).replace('[', '').replace(']', '').replace("'", "").replace('"', '')
        
        texte_details = f"""
        <table width="100%" style="margin-bottom: 2px;">
            <tr>
                <td align="left" style="color: #E2E8F0; font-weight: bold; font-size: 12px;">{type_item}</td>
                <td align="right" style="color: #D4AF37; font-weight: bold; font-size: 13px;">x{quantite}</td>
            </tr>
        </table>
        <span style="color: #9CA3AF; font-size: 11px;">
        🏷️ {tags_clean}<br>
        🌍 {provenance}
        """
        if len(ingredients) > 0:
            recette = ", ".join(ingredients)
            texte_details += f"<br>🪄 <i>{recette}</i>"
        texte_details += "</span>"

        self.lbl_details = QLabel(texte_details)
        self.lbl_details.setTextFormat(Qt.TextFormat.RichText) # Force l'interprétation HTML
        self.lbl_details.setStyleSheet("background: transparent;")

        inner_layout.addWidget(self.lbl_nom)
        inner_layout.addWidget(self.lbl_details)
        main_layout.addWidget(self.inner_widget)

        # Logique des couleurs
        mots_tags = [mot.lower() for mot in re.findall(r'\b\w+\b', str(tags))]
        couleurs = [TAG_COLORS[mot] for mot in mots_tags if mot in TAG_COLORS]

        if len(couleurs) == 0:
            fond_style = "background-color: #4A5568;"
        elif len(couleurs) == 1:
            fond_style = f"background-color: {couleurs[0]};"
        else:
            stops = ", ".join([f"stop: {i/(len(couleurs)-1)} {couleurs[i]}" for i in range(len(couleurs))])
            fond_style = f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, {stops});"

        self.setStyleSheet(f"ItemCard {{ {fond_style} border-radius: 6px; }}")