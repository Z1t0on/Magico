import os

from PIL import Image, ImageChops


class ImageProcessor:
    """Pipeline de détourage et d'export d'une image, sans dépendance à l'IHM."""

    ICON_SIZES = [
        (256, 256),
        (128, 128),
        (64, 64),
        (48, 48),
        (32, 32),
        (16, 16),
    ]
    FORMATS_SUPPORTES = frozenset(("ico", "png", "webp"))

    @classmethod
    def process_file(
        cls,
        source_path,
        session,
        output_format,
        invert_mask,
        destination_dir=None,
    ):
        """Traite un fichier et retourne le chemin de sortie créé."""
        output_format = output_format.lower()
        if output_format not in cls.FORMATS_SUPPORTES:
            raise ValueError(f"Format de sortie non supporté : {output_format}")

        output_dir = destination_dir or os.path.dirname(source_path)
        os.makedirs(output_dir, exist_ok=True)
        output_name = (
            f"{os.path.splitext(os.path.basename(source_path))[0]}."
            f"{output_format}"
        )
        output_path = os.path.join(output_dir, output_name)

        # Étape A : inférence IA avec la session active.
        with cls._infer_image(source_path, session) as detached_image:
            # Étape B : préparation RGBA et inversion éventuelle du masque.
            with detached_image.convert("RGBA") as export_image:
                if invert_mask:
                    cls._invert_alpha(export_image)

                # Étape C : formatage spécifique puis export.
                cls._export_image(export_image, output_path, output_format)

        return output_path

    @staticmethod
    def _infer_image(source_path, session):
        """Normalise l'entrée, exécute rembg et retourne une image indépendante."""
        from rembg import remove

        with Image.open(source_path) as source_image:
            with source_image.convert("RGBA") as source_rgba:
                with remove(source_rgba, session=session) as detached_image:
                    return detached_image.copy()

    @staticmethod
    def _invert_alpha(image):
        """Inverse uniquement le canal Alpha de l'image déjà détourée."""
        with image.getchannel("A") as alpha:
            with ImageChops.invert(alpha) as inverted_alpha:
                image.putalpha(inverted_alpha)

    @classmethod
    def _export_image(cls, image, output_path, output_format):
        if output_format == "ico":
            cls._export_ico(image, output_path)
        else:
            image.save(output_path, format=output_format.upper())

    @classmethod
    def _export_ico(cls, image, output_path):
        side = max(image.size)
        with Image.new("RGBA", (side, side), (0, 0, 0, 0)) as square_image:
            square_image.paste(
                image,
                (
                    (side - image.width) // 2,
                    (side - image.height) // 2,
                ),
            )
            square_image.save(output_path, format="ICO", sizes=cls.ICON_SIZES)