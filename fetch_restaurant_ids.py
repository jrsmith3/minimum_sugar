# coding: utf-8

"""
Fetch Restaurant IDs
====================
Nutritionix identifies restaurants by a unique number, but from what I
can tell they do not list those numbers. This notebook contains code
which creates a mapping between the names of restaurants I frequent
and Nutritionix's restaurant ID. This mapping is written to a file
called `restaurant_ids.json`.
"""

import requests
import json
import os

# Load credential data from file
with open("credentials.json", "r") as f:
    credentials = json.load(f)





restaurant_names = ["McDonalds",
                    "Wendy's",
                    "Taco Bell",
                    "Qdoba",
                    "Chipotle",
                    "Five Guys",]
                    #"Costco",]

restaurant_ids = [fetch_restaurant_id(name, credentials) for name in restaurant_names]

with open("restaurant_ids.json", "w") as f:
    f.write(json.dumps(restaurant_ids, indent=4, separators=(',', ': ')))
