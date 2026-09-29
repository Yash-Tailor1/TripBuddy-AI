import os
import re

import airportsdata
import pycountry
import requests
from dotenv import load_dotenv


# ============================================================
# Environment
# ============================================================

load_dotenv()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

# Default origin when user only provides a destination.
DEFAULT_ORIGIN_IATA = os.getenv("DEFAULT_ORIGIN_IATA", "BOM")

# Aviationstack API endpoint
BASE_URL = "https://api.aviationstack.com/v1/flights"

# Airport database
AIRPORTS = airportsdata.load("IATA")


# ============================================================
# Country aliases
# ============================================================

COUNTRY_ALIASES = {
    "india": "IN",
    "bharat": "IN",
    "ind": "IN",

    "usa": "US",
    "us": "US",
    "united states": "US",
    "united states of america": "US",
    "america": "US",

    "uk": "GB",
    "u.k.": "GB",
    "united kingdom": "GB",
    "great britain": "GB",
    "britain": "GB",
    "england": "GB",

    "uae": "AE",
    "u.a.e.": "AE",
    "united arab emirates": "AE",

    "australia": "AU",
    "aus": "AU",

    "canada": "CA",
    "can": "CA",

    "singapore": "SG",
    "sg": "SG",

    "thailand": "TH",
    "thai": "TH",

    "indonesia": "ID",
    "indo": "ID",

    "malaysia": "MY",
    "malay": "MY",

    "japan": "JP",
    "jpn": "JP",

    "south korea": "KR",
    "korea": "KR",
    "republic of korea": "KR",

    "china": "CN",
    "prc": "CN",
    "people's republic of china": "CN",

    "france": "FR",
    "fra": "FR",

    "germany": "DE",
    "deutschland": "DE",
    "ger": "DE",

    "italy": "IT",
    "ita": "IT",

    "spain": "ES",
    "esp": "ES",

    "switzerland": "CH",
    "swiss": "CH",

    "netherlands": "NL",
    "holland": "NL",

    "new zealand": "NZ",
    "nz": "NZ",

    "turkey": "TR",
    "türkiye": "TR",
    "turkiye": "TR",

    "egypt": "EG",
    "egy": "EG",

    "south africa": "ZA",
    "rsa": "ZA",

    "brazil": "BR",
    "bra": "BR",

    "mexico": "MX",
    "mex": "MX",

    "portugal": "PT",
    "prt": "PT",

    "greece": "GR",
    "hellas": "GR",

    "austria": "AT",
    "belgium": "BE",
    "ireland": "IE",
    "norway": "NO",
    "sweden": "SE",
    "denmark": "DK",
    "finland": "FI",
    "iceland": "IS",

    "russia": "RU",
    "russian federation": "RU",

    "vietnam": "VN",
    "viet nam": "VN",

    "philippines": "PH",
    "nepal": "NP",

    "sri lanka": "LK",
    "ceylon": "LK",

    "bangladesh": "BD",
    "pakistan": "PK",
    "bhutan": "BT",
    "maldives": "MV",

    "saudi arabia": "SA",
    "ksa": "SA",

    "qatar": "QA",
    "oman": "OM",
    "bahrain": "BH",
    "kuwait": "KW",

    "israel": "IL",
    "jordan": "JO",
    "morocco": "MA",
    "kenya": "KE",
    "tanzania": "TZ",
    "mauritius": "MU",
    "seychelles": "SC",
}


# ============================================================
# Default airport for each country
# ============================================================

COUNTRY_MAIN_AIRPORT = {
    "IN": "DEL",
    "US": "ATL",
    "GB": "LHR",
    "AE": "DXB",
    "SG": "SIN",
    "TH": "BKK",
    "ID": "CGK",
    "MY": "KUL",
    "JP": "NRT",
    "KR": "ICN",
    "CN": "PEK",
    "FR": "CDG",
    "DE": "FRA",
    "IT": "FCO",
    "ES": "MAD",
    "CH": "ZRH",
    "NL": "AMS",
    "AU": "SYD",
    "NZ": "AKL",
    "CA": "YYZ",
    "TR": "IST",
    "EG": "CAI",
    "ZA": "JNB",
    "BR": "GRU",
    "MX": "MEX",
    "GR": "ATH",
    "PT": "LIS",
    "AT": "VIE",
    "BE": "BRU",
    "IE": "DUB",
    "NO": "OSL",
    "SE": "ARN",
    "DK": "CPH",
    "FI": "HEL",
    "IS": "KEF",
    "RU": "SVO",
    "VN": "SGN",
    "PH": "MNL",
    "NP": "KTM",
    "LK": "CMB",
    "BD": "DAC",
    "PK": "LHE",
    "BT": "PBH",
    "MV": "MLE",
    "SA": "RUH",
    "QA": "DOH",
    "OM": "MCT",
    "BH": "BAH",
    "KW": "KWI",
    "IL": "TLV",
    "JO": "AMM",
    "MA": "CMN",
    "KE": "NBO",
    "TZ": "JRO",
    "MU": "MRU",
    "SC": "SEZ",
}


# ============================================================
# City -> Airport
# ============================================================

CITY_MAIN_AIRPORT = {
    # India
    "mumbai": "BOM",
    "delhi": "DEL",
    "new delhi": "DEL",
    "bangalore": "BLR",
    "bengaluru": "BLR",
    "hyderabad": "HYD",
    "chennai": "MAA",
    "kolkata": "CCU",
    "pune": "PNQ",
    "ahmedabad": "AMD",
    "goa": "GOI",
    "panaji": "GOI",
    "jaipur": "JAI",
    "lucknow": "LKO",
    "kochi": "COK",
    "cochin": "COK",
    "chandigarh": "IXC",
    "indore": "IDR",
    "varanasi": "VNS",
    "amritsar": "ATQ",
    "bhubaneswar": "BBI",
    "patna": "PAT",
    "srinagar": "SXR",
    "surat": "STV",
    "nagpur": "NAG",

    # UAE
    "dubai": "DXB",
    "abu dhabi": "AUH",
    "sharjah": "SHJ",

    # UK
    "london": "LHR",
    "manchester": "MAN",
    "edinburgh": "EDI",

    # USA
    "new york": "JFK",
    "los angeles": "LAX",
    "san francisco": "SFO",
    "chicago": "ORD",
    "miami": "MIA",
    "las vegas": "LAS",
    "seattle": "SEA",
    "boston": "BOS",
    "washington": "IAD",
    "orlando": "MCO",

    # Canada
    "toronto": "YYZ",
    "vancouver": "YVR",
    "montreal": "YUL",

    # Singapore
    "singapore": "SIN",

    # Thailand
    "bangkok": "BKK",
    "phuket": "HKT",
    "chiang mai": "CNX",

    # Indonesia
    "bali": "DPS",
    "denpasar": "DPS",
    "jakarta": "CGK",

    # Malaysia
    "kuala lumpur": "KUL",
    "langkawi": "LGK",
    "penang": "PEN",

    # Japan
    "tokyo": "NRT",
    "osaka": "KIX",
    "kyoto": "KIX",
    "nagoya": "NGO",

    # South Korea
    "seoul": "ICN",
    "busan": "PUS",

    # China
    "beijing": "PEK",
    "shanghai": "PVG",
    "guangzhou": "CAN",
    "shenzhen": "SZX",
    "hong kong": "HKG",

    # France
    "paris": "CDG",
    "nice": "NCE",
    "lyon": "LYS",

    # Germany
    "frankfurt": "FRA",
    "berlin": "BER",
    "munich": "MUC",

    # Italy
    "rome": "FCO",
    "milan": "MXP",
    "venice": "VCE",
    "florence": "FLR",

    # Spain
    "madrid": "MAD",
    "barcelona": "BCN",
    "seville": "SVQ",

    # Switzerland
    "zurich": "ZRH",
    "geneva": "GVA",

    # Netherlands
    "amsterdam": "AMS",

    # Australia
    "sydney": "SYD",
    "melbourne": "MEL",
    "brisbane": "BNE",
    "perth": "PER",

    # New Zealand
    "auckland": "AKL",
    "queenstown": "ZQN",

    # Turkey
    "istanbul": "IST",
    "ankara": "ESB",

    # Egypt
    "cairo": "CAI",

    # South Africa
    "johannesburg": "JNB",
    "cape town": "CPT",

    # Brazil
    "sao paulo": "GRU",
    "rio de janeiro": "GIG",

    # Mexico
    "mexico city": "MEX",
    "cancun": "CUN",

    # Greece
    "athens": "ATH",
    "santorini": "JTR",

    # Portugal
    "lisbon": "LIS",
    "porto": "OPO",

    # Ireland
    "dublin": "DUB",

    # Norway
    "oslo": "OSL",

    # Sweden
    "stockholm": "ARN",

    # Denmark
    "copenhagen": "CPH",

    # Finland
    "helsinki": "HEL",

    # Russia
    "moscow": "SVO",
    "st petersburg": "LED",

    # Vietnam
    "ho chi minh city": "SGN",
    "hanoi": "HAN",

    # Philippines
    "manila": "MNL",

    # Nepal
    "kathmandu": "KTM",

    # Sri Lanka
    "colombo": "CMB",

    # Maldives
    "male": "MLE",

    # Saudi Arabia
    "riyadh": "RUH",
    "jeddah": "JED",

    # Qatar
    "doha": "DOH",

    # Oman
    "muscat": "MCT",

    # Israel
    "tel aviv": "TLV",

    # Jordan
    "amman": "AMM",

    # Morocco
    "casablanca": "CMN",
    "marrakech": "RAK",

    # Kenya
    "nairobi": "NBO",

    # Mauritius
    "mauritius": "MRU",
    "port louis": "MRU",

    # Seychelles
    "mahe": "SEZ",
    "victoria": "SEZ",
}


