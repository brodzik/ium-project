import typing
from typing import Literal, TypedDict, cast

import pandas as pd

City = Literal[
    "Gdynia",
    "Konin",
    "Kutno",
    "Mielec",
    "Police",
    "Radom",
    "Szczecin",
    "Warszawa",
]
CodedCity = TypedDict(
    "CodedCity",
    {
        "city_Gdynia": bool,
        "city_Konin": bool,
        "city_Kutno": bool,
        "city_Mielec": bool,
        "city_Police": bool,
        "city_Radom": bool,
        "city_Szczecin": bool,
        "city_Warszawa": bool,
    },
)


def code_city(city: City) -> CodedCity:
    coded_city = cast(
        CodedCity, {"city_" + city_name: False for city_name in typing.get_args(City)}
    )
    coded_city["city_" + city] = True
    return coded_city


def city_from_features(features: pd.DataFrame) -> City:
    for city in typing.get_args(City):
        if bool(features["city_" + city][0]) is True:
            return city

    raise TypeError("Incorrect features (no city was selected)")
