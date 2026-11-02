from datetime import datetime
from zoneinfo import ZoneInfo
from src.calendar_utils import is_store_open, get_holiday_name, get_weekday_name_pt

def test_store_hours_and_holidays_fixed_clock():
    """Block 2a: Store hours on weekdays, saturdays, sundays and holidays."""
    tz = ZoneInfo("America/Campo_Grande")

    # 1. Holiday: 02/11/2026 10h (Finados) -> closed
    dt_finados = datetime(2026, 11, 2, 10, 0, tzinfo=tz)
    is_open, desc = is_store_open(dt_finados)
    assert is_open is False
    assert "Finados" in desc

    # 2. Regular Tuesday: 03/11/2026 10h -> open
    dt_terca = datetime(2026, 11, 3, 10, 0, tzinfo=tz)
    is_open_t, desc_t = is_store_open(dt_terca)
    assert is_open_t is True
    assert "09:00 às 18:00" in desc_t

    # 3. Saturday after hours: 07/11/2026 14h -> closed (closes at 13h)
    dt_sab = datetime(2026, 11, 7, 14, 0, tzinfo=tz)
    is_open_s, desc_s = is_store_open(dt_sab)
    assert is_open_s is False

    # 4. Weekday in Portuguese
    assert get_weekday_name_pt(0) == "segunda-feira"
    assert get_weekday_name_pt(1) == "terça-feira"
    assert get_weekday_name_pt(6) == "domingo"
