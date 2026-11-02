from datetime import datetime, date
from typing import Dict, Optional, Tuple

# National Holidays of Brazil for 2026 and 2027 (Lei Federal nº 662/1949, 6.802/1980, 10.607/2002, 14.759/2023)
# Note: municipal holidays of Campo Grande/MS (e.g. 26/08 - Aniversário de Campo Grande) are not included in this minimal version.
BRAZIL_NATIONAL_HOLIDAYS: Dict[str, str] = {
    # 2026
    "2026-01-01": "Confraternização Universal (Ano Novo)",
    "2026-02-17": "Carnaval",
    "2026-04-03": "Sexta-feira Santa",
    "2026-04-21": "Tiradentes",
    "2026-05-01": "Dia Mundial do Trabalho",
    "2026-06-04": "Corpus Christi",
    "2026-09-07": "Independência do Brasil",
    "2026-10-12": "Nossa Senhora Aparecida",
    "2026-11-02": "Finados",
    "2026-11-15": "Proclamação da República",
    "2026-11-20": "Dia da Consciência Negra",
    "2026-12-25": "Natal",
    # 2027
    "2027-01-01": "Confraternização Universal (Ano Novo)",
    "2027-02-09": "Carnaval",
    "2027-03-26": "Sexta-feira Santa",
    "2027-04-21": "Tiradentes",
    "2027-05-01": "Dia Mundial do Trabalho",
    "2027-05-27": "Corpus Christi",
    "2027-09-07": "Independência do Brasil",
    "2027-10-12": "Nossa Senhora Aparecida",
    "2027-11-02": "Finados",
    "2027-11-15": "Proclamação da República",
    "2027-11-20": "Dia da Consciência Negra",
    "2027-12-25": "Natal",
}

WEEKDAYS_PT: Dict[int, str] = {
    0: "segunda-feira",
    1: "terça-feira",
    2: "quarta-feira",
    3: "quinta-feira",
    4: "sexta-feira",
    5: "sábado",
    6: "domingo",
}

def get_holiday_name(d: date) -> Optional[str]:
    """Returns the holiday name if date is a Brazilian national holiday in 2026-2027, else None."""
    return BRAZIL_NATIONAL_HOLIDAYS.get(d.strftime("%Y-%m-%d"))

def get_weekday_name_pt(weekday: int) -> str:
    """Returns Portuguese weekday name without locale dependency."""
    return WEEKDAYS_PT.get(weekday, "segunda-feira")

def is_store_open(dt: datetime) -> Tuple[bool, str]:
    """Calculates if the store is open based on manual §2:
    - Seg-Sex: 09:00 às 18:00
    - Sáb: 09:00 às 13:00
    - Domingos e Feriados: Fechado
    """
    holiday = get_holiday_name(dt.date())
    if holiday:
        return False, f"Fechado (Feriado Nacional: {holiday})"

    weekday = dt.weekday()
    time_val = dt.hour + dt.minute / 60.0

    if weekday == 6:  # Domingo
        return False, "Fechado (Domingo)"
    elif weekday == 5:  # Sábado
        if 9.0 <= time_val < 13.0:
            return True, "Aberto (Sábado, 09:00 às 13:00)"
        return False, "Fechado (Sábado: expediente 09:00 às 13:00)"
    else:  # Segunda a sexta
        if 9.0 <= time_val < 18.0:
            dia = get_weekday_name_pt(weekday)
            return True, f"Aberto ({dia.capitalize()}, 09:00 às 18:00)"
        return False, "Fechado (Seg-Sex: expediente 09:00 às 18:00)"
