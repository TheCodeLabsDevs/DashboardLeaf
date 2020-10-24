from logic import Constants


def join_url_parts(*args: str) -> str:
    return '/'.join(part.strip('/') for part in args)


def round_to_decimals(value, decimals) -> str:
    return '{:.{}f}'.format(value, decimals)


def determine_color_for_temperature(temperature: float) -> str:
    if temperature < 0:
        return Constants.BLUE.to_rgba()
    elif temperature < 20:
        return Constants.GREEN.to_rgba()
    elif temperature < 25:
        return Constants.ORANGE.to_rgba()
    else:
        return Constants.RED.to_rgba()


def determine_color_for_wind(windSpeed: float) -> str:
    if windSpeed < 20:
        return Constants.WHITE.to_rgba()
    elif windSpeed < 60:
        return Constants.ORANGE.to_rgba()
    else:
        return Constants.RED.to_rgba()


def determine_color_for_weather_icon(iconId: int):
    if 200 <= iconId < 300:  # thunderstorm
        return Constants.RED.to_rgba()
    elif 300 <= iconId < 400:  # drizzle
        return Constants.BLUE.to_rgba()
    elif 500 <= iconId < 600:  # rain
        return Constants.BLUE.to_rgba()
    elif 600 <= iconId < 700:  # snow
        return Constants.WHITE.to_rgba()
    elif 700 <= iconId < 800:  # fog
        return Constants.WHITE.to_rgba()
    elif 800 <= iconId < 802:  # clear of partly cloudy (up to 25%)
        return Constants.ORANGE.to_rgba()
    elif 802 <= iconId < 805:  # clouds > 25%
        return Constants.WHITE.to_rgba()
