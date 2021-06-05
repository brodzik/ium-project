from __future__ import annotations
import dataclasses
from dataclasses import dataclass
from typing import Callable, Literal, TypedDict, cast, get_args
import typing
from datetime import datetime
import math

from fastapi import FastAPI
import pandas as pd
from pydantic import BaseModel
import xgboost
from sklearn.ensemble import RandomForestRegressor
import joblib

app = FastAPI()

Category = Literal["gry i konsole", "komputery", "sprzęt rtv", "telefony i akcesoria"]

CodedCategory = TypedDict(
    "CodedCategory",
    {
        "category_gry i konsole": bool,
        "category_komputery": bool,
        "category_sprzęt rtv": bool,
        "category_telefony i akcesoria": bool,
    },
)


def code_category(category: Category) -> CodedCategory:
    coded_category = cast(
        CodedCategory,
        {
            "category_" + category_name: False
            for category_name in typing.get_args(Category)
        },
    )
    coded_category["category_" + category] = True
    return coded_category


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


DeliveryCompany = Literal["360", "516", "620"]


CodedDeliveryCompany = TypedDict(
    "CodedDeliveryCompany",
    {
        "delivery_company_360": bool,
        "delivery_company_516": bool,
        "delivery_company_620": bool,
    },
)


def code_delivery_compnay(delivery_company: DeliveryCompany) -> CodedDeliveryCompany:
    coded_delivery_compnay = cast(
        CodedDeliveryCompany,
        {
            "delivery_company_" + delivery_company_name: False
            for delivery_company_name in typing.get_args(DeliveryCompany)
        },
    )
    coded_delivery_compnay["delivery_company_" + delivery_company] = True
    return coded_delivery_compnay


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


class Query(BaseModel):
    category: Category
    city: City
    delivery_company: DeliveryCompany
    price: float
    purchase: datetime

    def to_features(self) -> pd.DataFrame:
        coded_category = code_category(self.category)
        coded_city = code_city(self.city)
        coded_delivery_company = code_delivery_compnay(self.delivery_company)
        coded_purchase = dataclasses.asdict(
            CodedPurchaseDateTime.from_datetime(self.purchase)
        )

        data: dict = {
            **coded_category,
            **coded_city,
            **coded_delivery_company,
            "price": self.price,
            **coded_purchase,
        }
        df = pd.DataFrame([data])
        return df


ExpectedTime = float

ModelCallback = Callable[[pd.DataFrame], ExpectedTime]


@dataclass
class ModelsCallbacks:
    simple: ModelCallback
    xgboost: ModelCallback
    random_forest: ModelCallback


def not_implemented_model_callback(features: pd.DataFrame) -> ExpectedTime:
    raise NotImplementedError()


models_callbacks = ModelsCallbacks(
    simple=not_implemented_model_callback,
    xgboost=not_implemented_model_callback,
    random_forest=not_implemented_model_callback,
)


def city_from_features(features: pd.DataFrame) -> City:
    for city in get_args(City):
        if bool(features["city_" + city][0]) is True:
            return city

    raise TypeError("Incorrect features (no city was selected)")


def simple_model_callback_from_statistic(statistic: pd.DataFrame) -> ModelCallback:
    statistic_as_dict = statistic.to_dict()
    cities = statistic_as_dict["city"].values()
    means = statistic_as_dict["mean"].values()
    city_to_mean = {city: mean for city, mean in zip(cities, means)}

    def simple_model_callback(features: pd.DataFrame) -> ExpectedTime:
        city = city_from_features(features)
        mean = city_to_mean[city]
        return mean

    return simple_model_callback


@app.on_event("startup")
async def startup_event():
    statistic_for_simple_model = pd.read_csv("../models/statistic_for_simple_model.csv")
    simple_model_callback = simple_model_callback_from_statistic(
        statistic_for_simple_model
    )
    models_callbacks.simple = simple_model_callback

    xgboost_model = xgboost.XGBRegressor()
    xgboost_model.load_model("../models/xgboost.json")

    def xgboost_model_callback(features: pd.DataFrame) -> ExpectedTime:
        predict = xgboost_model.predict(features)
        return float(predict[0])

    models_callbacks.xgboost = xgboost_model_callback

    random_forest_model: RandomForestRegressor = joblib.load(
        "../models/random_forest.joblib"
    )

    def random_forest_model_callback(features: pd.DataFrame) -> ExpectedTime:
        predict = random_forest_model.predict(features)
        return float(predict[0])

    models_callbacks.random_forest = random_forest_model_callback


ModelType = Literal["simple", "xgboost", "random-forest"]


@app.post("/predict")
def predict(query: Query, model_type: ModelType):
    features = query.to_features()
    model_callback: ModelCallback
    if model_type == "simple":
        model_callback = models_callbacks.simple
    elif model_type == "xgboost":
        model_callback = models_callbacks.xgboost
    else:
        model_callback = models_callbacks.random_forest

    result = model_callback(features)

    return result
