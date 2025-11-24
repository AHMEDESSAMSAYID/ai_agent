CITY_MAP = {
    "جدة": "Jeddah",
    "جده": "Jeddah",
    "الرياض": "Riyadh",
    "رياض": "Riyadh",
    "دمام": "Dammam",
    "الدمام": "Dammam",
    "مكة": "Mecca",
    "مكه": "Mecca",
}

def normalize_city(city: str | None) -> str | None:
    if not city:
        return None
    city = city.strip()
    # لو المدينة بالعربي
    if city in CITY_MAP:
        return CITY_MAP[city]
    # لو المدينة بالإنجليزي
    return city.capitalize()
