import datetime
import holidays
import calendar
from zoneinfo import ZoneInfo
from typing import Any, Dict, Optional

# Standardinställningar och listor
TZ = ZoneInfo("Europe/Stockholm")
WEEKDAY_NAMES = ["måndag", "tisdag", "onsdag", "torsdag", "fredag", "lördag", "söndag"]
MONTH_NAMES = ["januari", "februari", "mars", "april", "maj", "juni",
               "juli", "augusti", "september", "oktober", "november", "december"]

# Svenska helgdagar (1900–2100 som standard)
se_holidays = holidays.Sweden(language="sv")

def _is_generic_sunday(name: Optional[str]) -> bool:
    # Returnerar True om namnet är en vanlig "Söndag"
    if not name:
        return False
    return name.strip().casefold() == "söndag"

def _clean_holiday_name(raw: Optional[str]) -> Optional[str]:
    # Tar bort "Söndag" om det finns ett annat helgdagsnamn
    if not raw:
        return None
    names = [x.strip() for x in raw.split(";") if x.strip()]
    if len(names) > 1:
        names = [n for n in names if n.casefold() != "söndag"]
    return "; ".join(names) if names else None

def _next_non_generic_holiday(from_date: datetime.date) -> tuple[Optional[str], Optional[int]]:
    # Letar upp nästa riktiga helgdag, max 200 dagar framåt
    for offset in range(1, 200):
        d = from_date + datetime.timedelta(days=offset)
        name = _clean_holiday_name(se_holidays.get(d))
        if name and not _is_generic_sunday(name):
            return name, offset
    return None, None

def get_date_info(date: datetime.date) -> Dict[str, Any]:
    today = datetime.datetime.now(TZ).date()

    # Vecka och veckodag
    week_number = date.isocalendar()[1]
    weekday_number = date.weekday() + 1  # måndag=1
    weekday_name = WEEKDAY_NAMES[date.weekday()]

    # Månad och året
    month_name = MONTH_NAMES[date.month - 1]
    days_in_month = calendar.monthrange(date.year, date.month)[1]
    is_leap = calendar.isleap(date.year)
    day_of_year = (date - datetime.date(date.year, 1, 1)).days + 1

    # Helgdagar
    raw_name = _clean_holiday_name(se_holidays.get(date))
    if _is_generic_sunday(raw_name):
        is_holiday = False
        holiday_name = None
    else:
        is_holiday = date in se_holidays
        holiday_name = raw_name

    next_name, days_until_next = _next_non_generic_holiday(date)

    # Relativa datum
    delta_days = (date - today).days
    is_today = delta_days == 0
    is_business_day = (weekday_number <= 5) and not is_holiday

    return {
        "date": date.isoformat(),                   # Datum som ISO-sträng
        "is_today": is_today,                       # True om datumet är idag
        "days_from_today": delta_days,              # Antal dagar från idag
        "is_business_day": is_business_day,         # True om arbetsdag

        "weekday_name": weekday_name,               # Namn på veckodag
        "weekday_number": weekday_number,           # Veckodag som siffra (mån=1)
        "week_number": week_number,                 # Veckonummer

        "month_name": month_name,                   # Namn på månad
        "days_in_month": days_in_month,             # Antal dagar i månaden

        "day_of_year": day_of_year,                 # Dag på året
        "is_leap": is_leap,                         # True om skottår

        "is_holiday": is_holiday,                   # True om helgdag
        "holiday_name": holiday_name,               # Namn på helgdag
        "next_holiday_name": next_name,             # Nästa helgdag
        "days_until_next_holiday": days_until_next, # Dagar till nästa helgdag
    }