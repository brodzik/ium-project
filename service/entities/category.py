import typing
from typing import Literal, TypedDict, cast

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
