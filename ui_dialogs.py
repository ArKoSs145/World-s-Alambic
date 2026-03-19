from PyQt6.QtWidgets import (QFormLayout, QLineEdit, QTextEdit, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, 
                             QScrollArea, QWidget)
from PyQt6.QtCore import Qt

class CreationPanel(QFrame):
    def __init__(self, ingredients, main_app, item_to_edit=None):
        super().__init__()
        self.main_app = main_app
        self.item_to_edit = item_to_edit
        
        # Style du panneau flottant
        self.setStyleSheet("""
            QFrame { background-color: #1F2937; border-radius: 8px; border: 1px solid #D4AF37; }
            QLabel { border: none; font-weight: bold; color: #D4AF37; }
        """)
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout(self)
        
        # Titre
        titre_texte = "✏️ Modification de l'Artefact" if item_to_edit else "✨ Nouvelle Découverte Alchimique ✨"
        lbl_titre = QLabel(titre_texte)
        lbl_titre.setStyleSheet("font-size: 16px; margin-bottom: 10px; text-align: center;")
        lbl_titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_titre)

        if item_to_edit:
            self.ingredients_utilises = item_to_edit.get('ingredients', [])
        else:
            self.ingredients_utilises = ingredients

        form_layout = QFormLayout()

        self.ingredients_input = QLineEdit()
        if self.ingredients_utilises == ["Recette inconnue"]:
            ingredients_text = ""
        else:
            ingredients_text = ", ".join(self.ingredients_utilises)
            
        self.ingredients_input.setText(ingredients_text)
        self.ingredients_input.setPlaceholderText("Ex: Épée, Fleur de Feu (Vide = Recette inconnue)")
        form_layout.addRow("Ingrédients :", self.ingredients_input)

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
            if isinstance(tags_val, list): tags_val = ", ".join(tags_val)
            self.tags_input.setText(str(tags_val).replace('[', '').replace(']', '').replace("'", ""))
            self.quantite_input.setText(str(item_to_edit.get('quantite', '1')))
            self.desc_input.setPlainText(item_to_edit.get('desc', ''))
        else:
            self.nom_input.setPlaceholderText("Ex: Potion de Soin Mineure")
            self.provenance_input.setText("Atelier Alchimique")
            self.type_input.setPlaceholderText("Ex: Item, Arme...")
            self.tags_input.setPlaceholderText("Ex: Soin, Magie")
            self.quantite_input.setText("1")

        form_layout.addRow("Nom :", self.nom_input)
        form_layout.addRow("Provenance :", self.provenance_input)
        form_layout.addRow("Type :", self.type_input)
        form_layout.addRow("Tags :", self.tags_input)
        form_layout.addRow("Quantité :", self.quantite_input)
        form_layout.addRow("Description :", self.desc_input)
        
        layout.addLayout(form_layout)

        # Boutons d'action
        btn_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("❌ Annuler")
        self.btn_cancel.setStyleSheet("background-color: #4A5568; color: white;")
        self.btn_cancel.clicked.connect(self.main_app.fermer_overlay)
        
        texte_bouton = "💾 Sauvegarder" if item_to_edit else "✨ Enregistrer"
        self.btn_save = QPushButton(texte_bouton)
        self.btn_save.setStyleSheet("background-color: #10B981; color: white;")
        self.btn_save.clicked.connect(self.valider)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def valider(self):
        ingredients_bruts = self.ingredients_input.text().strip()
        liste_ingredients = [ing.strip() for ing in ingredients_bruts.split(',') if ing.strip()] if ingredients_bruts else ["Recette inconnue"]
            
        data = {
            "nom": self.nom_input.text(),
            "provenance": self.provenance_input.text(),
            "type": self.type_input.text(),
            "tags": self.tags_input.text(),
            "quantite": self.quantite_input.text(),
            "desc": self.desc_input.toPlainText(),
            "ingredients": liste_ingredients
        }
        
        # On envoie les données à l'application principale pour qu'elle s'occupe de la sauvegarde
        nom_original = self.item_to_edit.get('nom') if self.item_to_edit else None
        self.main_app.traiter_sauvegarde_artefact(data, nom_original)

