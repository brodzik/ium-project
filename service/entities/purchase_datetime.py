from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CodedPurchaseDateTime:

    purchase_day: int
    purchase_day_cos: float
    purchase_day_sin: float

    purchase_dayofweek: int
    purchase_dayofweek_cos: float
    purchase_dayofweek_sin: float

    purchase_hour: int
    purchase_hour_cos: float
    purchase_hour_sin: float

    purchase_minute: int
    purchase_minute_cos: float
    purchase_minute_sin: float

    purchase_month: int
    purchase_month_cos: float
    purchase_month_sin: float

    purchase_second: int
    purchase_second_cos: float
    purchase_second_sin: float

    purchase_year: int

    @staticmethod
    def from_datetime(purchase_datetime: datetime) -> CodedPurchaseDateTime:
        year = purchase_datetime.year

        month = purchase_datetime.month
        month_cos = math.cos(2 * math.pi * month / 12)
        month_sin = math.cos(2 * math.pi * month / 12)

        day = purchase_datetime.day
        day_cos = math.cos(2 * math.pi * day / 31)
        day_sin = math.cos(2 * math.pi * day / 31)

        dayofweek = purchase_datetime.weekday()
        dayofweek_cos = math.cos(2 * math.pi * dayofweek / 7)
        dayofweek_sin = math.cos(2 * math.pi * dayofweek / 7)

        hour = purchase_datetime.hour
        hour_cos = math.cos(2 * math.pi * hour / 24)
        hour_sin = math.cos(2 * math.pi * hour / 24)

        minute = purchase_datetime.minute
        minute_cos = math.cos(2 * math.pi * minute / 24)
        minute_sin = math.cos(2 * math.pi * hour / 24)

        second = purchase_datetime.second
        second_cos = math.cos(2 * math.pi * second / 60)
        second_sin = math.cos(2 * math.pi * second / 60)

        return CodedPurchaseDateTime(
            purchase_year=year,
            purchase_month=month,
            purchase_month_cos=month_cos,
            purchase_month_sin=month_sin,
            purchase_day=day,
            purchase_day_cos=day_cos,
            purchase_day_sin=day_sin,
            purchase_hour=hour,
            purchase_hour_cos=hour_cos,
            purchase_hour_sin=hour_sin,
            purchase_minute=minute,
            purchase_minute_cos=minute_cos,
            purchase_minute_sin=minute_sin,
            purchase_second=second,
            purchase_second_cos=second_cos,
            purchase_second_sin=second_sin,
            purchase_dayofweek=dayofweek,
            purchase_dayofweek_cos=dayofweek_cos,
            purchase_dayofweek_sin=dayofweek_sin,
        )
