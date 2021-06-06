import dataclasses
from dataclasses import dataclass
from typing import Callable, Literal

import joblib
import pandas as pd
import xgboost
from service.entities.city import city_from_features
from sklearn.ensemble import RandomForestRegressor

ExpectedTime = float

ModelCallback = Callable[[pd.DataFrame], ExpectedTime]


ModelName = Literal["simple", "xgboost", "random-forest"]


@dataclass
class Model:
    name: str
    callback: ModelCallback


def not_implemented_model_callback(features: pd.DataFrame) -> ExpectedTime:
    raise NotImplementedError()


@dataclass
class ModelNameToCallback:
    simple: ModelCallback = dataclasses.field(
        default_factory=lambda: not_implemented_model_callback
    )
    xgboost: ModelCallback = dataclasses.field(
        default_factory=lambda: not_implemented_model_callback
    )
    random_forest: ModelCallback = dataclasses.field(
        default_factory=lambda: not_implemented_model_callback
    )


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


def load_simple_model_callback() -> ModelCallback:
    statistic_for_simple_model = pd.read_csv("models/statistic_for_simple_model.csv")
    simple_model_callback = simple_model_callback_from_statistic(
        statistic_for_simple_model
    )
    return simple_model_callback


def load_xgboost_model_callback() -> ModelCallback:
    xgboost_model = xgboost.XGBRegressor()
    xgboost_model.load_model("models/xgboost.json")

    def xgboost_model_callback(features: pd.DataFrame) -> ExpectedTime:
        predict = xgboost_model.predict(features)
        return float(predict[0])

    return xgboost_model_callback


def load_random_forest_model_callback() -> ModelCallback:
    random_forest_model: RandomForestRegressor = joblib.load(
        "models/random_forest.joblib"
    )

    def random_forest_model_callback(features: pd.DataFrame) -> ExpectedTime:
        predict = random_forest_model.predict(features)
        return float(predict[0])

    return random_forest_model_callback
