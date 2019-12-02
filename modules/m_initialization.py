import secrets  # python 3.6 necessary
import random
import numpy as np
import pandas as pd  # we try not to depend on pandas, to better translate later?
from copy import deepcopy
from modules.m_demographic import generate_person


def initialize(params):

    INITIAL_PRICE, INTIAL_AMENITIES = params['INITIAL_PRICE'], params[
        'INTIAL_AMENITIES']
    CITY_X, CITY_Y = params['CITY_X'], params[
        'CITY_Y']
    persons, houses, ask_df, bid_df = None, None, None, None
    persons = {}
    for _ in range(10):
        persons[secrets.token_hex(4)] = generate_person(params)
    persons = pd.DataFrame.from_dict(persons, orient='index')

    persons['house_staying'] = persons['house_staying'].astype(object)
    persons['house_selling'] = persons['house_selling'].astype(object)

    houses = {}
    for x in range(10):
        for y in range(10):
            houses[(x, y)] = {
                "location": (x, y),  # also the key
                "last_bought_price": INITIAL_PRICE(),
                "status": "empty",  # "empty", "occupied", "selling"
                'amenities': INTIAL_AMENITIES(),  # UPDATE(weets, 191125)
                "occupant": np.NaN,
                "last_updated": 0,
                # update(weets,191202) -- euclidean dist
                "distance_to_city": ((x-CITY_X())**2+(y-CITY_Y())**2)**(0.5)
            }
            houses[(x, y)]["market_price"] = houses[(
                x, y)]["last_bought_price"]

    houses = pd.DataFrame.from_dict(houses, orient='index')

    ask_df = pd.DataFrame(
        columns=['location', 'occupant_id', 'amenities', 'distance_to_city',
                 'ask_price'])  # init empty ask_df with col
    bid_df = pd.DataFrame(columns=[
        'location', 'bidder_id', 'utility_to_buyer', 'max_bid_price',
        'bid_price'
    ])

    return persons, houses, ask_df, bid_df


def status_to_float(status):
    if status == "empty":
        return 0
    if status == "occupied":
        return 1
    if status == "selling":
        return 2
