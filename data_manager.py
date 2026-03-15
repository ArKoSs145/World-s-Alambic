import json
import os

class DataManager:
    def __init__(self, filepath="data.json"):
        self.filepath = filepath
        self.data = self.load_data()

    def load_data(self):
        """Charge le JSON ou crée une base de données par défaut s'il n'existe pas."""
        if not os.path.exists(self.filepath):
            default_data = [
                {"nom": "Fleur de Feu", "provenance": "Nature", "type": "Item", "tags": ["Feu", "Plante"], "quantite": "4", "desc": "Une fleure enflammée.", "ingredients": []},
                {"nom": "Cailloux", "provenance": "Nature", "type": "Item", "tags": ["Terre", "Solide"], "quantite": "4", "desc": "Kayou.", "ingredients": []},
                {"nom": "Épée", "provenance": "Achat/Forge", "type": "Arme", "tags": ["Fer", "Solide", "Tranchant"], "quantite": "1", "desc": "Average épée random.", "ingredients": []},  
                {"nom": "Épée Enflammée", "provenance": "Atelier Alchimique", "type": "Arme Magique", "tags": ["Feu", "Fer", "Magie"], "quantite": "1", "desc": "Une épée qui brûle ses ennemis.", "ingredients": ["Épée", "Fleur de Feu"]}
            ]
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=4, ensure_ascii=False)
            return default_data
            
        with open(self.filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_item(self, nouvel_objet):
        """Ajoute un nouvel objet à la liste et sauvegarde le fichier."""
        self.data.append(nouvel_objet)
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)