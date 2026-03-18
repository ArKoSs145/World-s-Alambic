from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QPushButton, QMessageBox, 
                             QAbstractItemView, QDialog, QLabel, QListWidgetItem,
                             QLineEdit, QComboBox, QMenu)
from PyQt6.QtCore import Qt, QSize
from data_manager import DataManager
from ui_dialogs import CreationDialog, FilterDialog
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
        self.provenance_exact = provenance
        self.tags_exact = tags

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
        self.setGeometry(100, 100, 1500, 900)
        
        self.db = DataManager()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tab_grimoire = QWidget()
        self.tab_atelier = QWidget()

        self.tabs.addTab(self.tab_grimoire, "📖 Grimoire (Base de Données)")
        self.tabs.addTab(self.tab_atelier, "🧪 Atelier Alchimique")

        self.setup_grimoire_tab()
        self.setup_atelier_tab()
        self.filtres_actifs = {'tags': [], 'types': [], 'provenances': []}
        self.charger_donnees() 

    def setup_grimoire_tab(self):
        # --- LAYOUT PRINCIPAL (Division Gauche/Droite) ---
        main_layout = QHBoxLayout()
        
        # === PARTIE GAUCHE : La Liste et les Filtres (70%) ===
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        top_bar_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Rechercher par nom, tag...")
        self.search_bar.textChanged.connect(self.filtrer_grimoire)
        
        self.btn_filter = QPushButton("⚙️ Filtres")
        self.btn_filter.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_filter.clicked.connect(self.ouvrir_popup_filtres)
        
        top_bar_layout.addWidget(self.search_bar, 4)
        top_bar_layout.addWidget(self.btn_filter, 1)
        # (Le bouton Ajouter a été retiré d'ici)
        
        self.db_list = QListWidget()
        self.db_list.setObjectName("inventory_list") 
        self.db_list.setFlow(QListWidget.Flow.LeftToRight)
        self.db_list.setWrapping(True)
        self.db_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.db_list.setSpacing(8)
        self.db_list.itemClicked.connect(self.afficher_details_panneau)
        
        left_layout.addLayout(top_bar_layout)
        left_layout.addWidget(self.db_list)
        
        # === PARTIE DROITE : Le Panneau d'Inspection (30%) ===
        self.details_panel = QWidget()
        self.details_panel.setStyleSheet("""
            QWidget { background-color: #1F2937; border-radius: 8px; border: 1px solid #4A5568; }
            QLabel { border: none; background: transparent; }
        """)
        details_layout = QVBoxLayout(self.details_panel)
        details_layout.setContentsMargins(15, 15, 15, 15)
        details_layout.setSpacing(10)

        self.lbl_detail_nom = QLabel("Sélectionnez un artefact")
        self.lbl_detail_nom.setStyleSheet("font-size: 18px; color: #D4AF37; font-weight: bold;")
        self.lbl_detail_nom.setWordWrap(True)
        
        self.lbl_detail_stats = QLabel("Parcourez votre Grimoire pour révéler les secrets de vos créations.")
        self.lbl_detail_stats.setStyleSheet("color: #9CA3AF; font-size: 12px; font-style: italic;")
        self.lbl_detail_stats.setWordWrap(True)
        
        self.lbl_detail_desc = QLabel("")
        self.lbl_detail_desc.setStyleSheet("color: #E2E8F0; font-size: 13px; margin-top: 10px;")
        self.lbl_detail_desc.setWordWrap(True)
        self.lbl_detail_desc.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 1. Bouton Supprimer (Caché par défaut)
        self.btn_supprimer = QPushButton("❌ Détruire cet artefact")
        self.btn_supprimer.setStyleSheet("background-color: #7F1D1D; color: white; border: 1px solid #EF4444; padding: 8px; border-radius: 4px;")
        self.btn_supprimer.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_supprimer.hide() 
        self.btn_supprimer.clicked.connect(self.supprimer_artefact_selectionne)

        # 2. Bouton Ajouter (Toujours visible en bas)
        self.btn_add = QPushButton("➕ Ajouter un artefact")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet("background-color: #10B981; color: white; border: none; padding: 10px; font-weight: bold; border-radius: 4px;")
        self.btn_add.clicked.connect(self.ajouter_artefact_manuel)

        # Ordre d'ajout dans le panneau : la description pousse les boutons vers le bas
        details_layout.addWidget(self.lbl_detail_nom)
        details_layout.addWidget(self.lbl_detail_stats)
        details_layout.addWidget(self.lbl_detail_desc, 1) # Le "1" crée l'espace vide
        details_layout.addWidget(self.btn_supprimer)      # Juste au-dessus
        details_layout.addWidget(self.btn_add)            # Tout en bas

        # === ASSEMBLAGE FINAL ===
        main_layout.addWidget(left_panel, 7) 
        main_layout.addWidget(self.details_panel, 3) 
        
        self.tab_grimoire.setLayout(main_layout)
        self.artefact_en_lecture = None

    def ajouter_artefact_manuel(self):
        """Ouvre la fenêtre de création d'objet sans passer par le chaudron"""
        
        # On appelle notre boîte de dialogue existante avec une liste vide d'ingrédients []
        dialog = CreationDialog([], self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nouvel_objet = dialog.get_data()
            
            # On sauvegarde et on rafraîchit !
            self.db.save_item(nouvel_objet)
            self.charger_donnees()
            
            QMessageBox.information(self, "Succès", f"L'artefact '{nouvel_objet['nom']}' a été consigné dans le Grimoire !")

    def afficher_details_panneau(self, item):
        """Met à jour le panneau latéral de droite avec les infos de la carte cliquée"""
        nom_objet = item.data(Qt.ItemDataRole.UserRole)
        self.artefact_en_lecture = nom_objet # On mémorise quel objet est affiché
        
        # On cherche l'objet dans la base de données
        item_data = next((i for i in self.db.data if i.get('nom') == nom_objet), None)
        if not item_data:
            return

        # 1. Mise à jour du Titre
        self.lbl_detail_nom.setText(item_data['nom'])
        
        # 2. Mise à jour des Stats
        stats = f"Type : {item_data.get('type', 'Inconnu')}\n"
        stats += f"Tags : {item_data.get('tags', 'Aucun')}\n"
        stats += f"Provenance : {item_data.get('provenance', 'Inconnue')}\n"
        stats += f"Quantité : {item_data.get('quantite', 1)}"
        self.lbl_detail_stats.setText(stats)

        # 3. Mise à jour de la Description et Recette
        desc = item_data.get('desc', "Aucune description n'a été notée.")
        ingredients = item_data.get('ingredients', [])
        recette = ", ".join(ingredients) if ingredients else "Création spontanée"
        
        texte_desc = f"<b>📖 Description :</b><br>{desc}<br><br>"
        texte_desc += f"<b>🧪 Recette :</b><br>{recette}"
        self.lbl_detail_desc.setText(texte_desc)

        # 4. On affiche enfin le bouton de suppression !
        self.btn_supprimer.show()

    def supprimer_artefact_selectionne(self):
        """Supprime l'objet actuellement affiché dans le panneau"""
        if not self.artefact_en_lecture:
            return

        reponse = QMessageBox.question(
            self, 
            "Destruction d'objet", 
            f"Es-tu sûr de vouloir incinérer '{self.artefact_en_lecture}' ?\nCette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reponse == QMessageBox.StandardButton.Yes:
            self.db.delete_item(self.artefact_en_lecture) 
            self.charger_donnees()
            
            # On remet le panneau à zéro après la suppression
            self.lbl_detail_nom.setText("Sélectionnez un artefact")
            self.lbl_detail_stats.setText("Parcourez votre Grimoire pour révéler les secrets de vos créations.")
            self.lbl_detail_desc.setText("")
            self.btn_supprimer.hide()
            self.artefact_en_lecture = None

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

        main_layout.addWidget(self.inventory_list, 6)
        main_layout.addLayout(right_panel, 4)
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

    def ouvrir_popup_filtres(self):
        types_uniques = set()
        prov_uniques = set()
        tags_uniques = set()
        
        for item in self.db.data:
            types_uniques.add(item.get('type', 'Inconnu'))
            prov_uniques.add(item.get('provenance', 'Inconnue'))
            
            # On découpe les mots pour séparer 'Feu' et 'Plante'
            mots = [m.capitalize() for m in re.findall(r'\b\w+\b', str(item.get('tags', '')))]
            tags_uniques.update(mots)
        
        dialog = FilterDialog(list(tags_uniques), list(types_uniques), list(prov_uniques), self.filtres_actifs, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.filtres_actifs = dialog.get_filters()
            self.filtrer_grimoire()

    def filtrer_grimoire(self, *args):
        texte_recherche = self.search_bar.text().lower()
        
        # On récupère les listes de boutons cochés
        filtres_tags = self.filtres_actifs.get('tags', [])
        filtres_types = self.filtres_actifs.get('types', [])
        filtres_prov = self.filtres_actifs.get('provenances', [])
        
        for i in range(self.db_list.count()):
            item = self.db_list.item(i)
            widget_carte = self.db_list.itemWidget(item)
            
            if widget_carte:
                nom = widget_carte.lbl_nom.text().lower()
                details = widget_carte.lbl_details.text().lower()
                
                # On récupère les tags de cette carte sous forme de liste de mots
                tags_carte = [m.capitalize() for m in re.findall(r'\b\w+\b', str(widget_carte.tags_exact))]
                
                # --- LES CONDITIONS (Si la liste est vide, on accepte tout) ---
                ok_texte = (texte_recherche in nom) or (texte_recherche in details)
                ok_type = (not filtres_types) or (widget_carte.type_item_exact in filtres_types)
                ok_prov = (not filtres_prov) or (widget_carte.provenance_exact in filtres_prov)
                
                # Est-ce que la carte possède AU MOINS UN des tags cochés ?
                ok_tags = (not filtres_tags) or any(t in tags_carte for t in filtres_tags)
                
                if ok_texte and ok_type and ok_prov and ok_tags:
                    item.setHidden(False)
                else:
                    item.setHidden(True)

    def afficher_details_carte(self, nom_objet):
        """Ouvre une fenêtre pour lire toutes les informations d'un objet"""
        # 1. On cherche l'objet complet dans la base de données
        item_data = next((item for item in self.db.data if item.get('nom') == nom_objet), None)
        
        if not item_data:
            return

        # 2. On récupère les infos (avec des valeurs par défaut si elles sont vides)
        desc = item_data.get('desc', "Aucune description n'a été notée pour cet artefact mystérieux...")
        ingredients = item_data.get('ingredients', [])
        
        if ingredients:
            recette = ", ".join(ingredients)
        else:
            recette = "Aucune (Trouvé tel quel)"

        # 3. On construit le texte final
        texte_complet = f"""
        <b>Nom :</b> {item_data.get('nom')}
        <b>Type :</b> {item_data.get('type', 'Inconnu')}
        <b>Tags :</b> {item_data.get('tags', 'Aucun')}
        <b>Provenance :</b> {item_data.get('provenance', 'Inconnue')}
        <b>En stock :</b> {item_data.get('quantite', 1)}
        
        <br><br><b>📖 Description :</b><br>
        <i>{desc}</i>
        
        <br><br><b>🧪 Recette d'origine :</b><br>
        {recette}
        """

        # 4. On affiche la pop-up de lecture
        msg = QMessageBox(self)
        msg.setWindowTitle(f"Détails : {nom_objet}")
        msg.setText(texte_complet)
        
        # Petit style pour que la pop-up reste dans le thème sombre de l'app
        msg.setStyleSheet("""
            QMessageBox { background-color: #2D3748; } 
            QLabel { color: #E2E8F0; font-size: 13px; } 
            QPushButton { background-color: #374151; color: white; padding: 5px 15px; border-radius: 3px; }
        """)
        msg.exec()

    def menu_contexte_grimoire(self, position):
        """Affiche un menu lors d'un clic droit sur une carte du grimoire"""
        item_clique = self.db_list.itemAt(position)
        
        if not item_clique:
            return 

        nom_objet = item_clique.data(Qt.ItemDataRole.UserRole)

        menu = QMenu()
        menu.setStyleSheet("""
            QMenu { background-color: #1F2937; color: white; border: 1px solid #D4AF37; padding: 5px; } 
            QMenu::item { padding: 5px 20px; }
            QMenu::item:selected { background-color: #374151; color: #D4AF37; }
        """)
        
        # 👇 NOUVEAU : Option pour voir les détails
        action_details = menu.addAction("📖 Voir les détails")
        menu.addSeparator() # Ligne de séparation visuelle
        action_supprimer = menu.addAction("❌ Supprimer du Grimoire")
        
        action_choisie = menu.exec(self.db_list.mapToGlobal(position))

        # --- GESTION DES CLICS ---
        if action_choisie == action_details:
            self.afficher_details_carte(nom_objet) # On lance la nouvelle fonction !
            
        elif action_choisie == action_supprimer:
            reponse = QMessageBox.question(
                self, 
                "Destruction d'objet", 
                f"Es-tu sûr de vouloir incinérer '{nom_objet}' ?\nCette action est irréversible.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reponse == QMessageBox.StandardButton.Yes:
                self.db.delete_item(nom_objet) 
                self.charger_donnees()

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