import re
from datetime import datetime


def clean_number(value):
    if value == "N/A" or value is None:
        return None

    cleaned = re.sub(r"[^\d.]", "", str(value))

    if cleaned == "":
        return None

    return int(float(cleaned))


def extract_price(text):
    match = re.search(r"\$[\d,]+", text)
    return clean_number(match.group(0)) if match else None


def extract_bedrooms(text):
    match = re.search(r"(\d+)\s+bd", text)
    return clean_number(match.group(1)) if match else None


def extract_bathrooms(text):
    match = re.search(r"(\d+)\s+ba", text)
    return clean_number(match.group(1)) if match else None


def extract_square_feet(text):
    match = re.search(r"(\d+)\s+sf", text)
    return clean_number(match.group(1)) if match else None


def extract_lot_size(text):
    match = re.search(r"(\d+\s+x\s+\d+\s+ft)", text)
    return match.group(1) if match else "N/A"


def extract_property_type(text):
    property_types = ["Apt/Condo", "Townhouse", "Duplex", "House"]

    for property_type in property_types:
        if property_type.lower() in text.lower():
            return property_type

    return "N/A"


def extract_address(text):
    text = re.sub(r"^\[\]\s*", "", text)
    text = re.sub(r"^\[.*?\]\s*", "", text)
    text = re.sub(r"^(Featured|V Tour|Virtual Tour|Open \w+|Open|Follow)\s+", "", text)
    text = text.replace("Follow Follow", "").strip()

    match = re.search(r"\$[\d,]+(?:/month)?\s+(.*?)\s+\d+\s+bd", text)

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
        "Fraser East",
        "Renfrew Heights",
        "Renfrew",
        "Shaughnessy",
        "Point Grey",
        "South Vancouver",
        "University (Ubc)",
        "Kerrisdale",
        "Killarney",
        "South Marine",
        "Fraserview East",
        "Quilchena",
        "Hastings Sunrise",
        "Oakridge",
        "Strathcona",
        "Victoria East",
        "Dunbar",
        "South Granville",
        "Southlands",
    ]

    formatted = address

    for neighbourhood in neighbourhoods:
        if neighbourhood in formatted:
            formatted = formatted.replace(
                f" {neighbourhood} Vancouver",
                f", {neighbourhood}, Vancouver, BC"
            )
            return formatted

    formatted = formatted.replace(" Vancouver", ", Vancouver, BC")
    return formatted


def split_address(address):
    if address == "N/A":
        return {
            "street_address": "N/A",
            "neighbourhood": "N/A",
            "city": "N/A",
            "province": "N/A",
        }

    parts = [part.strip() for part in address.split(",")]

    return {
        "street_address": parts[0] if len(parts) > 0 else "N/A",
        "neighbourhood": parts[1] if len(parts) > 1 else "N/A",
        "city": parts[2] if len(parts) > 2 else "N/A",
        "province": parts[3] if len(parts) > 3 else "N/A",
    }


def extract_agent_name(text):
    match = re.search(
        r"(House|Townhouse|Apt/Condo|Duplex)\s+(.*?)\s+(RE/MAX|Oakwyn|Macdonald|Dexter|Engel|Royal|Stilhavn|FaithWilson|Sutton|Nu Stream|Dracco|VIRANI|One Percent|Coldwell)",
        text,
        re.IGNORECASE,
    )

    return match.group(2).strip() if match else "N/A"


def extract_brokerage(text):
    brokerages = [
        "RE/MAX Real Estate Services",
        "RE/MAX Select Realty",
        "RE/MAX Crest Realty",
        "RE/MAX City Realty",
        "Oakwyn Realty Ltd.",
        "Oakwyn Realty Northwest",
        "Macdonald Realty",
        "Dexter Realty",
        "Engel & Völkers Vancouver",
        "Royal LePage Sussex",
        "Stilhavn Real Estate Services",
        "FaithWilson Christies International Real Estate",
        "Sutton Group-Alliance R.E.S.",
        "Nu Stream Realty Inc.",
        "Dracco Pacific Realty",
        "VIRANI REAL ESTATE ADVISORS",
        "One Percent Realty Ltd.",
        "Coldwell Banker Universe Realty",
    ]

    for brokerage in brokerages:
        if brokerage.lower() in text.lower():
            return brokerage

    return "N/A"


def parse_rew_listing(title, listing_url):
    formatted_address = format_address(extract_address(title))
    address_parts = split_address(formatted_address)

    return {
        "title": title,
        "price": extract_price(title),
        "address": formatted_address,
        "street_address": address_parts["street_address"],
        "neighbourhood": address_parts["neighbourhood"],
        "city": address_parts["city"],
        "province": address_parts["province"],
        "bedrooms": extract_bedrooms(title),
        "bathrooms": extract_bathrooms(title),
        "square_feet": extract_square_feet(title),
        "lot_size": extract_lot_size(title),
        "property_type": extract_property_type(title),
        "features": "N/A",
        "facilities": "N/A",
        "agent_name": extract_agent_name(title),
        "brokerage": extract_brokerage(title),
        "listing_url": listing_url,
        "source_website": "REW.ca",
        "first_seen": datetime.now().strftime("%Y-%m-%d"),
        "last_seen": datetime.now().strftime("%Y-%m-%d"),
        "status": "active",
    }

def extract_property_manager(text):
    match = re.search(r"Property Manager\s*(.*)$", text)

    if not match:
        return "N/A"

    manager = match.group(1).strip()

    return manager if manager else "N/A"


def parse_rew_rental_listing(title, listing_url):
    formatted_address = format_address(extract_address(title))
    address_parts = split_address(formatted_address)

    return {
        "title": title,
        "price": extract_price(title),
        "monthly_rent": extract_price(title),
        "address": formatted_address,
        "street_address": address_parts["street_address"],
        "neighbourhood": address_parts["neighbourhood"],
        "city": address_parts["city"],
        "province": address_parts["province"],
        "bedrooms": extract_bedrooms(title),
        "bathrooms": extract_bathrooms(title),
        "square_feet": extract_square_feet(title),
        "lot_size": "N/A",
        "property_type": extract_property_type(title),
        "features": "N/A",
        "facilities": "N/A",
        "agent_name": "N/A",
        "brokerage": "N/A",
        "property_manager": extract_property_manager(title),
        "listing_url": listing_url,
        "source_website": "REW.ca",
        "listing_type": "rental",
        "first_seen": datetime.now().strftime("%Y-%m-%d"),
        "last_seen": datetime.now().strftime("%Y-%m-%d"),
        "status": "active",
    }