# ============================================================
# Text cleaning
# ============================================================

def clean_text(text: str) -> str:
    """
    Normalize user text so it can be matched against
    city/country dictionaries.
    """

    text = text.lower().strip()

    # Keep letters, numbers and spaces
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Normalize multiple spaces
    text = re.sub(r"\s+", " ", text)

    stop_words = {
        "flight",
        "flights",
        "ticket",
        "tickets",
        "trip",
        "travel",
        "plan",
        "complete",
        "days",
        "sightseeing",
        "day",
        "including",
        "hotel",
        "hotels",
        "under",
        "budget",
        "info",
        "information",
    }

    words = [
        word
        for word in text.split()
        if word not in stop_words
    ]

    return " ".join(words).strip()


# ============================================================
# Country resolution
# ============================================================

def country_name_to_code(text: str):
    """
    Convert a country name or alias into ISO alpha-2 code.
    """

    text = clean_text(text)

    if not text:
        return None

    if text in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[text]

    try:
        country = pycountry.countries.lookup(text)
        return country.alpha_2
    except LookupError:
        pass

    # Search country names inside longer text
    for country in pycountry.countries:
        country_name = country.name.lower()

        if country_name in text:
            return country.alpha_2

    # Search aliases inside longer text
    for alias, code in COUNTRY_ALIASES.items():
        if re.search(
            rf"\b{re.escape(alias)}\b",
            text
        ):
            return code

    return None


# ============================================================
# Airport helpers
# ============================================================

def airport_country_matches(
    airport: dict,
    country_code: str
) -> bool:
    """
    Check whether an airport belongs to a country.
    """

    airport_country = str(
        airport.get("country", "")
    ).upper().strip()

    if airport_country == country_code:
        return True

    try:
        country = pycountry.countries.get(
            alpha_2=country_code
        )

        if country:
            country_name = country.name.lower()

            if airport_country.lower() == country_name:
                return True

    except Exception:
        pass

    return False


