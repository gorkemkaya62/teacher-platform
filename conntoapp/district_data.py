import json
from functools import lru_cache
from pathlib import Path


@lru_cache
def _load_districts():
    path = Path(__file__).resolve().parent / "data" / "turkey_districts.json"
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def get_district_choices(city_slug):
    if not city_slug:
        return [("", "Seçiniz")]
    districts = _load_districts().get(city_slug, [])
    return [("", "Seçiniz")] + districts


def get_district_label(city_slug, district_slug):
    if not city_slug or not district_slug:
        return district_slug or ""
    for slug, label in _load_districts().get(city_slug, []):
        if slug == district_slug:
            return label
    return district_slug


def is_valid_district(city_slug, district_slug):
    if not city_slug or not district_slug:
        return False
    return any(slug == district_slug for slug, _ in _load_districts().get(city_slug, []))
