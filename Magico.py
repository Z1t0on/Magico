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
        self.animating = False
        self.animation_index = 0

        # Titre & Sous-titre
        self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.title_frame.pack(pady=(25, 5))

        self.letter_labels = []
        for char in "Magico":
            label = ctk.CTkLabel(
                self.title_frame,
                text=char,
                font=ctk.CTkFont(size=24, weight="bold")
            )
            label.pack(side="left", padx=2)
            self.letter_labels.append(label)

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
        self.modele_menu.pack(pady=(0, 15))

        # Statut
        self.status = ctk.CTkLabel(
            self, text="Prêt", text_color="gray50", font=ctk.CTkFont(size=12)
        )
        self.status.pack(pady=(15, 0))

    def animate_title(self):
        if not self.animating:
            return
        for i, label in enumerate(self.letter_labels):
            offset = (self.animation_index + i * 2) % 10
            if offset < 5:
                y_offset = offset
            else:
                y_offset = 10 - offset
            label.configure(text=label.cget("text"))
            label.place_forget()
            label.place(x=i * 30, y=-y_offset)
        self.animation_index += 1
        self.after(100, self.animate_title)

    def stop_animation(self):
        self.animating = False
        for i, label in enumerate(self.letter_labels):
            label.place_forget()
            label.pack(side="left", padx=2)

    def start_animation(self):
        self.animating = True
        self.animation_index = 0
        for label in self.letter_labels:
            label.pack_forget()
        self.animate_title()

    def charger_modele(self):
        if not self.session:
            self.status.configure(text="Chargement du modèle IA...")
            self.update()
            self.start_animation()
            from rembg import new_session
            modele = self.modele_var.get()
            self.session = new_session(modele)
            self.stop_animation()

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
                    from rembg import remove
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