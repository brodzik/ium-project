import dataclasses

import random
from datetime import datetime
from typing import List, Literal

import joblib
import pandas as pd
import xgboost
from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.ensemble import RandomForestRegressor

from entities.category import Category, code_category
from entities.city import City, code_city
from entities.delivery_company import DeliveryCompany, code_delivery_compnay
from entities.purchase_datetime import CodedPurchaseDateTime
from models import (
    ModelNameToCallback,
    ModelCallback,
    Model,
    load_simple_model_callback,
    load_xgboost_model_callback,
    load_random_forest_model_callback,
    ModelName,
)

app = FastAPI()


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


model_name_to_callback = ModelNameToCallback()

models: List[Model] = []


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
    features = query.to_features()
    model_callback: ModelCallback
    if model_type == "simple":
        model_callback = model_name_to_callback.simple
    elif model_type == "xgboost":
        model_callback = model_name_to_callback.xgboost
    else:
        model_callback = model_name_to_callback.random_forest

    expected_time = model_callback(features)

    return expected_time


@app.post("/ab-test")
def ab_test(query: Query):
    features = query.to_features()

    chosed_model = random.choice(models)
    expected_time = chosed_model.callback(features)

    return {"model_type": chosed_model.name, "expected_time": expected_time}
