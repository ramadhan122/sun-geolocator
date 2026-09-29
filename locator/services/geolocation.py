import math


def solar_position(
    latitude,
    longitude,
    date,
    time,
    timezone_offset,
):
    """
    Menghitung posisi Matahari untuk koordinat tertentu.
    """

    day_of_year = date.timetuple().tm_yday

    local_hour = (
        time.hour
        + time.minute / 60
        + time.second / 3600
    )

    gamma = (
        2
        * math.pi
        / 365
        * (
            day_of_year - 1
            + (local_hour - 12) / 24
        )
    )

    equation_of_time = 229.18 * (
        0.000075
        + 0.001868 * math.cos(gamma)
        - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2 * gamma)
        - 0.040849 * math.sin(2 * gamma)
    )

    declination = (
        0.006918
        - 0.399912 * math.cos(gamma)
        + 0.070257 * math.sin(gamma)
        - 0.006758 * math.cos(2 * gamma)
        + 0.000907 * math.sin(2 * gamma)
        - 0.002697 * math.cos(3 * gamma)
        + 0.001480 * math.sin(3 * gamma)
    )

    time_offset = (
        equation_of_time
        + 4 * longitude
        - 60 * timezone_offset
    )

    true_solar_time = (
        local_hour * 60
        + time_offset
    )

    hour_angle = (
        true_solar_time / 4
    ) - 180

    latitude_rad = math.radians(latitude)
    hour_angle_rad = math.radians(hour_angle)

    cosine_zenith = (
        math.sin(latitude_rad)
        * math.sin(declination)
        +
        math.cos(latitude_rad)
        * math.cos(declination)
        * math.cos(hour_angle_rad)
    )

    cosine_zenith = max(
        -1,
        min(1, cosine_zenith)
    )

    zenith = math.acos(cosine_zenith)

    elevation = 90 - math.degrees(zenith)

    azimuth = math.degrees(
        math.atan2(
            math.sin(hour_angle_rad),
            (
                math.cos(hour_angle_rad)
                * math.sin(latitude_rad)
                -
                math.tan(declination)
                * math.cos(latitude_rad)
            ),
        )
    )

    azimuth = (azimuth + 180) % 360

    return {
        "elevation": elevation,
        "azimuth": azimuth,
    }


def angular_difference(a, b):
    """
    Menghitung selisih sudut terkecil.
    """

    difference = abs(a - b)

    return min(
        difference,
        360 - difference,
    )


def calculate_error(
    position,
    target_elevation,
    target_azimuth,
):
    """
    Menghitung error posisi Matahari.
    """

    elevation_error = abs(
        position["elevation"]
        - target_elevation
    )

    azimuth_error = angular_difference(
        position["azimuth"],
        target_azimuth,
    )

    # Gabungkan kedua error.
    total_error = math.sqrt(
        elevation_error ** 2
        + azimuth_error ** 2
    )

    return {
        "elevation_error": elevation_error,
        "azimuth_error": azimuth_error,
        "error": total_error,
    }


def evaluate_point(
    latitude,
    longitude,
    date,
    time,
    timezone_offset,
    target_elevation,
    target_azimuth,
):
    """
    Mengevaluasi satu koordinat.
    """

    position = solar_position(
        latitude=latitude,
        longitude=longitude,
        date=date,
        time=time,
        timezone_offset=timezone_offset,
    )

    # Matahari di bawah horizon
    if position["elevation"] <= 0:
        return None

    error = calculate_error(
        position,
        target_elevation,
        target_azimuth,
    )

    return {
        "latitude": latitude,
        "longitude": longitude,
        "elevation": position["elevation"],
        "azimuth": position["azimuth"],
        "elevation_error": error["elevation_error"],
        "azimuth_error": error["azimuth_error"],
        "error": error["error"],
    }


def global_search(
    date,
    time,
    timezone_offset,
    target_elevation,
    target_azimuth,
    step=2,
):
    """
    Pencarian seluruh dunia dengan grid kasar.
    """

    candidates = []

    latitude = -90

    while latitude <= 90:

        longitude = -180

        while longitude <= 180:

            candidate = evaluate_point(
                latitude=latitude,
                longitude=longitude,
                date=date,
                time=time,
                timezone_offset=timezone_offset,
                target_elevation=target_elevation,
                target_azimuth=target_azimuth,
            )

            if candidate:
                candidates.append(candidate)

            longitude += step

        latitude += step

    candidates.sort(
        key=lambda item: item["error"]
    )

    return candidates[:20]


def refinement_search(
    rough_candidates,
    date,
    time,
    timezone_offset,
    target_elevation,
    target_azimuth,
    radius=2,
    step=0.1,
):
    """
    Memperhalus kandidat hasil global search.

    Contoh:
        kandidat kasar:
            -6, 108

        radius:
            2°

        step:
            0.1°

        Maka akan diperiksa area:
            -8 sampai -4
            106 sampai 110
    """

    refined = []

    checked = set()

    for rough in rough_candidates:

        min_lat = rough["latitude"] - radius
        max_lat = rough["latitude"] + radius

        min_lon = rough["longitude"] - radius
        max_lon = rough["longitude"] + radius

        latitude = min_lat

        while latitude <= max_lat:

            longitude = min_lon

            while longitude <= max_lon:

                # Hindari koordinat duplikat
                key = (
                    round(latitude, 4),
                    round(longitude, 4),
                )

                if key not in checked:

                    checked.add(key)

                    candidate = evaluate_point(
                        latitude=latitude,
                        longitude=longitude,
                        date=date,
                        time=time,
                        timezone_offset=timezone_offset,
                        target_elevation=target_elevation,
                        target_azimuth=target_azimuth,
                    )

                    if candidate:
                        refined.append(candidate)

                longitude += step

            latitude += step

    refined.sort(
        key=lambda item: item["error"]
    )

    return refined[:20]


def find_candidates(
    date,
    time,
    timezone_offset,
    target_elevation,
    target_azimuth,
):
    """
    Pipeline pencarian:

    1. Global search 2°
    2. Refinement 0.1°
    """

    rough_candidates = global_search(
        date=date,
        time=time,
        timezone_offset=timezone_offset,
        target_elevation=target_elevation,
        target_azimuth=target_azimuth,
        step=2,
    )

    refined_candidates = refinement_search(
        rough_candidates=rough_candidates,
        date=date,
        time=time,
        timezone_offset=timezone_offset,
        target_elevation=target_elevation,
        target_azimuth=target_azimuth,
        radius=2,
        step=0.1,
    )

    # Rapikan angka untuk template
    for candidate in refined_candidates:

        candidate["latitude"] = round(
            candidate["latitude"],
            4,
        )

        candidate["longitude"] = round(
            candidate["longitude"],
            4,
        )

        candidate["elevation"] = round(
            candidate["elevation"],
            2,
        )

        candidate["azimuth"] = round(
            candidate["azimuth"],
            2,
        )

        candidate["elevation_error"] = round(
            candidate["elevation_error"],
            2,
        )

        candidate["azimuth_error"] = round(
            candidate["azimuth_error"],
            2,
        )

        candidate["error"] = round(
            candidate["error"],
            2,
        )

    return refined_candidates