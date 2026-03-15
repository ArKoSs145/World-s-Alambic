from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QPushButton, QMessageBox, 
                             QAbstractItemView, QDialog, QLabel, QListWidgetItem,
                             QLineEdit, QComboBox)
from PyQt6.QtCore import Qt, QSize
from data_manager import DataManager
from ui_dialogs import CreationDialog
import re

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
    'magie': '#D946EF'     
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

# --- CLASSE : LA CARTE VISUELLE ---
class ItemCard(QWidget):
    def __init__(self, nom, provenance, type_item, tags, quantite, ingredients=None):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True) # Active le style de fond

        self.type_item_exact = type_item
        
        if ingredients is None:
            ingredients = []
            
        # 1. Layout principal (Il gère l'épaisseur de notre "bordure")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2) # Épaisseur de la bordure (2 pixels)
        main_layout.setSpacing(0)

        # 2. Le conteneur interne (Gris foncé)
        self.inner_widget = QWidget()
        self.inner_widget.setStyleSheet("background-color: #2D3748; border-radius: 4px;")
        inner_layout = QVBoxLayout(self.inner_widget)
        inner_layout.setContentsMargins(8, 8, 8, 8)
        inner_layout.setSpacing(2)

        # Textes
        self.lbl_nom = QLabel(nom)
        self.lbl_nom.setStyleSheet("font-weight: bold; color: #D4AF37; font-size: 13px; background: transparent;")

        texte_details = f"{type_item} - {tags}\n{provenance} - Qte: {quantite}"
        if len(ingredients) > 0:
            recette = ", ".join(ingredients)
            texte_details += f"\nCréé avec : {recette}"

        self.lbl_details = QLabel(texte_details)
        self.lbl_details.setStyleSheet("color: #9CA3AF; font-size: 13px; font-style: italic; background: transparent;")

        inner_layout.addWidget(self.lbl_nom)
        inner_layout.addWidget(self.lbl_details)
        
        main_layout.addWidget(self.inner_widget)

        # 3. LOGIQUE DES COULEURS DE LA BORDURE (Le fond du widget principal)
        mots_tags = [mot.lower() for mot in re.findall(r'\b\w+\b', str(tags))]
        couleurs = [TAG_COLORS[mot] for mot in mots_tags if mot in TAG_COLORS]

        if len(couleurs) == 0:
            fond_style = "background-color: #4A5568;" # Bordure grise par défaut
        elif len(couleurs) == 1:
            fond_style = f"background-color: {couleurs[0]};" # Une seule couleur
        else:
            # Plusieurs couleurs : On crée un dégradé linéaire (Linear Gradient) !
            stops = ", ".join([f"stop: {i/(len(couleurs)-1)} {couleurs[i]}" for i in range(len(couleurs))])
            fond_style = f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, {stops});"

        self.setStyleSheet(f"ItemCard {{ {fond_style} border-radius: 6px; }}")

