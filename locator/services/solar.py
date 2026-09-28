import math


def calculate_solar_elevation(height, shadow_length):
    """
    Menghitung elevasi Matahari berdasarkan tinggi objek
    dan panjang bayangannya.

    height:
        tinggi tiang dalam meter

    shadow_length:
        panjang bayangan dalam meter

    return:
        sudut elevasi Matahari dalam derajat
    """

    if height <= 0:
        raise ValueError("Tinggi tiang harus lebih dari 0.")

    if shadow_length <= 0:
        raise ValueError("Panjang bayangan harus lebih dari 0.")

    elevation = math.degrees(
        math.atan(height / shadow_length)
    )

    return elevation


def shadow_azimuth_to_sun_azimuth(shadow_azimuth):
    """
    Arah Matahari berlawanan dengan arah bayangan.

    0°   = Utara
    90°  = Timur
    180° = Selatan
    270° = Barat
    """

    if not 0 <= shadow_azimuth <= 360:
        raise ValueError("Azimuth harus berada antara 0° dan 360°.")

    sun_azimuth = (shadow_azimuth + 180) % 360

    return sun_azimuth