import pandas as pd
import numpy as np


def ah_kong_priorities(params, persons, houses):
    '''
    0. Determine priorities
    0.1 Calculate metrics
    0.2 Budget planning
    '''
    focus = {'fengshui': 0.3, 'transport': 0.7}

    occupied = houses[houses.occupant.notnull()].groupby(['town'
                                                         ])['location'].count()
    empty = houses[houses.occupant.isnull()].groupby(['town'
                                                     ])['location'].count()
    occupancy_rate_by_town = occupied.combine(
        empty, func=(lambda x1, x2: x1 / (x1 + x2)))

    houses_count = houses['location'].count()
    mean_occupancy = occupancy_rate_by_town.mean()
    town_with_highest_occupancy = occupancy_rate_by_town.sort_values(
        ascending=False).index[0]

    if mean_occupancy > 0.8:
        # BOB THE BUILDER
        grid = 1
        amenities_increment = 0
        quantile = .3
        target_grid = town_with_highest_occupancy
        transport_discount = 1
    else:
        grid = 0
        amenities_increment = 1
        quantile = .3
        target_grid = town_with_highest_occupancy
        transport_discount = 0.8
    return grid, amenities_increment, quantile, target_grid, transport_discount


def ah_kong_intervention(params, persons, houses):
    priorities = ah_kong_priorities(params, persons, houses)
    '''
    1. Build houses
    1.1 Define town size
    1.2 Define new location to build town
    1.3 Append new houses into houses
    
    2. Improve amenities
    2.1 Identify 50% percentile of existing houses and increment amentities by a random number 
    2.2 Identify most densely populated towns and reduce transportation cost coefficient
    '''
    fengshui_mu, fengshui_sigma = params['fengshui_mu'], params[
        'fengshui_sigma']
    grid, amenities_increment, quantile, target_grid, transport_discount = priorities

    # 1. build houses

    if grid == 1:
        min_price = houses.market_price.min()
        land_plots = []
        for i in range(10):
            for j in range(10):
                if (i, j) not in houses.indexes:
                    land_plots.append((i, j))

        new_houses = {}
        (x, y) = land_plots[0]
        new_houses[(x, y)] = {
            "location": (x, y),  # also the key 
            "last_bought_price": np.random.normal(min_price, 50)[0],
            "status": "empty",  # "empty", "occupied", "selling" 
            "amenities": {
                "fengshui": np.random.normal(fengshui_mu, fengshui_sigma, 1)[0],
                #  'transport': 1
            },
            "occupant": np.NaN,
            "last_updated": 0
        }
        new_houses[(x,
                    y)]["market_price"] = new_houses[(x,
                                                      y)]["last_bought_price"]

        houses_append = pd.DataFrame.from_dict(new_houses, orient='index')
        houses = houses.append(houses_append, ignore_index=True)

    # 2.1 Improve amentities

    fengshui_series = pd.Series()
    for index, row in houses.iterrows():
        fengshui = pd.Series([row['amenities']['fengshui']])
        fengshui.index = [index]
        fengshui_series = fengshui_series.append(fengshui)

    for index, row in houses.iterrows():
        if row['amenities']['fengshui'] < quantile:
            row['amenities']['fengshui'] += amenities_increment

    print(fengshui_series.mean())
    # 2.2

    # for index, row in houses.iterrows():
    #     if row['location'] == target_grid:
    #         row['amenities']['transport'] *= transport_discount
