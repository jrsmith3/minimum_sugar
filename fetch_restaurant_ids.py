
# coding: utf-8

# # Fetch Restaurant IDs
# Nutritionix identifies restaurants by a unique number, but from what I can tell they do not list those numbers. This notebook contains code which creates a mapping between the names of restaurants I frequent and Nutritionix's restaurant ID. This mapping is written to a file called `restaurant_ids.json`.

# In[1]:

import requests
import json
import os

# Load credential data from file
with open("credentials.json", "r") as f:
    credentials = json.load(f)


# In[23]:

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


# In[28]:

restaurant_names = ["McDonalds",
                    "Wendy's",
                    "Taco Bell",
                    "Qdoba",
                    "Chipotle",
                    "Five Guys",]
                    #"Costco",]

restaurant_ids = [fetch_restaurant_id(name, credentials) for name in restaurant_names]


# In[34]:

with open("restaurant_ids.json", "w") as f:
    f.write(json.dumps(restaurant_ids, indent=4, separators=(',', ': ')))


# In[ ]:



