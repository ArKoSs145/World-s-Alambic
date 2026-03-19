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
                {"nom": "Potion de soin mineure", "provenance": "Alambic", "type": "Potion", "tags": ["Soin", "Mineur", "Magie"], "quantite": "1", "desc": "Potion qui soigne quand appliqué sur la blessure", "ingredients": ["Base eau","Sel d'ammoniac", "Écorce de chêne","Feuille de Chêne"]},
                {"nom": "Potion de mana mineure", "provenance": "Alambic", "type": "Potion", "tags": ["Mana", "Mineur", "Magie"], "quantite": "1", "desc": "Potion qui régenère le mana quand consommé", "ingredients": ["Base eau","Mana", "Pourdre de magnétite","Champignons luisants"]},
                {"nom": "Potion de poison mineure", "provenance": "Alambic", "type": "Potion", "tags": ["Poison", "Mineur", "Magie"], "quantite": "1", "desc": "Potion qui empoisonne quand consommé", "ingredients": ["Base Huile", "Queue de rat","Balignes","Sel d'ammoniac"]},
                {"nom": "Potion de paralysie", "provenance": "Alambic", "type": "Potion", "tags": ["Foudre", "Moyen", "Magie"], "quantite": "1", "desc": "Potion qui taze quand consommé", "ingredients": ["Base eau", "Champignons paralysants","Pourdre de magnétite","Pierre de mana"]}


            ]
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=4, ensure_ascii=False)
            return default_data
            
        with open(self.filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
        
    def save_data(self):
        """Sauvegarde la liste complète des données actuelles dans le JSON."""
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def save_item(self, nouvel_objet):
        """Ajoute un nouvel objet à la liste et sauvegarde le fichier."""
        self.data.append(nouvel_objet)
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def delete_item(self, nom_item):
        """Supprime un objet par son nom et sauvegarde le fichier JSON"""
        # On garde tous les objets SAUF celui qui a le nom qu'on veut supprimer
        self.data = [item for item in self.data if item.get('nom') != nom_item]
        self.save_data()

    def update_item(self, nom_original, nouvelles_donnees):
        """Met à jour un objet existant en le remplaçant par ses nouvelles données."""
        for i, item in enumerate(self.data):
            if item.get('nom') == nom_original:
                self.data[i] = nouvelles_donnees # On remplace l'ancienne carte par la nouvelle
                break
        self.save_data()