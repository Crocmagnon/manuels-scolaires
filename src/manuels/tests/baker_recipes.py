import random

from model_bakery import seq
from model_bakery.recipe import Recipe


def random_bool():
    return random.choice([True, False])


book = Recipe(
    "Book",
    title=seq("book title "),
    field=seq("field "),
    authors=seq("author "),
    previously_acquired=random_bool,
    consumable=random_bool,
)

supply = Recipe(
    "SuppliesRequirement",
    field=seq("field "),
)
