from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QTextEdit, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, 
                             QScrollArea, QWidget)
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QTextEdit, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, 
                             QScrollArea, QWidget)
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QTextEdit, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, 
                             QScrollArea, QWidget)
from PyQt6.QtCore import Qt

class CreationDialog(QDialog):
    def __init__(self, ingredients, parent=None, item_to_edit=None):
        super().__init__(parent)
        
        titre = "✏️ Modification de la Carte" if item_to_edit else "✨ Nouvelle Découverte Alchimique ✨"
        self.setWindowTitle(titre)
        self.setMinimumWidth(400)
        
        if item_to_edit:
            self.ingredients_utilises = item_to_edit.get('ingredients', [])
        else:
            self.ingredients_utilises = ingredients

        layout = QFormLayout()

        # 👇 NOUVEAU : Le champ des ingrédients est maintenant modifiable !
        self.ingredients_input = QLineEdit()
        
        # On nettoie la liste s'il y avait "Recette inconnue" pour ne pas polluer le champ à la modification
        if self.ingredients_utilises == ["Recette inconnue"]:
            ingredients_text = ""
        else:
            ingredients_text = ", ".join(self.ingredients_utilises)
            
        self.ingredients_input.setText(ingredients_text)
        self.ingredients_input.setPlaceholderText("Ex: Épée, Fleur de Feu (Vide = Recette inconnue)")
        layout.addRow("Ingrédients :", self.ingredients_input)

        # --- CHAMPS DU FORMULAIRE ---
        self.nom_input = QLineEdit()
        self.provenance_input = QLineEdit()
        self.type_input = QLineEdit()
        self.tags_input = QLineEdit()
        self.quantite_input = QLineEdit()
        self.desc_input = QTextEdit()

        if item_to_edit:
            self.nom_input.setText(item_to_edit.get('nom', ''))
            self.provenance_input.setText(item_to_edit.get('provenance', ''))
            self.type_input.setText(item_to_edit.get('type', ''))
            
            tags_val = item_to_edit.get('tags', '')
            if isinstance(tags_val, list):
                tags_val = ", ".join(tags_val)
            self.tags_input.setText(str(tags_val).replace('[', '').replace(']', '').replace("'", ""))
            
            self.quantite_input.setText(str(item_to_edit.get('quantite', '1')))
            self.desc_input.setPlainText(item_to_edit.get('desc', ''))
        else:
            self.nom_input.setPlaceholderText("Ex: Potion de Soin Mineure")
            self.provenance_input.setText("Atelier Alchimique")
            self.provenance_input.setPlaceholderText("Ex: Nature, Atelier Alchimique...")
            self.type_input.setPlaceholderText("Ex: Item, Potion, Arme...")
            self.tags_input.setPlaceholderText("Ex: Soin, Magie")
            self.quantite_input.setText("1")
            self.desc_input.setPlaceholderText("Description et effets de l'objet...")

        layout.addRow("Nom :", self.nom_input)
        layout.addRow("Provenance :", self.provenance_input)
        layout.addRow("Type :", self.type_input)
        layout.addRow("Tags :", self.tags_input)
        layout.addRow("Quantité :", self.quantite_input)
        layout.addRow("Description :", self.desc_input)

        texte_bouton = "💾 Sauvegarder les modifications" if item_to_edit else "Enregistrer dans le Grimoire"
        self.btn_save = QPushButton(texte_bouton)
        self.btn_save.clicked.connect(self.accept)
        layout.addRow(self.btn_save)

        self.setLayout(layout)

    def get_data(self):
        """Retourne les données saisies sous forme de dictionnaire"""
        
        # 👇 NOUVEAU : On lit le champ texte et on le transforme en liste Python !
        ingredients_bruts = self.ingredients_input.text().strip()
        
        if ingredients_bruts:
            # On coupe le texte à chaque virgule pour créer une liste proprement
            liste_ingredients = [ing.strip() for ing in ingredients_bruts.split(',') if ing.strip()]
        else:
            # Si le champ est totalement vide, on met notre valeur par défaut
            liste_ingredients = ["Recette inconnue"]
            
        return {
            "nom": self.nom_input.text(),
            "provenance": self.provenance_input.text(),
            "type": self.type_input.text(),
            "tags": self.tags_input.text(),
            "quantite": self.quantite_input.text(),
            "desc": self.desc_input.toPlainText(),
            "ingredients": liste_ingredients # On sauvegarde la nouvelle liste générée !
        }

