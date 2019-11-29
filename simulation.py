from modules.m_demographic import aging, birth, dying
from modules.m_transaction import gen_asks, gen_bids, match_ask_bid, update_market_price
from modules.m_government import ah_kong_intervention

import numpy as np


def simulate(params, persons, houses, ask_df, bid_df):
    aging(params, persons, houses)
    print('B01')
    birth(params, persons, houses)
    print('B02')
    dying(params, persons, houses)
    print('B03')
    persons, houses, ask_df = gen_asks(params, persons, houses, ask_df)
    print('B04')
    persons, houses, bid_df = gen_bids(params, persons, houses, ask_df, bid_df)
    print('B05')
    persons, houses, match_df = match_ask_bid(params, persons, houses, ask_df,
                                              bid_df)
    print('B06')
    persons, houses = update_market_price(params, persons, houses, match_df)
    # ah_kong_intervention(params, persons, houses)

    # hotfix as NaN row appears in houses
    print('B07')
    houses = drop_NaN_row(houses)
    print('B08')
    houses.index = houses.index.map(convert_to_tuple_int)
    print('B09')
    return persons, houses, ask_df, bid_df


def update_history(history, persons, houses, verbose=False):
    # history["popn_with_zero_house"].append(
    #     (persons.house_staying.values != persons.house_staying.values).sum())
    # history["popn_with_one_house"].append(
    #     (persons.house_selling.values != persons.house_selling.values).sum())
    # history["popn_with_two_house"].append(
    #     (persons.house_selling.values == persons.house_selling.values).sum())
    # history["average_wealth"].append(np.mean(persons["wealth"]))
    # history["total_houses_empty"].append((houses.status == "empty").sum())
    # history["total_houses_occupied"].append((houses.status == "occupied").sum())
    # history["total_houses_selling"].append((houses.status == "selling").sum())
    print('B10')
    history["mean_market_price"].append((houses.market_price).mean())
    print('B11')
    history["occupancy_rate"].append(houses.occupant.count() /
                                     houses.location.count())

    return None


def drop_NaN_row(df):
    if np.NaN in df.index:
        df = df.drop([np.NaN])
    return df


def convert_to_tuple_int(index):
    return (int(index[0]), int(index[1]))