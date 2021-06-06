import dataclasses
import random
from datetime import datetime
from typing import List
import typing

import pandas as pd
from service.entities.category import Category, code_category
from service.entities.city import City, code_city
from service.entities.delivery_company import DeliveryCompany, code_delivery_compnay
from service.entities.purchase_datetime import CodedPurchaseDateTime
from fastapi import FastAPI
from pydantic import BaseModel

from .models import (
    Model,
    ModelCallback,
    ModelName,
    ModelNameToCallback,
    load_random_forest_model_callback,
    load_simple_model_callback,
    load_xgboost_model_callback,
)

app = FastAPI()

model_name_to_callback = ModelNameToCallback()
models: List[Model] = []


class Query(BaseModel):
    category: Category
    city: City
    price: float
    purchase: datetime

    def to_features(self, delivery_company: DeliveryCompany) -> pd.DataFrame:
        coded_category = code_category(self.category)
        coded_city = code_city(self.city)
        coded_delivery_company = code_delivery_compnay(delivery_company)
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


@app.on_event("startup")
async def startup_event():
    model_name_to_callback.simple = load_simple_model_callback()
    model_name_to_callback.xgboost = load_xgboost_model_callback()
    model_name_to_callback.random_forest = load_random_forest_model_callback()

    models.append(Model(name="simple", callback=model_name_to_callback.simple))
    models.append(Model(name="xgboost", callback=model_name_to_callback.xgboost))
    models.append(
        Model(name="random_forest", callback=model_name_to_callback.random_forest)
    )


@app.post("/predict")
def predict(query: Query, model_type: ModelName):
    delivery_company_to_features = {
        delivery_company: query.to_features(delivery_company)
        for delivery_company in typing.get_args(DeliveryCompany)
    }

    model_callback: ModelCallback
    if model_type == "simple":
        model_callback = model_name_to_callback.simple
    elif model_type == "xgboost":
        model_callback = model_name_to_callback.xgboost
    else:
        model_callback = model_name_to_callback.random_forest

    delivery_company_to_expected_time = {
        delivery_company: model_callback(delivery_company_to_features[delivery_company])
        for delivery_company in typing.get_args(DeliveryCompany)
    }

    return delivery_company_to_expected_time


@app.post("/ab-test-debug")
def ab_test_debug(query: Query):
    delivery_company_to_features = {
        delivery_company: query.to_features(delivery_company)
        for delivery_company in typing.get_args(DeliveryCompany)
    }

    chosed_model = random.choice(models)
    delivery_company_to_expected_time = {
        delivery_company: chosed_model.callback(
            delivery_company_to_features[delivery_company]
        )
        for delivery_company in typing.get_args(DeliveryCompany)
    }

    return {
        "model_type": chosed_model.name,
        "delivery_company_to_expected_time": delivery_company_to_expected_time,
    }


@app.post("/ab-test")
def ab_test(query: Query):
    delivery_company_to_features = {
        delivery_company: query.to_features(delivery_company)
        for delivery_company in typing.get_args(DeliveryCompany)
    }

    chosed_model = random.choice(models)
    delivery_company_to_expected_time = {
        delivery_company: chosed_model.callback(
            delivery_company_to_features[delivery_company]
        )
        for delivery_company in typing.get_args(DeliveryCompany)
    }

    return delivery_company_to_expected_time