def get_best_airport_for_country(
    country_code: str
):
    """
    Return the preferred airport for a country.
    Falls back to airport database scoring if necessary.
    """

    preferred = COUNTRY_MAIN_AIRPORT.get(
        country_code
    )

    if preferred and preferred in AIRPORTS:
        return preferred

    candidates = []

    for iata, airport in AIRPORTS.items():

        if not iata:
            continue

        if airport_country_matches(
            airport,
            country_code
        ):

            name = str(
                airport.get("name", "")
            ).lower()

            city = str(
                airport.get("city", "")
            ).lower()

            score = 0

            if "international" in name:
                score += 5

            if "capital" in name:
                score += 20

            if city:
                score += 5

            candidates.append(
                (score, iata)
            )

    if not candidates:
        return None

    candidates.sort(reverse=True)

    return candidates[0][1]


# ============================================================
# Location -> IATA
# ============================================================

def resolve_location_to_iata(
    location: str
):
    """
    Convert country/city/airport/IATA into an IATA code.

    Examples:
        India       -> DEL
        Japan       -> NRT
        Mumbai      -> BOM
        Tokyo       -> NRT
        DAC         -> DAC
    """

    if not location:
        return None

    raw_location = location.strip()

    # --------------------------------------------------------
    # Direct IATA code
    # --------------------------------------------------------

    if re.fullmatch(
        r"[A-Za-z]{3}",
        raw_location
    ):

        code = raw_location.upper()

        if code in AIRPORTS:
            return code

    location_clean = clean_text(
        raw_location
    )

    if not location_clean:
        return None

    # --------------------------------------------------------
    # Exact city map match
    # --------------------------------------------------------

    if location_clean in CITY_MAIN_AIRPORT:
        return CITY_MAIN_AIRPORT[
            location_clean
        ]

    # --------------------------------------------------------
    # Country match
    # --------------------------------------------------------

    country_code = country_name_to_code(
        location_clean
    )

    if country_code:

        airport = get_best_airport_for_country(
            country_code
        )

        if airport:
            return airport

    # --------------------------------------------------------
    # Airport database city search
    # --------------------------------------------------------

    city_matches = []

    for iata, airport in AIRPORTS.items():

        city = str(
            airport.get("city", "")
        ).lower().strip()

        name = str(
            airport.get("name", "")
        ).lower().strip()

        score = 0

        if city == location_clean:
            score += 100

        elif location_clean in city:
            score += 70

        if location_clean in name:
            score += 50

        if "international" in name:
            score += 10

        if score > 0:
            city_matches.append(
                (score, iata)
            )

    if city_matches:

        city_matches.sort(reverse=True)

        return city_matches[0][1]

    return None


# ============================================================
# Find location mentions
# ============================================================

def find_location_mentions(
    query: str
):
    """
    Find country and city names inside a
    natural-language query.
    """

    q = query.lower()

    mentions = []

    # Country aliases
    for alias in COUNTRY_ALIASES:

        if re.search(
            rf"\b{re.escape(alias)}\b",
            q
        ):
            mentions.append(alias)

    # Country names from pycountry
    for country in pycountry.countries:

        name = country.name.lower()

        if len(name) >= 4:

            if re.search(
                rf"\b{re.escape(name)}\b",
                q
            ):
                mentions.append(name)

    # Cities
    for city in CITY_MAIN_AIRPORT:

        if re.search(
            rf"\b{re.escape(city)}\b",
            q
        ):
            mentions.append(city)

    # Remove duplicates
    unique_mentions = []

    for item in mentions:

        if item not in unique_mentions:
            unique_mentions.append(item)

    return unique_mentions


