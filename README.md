# DatumAPI

Ett enkelt API byggt med FastAPI för att hämta information om svenska datum, veckonummer och helgdagar.  
API:et visar även arbetsdagar, veckodag, månader och info om nästa helgdag.

http://datumapi.duckdns.org

## Funktioner

- Kontrollera om ett datum är en helgdag eller arbetsdag.
- Hämta namn och nummer på veckodag, veckonummer, månadens namn och antal dagar i månaden.
- Få info om närmaste kommande helgdag.
- Allt presenteras på svenska.

## Exempel

**API-anrop:**

```
GET /api/v1/date/2025-12-24
eller
GET /api/v1/date/20251224
```

**Svar:**

```json
{
  "date": "2025-12-24",
  "is_today": false,
  "days_from_today": 123,
  "is_business_day": false,
  "weekday_name": "onsdag",
  "weekday_number": 3,
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

### Eller med Docker

Bygg och starta:

```sh
docker build -t datumapi .
docker run -p 8000:8000 datumapi
```

### Eller med docker-compose

```sh
docker-compose up --build
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

