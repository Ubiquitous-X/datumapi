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


# Modell för API-svaret
class DateInfo(BaseModel):
    date: str = Field(example="2025-12-24", description="Datum i ISO-format (YYYY-MM-DD).")
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


# API-endpoint för datuminfo
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
    # Försök tolka datumet. Kasta 400 vid fel format.
    try:
        date_obj = datetime.date.fromisoformat(date)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Ogiltigt datum eller felaktigt format. Använd YYYY-MM-DD eller YYYYMMDD",
        )
    return get_date_info(date_obj)  # Använd befintlig logik för att skapa svaret


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
