# Data

Raw trip records are **not committed to this repository**. The TLC files are
large and the assignment brief requires that datasets be referenced rather than
redistributed.

## Source

NYC Taxi and Limousine Commission, High Volume For-Hire Vehicle (HVFHV) trip
records.

- Landing page: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- Monthly files: `https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_YYYY-MM.parquet`
- Zone lookup: https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv
- Zone shapefile: https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip
- Data dictionary: https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_hvfhs.pdf
- Mirror: AWS Open Data Registry, `s3://nyc-tlc` (us-east-1)

Coverage begins February 2019. Files are published monthly with roughly a
two-month lag to allow for vendor submissions.

## Obtaining the data

```bash
python src/download_data.py processing   # 2025 calendar year, ~6 GB
python src/download_data.py working      # 2024-01 onward, ~14 GB
```

Files land in `data/raw/`. The script skips anything already downloaded at the
expected size.

## Schema

`fhvhv_tripdata_*.parquet`, one row per completed trip:

| Column | Type | Notes |
|---|---|---|
| `hvfhs_license_num` | string | HV0002 Juno, HV0003 Uber, HV0004 Via, HV0005 Lyft |
| `dispatching_base_num` | string | TLC base that dispatched the trip |
| `originating_base_num` | string | often null |
| `request_datetime` | timestamp | when the passenger requested (2021+) |
| `on_scene_datetime` | timestamp | driver arrival (2021+; unevenly populated) |
| `pickup_datetime` | timestamp | |
| `dropoff_datetime` | timestamp | |
| `PULocationID` / `DOLocationID` | int | taxi zone, join to `taxi_zone_lookup.csv`; 264/265 are unknown |
| `trip_miles` | double | passenger-carrying distance |
| `trip_time` | long | seconds |
| `base_passenger_fare` | double | before tolls, tax and surcharges |
| `tolls`, `bcf`, `sales_tax`, `congestion_surcharge`, `airport_fee`, `tips` | double | itemised |
| `driver_pay` | double | excluding tolls, tips and surcharges |
| `shared_request_flag` / `shared_match_flag` | Y/N | requested vs. actually shared |
| `access_a_ride_flag` | Y/N | administered on behalf of the MTA |
| `wav_request_flag` / `wav_match_flag` | Y/N | wheelchair-accessible vehicle |
| `cbd_congestion_fee` | double | congestion pricing, 2025+ only |

**Schema is not stable across years** — see the README before reading multiple
years in one Spark job.

## Privacy and ethics

The dataset carries no rider, driver or vehicle identifiers. Pickup and dropoff
locations are generalised to 265 administrative taxi zones; the TLC stopped
publishing GPS coordinates in July 2016. No re-identification is attempted in
this project.

## Licence

NYC.gov Terms of Use (https://www.nyc.gov/home/terms-of-use.page), published as
NYC Open Data. Free public reuse including research, with attribution to the
City of New York. The TLC states that the trip data was not created by the TLC
and it makes no representations as to its accuracy.
