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
        self.geometry("480x380")

        # Ajout de l'icône de l'application
        icon_path = os.path.join(BASE_DIR, "app.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        self.session = None
        self.current_modele = None

        # Titre & Sous-titre
        self.title_label = ctk.CTkLabel(
            self, text="Magico", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(25, 5))

        # Barre de chargement
        self.progress = ctk.CTkProgressBar(
            self, width=200, height=4, mode="indeterminate"
        )
        self.progress.pack(pady=(5, 10))
        self.progress.set(0)

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

        # Menu déroulant pour choisir le modèle IA
        self.modele_label = ctk.CTkLabel(
            self, text="Modèle IA :", font=ctk.CTkFont(size=12)
        )
        self.modele_label.pack(pady=(10, 0))

        self.modele_var = ctk.StringVar(value="u2net")
        self.modele_menu = ctk.CTkOptionMenu(
            self,
            variable=self.modele_var,
            values=["u2net", "u2netp", "isnet-general-use"],
            font=ctk.CTkFont(size=12),
            width=200,
        )
        self.modele_menu.pack(pady=(0, 5))

        # Menu déroulant pour choisir le format de sortie
        self.format_label = ctk.CTkLabel(
            self, text="Format de sortie :", font=ctk.CTkFont(size=12)
        )
        self.format_label.pack(pady=(0, 0))

        self.format_var = ctk.StringVar(value="ICO")
        self.format_menu = ctk.CTkOptionMenu(
            self,
            variable=self.format_var,
            values=["ICO", "PNG"],
            font=ctk.CTkFont(size=12),
            width=200,
        )
        self.format_menu.pack(pady=(0, 15))

        # Statut
        self.status = ctk.CTkLabel(
            self, text="Prêt", text_color="gray50", font=ctk.CTkFont(size=12)
        )
        self.status.pack(pady=(15, 0))

    def start_loading(self):
        self.progress.start()

    def stop_loading(self):
        self.progress.stop()
        self.progress.set(0)

    def charger_modele(self):
        modele_souhaite = self.modele_var.get()
        if self.session is None or self.current_modele != modele_souhaite:
            self.status.configure(text="Chargement du modèle IA...")
            self.update()
            self.start_loading()
            from rembg import new_session
            if self.session is not None:
                del self.session
            self.session = new_session(modele_souhaite)
            self.current_modele = modele_souhaite
            self.stop_loading()
            self.status.configure(text="Prêt")

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
        format_sortie = self.format_var.get().lower()
        dossier_sortie = os.path.join(dossier_exe, f"Images_{format_sortie}")
        os.makedirs(dossier_sortie, exist_ok=True)

        succes = 0
        echecs = 0
        for i, f in enumerate(fichiers, 1):
            self.status.configure(
                text=f"Traitement : {i}/{len(fichiers)} — {f}"
            )

            src = os.path.join(dossier_source, f)
            nom_sans_ext = os.path.splitext(f)[0]
            if format_sortie == "ico":
                dest = os.path.join(dossier_sortie, f"{nom_sans_ext}.ico")
            else:
                dest = os.path.join(dossier_sortie, f"{nom_sans_ext}.{format_sortie}")

            try:
                with Image.open(src) as img:
                    img_rgba = img.convert("RGBA")
                    from rembg import remove
                    img_detouree = remove(img_rgba, session=self.session)

                    if format_sortie == "ico":
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
                    else:
                        img_detouree.save(dest, format=format_sortie.upper())
                    succes += 1
            except Exception as e:
                echecs += 1

        if echecs > 0:
            self.status.configure(
                text=f"Terminé ! {succes} image(s) générée(s), {echecs} échec(s).",
                text_color="#f59e0b",
            )
        else:
            self.status.configure(
                text=f"Terminé ! {succes} image(s) dans 'Images_{format_sortie}'.",
                text_color="#22c55e",
            )
        try:
            import winsound
            winsound.Beep(1000, 300)
        except:
            pass
        self.btn_lancer.configure(state="normal")


if __name__ == "__main__":
    app = MagicoApp()
    app.mainloop()