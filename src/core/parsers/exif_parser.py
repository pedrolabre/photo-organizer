"""
EXIF Parser Module.

Responsável por extrair e parsear dados EXIF de imagens.
"""

from pathlib import Path
from typing import Dict, Any
import piexif
from PIL import Image

from .gps_parser import GPSParser


class EXIFParser:
    """Parser para dados EXIF de imagens."""

    @staticmethod
    def read_exif_data(file_path: Path) -> Dict[str, Any]:
        """
        Lê dados EXIF do arquivo.

        Args:
            file_path: Caminho do arquivo de imagem

        Returns:
            Dicionário com dados EXIF parseados
        """
        try:
            exif_dict = piexif.load(str(file_path))
            metadata = {}

            # Parse IFD0 (informações básicas)
            if "0th" in exif_dict:
                metadata.update(EXIFParser._parse_ifd0(exif_dict["0th"]))

            # Parse EXIF IFD
            if "Exif" in exif_dict:
                metadata.update(EXIFParser._parse_exif_ifd(exif_dict["Exif"]))

            # Parse GPS IFD
            if "GPS" in exif_dict:
                metadata.update(GPSParser._parse_gps(exif_dict["GPS"]))

            return metadata
        except Exception:
            return {}

    @staticmethod
    def _parse_ifd0(ifd0: dict) -> Dict[str, Any]:
        """Parse IFD0 (informações básicas da imagem)."""
        metadata = {}

        # Fabricante e modelo da câmera
        if piexif.ImageIFD.Make in ifd0:
            metadata["camera_make"] = ifd0[piexif.ImageIFD.Make].decode('utf-8', errors='ignore').strip('\x00')

        if piexif.ImageIFD.Model in ifd0:
            metadata["camera_model"] = ifd0[piexif.ImageIFD.Model].decode('utf-8', errors='ignore').strip('\x00')

        # Orientação
        if piexif.ImageIFD.Orientation in ifd0:
            metadata["orientation"] = ifd0[piexif.ImageIFD.Orientation]

        # Resolução
        if piexif.ImageIFD.XResolution in ifd0:
            metadata["x_resolution"] = ifd0[piexif.ImageIFD.XResolution]

        if piexif.ImageIFD.YResolution in ifd0:
            metadata["y_resolution"] = ifd0[piexif.ImageIFD.YResolution]

        return metadata

    @staticmethod
    def _parse_exif_ifd(exif_ifd: dict) -> Dict[str, Any]:
        """Parse EXIF IFD (informações técnicas da câmera)."""
        metadata = {}

        # Data/hora original
        if piexif.ExifIFD.DateTimeOriginal in exif_ifd:
            dt_str = exif_ifd[piexif.ExifIFD.DateTimeOriginal].decode('utf-8', errors='ignore').strip('\x00')
            metadata["datetime_original"] = dt_str

        # Data/hora digitalizada
        if piexif.ExifIFD.DateTimeDigitized in exif_ifd:
            dt_str = exif_ifd[piexif.ExifIFD.DateTimeDigitized].decode('utf-8', errors='ignore').strip('\x00')
            metadata["datetime_digitized"] = dt_str

        # Configurações da câmera
        if piexif.ExifIFD.FNumber in exif_ifd:
            metadata["f_number"] = exif_ifd[piexif.ExifIFD.FNumber]

        if piexif.ExifIFD.ExposureTime in exif_ifd:
            metadata["exposure_time"] = exif_ifd[piexif.ExifIFD.ExposureTime]

        if piexif.ExifIFD.ISOSpeedRatings in exif_ifd:
            metadata["iso"] = exif_ifd[piexif.ExifIFD.ISOSpeedRatings]

        if piexif.ExifIFD.FocalLength in exif_ifd:
            metadata["focal_length"] = exif_ifd[piexif.ExifIFD.FocalLength]

        # Flash
        if piexif.ExifIFD.Flash in exif_ifd:
            metadata["flash"] = exif_ifd[piexif.ExifIFD.Flash]

        return metadata