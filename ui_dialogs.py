from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QTextEdit, QPushButton

class CreationDialog(QDialog):
    def __init__(self, ingredients, parent=None):
        super().__init__(parent)
        self.setWindowTitle("✨ Nouvelle Découverte Alchimique ✨")
        self.setMinimumWidth(400)
        
        # 1. On stocke les ingrédients en mémoire pour la recette finale
        self.ingredients_utilises = ingredients

        layout = QFormLayout()

        # Ingrédients utilisés (affichage en lecture seule pour rappel visuel)
        ingredients_text = ", ".join(ingredients)
        if not ingredients_text:
            ingredients_text = "Aucun (Création spontanée)"
        layout.addRow("Ingrédients utilisés :", QLineEdit(ingredients_text, readOnly=True))

        # --- CHAMPS DU FORMULAIRE (Adaptés à tes données) ---
        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Ex: Potion de Soin Mineure")
        
        self.provenance_input = QLineEdit()
        self.provenance_input.setText("Atelier Alchimique") # Valeur par défaut logique pour un craft
        self.provenance_input.setPlaceholderText("Ex: Nature, Atelier Alchimique...")
        
        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("Ex: Item, Potion, Arme...")
        
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Ex: [Soin, Magie]")
        
        self.quantite_input = QLineEdit()
        self.quantite_input.setText("1") # On crée généralement 1 objet à la fois par défaut
        
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Description et effets de l'objet...")

        # Ajout des champs au layout
        layout.addRow("Nom :", self.nom_input)
        layout.addRow("Provenance :", self.provenance_input)
        layout.addRow("Type :", self.type_input)
        layout.addRow("Tags :", self.tags_input)
        layout.addRow("Quantité :", self.quantite_input)
        layout.addRow("Description :", self.desc_input)

        # Bouton de validation
        self.btn_save = QPushButton("Enregistrer dans le Grimoire")
        self.btn_save.clicked.connect(self.accept)
        layout.addRow(self.btn_save)

        self.setLayout(layout)

    def get_data(self):
        """Retourne les données saisies sous forme de dictionnaire compatible avec data.json"""
        return {
            "nom": self.nom_input.text(),
            "provenance": self.provenance_input.text(),
            "type": self.type_input.text(),
            "tags": self.tags_input.text(),
            "quantite": self.quantite_input.text(),
            "desc": self.desc_input.toPlainText(),
            "ingredients": self.ingredients_utilises # 🪄 La fameuse recette sauvegardée ici !
        }