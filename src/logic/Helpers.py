def join_url_parts(*args: str) -> str:
    return '/'.join(part.strip('/') for part in args)


def round_to_decimals(value, decimals) -> str:
    return '{:.{}f}'.format(value, decimals)


def determine_color_for_temperature(temperature: float) -> str:
    if temperature < 0:
        return 'rgba(70, 138, 221, 1)'  # blue
    elif temperature < 20:
        return 'rgba(117, 190, 84, 1)'  # green
    elif temperature < 25:
        return 'rgba(254, 151, 0, 1)'  # orange
    else:
        return 'rgba(230, 76, 60, 1)'  # red


def determine_color_for_wind(windSpeed: float) -> str:
    if windSpeed < 20:
        return 'rgba(255, 255, 255, 1)'  # white
    elif windSpeed < 60:
        return 'rgba(254, 151, 0, 1)'  # orange
    else:
        return 'rgba(230, 76, 60, 1)'  # red


def determine_color_for_weather_icon(iconId: int):
    if 200 <= iconId < 300:  # thunderstorm
        return 'rgba(230, 76, 60, 1)'  # red
    elif 300 <= iconId < 400:  # drizzle
        return 'rgba(70, 138, 221, 1)'  # blue
    elif 500 <= iconId < 600:  # rain
        return 'rgba(70, 138, 221, 1)'  # blue
    elif 600 <= iconId < 700:  # snow
        return 'rgba(255, 255, 255, 1)'  # white
    elif 700 <= iconId < 800:  # fog
        return 'rgba(255, 255, 255, 1)'  # white
    elif 800 <= iconId < 802:  # clear of partly cloudy (up to 25%)
        return 'rgba(254, 151, 0, 1)'  # orange
    elif 802 <= iconId < 805:  # clouds > 25%
        return 'rgba(255, 255, 255, 1)'  # white
