from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QPushButton, QMessageBox, 
                             QLabel, QListWidgetItem, QLineEdit, QDialog)
from PyQt6.QtCore import Qt, QSize
import re

from data_manager import DataManager
from ui_dialogs import CreationDialog, FilterDialog
from ui_components import CauldronWidget, ItemCard # <-- Import depuis le nouveau fichier !

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
        main_layout = QHBoxLayout()
        
        # === PARTIE GAUCHE (70%) ===
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
        
        self.db_list = QListWidget()
        self.db_list.setObjectName("inventory_list") 
        self.db_list.setFlow(QListWidget.Flow.LeftToRight)
        self.db_list.setWrapping(True)
        self.db_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.db_list.setSpacing(8)
        self.db_list.itemClicked.connect(self.afficher_details_panneau)
        
        left_layout.addLayout(top_bar_layout)
        left_layout.addWidget(self.db_list)
        
        # === PARTIE DROITE (30%) ===
        self.details_panel = QWidget()
        self.details_panel.setStyleSheet("""
            QWidget { background-color: #1F2937; border-radius: 8px; border: 1px solid #4A5568; }
            QLabel { border: none; background: transparent; }
        """)
        details_layout = QVBoxLayout(self.details_panel)
        details_layout.setContentsMargins(15, 15, 15, 15)
        details_layout.setSpacing(10)

        self.lbl_detail_nom = QLabel("Sélectionnez une carte")
        self.lbl_detail_nom.setStyleSheet("font-size: 18px; color: #D4AF37; font-weight: bold;")
        self.lbl_detail_nom.setWordWrap(True)
        
        self.lbl_detail_stats = QLabel("Parcourez votre Grimoire pour révéler les secrets de vos créations.")
        self.lbl_detail_stats.setStyleSheet("color: #9CA3AF; font-size: 12px; font-style: italic;")
        self.lbl_detail_stats.setWordWrap(True)
        
        self.lbl_detail_desc = QLabel("")
        self.lbl_detail_desc.setStyleSheet("color: #E2E8F0; font-size: 13px; margin-top: 10px;")
        self.lbl_detail_desc.setWordWrap(True)
        self.lbl_detail_desc.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.btn_modifier = QPushButton("✏️ Modifier cette carte")
        self.btn_modifier.setStyleSheet("background-color: #D4AF37; color: #121212; border: none; padding: 8px; border-radius: 4px; font-weight: bold;")
        self.btn_modifier.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_modifier.hide() 
        self.btn_modifier.clicked.connect(self.modifier_artefact_selectionne)

        self.btn_supprimer = QPushButton("❌ Détruire cette carte")
        self.btn_supprimer.setStyleSheet("background-color: #7F1D1D; color: white; border: 1px solid #EF4444; padding: 8px; border-radius: 4px;")
        self.btn_supprimer.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_supprimer.hide() 
        self.btn_supprimer.clicked.connect(self.supprimer_artefact_selectionne)

        self.btn_add = QPushButton("➕ Ajouter une carte")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet("background-color: #10B981; color: white; border: none; padding: 10px; font-weight: bold; border-radius: 4px;")
        self.btn_add.clicked.connect(self.ajouter_artefact_manuel)

        details_layout.addWidget(self.lbl_detail_nom)
        details_layout.addWidget(self.lbl_detail_stats)
        details_layout.addWidget(self.lbl_detail_desc, 1)
        details_layout.addWidget(self.btn_modifier)
        details_layout.addWidget(self.btn_supprimer)      
        details_layout.addWidget(self.btn_add)            

        main_layout.addWidget(left_panel, 7) 
        main_layout.addWidget(self.details_panel, 3) 
        
        self.tab_grimoire.setLayout(main_layout)
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

    def filtrer_grimoire(self, *args):
        texte_recherche = self.search_bar.text().lower()
        filtres_tags = self.filtres_actifs.get('tags', [])
        filtres_types = self.filtres_actifs.get('types', [])
        filtres_prov = self.filtres_actifs.get('provenances', [])
        
        for i in range(self.db_list.count()):
            item = self.db_list.item(i)
            widget_carte = self.db_list.itemWidget(item)
            
            if widget_carte:
                nom = widget_carte.lbl_nom.text().lower()
                details = widget_carte.lbl_details.text().lower()
                tags_carte = [m.capitalize() for m in re.findall(r'\b\w+\b', str(widget_carte.tags_exact))]
                
                ok_texte = (texte_recherche in nom) or (texte_recherche in details)
                ok_type = (not filtres_types) or (widget_carte.type_item_exact in filtres_types)
                ok_prov = (not filtres_prov) or (widget_carte.provenance_exact in filtres_prov)
                ok_tags = (not filtres_tags) or any(t in tags_carte for t in filtres_tags)
                
                if ok_texte and ok_type and ok_prov and ok_tags:
                    item.setHidden(False)
                else:
                    item.setHidden(True)

    def ouvrir_popup_filtres(self):
        types_uniques = set()
        prov_uniques = set()
        tags_uniques = set()
        
        for item in self.db.data:
            types_uniques.add(item.get('type', 'Inconnu'))
            prov_uniques.add(item.get('provenance', 'Inconnue'))
            mots = [m.capitalize() for m in re.findall(r'\b\w+\b', str(item.get('tags', '')))]
            tags_uniques.update(mots)
        
        dialog = FilterDialog(list(tags_uniques), list(types_uniques), list(prov_uniques), self.filtres_actifs, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.filtres_actifs = dialog.get_filters()
            self.filtrer_grimoire()

    def ajouter_artefact_manuel(self):
        dialog = CreationDialog([], self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nouvel_objet = dialog.get_data()
            self.db.save_item(nouvel_objet)
            self.charger_donnees()
            QMessageBox.information(self, "Succès", f"L'artefact '{nouvel_objet['nom']}' a été consigné !")

    def afficher_details_panneau(self, item):
        nom_objet = item.data(Qt.ItemDataRole.UserRole)
        self.artefact_en_lecture = nom_objet 
        
        item_data = next((i for i in self.db.data if i.get('nom') == nom_objet), None)
        if not item_data: return

        # 1. Titre
        self.lbl_detail_nom.setText(item_data['nom'])
        
        # 2. Stats (Alignées dans un tableau HTML propre)
        tags_clean = str(item_data.get('tags', 'Aucun')).replace('[', '').replace(']', '').replace("'", "").replace('"', '')
        
        stats = f"""
        <table width="100%" cellspacing="4">
            <tr><td style="color:#9CA3AF;" width="85"><b>Type :</b></td><td style="color:#E2E8F0;">{item_data.get('type', 'Inconnu')}</td></tr>
            <tr><td style="color:#9CA3AF;"><b>Tags :</b></td><td style="color:#E2E8F0;">{tags_clean}</td></tr>
            <tr><td style="color:#9CA3AF;"><b>Provenance :</b></td><td style="color:#E2E8F0;">{item_data.get('provenance', 'Inconnue')}</td></tr>
            <tr><td style="color:#9CA3AF;"><b>En stock :</b></td><td style="color:#D4AF37; font-weight:bold; font-size:14px;">{item_data.get('quantite', 1)}</td></tr>
        </table>
        """
        self.lbl_detail_stats.setText(stats)

        # 3. Description et Recette (Titres colorés et espacés)
        desc = item_data.get('desc', "Aucune description n'a été notée.")
        ingredients = item_data.get('ingredients', [])
        recette = ", ".join(ingredients) if ingredients else "Création spontanée"
        
        texte_desc = f"""
        <p style="color: #D4AF37; font-size: 14px; margin-bottom: 2px;"><b>📖 Description</b></p>
        <p style="color: #E2E8F0; font-size: 13px; margin-top: 0px; margin-bottom: 15px; line-height: 1.3;">{desc}</p>
        
        <p style="color: #10B981; font-size: 14px; margin-bottom: 2px;"><b>🧪 Recette d'origine</b></p>
        <p style="color: #E2E8F0; font-size: 13px; margin-top: 0px;"><i>{recette}</i></p>
        """
        self.lbl_detail_desc.setText(texte_desc)
        
        # 4. Affichage du bouton
        self.btn_modifier.show()
        self.btn_supprimer.show()

    def supprimer_artefact_selectionne(self):
        if not self.artefact_en_lecture: return

        reponse = QMessageBox.question(
            self, "Destruction d'objet", 
            f"Es-tu sûr de vouloir incinérer '{self.artefact_en_lecture}' ?\nCette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reponse == QMessageBox.StandardButton.Yes:
            self.db.delete_item(self.artefact_en_lecture) 
            self.charger_donnees()
            self.lbl_detail_nom.setText("Sélectionnez un artefact")
            self.lbl_detail_stats.setText("Parcourez votre Grimoire pour révéler les secrets de vos créations.")
            self.lbl_detail_desc.setText("")
            self.btn_modifier.hide()
            self.btn_supprimer.hide()
            self.artefact_en_lecture = None

    def modifier_artefact_selectionne(self):
        """Ouvre la fenêtre pré-remplie pour modifier l'objet actuel"""
        if not self.artefact_en_lecture: return

        # On récupère toutes les données de l'objet actuellement affiché
        item_data = next((i for i in self.db.data if i.get('nom') == self.artefact_en_lecture), None)
        if not item_data: return

        # On ouvre notre pop-up intelligente en lui passant l'objet
        dialog = CreationDialog([], self, item_to_edit=item_data)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nouvel_objet = dialog.get_data()
            
            # On met à jour la base de données
            self.db.update_item(self.artefact_en_lecture, nouvel_objet)
            self.charger_donnees()
            
            # On remet le panneau à zéro pour forcer l'utilisateur à recliquer (plus sécurisé)
            self.lbl_detail_nom.setText("Sélectionnez une carte")
            self.lbl_detail_stats.setText("Parcourez votre Grimoire pour révéler les secrets de vos créations.")
            self.lbl_detail_desc.setText("")
            self.btn_modifier.hide()
            self.btn_supprimer.hide()
            self.artefact_en_lecture = None
            
            QMessageBox.information(self, "Succès", f"La carte a été mis à jour avec succès !")

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