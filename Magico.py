import os
import sys
import ctypes
import importlib.metadata

# Patch pour les métadonnées manquantes dans l'exécutable
_original_version = importlib.metadata.version

def _patched_version(package_name):
    try:
        return _original_version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return "0.0.0"

importlib.metadata.version = _patched_version

# Force l'icône dans la barre des tâches sous Windows
try:
    myappid = "vibe.coding.magico.1.0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

import threading
import customtkinter as ctk
from PIL import Image
from rembg import new_session, remove

# Configuration du thème
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
ICON_SIZES = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]

# Obtenir le dossier racine (compatible mode .py et mode .exe PyInstaller)
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class MagicoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Magico — Convertisseur d'icônes")
        self.geometry("480x280")
        self.resizable(False, False)

        # Ajout de l'icône de l'application
        try:
            self.iconbitmap(os.path.join(BASE_DIR, "app.ico"))
        except Exception:
            pass

        self.session = None

        # Titre & Sous-titre
        self.title_label = ctk.CTkLabel(
            self, text="Magico", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(25, 5))

        self.subtitle_label = ctk.CTkLabel(
            self,
            text="Transforme tes images en .ico transparents",
            font=ctk.CTkFont(size=13),
            text_color="gray70",
        )
        self.subtitle_label.pack(pady=(0, 20))

        # Bouton principal
        self.btn_lancer = ctk.CTkButton(
            self,
            text="Sélectionner un dossier",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=220,
            corner_radius=8,
            command=self.lancer_traitement_thread,
        )
        self.btn_lancer.pack(pady=10)

        # Statut
        self.status = ctk.CTkLabel(
            self, text="Prêt", text_color="gray50", font=ctk.CTkFont(size=12)
        )
        self.status.pack(pady=(15, 0))

    def charger_modele(self):
        if not self.session:
            self.status.configure(text="Chargement du modèle IA...")
            self.session = new_session("u2net")

    def lancer_traitement_thread(self):
        dossier_source = ctk.filedialog.askdirectory(
            title="Choisir le dossier contenant les images"
        )
        if not dossier_source:
            return

        self.btn_lancer.configure(state="disabled")
        threading.Thread(
            target=self.traiter_dossier, args=(dossier_source,), daemon=True
        ).start()

    def traiter_dossier(self, dossier_source):
        fichiers = [
            f
            for f in os.listdir(dossier_source)
            if f.lower().endswith(EXTENSIONS)
        ]
        if not fichiers:
            self.status.configure(text="Aucune image trouvée dans ce dossier.")
            self.btn_lancer.configure(state="normal")
            return

        self.charger_modele()

# Récupère le vrai dossier du .exe
        if getattr(sys, 'frozen', False):
            dossier_exe = os.path.dirname(sys.executable)
        else:
            dossier_exe = os.path.dirname(os.path.abspath(__file__))

        # Dossier de sortie à côté de Magico.exe
        dossier_sortie = os.path.join(dossier_exe, "Icones_Générées")
        os.makedirs(dossier_sortie, exist_ok=True)

        succes = 0
        for i, f in enumerate(fichiers, 1):
            self.status.configure(
                text=f"Traitement : {i}/{len(fichiers)} — {f}"
            )

            src = os.path.join(dossier_source, f)
            dest = os.path.join(dossier_sortie, f"{os.path.splitext(f)[0]}.ico")

            try:
                with Image.open(src) as img:
                    img_rgba = img.convert("RGBA")
                    img_detouree = remove(img_rgba, session=self.session)

                    side = max(img_detouree.size)
                    carre = Image.new("RGBA", (side, side), (0, 0, 0, 0))
                    carre.paste(
                        img_detouree,
                        (
                            (side - img_detouree.width) // 2,
                            (side - img_detouree.height) // 2,
                        ),
                    )
                    carre.save(dest, format="ICO", sizes=ICON_SIZES)
                    succes += 1
            except Exception as e:
                print(f"Erreur sur {f}: {e}")

        self.status.configure(
            text=f"Terminé ! {succes} icône(s) dans 'Icones_Générées'.",
            text_color="#22c55e",
        )
        self.btn_lancer.configure(state="normal")


if __name__ == "__main__":
    app = MagicoApp()
    app.mainloop()