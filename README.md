# DatumAPI

Ett enkelt API byggt med FastAPI för att hämta information om svenska datum, veckonummer och helgdagar.  
API:et visar även arbetsdagar, veckodag, månader och info om nästa helgdag.

https://datumapi.duckdns.org

## Funktioner

- Kontrollera om ett datum är en helgdag eller arbetsdag.
- Hämta namn och nummer på veckodag, veckonummer, månadens namn och antal dagar i månaden.
- Få info om närmaste kommande helgdag.
- Hämta alla helgdagar inom ett datumintervall.
- Hämta nästa arbetsdag efter ett datum.
- Räkna arbetsdagar inom ett datumintervall.
- Hämta icke-arbetsdagar för år eller datumintervall.
- Hämta helgdagar för ett helt år.
- Allt presenteras på svenska.

## Endpoints (översikt)

```text
GET /api/v1/date/{date}
GET /api/v1/next-business-day/{date}
GET /api/v1/business-days?start=YYYY-MM-DD&end=YYYY-MM-DD
GET /api/v1/non-business-days/{year}
GET /api/v1/non-business-days?start=YYYY-MM-DD&end=YYYY-MM-DD
GET /api/v1/holidays/{year}
GET /api/v1/holidays?start=YYYY-MM-DD&end=YYYY-MM-DD
```

## Exempel enskilt datum

**API-anrop:**

```
GET /api/v1/date/2026-12-24
eller
GET /api/v1/date/20261224
```

**Svar:**

```json
{
  "date": "2026-12-24",
  "is_today": false,
  "days_from_today": 291,
  "is_business_day": false,
  "weekday_name": "torsdag",
  "weekday_number": 4,
  "week_number": 52,
  "month_name": "december",
  "days_in_month": 31,
  "day_of_year": 358,
  "is_leap": false,
  "is_holiday": true,
  "holiday_name": "Julafton",
  "next_holiday_name": "Juldagen",
  "days_until_next_holiday": 1
}
```

## Exempel helgdagar inom datumintervall

**API-anrop:**

```
GET /api/v1/holidays?start=2026-12-01&end=2026-12-26
eller
GET /api/v1/holidays?start=20261201&end=20261226
```

**Svar:**

```json
[
  {
    "date": "2026-12-24",
    "holiday_name": "Julafton",
    "weekday_name": "torsdag"
  },
  {
    "date": "2026-12-25",
    "holiday_name": "Juldagen",
    "weekday_name": "fredag"
  },
  {
    "date": "2026-12-26",
    "holiday_name": "Annandag jul",
    "weekday_name": "lördag"
  }
]
```

## Exempel fler endpoints

```text
GET /api/v1/next-business-day/2026-12-24
GET /api/v1/business-days?start=2026-12-20&end=2026-12-31
GET /api/v1/non-business-days/2026
GET /api/v1/non-business-days?start=2026-12-20&end=2026-12-31
GET /api/v1/holidays/2026
```

## Installation

### Klona projektet

```sh
git clone https://github.com/Ubiquitous-X/datumapi.git
cd datumapi
```

### Installera beroenden

```sh
pip install -r requirements.txt
```

### Starta API:t (lokalt)

```sh
uvicorn app.main:app --reload
```

### Kör med Docker

Bygg image:
```sh
docker build -t datumapi .
```
Starta container:
```sh
docker run -p 8000:8000 datumapi
```

### Kör med docker compose

```sh
docker compose up --build
```

## Användning

Öppna din webbläsare och gå till [http://localhost:8000/docs](http://localhost:8000/docs) för att testa API:et via Swagger UI.

## Projektstruktur

```
app/
  main.py
  date_info.py
  static/
  templates/
requirements.txt
Dockerfile
docker-compose.yml
README.md
```

## Licens

Detta projekt är licensierat under [MIT-licensen](LICENSE).

---
