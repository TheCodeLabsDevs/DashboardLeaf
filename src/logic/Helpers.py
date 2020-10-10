def join_url_parts(*args: str) -> str:
    return '/'.join(part.strip('/') for part in args)
