from django.shortcuts import render

from .services.solar import (
    calculate_solar_elevation,
    shadow_azimuth_to_sun_azimuth,
)

from .services.locator import (
    find_candidates,
)


def index(request):
    context = {}

    if request.method == "POST":

        try:
            height = float(
                request.POST.get("height")
            )

            shadow_length = float(
                request.POST.get("shadow_length")
            )

            shadow_azimuth = float(
                request.POST.get("shadow_azimuth")
            )

            date = request.POST.get("date")
            time = request.POST.get("time")

            timezone_offset = int(
                request.POST.get("timezone")
            )

            elevation = calculate_solar_elevation(
                height,
                shadow_length,
            )

            sun_azimuth = shadow_azimuth_to_sun_azimuth(
                shadow_azimuth
            )

            candidates = find_candidates(
                date=date,
                time=time,
                timezone_offset=timezone_offset,
                target_elevation=elevation,
                target_azimuth=sun_azimuth,
            )

            print(
                "JUMLAH KANDIDAT:",
                len(candidates),
            )

            print(
                "KANDIDAT:",
                candidates[:3],
            )

            context["result"] = {
                "elevation": round(
                    elevation,
                    2,
                ),
                "sun_azimuth": round(
                    sun_azimuth,
                    2,
                ),
                "candidates": candidates,
            }

        except (
            ValueError,
            TypeError,
            KeyError,
        ) as error:

            context["error"] = str(error)

    return render(
        request,
        "locator/index.html",
        context,
    )