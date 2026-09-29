import math
from datetime import datetime

from astral import Observer
from astral.sun import azimuth, elevation


def angular_difference(a, b):
    """
    Menghitung selisih sudut terkecil antara dua azimuth.
    """
    difference = abs(a - b)

    if difference > 180:
        difference = 360 - difference

    return difference


def calculate_sun_position(
    latitude,
    longitude,
    date,
    time,
    timezone_offset,
):
    """
    Menghitung posisi Matahari pada koordinat tertentu.
    """

    observer = Observer(
        latitude=latitude,
        longitude=longitude,
    )

    dt = datetime.strptime(
        f"{date} {time}",
        "%Y-%m-%d %H:%M:%S",
    )

    # Astral bekerja dengan waktu UTC.
    utc_dt = dt - __import__("datetime").timedelta(
        hours=timezone_offset
    )

    sun_elevation = elevation(
        observer,
        utc_dt,
    )

    sun_azimuth = azimuth(
        observer,
        utc_dt,
    )

    return sun_elevation, sun_azimuth


def find_candidates(
    date,
    time,
    timezone_offset,
    target_elevation,
    target_azimuth,
):
    """
    Mencari kandidat lokasi berdasarkan posisi Matahari.

    Untuk tahap awal, seluruh dunia dipindai dengan grid
    latitude/longitude.
    """

    candidates = []

    # Resolusi awal.
    # 1° latitude × 1° longitude.
    latitude_step = 1.0
    longitude_step = 1.0

    latitude = -90.0

    while latitude <= 90.0:

        longitude = -180.0

        while longitude < 180.0:

            try:
                candidate_elevation, candidate_azimuth = (
                    calculate_sun_position(
                        latitude,
                        longitude,
                        date,
                        time,
                        timezone_offset,
                    )
                )

                elevation_error = abs(
                    candidate_elevation - target_elevation
                )

                azimuth_error = angular_difference(
                    candidate_azimuth,
                    target_azimuth,
                )

                total_error = (
                    elevation_error +
                    azimuth_error
                )

                candidates.append(
                    {
                        "latitude": round(latitude, 2),
                        "longitude": round(longitude, 2),
                        "elevation": round(
                            candidate_elevation,
                            2,
                        ),
                        "azimuth": round(
                            candidate_azimuth,
                            2,
                        ),
                        "elevation_error": round(
                            elevation_error,
                            2,
                        ),
                        "azimuth_error": round(
                            azimuth_error,
                            2,
                        ),
                        "error": round(
                            total_error,
                            2,
                        ),
                    }
                )

            except Exception:
                pass

            longitude += longitude_step

        latitude += latitude_step

    candidates.sort(
        key=lambda candidate: candidate["error"]
    )

    return candidates[:10]