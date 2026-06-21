import re


def clean_number(value):
    if value in (None, "N/A"):
        return "N/A"

    cleaned = re.sub(r"[^\d.]", "", str(value))
    return cleaned if cleaned else "N/A"


def extract_price(text):
    match = re.search(r"\$[\d,]+", text)
    return clean_number(match.group(0)) if match else "N/A"


def extract_bedrooms(text):
    match = re.search(r"(\d+)\s+bd", text)
    return match.group(1) if match else "N/A"


def extract_bathrooms(text):
    match = re.search(r"(\d+)\s+ba", text)
    return match.group(1) if match else "N/A"


def extract_square_feet(text):
    match = re.search(r"(\d+)\s+sf", text)
    return match.group(1) if match else "N/A"


def extract_address(text):
    text = text.replace("Follow Follow", "").strip()
    text = re.sub(r"^(Featured|V Tour|Virtual Tour|Open \w+|Open)\s+", "", text)

    match = re.search(
        r"\$[\d,]+(?:/month)?\s+(.*?)\s+\d+\s+bd",
        text
    )

    return match.group(1).strip() if match else "N/A"


def format_address(address):
    if address == "N/A":
        return "N/A"

    neighbourhoods = [
        "Kitsilano",
        "Marpole",
        "Arbutus",
        "Yaletown",
        "Knight",
        "Cambie",
        "Downtown West",
        "Downtown East",
        "Mount Pleasant East",
        "Mount Pleasant West",
        "Grandview East",
        "Hastings",
        "Main",
        "Fairview",
        "Coal Harbour",
        "West End",
        "False Creek",
        "Collingwood",
        "Renfrew",
        "Renfrew Heights",
        "Point Grey",
        "South Granville",
        "University (Ubc)",
        "Kerrisdale",
        "Dunbar",
        "Shaughnessy",
        "Oakridge",
        "Killarney",
        "South Vancouver",
        "Fraser East",
        "Strathcona",
        "Hastings Sunrise",
    ]

    formatted = address

    for neighbourhood in neighbourhoods:
        if neighbourhood in formatted:
            formatted = formatted.replace(
                f" {neighbourhood} Vancouver",
                f", {neighbourhood}, Vancouver, BC"
            )
            return formatted

    return formatted.replace(" Vancouver", ", Vancouver, BC")


def split_address(address):
    if address == "N/A":
        return {
            "street_address": "N/A",
            "neighbourhood": "N/A",
            "city": "N/A",
            "province": "N/A",
            "postal_code": "N/A",
        }

    parts = [part.strip() for part in address.split(",")]

    return {
        "street_address": parts[0] if len(parts) > 0 else "N/A",
        "neighbourhood": parts[1] if len(parts) > 1 else "N/A",
        "city": parts[2] if len(parts) > 2 else "N/A",
        "province": parts[3] if len(parts) > 3 else "N/A",
        "postal_code": "N/A",
    }


def build_bed_bath(text):
    beds = extract_bedrooms(text)
    baths = extract_bathrooms(text)

    return f"{beds} bd / {baths} ba"


def extract_post_id(url):
    clean_url = url.rstrip("/")

    match = re.search(r"/properties/([^/?]+)", clean_url)

    if match:
        return match.group(1)

    return clean_url.split("/")[-1]


def extract_days_on_rew(text):
    match = re.search(r"Days on REW\s+(\d+\s+Days?|\d+\s+Hours?)", text)
    return match.group(1) if match else "N/A"


def extract_mls_number(text):
    match = re.search(r"MLS® Number\s+([A-Z0-9]+)", text)
    return match.group(1) if match else "N/A"


def extract_year_built(text):
    match = re.search(r"Built in\s+(\d{4})", text)
    return match.group(1) if match else "N/A"


def extract_building_age(text):
    match = re.search(r"\((\d+)\s+yrs old\)", text)
    return match.group(1) if match else "N/A"