# ============================================================
# Parse route
# ============================================================
def parse_route(query: str):
    q = query.lower().strip()

    # Global flight request
    if any(
        phrase in q
        for phrase in [
            "global flights",
            "all flights",
            "worldwide flights",
            "flights worldwide",
        ]
    ):
        return None, None

    # ---------------------------------------------------------
    # Explicit IATA codes
    # Only accept codes when they are clearly written as codes.
    # ---------------------------------------------------------
    explicit_patterns = [
        r"\bfrom\s+([A-Za-z]{3})\s+to\s+([A-Za-z]{3})\b",
        r"\bto\s+([A-Za-z]{3})\s+from\s+([A-Za-z]{3})\b",
    ]

    for pattern in explicit_patterns:
        match = re.search(pattern, query, re.IGNORECASE)

        if match:
            codes = [match.group(1).upper(), match.group(2).upper()]

            if all(code in AIRPORTS for code in codes):
                return codes[0], codes[1]

    # ---------------------------------------------------------
    # Use location detection
    # ---------------------------------------------------------
    mentions = find_location_mentions(query)

    resolved = []

    for location in mentions:
        iata = resolve_location_to_iata(location)

        if iata and iata not in resolved:
            resolved.append(iata)

    # For:
    # "Dubai trip from Mumbai"
    # find_location_mentions() returns:
    # ['mumbai', 'dubai']
    #
    # Since "from Mumbai" is the origin, determine origin
    # from the phrase and use the other location as destination.
    # ---------------------------------------------------------

    origin = None
    destination = None

    # Find origin after "from"
    from_match = re.search(
        r"\bfrom\s+([a-zA-Z][a-zA-Z\s]*)",
        q,
        re.IGNORECASE,
    )

    if from_match:
        from_text = from_match.group(1).strip()

        # Resolve against the detected mentions
        for location in mentions:
            if location.lower() in from_text.lower():
                origin = resolve_location_to_iata(location)
                break

    # Find destination using "to"
    to_match = re.search(
        r"\bto\s+([a-zA-Z][a-zA-Z\s]*)",
        q,
        re.IGNORECASE,
    )

    if to_match:
        to_text = to_match.group(1).strip()

        for location in mentions:
            if location.lower() in to_text.lower():
                destination = resolve_location_to_iata(location)
                break

    # If we have an origin, the other resolved location is
    # the destination.
    if origin:
        for iata in resolved:
            if iata != origin:
                destination = iata
                break

    # If we have a destination, the other resolved location
    # is the origin.
    if destination:
        for iata in resolved:
            if iata != destination:
                origin = iata
                break

    # If exactly two locations were detected, use them.
    if len(resolved) >= 2:
        if origin and destination:
            return origin, destination

        return resolved[0], resolved[1]

    # One location only
    if len(resolved) == 1:
        return resolved[0], None

    return None, None


# ============================================================
# Format flight
# ============================================================

def format_flight(flight: dict):

    airline = (
        flight.get("airline", {}).get("name")
        or "Unknown airline"
    )

    flight_number = (
        flight.get("flight", {}).get("iata")
        or "Unknown flight number"
    )

    status = (
        flight.get("flight_status")
        or "Unknown"
    )

    departure = flight.get("departure") or {}

    dep_airport = (
        departure.get("airport")
        or "Unknown departure airport"
    )

    dep_iata = (
        departure.get("iata")
        or "Unknown"
    )

    dep_terminal = (
        departure.get("terminal")
        or "N/A"
    )

    dep_gate = (
        departure.get("gate")
        or "N/A"
    )

    dep_scheduled = (
        departure.get("scheduled")
        or "Unknown"
    )

    dep_delay = departure.get("delay")

    dep_delay_text = (
        f"{dep_delay} minutes"
        if dep_delay is not None
        else "N/A"
    )

    arrival = flight.get("arrival") or {}

    arr_airport = (
        arrival.get("airport")
        or "Unknown arrival airport"
    )

    arr_iata = (
        arrival.get("iata")
        or "Unknown"
    )

    arr_terminal = (
        arrival.get("terminal")
        or "N/A"
    )

    arr_gate = (
        arrival.get("gate")
        or "N/A"
    )

    arr_scheduled = (
        arrival.get("scheduled")
        or "Unknown"
    )

    arr_delay = arrival.get("delay")

    arr_delay_text = (
        f"{arr_delay} minutes"
        if arr_delay is not None
        else "N/A"
    )

    return f"""
Airline: {airline}
Flight: {flight_number}
Status: {status}

Departure:
- Airport: {dep_airport}
- IATA: {dep_iata}
- Terminal: {dep_terminal}
- Gate: {dep_gate}
- Scheduled: {dep_scheduled}
- Delay: {dep_delay_text}

Arrival:
- Airport: {arr_airport}
- IATA: {arr_iata}
- Terminal: {arr_terminal}
- Gate: {arr_gate}
- Scheduled: {arr_scheduled}
- Delay: {arr_delay_text}
""".strip()


