# 🪄 Magico — Convertisseur d'icônes  [![GitHub release](https://img.shields.io/github/v/release/Z1t0on/Magico)](https://github.com/Z1t0on/Magico/releases/latest)

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

1. Télécharge **`Magico.zip`** depuis la section Releases.
2. Clic droit sur **`Magico.zip`**, extraire tout.
3. Double-clique sur **`Magico.exe`** dans le dossier créé pour lancer l'application.

---

## 🛠️ Utilisation (Via les sources Python)

### 1. Prérequis
Installe les dépendances requises :
```cmd
pip install -r requirements.txt
