# MIT 805 Big Data — NYC High Volume For-Hire Vehicle (HVFHV) Analysis

University of Pretoria, MIT 805 semester project (2026).
**Group members:** \<Name 1\> (\<student no.\>), \<Name 2\> (\<student no.\>)

Analysis of New York City Taxi and Limousine Commission High Volume For-Hire
Vehicle trip records — every trip dispatched by Uber, Lyft, Via and Juno — using
PySpark for distributed, MapReduce-style processing.

| | |
|---|---|
| Part 1 (data collection, EDA, 7 Vs) | `notebooks/01_part1_data_and_eda.ipynb` |
| Part 2 (MapReduce, visualisation) | `notebooks/02_part2_mapreduce.ipynb` *(to come)* |
| Reports | `report/` |

---

## Dataset

| | |
|---|---|
| Publisher | NYC Taxi and Limousine Commission |
| Landing page | https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page |
| Data dictionary | https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_hvfhs.pdf |
| File pattern | `https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_YYYY-MM.parquet` |
| Zone lookup | https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv |
| Mirror | AWS Open Data Registry, `s3://nyc-tlc` (us-east-1) |
| Coverage | February 2019 onward, monthly, ~2-month publication lag |
| Format | Apache Parquet (columnar, compressed) |
| Licence | NYC.gov Terms of Use; published as NYC Open Data. Free reuse including research, with attribution to the City of New York. |

**No trip record data is committed to this repository.** The TLC files are large
and the assignment brief asks that datasets be referenced rather than
redistributed. `data/raw/` is gitignored; run the download step below.

### A note on schema evolution

The HVFHV series is **not schema-stable** and this will break a naive read:

| Period | Notes |
|---|---|
| 2019-02 – 2020-12 | Reduced schema: licensee, base, pickup/dropoff time, PU/DO zone, `SR_Flag` only |
| 2021-01 onward | Adds `request_datetime`, `on_scene_datetime`, `trip_miles`, `trip_time`, itemised fares, `driver_pay`, shared/WAV/Access-A-Ride flags |
| 2025-01 onward | Adds `cbd_congestion_fee` for NYC congestion pricing |

Read with `mergeSchema` enabled, or restrict to a single-schema window.

### Dataset tiers

Defined in `src/config.py` and measured by `src/sizes.py`:

- **Raw** — the full published archive (2019-02 to 2026-05). Measured via HTTP
  `HEAD` requests; never downloaded in full.
- **Working** — 2024-01 onward; the modern, schema-consistent window.
- **Processing** — calendar year 2025; the first complete year under NYC
  congestion pricing.

Actual measured sizes are written to `output/dataset_sizes.csv`.

---

## Reproducing the analysis

### Google Colab (recommended)

Open `notebooks/01_part1_data_and_eda.ipynb` in Colab and run all cells. It
installs PySpark, measures the dataset tiers, downloads the processing set,
runs the EDA and writes results to `output/` and `figures/`. Set
`FAST_MODE = True` in the tier-definition cell to use 7 months instead of 12.

### Locally

Requires Python 3.10+ and a Java 11 or 17 runtime (PySpark needs a JVM).

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python src/sizes.py                      # measure all three tiers (~1 min)
python src/download_data.py processing   # ~6 GB over 12 files
jupyter lab notebooks/01_part1_data_and_eda.ipynb
```

`src/download_data.py` skips files already present at the expected size, so it
is safe to re-run after an interrupted download.

---

## Layout

```
.
├── README.md
├── requirements.txt
├── data/
│   ├── README.md          how to obtain the data; raw files are not committed
│   └── raw/               (gitignored)
├── notebooks/             analysis notebooks
├── src/                   config, size audit, download helpers
├── output/                computed aggregates (CSV/JSON), committed
├── figures/               generated plots, committed
└── report/                LaTeX source and compiled PDFs
```

## Outputs

| File | Contents |
|---|---|
| `output/dataset_sizes.csv` | raw / working / processing sizes |
| `output/file_sizes.csv` | per-month file size for the whole archive |
| `output/missingness.csv` | null counts and percentages by column |
| `output/quality_checks.csv` | validity audit |
| `output/numeric_summary.csv` | distributional statistics |
| `output/market_share.csv` | trips and averages by licensee |
| `output/daily_trips.csv` | daily trip volume |
| `output/wait_by_hour.csv` | mean passenger wait by hour |
| `output/match_rates.csv` | shared-ride and WAV request vs. match rates |
| `output/top_pickup_zones.csv` | busiest pickup zones |
| `output/borough_flows.csv` | borough-to-borough origin-destination matrix |
| `output/monthly_economics.csv` | driver pay and tips as a share of fares |
| `output/report_numbers.json` | headline figures used in the report |

## Attribution

Trip data © City of New York, published by the NYC Taxi and Limousine
Commission under the NYC.gov Terms of Use. The TLC states that the trip data was
not created by the TLC and it makes no representations as to its accuracy.
