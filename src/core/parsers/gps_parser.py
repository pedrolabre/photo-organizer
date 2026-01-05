"""
GPS Parser Module.

Responsável por extrair e parsear coordenadas GPS de metadados EXIF.
"""

from typing import Dict, Any, Optional
import piexif


class GPSParser:
    """Parser para dados GPS de imagens."""

    @staticmethod
    def _parse_gps(gps_ifd: dict) -> Dict[str, Any]:
        """Parse GPS IFD (informações de localização)."""
        metadata = {}

        try:
            # Latitude
            if piexif.GPSIFD.GPSLatitude in gps_ifd and piexif.GPSIFD.GPSLatitudeRef in gps_ifd:
                lat = gps_ifd[piexif.GPSIFD.GPSLatitude]
                lat_ref = gps_ifd[piexif.GPSIFD.GPSLatitudeRef].decode('utf-8', errors='ignore')
                latitude = GPSParser._convert_gps_coordinate(lat)
                if lat_ref == 'S':
                    latitude = -latitude
                metadata["latitude"] = latitude

            # Longitude
            if piexif.GPSIFD.GPSLongitude in gps_ifd and piexif.GPSIFD.GPSLongitudeRef in gps_ifd:
                lon = gps_ifd[piexif.GPSIFD.GPSLongitude]
                lon_ref = gps_ifd[piexif.GPSIFD.GPSLongitudeRef].decode('utf-8', errors='ignore')
                longitude = GPSParser._convert_gps_coordinate(lon)
                if lon_ref == 'W':
                    longitude = -longitude
                metadata["longitude"] = longitude

            # Altitude
            if piexif.GPSIFD.GPSAltitude in gps_ifd:
                alt = gps_ifd[piexif.GPSIFD.GPSAltitude]
                altitude = alt[0] / alt[1] if isinstance(alt, tuple) else alt
                metadata["altitude"] = altitude

            # Precisão
            if piexif.GPSIFD.GPSDOP in gps_ifd:
                dop = gps_ifd[piexif.GPSIFD.GPSDOP]
                metadata["gps_dop"] = dop[0] / dop[1] if isinstance(dop, tuple) else dop

            # Satélites
            if piexif.GPSIFD.GPSSatellites in gps_ifd:
                satellites = gps_ifd[piexif.GPSIFD.GPSSatellites].decode('utf-8', errors='ignore').strip('\x00')
                metadata["gps_satellites"] = satellites

        except Exception:
            pass

        return metadata

    @staticmethod
    def _convert_gps_coordinate(coord: tuple) -> float:
        """
        Converte coordenada GPS de formato EXIF para graus decimais.

        Args:
            coord: Tupla (graus, minutos, segundos) onde cada elemento é (numerador, denominador)

        Returns:
            Coordenada em graus decimais
        """
        if not coord or len(coord) != 3:
            return 0.0

        degrees = coord[0][0] / coord[0][1] if isinstance(coord[0], tuple) else coord[0]
        minutes = coord[1][0] / coord[1][1] if isinstance(coord[1], tuple) else coord[1]
        seconds = coord[2][0] / coord[2][1] if isinstance(coord[2], tuple) else coord[2]

        return degrees + (minutes / 60.0) + (seconds / 3600.0)