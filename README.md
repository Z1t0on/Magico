# 🪄 Magico — Convertisseur d'icônes

Magico est un outil Python avec interface graphique (GUI) qui détoure automatiquement vos images (PNG, JPG, WEBP) grâce à une IA locale et les transforme en fichiers `.ico` transparents pour Windows.

## ✨ Fonctionnalités

- 🖼️ **Support multi-formats** : `.png`, `.jpg`, `.jpeg`, `.webp`
- 🤖 **Détourage IA auto** : Suppression de l'arrière-plan via `u2net` (`rembg`)
- 📐 **Ratio carré** : Centrage et ajustement sans déformer l'image
- 📦 **Multi-résolutions** : Tailles intégrées de 16x16 jusqu'à 256x256
- ⚡ **Traitement par lot** : Dossier entier en un clic
- 🧵 **Multithread** : Interface fluide pendant les traitements

---

## 🚀 Utilisation (Sans installation)

Si tu utilises l'exécutable portable :

1. Télécharge **`Magico.exe`** depuis la section Releases.
2. Double-clique sur **`Magico.exe`** pour lancer l'application.

---

## 🛠️ Utilisation (Via les sources Python)

### 1. Prérequis
Installe les dépendances requises :
```cmd
pip install -r requirements.txt