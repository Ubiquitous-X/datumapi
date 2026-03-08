from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import datetime

from .date_info import get_date_info

# Skapar API:t med metadata (visas i Swagger)
app = FastAPI(
    title="DatumAPI (SE)",
    description="API för datum och svenska helgdagar",
    version="1.0.0",
    contact={
        "name": "DatumAPI",
    },

)

# Statiska filer som CSS/JS
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# HTML-templates
templates = Jinja2Templates(directory="app/templates")


def _parse_date_or_400(value: str) -> datetime.date:
    # Accepterar både YYYY-MM-DD och YYYYMMDD
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Ogiltigt datumformat. Använd YYYY-MM-DD eller YYYYMMDD",
        )


# Modell för API-svaret
class DateInfo(BaseModel):
    date: str = Field(example="2026-12-24", description="Datum i ISO-format (YYYY-MM-DD).")
    is_today: bool = Field(description="True om datumet är idag.")
    days_from_today: int = Field(description="Antal dagar från idag.")
    is_business_day: bool = Field(description="True om det är en arbetsdag (mån-fre, ej helgdag).")

    weekday_name: str = Field(example="onsdag", description="Veckodagens namn.")
    weekday_number: int = Field(example=3, description="Veckodag som siffra: måndag=1, söndag=7.")
    week_number: int = Field(example=52, description="Veckonummer.")

    month_name: str = Field(example="december", description="Månadens namn.")
    days_in_month: int = Field(example=31, description="Antal dagar i månaden.")

    day_of_year: int = Field(example=358, description="Vilken dag under året (1-365/366).")
    is_leap: bool = Field(description="True om året är skottår.")

    is_holiday: bool = Field(description="True om datumet är en helgdag.")
    holiday_name: str | None = Field(default=None, example="Julafton", description="Namn på helgdag.")
    next_holiday_name: str | None = Field(default=None, example="Juldagen", description="Namn på nästa helgdag.")
    days_until_next_holiday: int | None = Field(default=None, example=1, description="Dagar till nästa helgdag.")

    class Config:
        # Exempel som visas i Swagger
        json_schema_extra = {
            "example": {
                "date": "2026-12-24",
                "is_today": False,
                "days_from_today": 187,
                "is_business_day": False,
                "weekday_name": "torsdag",
                "weekday_number": 4,
                "week_number": 52,
                "month_name": "december",
                "days_in_month": 31,
                "day_of_year": 358,
                "is_leap": False,
                "is_holiday": True,
                "holiday_name": "Julafton",
                "next_holiday_name": "Juldagen",
                "days_until_next_holiday": 1,
            }
        }


# API-endpoint för datuminfo ett specifikt datum
@app.get(
    "/api/v1/date/{date}",
    response_class=JSONResponse,
    response_model=DateInfo,
    response_model_exclude_none=True,  # Ta bort fält med None i svaret
    tags=["Date"],
    summary="Hämta information om ett datum",
    description=(
        "Ger info om ett datum: veckonummer, arbetsdag/helgdag och nästa helgdag. "
        "Ange datum som `YYYY-MM-DD` eller `YYYYMMDD`."
    ),
    responses={
        200: {
            "description": "Datuminfo hämtad",
            "content": {
                "application/json": {
                    "example": {
                        "date": "2026-12-24",
                        "is_today": False,
                        "days_from_today": 187,
                        "is_business_day": False,
                        "weekday_name": "torsdag",
                        "weekday_number": 4,
                        "week_number": 52,
                        "month_name": "december",
                        "days_in_month": 31,
                        "day_of_year": 358,
                        "is_leap": False,
                        "is_holiday": True,
                        "holiday_name": "Julafton",
                        "next_holiday_name": "Juldagen",
                        "days_until_next_holiday": 1,
                    }
                }
            },
        },
        400: {
            "description": "Felaktigt datumformat",
            "content": {
                "application/json": {
                    "example": {"detail": "Ogiltigt datum eller felaktigt format. Använd YYYY-MM-DD eller YYYYMMDD"}
                }
            },
        },
    },
)
def api_date(date: str):
    date_obj = _parse_date_or_400(date)
    return get_date_info(date_obj)


# API-endpoint för att hitta nästa arbetsdag efter ett givet datum
@app.get(
    "/api/v1/next-business-day/{date}",
    response_class=JSONResponse,
    tags=["Date"],
    summary="Hämta nästa arbetsdag",
)
def api_next_business_day(date: str):
    date_obj = _parse_date_or_400(date)

    d = date_obj + datetime.timedelta(days=1)

    while True:
        info = get_date_info(d)

        if info["is_business_day"]:
            return {
                "date": date_obj.isoformat(),
                "next_business_day": d.isoformat(),
                "days_until": (d - date_obj).days,
            }

        d += datetime.timedelta(days=1)