class FilterDialog(QDialog):
    def __init__(self, tags_list, types_list, prov_list, filtres_actuels, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Filtres Avancés de l'Alambic")
        self.setMinimumWidth(550)
        self.setMinimumHeight(450)

        # Dictionnaires pour mémoriser l'état de chaque bouton
        self.btn_tags = {}
        self.btn_types = {}
        self.btn_prov = {}

        main_layout = QVBoxLayout(self)

        # --- Zone de défilement (Scroll Area) si on a beaucoup de filtres ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # --- Création de nos 3 sections stylisées ---
        self.creer_section(scroll_layout, "🏷️ Tags Élémentaires", tags_list, self.btn_tags, filtres_actuels.get('tags', []))
        self.creer_section(scroll_layout, "📦 Types d'Objets", types_list, self.btn_types, filtres_actuels.get('types', []))
        self.creer_section(scroll_layout, "🌍 Provenances", prov_list, self.btn_prov, filtres_actuels.get('provenances', []))

        scroll_layout.addStretch() # Pousse tout vers le haut proprement
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # --- Boutons d'action (Appliquer / Reset) ---
        btn_layout = QHBoxLayout()
        btn_reset = QPushButton("Réinitialiser")
        btn_apply = QPushButton("Appliquer les filtres")

        btn_reset.clicked.connect(self.reset_filters)
        btn_apply.clicked.connect(self.accept)

        btn_layout.addWidget(btn_reset)
        btn_layout.addWidget(btn_apply)
        main_layout.addLayout(btn_layout)

    def creer_section(self, parent_layout, titre, elements, btn_dict, actifs):
        """Créé un Titre, une ligne de séparation, et une grille de boutons"""
        # 1. En-tête (Titre + Ligne)
        header_layout = QHBoxLayout()
        lbl_titre = QLabel(titre)
        lbl_titre.setStyleSheet("font-weight: bold; color: #D4AF37; font-size: 14px;")
        
        ligne = QFrame()
        ligne.setFrameShape(QFrame.Shape.HLine)
        ligne.setStyleSheet("background-color: #4A5568;")

        header_layout.addWidget(lbl_titre)
        header_layout.addWidget(ligne, 1) # Le "1" permet à la ligne de s'étirer à l'infini
        parent_layout.addLayout(header_layout)

        # 2. Grille de boutons (4 colonnes maximum)
        grid = QGridLayout()
        grid.setSpacing(8)
        row, col = 0, 0
        max_cols = 4 

        for element in sorted(elements):
            if not element: continue
            
            btn = QPushButton(element)
            btn.setCheckable(True) # Rend le bouton "cochable" (On/Off)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            if element in actifs:
                btn.setChecked(True) # Si le filtre était déjà actif, on l'enfonce

            grid.addWidget(btn, row, col)
            btn_dict[element] = btn

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        parent_layout.addLayout(grid)
        parent_layout.addSpacing(20) # Espace avant la section suivante

    def reset_filters(self):
        """Décoche tous les boutons"""
        for btn in self.btn_tags.values(): btn.setChecked(False)
        for btn in self.btn_types.values(): btn.setChecked(False)
        for btn in self.btn_prov.values(): btn.setChecked(False)

    def get_filters(self):
        """Renvoie un dictionnaire avec uniquement les noms des boutons enfoncés"""
        return {
            'tags': [name for name, btn in self.btn_tags.items() if btn.isChecked()],
            'types': [name for name, btn in self.btn_types.items() if btn.isChecked()],
            'provenances': [name for name, btn in self.btn_prov.items() if btn.isChecked()]
        }