class FilterPanel(QFrame):
    def __init__(self, tags_list, types_list, prov_list, filtres_actuels, main_app):
        super().__init__()
        self.main_app = main_app
        
        # 👇 1. On donne un nom au panneau pour isoler sa bordure !
        self.setObjectName("PopupPanel")
        self.setStyleSheet("""
            #PopupPanel { 
                background-color: #1F2937; 
                border-radius: 8px; 
                border: 2px solid #D4AF37; 
            }
        """)
        self.setMinimumWidth(550)
        self.setMinimumHeight(450)

        self.btn_tags = {}
        self.btn_types = {}
        self.btn_prov = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_titre = QLabel("⚙️ Filtres Avancés de l'Alambic")
        lbl_titre.setStyleSheet("font-size: 18px; font-weight: bold; color: #D4AF37; border: none; margin-bottom: 5px;")
        lbl_titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_titre)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)

        self.creer_section(scroll_layout, "🏷️ Tags Élémentaires", tags_list, self.btn_tags, filtres_actuels.get('tags', []))
        self.creer_section(scroll_layout, "📦 Types d'Objets", types_list, self.btn_types, filtres_actuels.get('types', []))
        self.creer_section(scroll_layout, "🌍 Provenances", prov_list, self.btn_prov, filtres_actuels.get('provenances', []))

        scroll_layout.addStretch() 
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Style des boutons du bas
        btn_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("❌ Fermer")
        self.btn_cancel.setStyleSheet("background-color: #4A5568; color: white; border: none; padding: 8px; border-radius: 4px;")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.main_app.fermer_overlay)
        
        btn_reset = QPushButton("Réinitialiser")
        btn_reset.setStyleSheet("background-color: #374151; color: white; border: 1px solid #4A5568; padding: 8px; border-radius: 4px;")
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.clicked.connect(self.reset_filters)
        
        btn_apply = QPushButton("Appliquer les filtres")
        btn_apply.setStyleSheet("background-color: #D4AF37; color: #121212; font-weight: bold; border: none; padding: 8px; border-radius: 4px;")
        btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_apply.clicked.connect(self.appliquer)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(btn_reset)
        btn_layout.addWidget(btn_apply)
        layout.addLayout(btn_layout)

    def creer_section(self, parent_layout, titre, elements, btn_dict, actifs):
        header_layout = QHBoxLayout()
        lbl_titre = QLabel(titre)
        lbl_titre.setStyleSheet("font-weight: bold; color: #E2E8F0; font-size: 14px; border: none;")
        
        # 👇 2. On répare les lignes de séparation !
        ligne = QFrame()
        ligne.setFrameShape(QFrame.Shape.HLine)
        ligne.setStyleSheet("border: none; background-color: #4A5568; max-height: 1px;") 
        
        header_layout.addWidget(lbl_titre)
        header_layout.addWidget(ligne, 1) 
        parent_layout.addLayout(header_layout)

        grid = QGridLayout()
        grid.setSpacing(10)
        row, col = 0, 0

        # 👇 3. Le fameux style "Pilule / Chip" pour les tags
        chip_style = """
            QPushButton {
                background-color: #2D3748;
                color: #9CA3AF;
                border: 1px solid #4A5568;
                border-radius: 12px;
                padding: 5px 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                border: 1px solid #D4AF37;
                color: #E2E8F0;
            }
            QPushButton:checked {
                background-color: #D4AF37;
                color: #121212;
                font-weight: bold;
                border: 1px solid #D4AF37;
            }
        """

        for element in sorted(elements):
            if not element: continue
            btn = QPushButton(element)
            btn.setCheckable(True) 
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(chip_style) # On force ce style spécifique !
            
            if element in actifs: 
                btn.setChecked(True) 
                
            grid.addWidget(btn, row, col)
            btn_dict[element] = btn
            
            col += 1
            if col >= 4:
                col = 0
                row += 1

        parent_layout.addLayout(grid)
        parent_layout.addSpacing(10)

    def reset_filters(self):
        for btn in self.btn_tags.values(): btn.setChecked(False)
        for btn in self.btn_types.values(): btn.setChecked(False)
        for btn in self.btn_prov.values(): btn.setChecked(False)

    def appliquer(self):
        filtres = {
            'tags': [name for name, btn in self.btn_tags.items() if btn.isChecked()],
            'types': [name for name, btn in self.btn_types.items() if btn.isChecked()],
            'provenances': [name for name, btn in self.btn_prov.items() if btn.isChecked()]
        }
        self.main_app.traiter_application_filtres(filtres)