# API-endpoint för att räkna antal arbetsdagar mellan två datum
@app.get(
    "/api/v1/business-days",
    response_class=JSONResponse,
    tags=["Date"],
    summary="Räkna arbetsdagar mellan två datum",
)
def api_business_days(start: str, end: str):
    start_date = _parse_date_or_400(start)
    end_date = _parse_date_or_400(end)

    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Startdatum måste vara före eller samma som slutdatum",
        )

    business_days = 0
    current = start_date

    while current <= end_date:
        info = get_date_info(current)

        if info["is_business_day"]:
            business_days += 1

        current += datetime.timedelta(days=1)

    return {
        "start": start,
        "end": end,
        "business_days": business_days,
    }


# API-endpoint för att lista alla icke-bankdagar under ett specifikt år
@app.get(
    "/api/v1/non-business-days/{year}",
    response_class=JSONResponse,
    tags=["Date"],
    summary="Hämta icke-bankdagar för ett år",
)
def api_non_business_days_year(year: int):

    if year < 1900 or year > 2100:
        raise HTTPException(
            status_code=400,
            detail="År måste vara mellan 1900 och 2100",
        )

    start = datetime.date(year, 1, 1)
    end = datetime.date(year, 12, 31)

    non_business_days = []
    current = start

    while current <= end:

        info = get_date_info(current)

        if not info["is_business_day"]:

            reason = info["holiday_name"]

            if not reason and info["weekday_number"] >= 6:
                reason = "Helg"

            non_business_days.append({
                "date": info["date"],
                "weekday_name": info["weekday_name"],
                "reason": reason,
            })

        current += datetime.timedelta(days=1)

    return {
        "year": year,
        "non_business_days": non_business_days,
    }


# API-endpoint för att lista alla icke-bankdagar inom ett datumintervall
@app.get(
    "/api/v1/non-business-days",
    response_class=JSONResponse,
    tags=["Date"],
    summary="Hämta icke-bankdagar inom ett datumintervall",
)
def api_non_business_days_range(start: str, end: str):
    start_date = _parse_date_or_400(start)
    end_date = _parse_date_or_400(end)

    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Startdatum måste vara före eller samma som slutdatum",
        )

    non_business_days = []
    current = start_date

    while current <= end_date:

        info = get_date_info(current)

        if not info["is_business_day"]:

            reason = info["holiday_name"]

            if not reason and info["weekday_number"] >= 6:
                reason = "Helg"

            non_business_days.append({
                "date": info["date"],
                "weekday_name": info["weekday_name"],
                "reason": reason,
            })

        current += datetime.timedelta(days=1)

    if not non_business_days:
        return {
            "message": "Inga icke-bankdagar hittades i datumintervallet"
        }

    return non_business_days


# API-endpoint för att lista alla helgdagar under ett specifikt år
@app.get(
    "/api/v1/holidays/{year}",
    response_class=JSONResponse,
    tags=["Date"],
    summary="Hämta alla helgdagar för ett år",
)
def api_holidays_year(year: int):

    if year < 1900 or year > 2100:
        raise HTTPException(
            status_code=400,
            detail="År måste vara mellan 1900 och 2100",
        )

    start = datetime.date(year, 1, 1)
    end = datetime.date(year, 12, 31)

    holidays_list = []
    current = start

    while current <= end:
        info = get_date_info(current)

        if info["is_holiday"]:
            holidays_list.append({
                "date": info["date"],
                "holiday_name": info["holiday_name"],
                "weekday_name": info["weekday_name"],
            })

        current += datetime.timedelta(days=1)

    return {
        "year": year,
        "holidays": holidays_list,
    }


# API-endpoint för helgdagar inom ett datumintervall
@app.get(
    "/api/v1/holidays",
    response_class=JSONResponse,
    tags=["Date"],
    summary="Hämta helgdagar inom ett datumintervall",
)
def api_holidays(start: str, end: str):
    start_date = _parse_date_or_400(start)
    end_date = _parse_date_or_400(end)

    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Startdatum måste vara före eller samma som slutdatum",
        )

    holidays_list = []

    current = start_date
    while current <= end_date:
        info = get_date_info(current)

        if info["is_holiday"]:
            holidays_list.append({
                "date": info["date"],
                "holiday_name": info["holiday_name"],
                "weekday_name": info["weekday_name"],
            })

        current += datetime.timedelta(days=1)

    if not holidays_list:
        return {
            "message": "Inga helgdagar hittades i datumintervallet"
        }

    return holidays_list


# Startsida
@app.get("/", include_in_schema=False, response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "year": datetime.datetime.now().year,
        }
    )
