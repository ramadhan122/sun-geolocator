from django.shortcuts import render

from .services.solar import (
    calculate_solar_elevation,
    shadow_azimuth_to_sun_azimuth,
)


def index(request):
    context = {}

    if request.method == "POST":

        try:
            height = float(request.POST.get("height"))
            shadow_length = float(request.POST.get("shadow_length"))
            shadow_azimuth = float(request.POST.get("shadow_azimuth"))

            elevation = calculate_solar_elevation(
                height,
                shadow_length,
            )

            sun_azimuth = shadow_azimuth_to_sun_azimuth(
                shadow_azimuth
            )

            context["result"] = {
                "elevation": round(elevation, 2),
                "sun_azimuth": round(sun_azimuth, 2),
            }

        except (ValueError, TypeError) as error:
            context["error"] = str(error)

    return render(
        request,
        "locator/index.html",
        context,
    )