# 🪄 Magico — Convertisseur d'images [![GitHub release](https://img.shields.io/github/v/release/Z1t0on/Magico)](https://github.com/Z1t0on/Magico/releases/latest)

Magico est un outil Python avec interface graphique (GUI) qui détourne automatiquement vos images (PNG, JPG, WEBP) grâce à une IA locale et les transforme en fichiers **ICO ou PNG** transparents.

## ✨ Fonctionnalités

- 🗃️ **Support multi-formats** : `.png`, `.jpg`, `.jpeg`, `.webp` (entrée)
- 🖼️ **Formats de sortie** : `.ico` (multi-résolutions) ou `.png` (transparence)
- 🤖 **Modèles IA au choix** : `u2net`, `u2netp`, `isnet-general-use`
- 📐 **Ratio carré** : Centrage et ajustement automatique pour les icônes
- 📦 **Multi-résolutions** : Tailles intégrées de 16x16 à 256x256 pour les ICO
- ⚡ **Traitement par lot** : Dossier entier en un clic
- 🧵 **Multithread** : Interface fluide pendant les traitements
- 📊 **Reporting visuel** : Compteur de succès et d'échecs à la fin du traitement

---

## 🚀 Utilisation (Sans installation)

Si tu utilises l'exécutable portable :

1. Télécharge **`Magico.zip`** depuis la section [Releases](https://github.com/Z1t0on/Magico/releases).
2. Clic droit sur **`Magico.zip`**, extraire tout.
3. Double-clique sur **`Magico.exe`** dans le dossier créé pour lancer l'application.

---

## 💻 Utilisation (Via les sources Python)

### 1. Prérequis
Installe les dépendances requises :
```cmd
pip install -r requirements.txt
```