# ============================================================
# Search flights
# ============================================================

def search_flights(
    query: str,
    limit: int = 10
):

    if not API_KEY:

        return (
            "Flight API ERROR: "
            "AVIATIONSTACK_API_KEY is missing.\n\n"
            "Please add this to your .env file:\n"
            "AVIATIONSTACK_API_KEY=your_api_key_here"
        )

    dep_iata, arr_iata = parse_route(
        query
    )

    params = {
        "access_key": API_KEY,
        "limit": min(limit, 100),
    }

    if dep_iata:
        params["dep_iata"] = dep_iata

    if arr_iata:
        params["arr_iata"] = arr_iata

    try:

        response = requests.get(
            BASE_URL,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

    except requests.exceptions.RequestException as e:

        return (
            f"Flight API request failed: {e}"
        )

    except ValueError:

        return (
            "Flight API returned invalid JSON."
        )

    # --------------------------------------------------------
    # API error
    # --------------------------------------------------------

    if "error" in data:

        error = data["error"]

        return (
            "Flight API error:\n"
            f"Code: {error.get('code', 'unknown')}\n"
            f"Message: {error.get('message', 'unknown error')}"
        )

    flight_data = data.get(
        "data",
        []
    )

    # --------------------------------------------------------
    # No results
    # --------------------------------------------------------

    if not flight_data:

        route_text = ""

        if dep_iata and arr_iata:

            route_text = (
                f" for route "
                f"{dep_iata} to {arr_iata}"
            )

        elif dep_iata:

            route_text = (
                f" from {dep_iata}"
            )

        elif arr_iata:

            route_text = (
                f" to {arr_iata}"
            )

        return (
            f"No live flight data found"
            f"{route_text}.\n\n"
            "Note: Aviationstack provides live/status "
            "flight data, not ticket prices. "
            "For actual fare prices, use a flight-pricing "
            "API such as Amadeus."
        )

    # --------------------------------------------------------
    # Format results
    # --------------------------------------------------------

    route_info = "Global live flights"

    if dep_iata and arr_iata:

        route_info = (
            f"Live flights from "
            f"{dep_iata} to {arr_iata}"
        )

    elif dep_iata:

        route_info = (
            f"Live flights from {dep_iata}"
        )

    elif arr_iata:

        route_info = (
            f"Live flights to {arr_iata}"
        )

    formatted_flights = [
        format_flight(flight)
        for flight in flight_data[:limit]
    ]

    return (
        f"{route_info}\n\n"
        + "\n\n---\n\n".join(
            formatted_flights
        )
    )


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":

    test_queries = [
        "Plan a 7-day trip to Japan from Mumbai for ₹1.5 lakh",
        "Plan a Japan trip from Mumbai",
        "flights from Mumbai to Tokyo",
        "Mumbai to Tokyo",
        "flights to Japan",
        "flights from Mumbai",
        "BOM to NRT",
    ]

    print("\nROUTE PARSER TESTS")
    print("=" * 60)

    for query in test_queries:

        print(f"\nQuery: {query}")

        dep, arr = parse_route(query)

        print(
            f"Route: {dep} -> {arr}"
        )

    print("\n" + "=" * 60)

    print(
        search_flights(
            "Plan a 7-day trip to Japan from Mumbai"
        )
    )