# --- CLASSE PRINCIPALE ---
class WorldsAlambicApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("World's Alambic - L'Œuvre au Noir")
        self.setGeometry(100, 100, 1000, 600)
        
        self.db = DataManager()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tab_grimoire = QWidget()
        self.tab_atelier = QWidget()

        self.tabs.addTab(self.tab_grimoire, "📖 Grimoire (Base de Données)")
        self.tabs.addTab(self.tab_atelier, "🧪 Atelier Alchimique")

        self.setup_grimoire_tab()
        self.setup_atelier_tab()
        self.charger_donnees() 

    def setup_grimoire_tab(self):
        layout = QVBoxLayout()

        top_bar_layout = QHBoxLayout()
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Rechercher par nom, tag, provenance...")
        self.search_bar.textChanged.connect(self.filtrer_grimoire)

        self.filter_combo = QComboBox()
        self.filter_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.filter_combo.currentTextChanged.connect(self.filtrer_grimoire)

        top_bar_layout.addWidget(self.search_bar,3)
        top_bar_layout.addWidget(self.filter_combo,1)
        
        self.db_list = QListWidget()
        self.db_list.setObjectName("inventory_list") 

        self.db_list.setFlow(QListWidget.Flow.LeftToRight) # Affichage de gauche à droite
        self.db_list.setWrapping(True)                     # Retour à la ligne automatique
        self.db_list.setResizeMode(QListWidget.ResizeMode.Adjust) # Ajustement fluide
        self.db_list.setSpacing(8)                         # Espace entre les cartes
        
        layout.addLayout(top_bar_layout)
        layout.addWidget(self.db_list)
        self.tab_grimoire.setLayout(layout)

    def setup_atelier_tab(self):
        main_layout = QHBoxLayout()

        self.inventory_list = QListWidget()
        self.inventory_list.setDragEnabled(True)
        self.inventory_list.setAcceptDrops(False)
        self.inventory_list.setDefaultDropAction(Qt.DropAction.CopyAction)
        self.inventory_list.setObjectName("inventory_list")

        self.inventory_list.setFlow(QListWidget.Flow.LeftToRight)
        self.inventory_list.setWrapping(True)
        self.inventory_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.inventory_list.setSpacing(8)

        right_panel = QVBoxLayout()
        
        self.cauldron_zone = CauldronWidget() 
        
        self.btn_craft = QPushButton("⚙️ Transmuter / Distiller les ingrédients ⚙️")
        self.btn_craft.clicked.connect(self.lancer_creation)

        right_panel.addWidget(self.cauldron_zone)
        right_panel.addWidget(self.btn_craft)

        main_layout.addWidget(self.inventory_list, 2)
        main_layout.addLayout(right_panel, 3)
        self.tab_atelier.setLayout(main_layout)

    def charger_donnees(self):
        self.db_list.clear()
        self.inventory_list.clear()
        
        for item_data in self.db.data:
            list_item_db = QListWidgetItem(self.db_list)
            list_item_inv = QListWidgetItem(self.inventory_list)
            
            # Largeur fixe de 250px, hauteur automatique (ex: 85px)
            list_item_db.setSizeHint(QSize(295, 95))
            list_item_inv.setSizeHint(QSize(350, 95))
            
            list_item_inv.setData(Qt.ItemDataRole.UserRole, item_data['nom'])
            list_item_db.setData(Qt.ItemDataRole.UserRole, item_data['nom']) 
            
            nom = item_data['nom']
            type_item = item_data.get('type', 'Inconnu')
            tags = item_data.get('tags', '')
            provenance = item_data.get('provenance', 'Nature')
            quantite = item_data.get('quantite', 1)
            ingredients = item_data.get('ingredients', [])

            carte_db = ItemCard(nom, provenance, type_item, tags, quantite, ingredients)
            carte_inv = ItemCard(nom, provenance, type_item, tags, quantite, ingredients)
            
            self.db_list.setItemWidget(list_item_db, carte_db)
            self.inventory_list.setItemWidget(list_item_inv, carte_inv)

    def filtrer_grimoire(self, texte_recherche):
        texte_recherche = texte_recherche.lower()
        
        for i in range(self.db_list.count()):
            item = self.db_list.item(i)
            widget_carte = self.db_list.itemWidget(item)
            
            if widget_carte:
                nom = widget_carte.lbl_nom.text().lower()
                details = widget_carte.lbl_details.text().lower()
                
                if texte_recherche in nom or texte_recherche in details:
                    item.setHidden(False)
                else:
                    item.setHidden(True)

    def lancer_creation(self):
        if self.cauldron_zone.count() == 0:
            QMessageBox.warning(self, "Alambic Vide", "Tu dois mettre des ingrédients dans l'alambic !")
            return

        ingredients = [self.cauldron_zone.item(i).text() for i in range(self.cauldron_zone.count())]

        dialog = CreationDialog(ingredients, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nouvel_objet = dialog.get_data()
            
            self.db.save_item(nouvel_objet)
            self.charger_donnees()
            self.cauldron_zone.clear()
            
            QMessageBox.information(self, "Succès", f"'{nouvel_objet['nom']}' a été ajouté au Grimoire !")