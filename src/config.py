"""
Central configuration for the MIT 805 HVFHV project.

Three dataset tiers are defined, as required by the assignment brief:

  RAW        - the full publicly available HVFHV archive (every monthly file
               the TLC publishes). We never download this in full; its size is
               measured with HTTP HEAD requests.
  WORKING    - the months actually downloaded and preprocessed locally.
  PROCESSING - the months actually read into Spark for the analysis.

Edit RAW_END, WORKING_MONTHS and PROCESSING_MONTHS if you need to hit
different size targets. Run `python src/sizes.py` after any change to
re-measure and regenerate output/dataset_sizes.csv.
"""

from datetime import date

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
ZONE_LOOKUP_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
ZONE_SHAPEFILE_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip"
SOURCE_PAGE = "https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page"
DATA_DICTIONARY = (
    "https://www.nyc.gov/assets/tlc/downloads/pdf/"
    "data_dictionary_trip_records_hvfhs.pdf"
)
LICENCE_URL = "https://www.nyc.gov/home/terms-of-use.page"

# HVFHV publication starts February 2019. Update RAW_END to the newest month
# listed on the TLC page (verified available: 2026-05).
RAW_START = date(2019, 2, 1)
RAW_END = date(2026, 5, 1)

# --- Tier definitions -------------------------------------------------------
# Working set: modern schema only (2021+ has request/on_scene times, trip_miles,
# driver_pay and the accessibility flags). Jan 2024 onward keeps the download
# manageable while comfortably clearing the 12 GB floor.
WORKING_START = date(2024, 1, 1)
WORKING_END = RAW_END

# Processing set: full calendar year 2025 - the first complete year under NYC
# congestion pricing, and the first year carrying cbd_congestion_fee.
PROCESSING_START = date(2025, 1, 1)
PROCESSING_END = date(2025, 12, 1)

LOCAL_DATA_DIR = "data/raw"
OUTPUT_DIR = "output"
FIGURES_DIR = "figures"

# Licensee codes used by the TLC for high-volume operators.
LICENSEES = {
    "HV0002": "Juno",
    "HV0003": "Uber",
    "HV0004": "Via",
    "HV0005": "Lyft",
}


def month_range(start: date, end: date):
    """Yield date objects for the first of every month from start to end."""
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        yield date(y, m, 1)
        m += 1
        if m == 13:
            y, m = y + 1, 1


def filename(d: date) -> str:
    return f"fhvhv_tripdata_{d.year:04d}-{d.month:02d}.parquet"


def url(d: date) -> str:
    return f"{BASE_URL}/{filename(d)}"


def months(tier: str):
    tier = tier.lower()
    if tier == "raw":
        return list(month_range(RAW_START, RAW_END))
    if tier == "working":
        return list(month_range(WORKING_START, WORKING_END))
    if tier == "processing":
        return list(month_range(PROCESSING_START, PROCESSING_END))
    raise ValueError(f"unknown tier: {tier}")
