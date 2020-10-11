def join_url_parts(*args: str) -> str:
    return '/'.join(part.strip('/') for part in args)


def round_to_decimals(value, decimals) -> str:
    return '{:.{}f}'.format(value, decimals)


def determine_weather_cache_key(lat: float, lon: float):
    return f'weather_{lat}_{lon}'
