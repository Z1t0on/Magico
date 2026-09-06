import os
import sys
import ctypes
import gc
import importlib.metadata
import logging
import queue

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
from tkinter import filedialog
from PIL import Image

# Configuration du thème
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ICON_SIZES = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]

# Obtenir le dossier racine (compatible mode .py et mode .exe PyInstaller)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(
    filename=os.path.join(BASE_DIR, "magico_debug.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(threadName)s — %(message)s",
)
logger = logging.getLogger("magico")


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
        self.dossier_destination = None
        self.ui_queue = queue.Queue()

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
            text="Transforme tes images en fichiers transparents",
            font=ctk.CTkFont(size=13),
            text_color="gray70",
        )
        self.subtitle_label.pack(pady=(0, 20))

        # Bouton principal
        self.btn_lancer = ctk.CTkButton(
            self,
            text="Sélectionner des images",
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
            values=["ICO", "PNG", "WEBP"],
            font=ctk.CTkFont(size=12),
            width=200,
        )
        self.format_menu.pack(pady=(0, 8))

        # Sélection du dossier de destination facultatif
        self.btn_destination = ctk.CTkButton(
            self,
            text="Choisir le dossier de sortie",
            font=ctk.CTkFont(size=12),
            height=32,
            width=220,
            command=self.choisir_destination,
        )
        self.btn_destination.pack(pady=(0, 4))

        self.destination_status = ctk.CTkLabel(
            self,
            text="Destination : dossier parent de chaque image",
            text_color="gray50",
            font=ctk.CTkFont(size=11),
            wraplength=430,
        )
        self.destination_status.pack(pady=(0, 8))

        # Statut
        self.status = ctk.CTkLabel(
            self, text="Prêt", text_color="gray50", font=ctk.CTkFont(size=12)
        )
        self.status.pack(pady=(15, 0))
        self.after(50, self._traiter_messages_ui)

    def start_loading(self):
        self.progress.start()

    def stop_loading(self):
        self.progress.stop()
        self.progress.set(0)

    def choisir_destination(self):
        dossier = filedialog.askdirectory(
            title="Choisir le dossier de sortie"
        )
        if not dossier:
            return

        self.dossier_destination = dossier
        self.destination_status.configure(text=f"Destination : {dossier}")

    def _publier_evenement_ui(self, evenement, **donnees):
        """Publie des données pour la boucle UI sans toucher à ses widgets."""
        self.ui_queue.put((evenement, donnees))

    def _traiter_messages_ui(self):
        """Applique les événements du worker exclusivement dans le thread UI."""
        try:
            while True:
                evenement, donnees = self.ui_queue.get_nowait()
                if evenement == "chargement_modele":
                    self.status.configure(
                        text="Chargement du modèle IA...", text_color="gray50"
                    )
                    self.start_loading()
                elif evenement == "modele_pret":
                    self.stop_loading()
                    self.status.configure(text="Prêt", text_color="gray50")
                elif evenement == "statut":
                    self.status.configure(
                        text=donnees["texte"],
                        text_color=donnees.get("couleur", "gray50"),
                    )
                elif evenement == "arret_chargement":
                    self.stop_loading()
                elif evenement == "bouton":
                    self.btn_lancer.configure(state=donnees["etat"])
        except queue.Empty:
            pass
        except Exception:
            logger.exception("Erreur lors de la mise à jour de l'IHM.")
        finally:
            self.after(50, self._traiter_messages_ui)

    def charger_modele(self, modele_souhaite):
        if self.session is None or self.current_modele != modele_souhaite:
            self._publier_evenement_ui("chargement_modele")
            try:
                from rembg import new_session
                if self.session is not None:
                    del self.session
                    self.session = None
                    gc.collect()
                self.session = new_session(modele_souhaite)
                self.current_modele = modele_souhaite
                self._publier_evenement_ui("modele_pret")
                return True
            except Exception as e:
                logger.exception("Impossible de charger le modèle %s.", modele_souhaite)
                self._publier_evenement_ui("arret_chargement")
                self._publier_evenement_ui(
                    "statut",
                    texte=f"Erreur : {str(e)}",
                    couleur="#ef4444",
                )
                self.current_modele = None
                return False
        return True

    def lancer_traitement_thread(self):
        fichiers = filedialog.askopenfilenames(
            title="Sélectionner une ou plusieurs images",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.webp *.bmp"),
            ],
        )
        if not fichiers:
            return

        logger.info("%d fichier(s) ajouté(s) à la file d'attente.", len(fichiers))
        modele_souhaite = self.modele_var.get()
        format_sortie = self.format_var.get().lower()
        dossier_destination = self.dossier_destination
        logger.info(
            "Export sélectionné : format=%s ; destination=%s.",
            format_sortie.upper(),
            dossier_destination or "dossier parent de chaque image",
        )
        self.btn_lancer.configure(state="disabled")
        threading.Thread(
            target=self._executer_traitement,
            args=(
                fichiers,
                modele_souhaite,
                format_sortie,
                dossier_destination,
            ),
            daemon=True,
        ).start()

    def _executer_traitement(
        self, fichiers, modele_souhaite, format_sortie, dossier_destination
    ):
        """Point d'entrée protégé du worker : aucune opération IHM directe."""
        try:
            self.traiter_fichiers(
                fichiers,
                modele_souhaite,
                format_sortie,
                dossier_destination,
            )
        except Exception:
            logger.exception("Erreur non gérée dans le worker de traitement.")
            self._publier_evenement_ui(
                "statut",
                texte="Erreur inattendue pendant le traitement.",
                couleur="#ef4444",
            )
        finally:
            self._publier_evenement_ui("bouton", etat="normal")

    def traiter_fichiers(
        self, fichiers, modele_souhaite, format_sortie, dossier_destination
    ):
        if not fichiers or not self.charger_modele(modele_souhaite):
            return

        succes = 0
        echecs = 0
        for i, src in enumerate(fichiers, 1):
            self._publier_evenement_ui(
                "statut",
                texte=f"Traitement : {i}/{len(fichiers)} — {os.path.basename(src)}",
            )

            nom_sans_ext = os.path.splitext(os.path.basename(src))[0]
            dossier_sortie = dossier_destination or os.path.dirname(src)
            dest = os.path.join(
                dossier_sortie, f"{nom_sans_ext}.{format_sortie}"
            )

            try:
                os.makedirs(dossier_sortie, exist_ok=True)
                with Image.open(src) as img:
                    img_rgba = img.convert("RGBA")
                    try:
                        from rembg import remove
                        img_detouree = remove(img_rgba, session=self.session)
                        try:
                            image_export = img_detouree.convert("RGBA")
                            try:
                                if format_sortie == "ico":
                                    side = max(image_export.size)
                                    carre = Image.new(
                                        "RGBA", (side, side), (0, 0, 0, 0)
                                    )
                                    try:
                                        carre.paste(
                                            image_export,
                                            (
                                                (side - image_export.width) // 2,
                                                (side - image_export.height) // 2,
                                            ),
                                        )
                                        carre.save(
                                            dest, format="ICO", sizes=ICON_SIZES
                                        )
                                    finally:
                                        carre.close()
                                else:
                                    image_export.save(
                                        dest, format=format_sortie.upper()
                                    )
                            finally:
                                image_export.close()
                        finally:
                            img_detouree.close()
                    finally:
                        img_rgba.close()
                    succes += 1
            except Exception:
                logger.exception("Échec du traitement de l'image %s.", src)
                echecs += 1

        if echecs > 0:
            self._publier_evenement_ui(
                "statut",
                texte=f"Terminé ! {succes} image(s) générée(s), {echecs} échec(s).",
                couleur="#f59e0b",
            )
        else:
            self._publier_evenement_ui(
                "statut",
                texte=(
                    f"Terminé ! {succes} image(s) dans "
                    f"'{dossier_destination or 'le dossier parent de chaque image'}'."
                ),
                couleur="#22c55e",
            )
        try:
            import winsound
            winsound.Beep(1000, 300)
        except Exception:
            logger.debug("Notification sonore indisponible.", exc_info=True)


if __name__ == "__main__":
    app = MagicoApp()
    app.mainloop()