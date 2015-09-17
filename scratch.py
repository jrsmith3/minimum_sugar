# coding: utf-8

import requests
import json
import os

def fetch_subset_menu_item_data(restaurant_id, credentials, offset=0):
    """
    Helper function to fetch a subset of a restaurant's menu item data
    
    Parameters
    ----------
    restaurant_id : str
        Nutritionix unique ID specifying restaurant
    credentials : dict
        Contains API credentials "appID" and "appKey"
    offset : int, optional
        Offset from which to request data
        
    Returns
    -------
    menu_item_data : dict
        Created from json returned by Nutritionix query
    """

    # Set base query URL
    query_url = u"https://api.nutritionix.com/v1_1/search"

    # Include API credentials in POST request
    payload = dict(credentials)
    # Use "filters" key to specify restaurant by ID
    payload["filters"] = {"brand_id": restaurant_id}
    # Use "offset" and "limit" to get different subsets of the total data
    payload["offset"] = offset
    payload["limit"] = 50
    # Request all data from database (according to the [master list](https://docs.google.com/a/nutritionix.com/spreadsheet/ccc?key=0AmQ7yz5GxBrvdFhtRUpPdjl3VWk2U0dvZENyUVNrWGc&usp=drive_web#gid=0))
    payload["fields"] = ["brand_name",
                         "item_name",
                         "brand_id",
                         "item_id",
                         "upc",
                         "item_type",
                         "item_description",
                         "nf_ingredient_statement",
                         "nf_water_grams",
                         "nf_calories",
                         "nf_calories_from_fat",
                         "nf_total_fat",
                         "nf_saturated_fat",
                         "nf_monounsaturated_fat",
                         "nf_polyunsaturated_fat",
                         "nf_trans_fatty_acid",
                         "nf_cholesterol",
                         "nf_sodium",
                         "nf_total_carbohydrate",
                         "nf_dietary_fiber",
                         "nf_sugars",
                         "nf_protein",
                         "nf_vitamin_a_iu",
                         "nf_vitamin_a_dv",
                         "nf_vitamin_c_mg",
                         "nf_vitamin_c_dv",
                         "nf_calcium_mg",
                         "nf_calcium_dv",
                         "nf_iron_mg",
                         "nf_iron_dv",
                         "nf_potassium",
                         "nf_refuse_pct",
                         "nf_servings_per_container",
                         "nf_serving_size_qty",
                         "nf_serving_size_unit",
                         "nf_serving_weight_grams",
                         "allergen_contains_milk",
                         "allergen_contains_eggs",
                         "allergen_contains_fish",
                         "allergen_contains_shellfish",
                         "allergen_contains_tree_nuts",
                         "allergen_contains_peanuts",
                         "allergen_contains_wheat",
                         "allergen_contains_soybeans",
                         "allergen_contains_gluten",
                         "images_front_full_url",
                         "updated_at",
                         "section_ids",]
    # Make request by sending payload as json
    r = requests.post(query_url, json=payload)
    
    return r.json()


def fetch_menu_item_data(restaurant_id, credentials):
    """
    Fetch data for all menu items from a specified restaurant

    Parameters
    ----------
    restaurant_id : str
        Nutritionix unique ID specifying restaurant
    credentials : dict
        Contains API credentials "appID" and "appKey"
        
    Returns
    -------
    menu_item_data : list
        All menu items and corresponding data
    """
    # Make first request to get some data and see how much data is left
    dat = fetch_subset_menu_item_data(restaurant_id, credentials)
    
    # Strip out just the nutrition data for the menu item by removing extra metadata
    menu_item_data = [itm["fields"] for itm in dat["hits"]]
    
    # Iterate if the menu has more than 50 items
    for indx in range(dat["total"]/50):
        offset = 50 * (indx + 1)
        dat = fetch_subset_menu_item_data(restaurant_id, credentials, offset=offset)
        menu_item_subset_data = [itm["fields"] for itm in dat["hits"]]
        menu_item_data.extend(menu_item_subset_data)
        
    return menu_item_data
