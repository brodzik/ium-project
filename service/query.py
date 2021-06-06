import dataclasses
from datetime import datetime

import pandas as pd
from pydantic import BaseModel
from typing_extensions import TypedDict

from service.entities.category import Category, code_category
from service.entities.city import code_city
from service.entities.delivery_company import (DeliveryCompany,
                                               code_delivery_compnay)
from service.entities.purchase_datetime import CodedPurchaseDateTime


class Query(BaseModel):
    category: Category
    city: str
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


Result = TypedDict("Result", {"360": float, "516": int, "620": str})
