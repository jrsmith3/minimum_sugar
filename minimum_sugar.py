# coding: utf-8

import requests
import json
import os
import numpy as np
import matplotlib.pyplot as plt


# Functions for getting data from Nutritionix
# ===========================================
def fetch_restaurant_id(restaurant_name, credentials):
    """
    Fetch Nutritionix restaurant ID for a given restaurant name
    
    Parameters
    ----------
    restaurant_name : str
    credentials : dict
        Contains API credentials "appID" and "appKey"
        
    Returns
    -------
    restaurant_id : dict
        Contains fields "name" and "id"
    """
    # Set base query URL
    query_url = u"https://api.nutritionix.com/v1_1/brand/search"
    
    payload = dict(credentials)
    payload["query"] = restaurant_name
    # "type" tells Nutritionix to return only restaurants (not food mfrs)
    payload["type"] = 1
    # "limit" results to a single result, no "offset"
    payload["limit"] = 1
    payload["offset"] = 0
    
    r = requests.get(query_url, payload)

    # Exception should be raised if r.status_code is not 200.
    
    # Break out the data I want.
    # The results are nested in various dicts and lists.
    # Consider the result of searching for "taco bell" as an example:
    #   {u'hits': [{u'_id': u'513fbc1283aa2dc80c000020',
    #      u'_index': u'f762ef22-e660-434f-9071-a10ea6691c27',
    #      u'_score': 9.773642,
    #      u'_type': u'brand',
    #      u'fields': {u'_id': u'513fbc1283aa2dc80c000020',
    #       u'name': u'Taco Bell',
    #       u'type': 1,
    #       u'website': None}}],
    #    u'max_score': 9.773642,
    #    u'total': 12}
    #
    # After converting Nutritionix's response to a dict, directly extract the 
    # desired data at the expense of clarity.
    dat = r.json()
    hit = dat["hits"][0]["fields"]
    
    # Soooo ugly
    restaurant_id = {"name": hit["name"],
                     "id": hit["_id"]}
    
    return restaurant_id


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


# Functions for handling data once its downloaded
# ===============================================
def filter_menu_items(menu_data, param, value, negate=False):
    """
    Sublist of menu items matching target query

    Parameters
    ----------
    menu_data : list
        Restaurant menu data.
    param : str
        Parameter to extract.
    value : str
        Query against which parameter values will be evaluated.
    negate : bool
        If `False`, return all menu items matching query. 
        If `True`, return all menu items not matching query (inverse).

    Returns
    -------
    menu_subdata : list
        List of items matching query.
    """

    # Probably a better way to do this.
    if negate:
        menu_subdata = [menu_item for menu_item in menu_data if menu_item[param] != value]
    else:
        menu_subdata = [menu_item for menu_item in menu_data if menu_item[param] == value]

    return menu_subdata


def extract_variable(menu_data, param):
    """
    Extract variable data from menu data of specified parameter

    Parameters
    ----------
    menu_data : list
        Restaurant menu data
    param : str
        Parameter to extract.
        This value should correspond to a key of the menu_data["menu"] dict who's value is numerical.
        
    Returns
    -------
    variable : list
        Values corresponding to `param`.
    """
    variable = [menu_item[param] for menu_item in menu_data]
    
    return variable


# Functions for visualization and reporting
# =========================================
def print_max_sugar_menu_item(menu_data, brand_name):
    """
    Print sugar content and menu item name containing max sugar
    """
    restaurant_menu_items = filter_menu_items(menu_data, "brand_name", brand_name)
    restaurant_entree_items = filter_menu_items(restaurant_menu_items, "menu_category", "entree")
    max_sugar = max(extract_variable(restaurant_entree_items, "nf_sugars"))

    print "Max sugar:", max_sugar
    menu_items = filter_menu_items(restaurant_entree_items, "nf_sugars", max_sugar)
    for menu_item in menu_items:
        print "Iten name:", menu_item["item_name"]


def print_low_sugar_calorie_report(menu_data, brand_name):
    """
    Print report on low sugar items
    """
    entree_items = filter_menu_items(menu_data, "menu_category", "entree")
    restaurant_entree_items = filter_menu_items(entree_items, "brand_name", brand_name)
    low_sugar_menu_items = [menu_item for menu_item in restaurant_entree_items if menu_item["nf_sugars"] < 3]
    calories = list(set(extract_variable(low_sugar_menu_items, "nf_calories")))
    calories.sort(reverse=True)

    items = []

    for calorie in calories:
        items.extend(filter_menu_items(low_sugar_menu_items, "nf_calories", calorie))

    print brand_name
    print "=" * len(brand_name)
    for item in items:
        print item["item_name"] + ":", str(item["nf_calories"]) + "cal,", str(item["nf_sugars"]) + "g sugar"


def menu_histogram(menu_data, param, x_max=None, title=None, param_name=None, fig=None, **kwargs):
    """
    Histogram of a specified parameter (e.g. sugar) for a given menu.
    
    Parameters
    ----------
    menu_data : list
        Restaurant menu data
    param : str
        Parameter on which to create the histogram. 
        This value should correspond to a key of the menu_data["menu"] dict who's value is numerical.
    param_name : str, optional
        Human-readable name describing `param`.
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure displaying histogram data
        
    Notes
    -----
    Histogram plotting was taken from [unutbu's solution on SO](http://stackoverflow.com/a/5328669).
    """
    variable = extract_variable(menu_data, param)

    if not x_max:
        x_max = max(variable)

    bins = np.linspace(0, x_max, 20)

    if not fig:
        fig = plt.figure()

    plt.hist(variable, bins, **kwargs)
    plt.ylabel("Number of menu items")

    if title:
        plt.title(title)
        
    if param_name:
        plt.xlabel(param_name)
    else:
        plt.xlabel(param)
        
    return fig
