
# coding: utf-8

# # Scratchwork to develop histogram plotting functionality
# This ipynb is for the development of a function that takes restaurant menu data and returns a histogram.

# In[1]:

get_ipython().magic(u'matplotlib inline')

import json
import numpy as np
import matplotlib.pyplot as plt

with open("restaurant_menu_data.json", "r") as f:
    restaurant_menu_data = json.load(f)


# In[58]:

# Some helper functions
# =====================

def menu_data_keys(menu_data):
    """
    Helper function returning list of nutrition data keys
    
    Its a pain to un-nest a menu data dict to determine the exact key for the desired data.
    This method returns the list so the user doesn't have to manually un-nest the data.
    
    Parameters
    ----------
    menu_data : dict
        Restaurant menu data.

    Returns
    -------
    data_keys : list
        Keys containing menu data
    """
    keys = menu_data["menu"][0].keys()
    
    return keys


def extract_variable(menu_data, param):
    """
    Extract variable data from menu data of specified parameter

    Parameters
    ----------
    menu_data : dict
        Restaurant menu data
    param : str
        Parameter to extract.
        This value should correspond to a key of the menu_data["menu"] dict who's value is numerical.
        
    Returns
    -------
    variable : list
        Values corresponding to `param`.
    """
    variable = [menu_item[param] for menu_item in menu_data["menu"]]
    
    return variable


def menu_items_max(menu_data, param):
    """
    Subset of menu items with maximum value of specified parameter
    
    Parameters
    ----------
    menu_data : dict
        Restaurant menu data
    param : str
        Parameter on which to return maximum.
        This value should correspond to a key of the menu_data["menu"] dict who's value is numerical.
        
    Returns
    -------
    menu_items : list
        List of menu items with maximum value of `param`.
        Note that if only one menu item has maximum `param`, this list will be one element long.
        On the other hand, there's no guarantee that only a single item has max `param`.
    """
    max_variable = max(extract_variable(menu_data, param))
    
    menu_items = [menu_item for menu_item in menu_data["menu"] if menu_item[param] == max_variable]
    
    return menu_items


def menu_items_min(menu_data, param):
    """
    Subset of menu items with minimum value of specified parameter
    
    Parameters
    ----------
    menu_data : dict
        Restaurant menu data
    param : str
        Parameter on which to return minimum.
        This value should correspond to a key of the menu_data["menu"] dict who's value is numerical.
        
    Returns
    -------
    menu_items : list
        List of menu items with minimum value of `param`.
        Note that if only one menu item has minimum `param`, this list will be one element long.
        On the other hand, there's no guarantee that only a single item has min `param`.
    """
    min_variable = min(extract_variable(menu_data, param))
    
    menu_items = [menu_item for menu_item in menu_data["menu"] if menu_item[param] == min_variable]
    
    return menu_items


# In[3]:

def menu_histogram(menu_data, param, param_name=None):
    """
    Histogram of a specified parameter (e.g. sugar) for a given menu.
    
    Parameters
    ----------
    menu_data : dict
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
    
    hist, bins = np.histogram(variable, bins=20)
    center = (bins[:-1] + bins[1:]) / 2
    width = 0.7 * (bins[1] - bins[0])
    
    fig = plt.figure()
    plt.bar(center, hist, align="center", width=width)
    plt.title(menu_data["name"])
    plt.ylabel("Number of menu items")
    if param_name:
        plt.xlabel(param_name)
    else:
        plt.xlabel(param)
        
    return fig


# ## Visualization: Histograms of menu items vs. sugar content

# In[80]:

param = "nf_sugars"

# First, find the menu item with the maximum amount of sugar
menu_items_max_sugar = [menu_items_max(menu_data, param) for menu_data in restaurant_menu_data]
sugar_values = [menu_item[0][param] for menu_item in menu_items_max_sugar]
max_sugar_value = max(sugar_values)

# for menu_data in restaurant_menu_data:
#     fig = menu_histogram(menu_data, param, "Sugar [g]")
#     fig.axes[0].set_xlim([0, max_sugar_value])
#     plt.show()


# ## Visualization: Histograms of menu items vs. calories

# In[81]:

param = "nf_calories"

# First, find the menu item with the maximum amount of calories
menu_items_max_calories = [menu_items_max(menu_data, param) for menu_data in restaurant_menu_data]
calories_values = [menu_item[0][param] for menu_item in menu_items_max_calories]
max_calories_value = max(calories_values)

# for menu_data in restaurant_menu_data:
#     fig = menu_histogram(menu_data, param, "Calories")
#     fig.axes[0].set_xlim([0, max_calories_value])
#     plt.show()


# In[ ]:



