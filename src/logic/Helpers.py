def join_url_parts(*args: str) -> str:
    return '/'.join(part.strip('/') for part in args)


def round_to_decimals(value, decimals) -> str:
    return '{:.{}f}'.format(value, decimals)


def determine_color_for_temperature(temperature: float):
    if temperature < 0:
        return 'rgba(70, 138, 221, 1)'  # blue
    elif temperature < 20:
        return 'rgba(117, 190, 84, 1)'  # green
    elif temperature < 25:
        return 'rgba(254, 151, 0, 1)'  # orange
    else:
        return 'rgba(230, 76, 60, 1)'  # red


def determine_color_for_wind(windSpeed: float):
    if windSpeed < 20:
        return 'rgba(255, 255, 255, 1)'  # white
    elif windSpeed < 60:
        return 'rgba(254, 151, 0, 1)'  # orange
    else:
        return 'rgba(230, 76, 60, 1)'  # red
