from typing import Literal, TypedDict, cast
import typing


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
