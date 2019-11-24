import secrets  # python 3.6 necessary
import random
import numpy as np
import pandas as pd  # we try not to depend on pandas, to better translate later?
from copy import deepcopy
from initialization_params import *


def gen_asks(persons, houses, ask_df):
    ''' phase 2 bid-ask
    1. Refresh ask_df pd.DataFrame()
    2. Add empty houses from `houses` to ask_df
    3. Add more listings from persons who can and want to sell houses
    '''
    ask_df_columns = ask_df.columns.to_list(
    )  # ['house_pos','current_occupant_id','amenities', 'ask_price']

    # 1. Refresh ask_df pd.DataFrame()
    ask_df.drop(ask_df.index, inplace=True)  # drops all rows

    # 2. Add empty houses from `houses` to ask_df
    empty_houses = houses[houses['status'] == 'empty']

    ## 2.1 Rename, reorder into ask_df column mold
    ## ask_df column order: ['house_pos','current_occupant_id','amenities', 'ask_price']
    empty_houses_listing = empty_houses.rename(columns={
        'occupant': 'occupant_id',
        'last_bought_price': 'ask_price',
    })
    empty_houses_listing = empty_houses_listing[ask_df_columns]  # reorder

    ask_df = ask_df.append(
        empty_houses_listing, ignore_index=True)  # TODO: optimise

    # 3. Add more listings from `persons` who can and want to sell houses
    ## 3.1 get sub df of persons who have a second house to sell
    COND_have_house_selling = persons['house_selling'] != None
    potential_sellers = persons[COND_have_house_selling]  # a persons sub df

    ## 3.2 Get sellable houses that have market price >= cost price
    potential_house_selling_loc = potential_sellers['house_selling']
    potential_house_selling = houses[houses['location'].isin(
        potential_house_selling_loc.values)]
    COND_market_greater_or_equal_cost_price = potential_house_selling[
        'market_price'] >= potential_house_selling['last_bought_price']
    no_loss_house_selling = potential_house_selling[
        COND_market_greater_or_equal_cost_price]  # a houses subdf

    ## 3.3 Random decide if want to sell or not
    COND_want_sell = no_loss_house_selling['status'].apply(
        lambda runif: np.random.uniform()) <= PROBA_SELL
    want_sell_houses = no_loss_house_selling[COND_want_sell]
    want_sell_houses_loc = want_sell_houses['location']
    actual_house_selling = potential_house_selling[
        potential_house_selling['location'].isin(want_sell_houses_loc.values)]

    ## 3.4 Rename, reorder actual_house_selling into ask_df column mold
    ## ask_df column order: ['house_pos','current_occupant_id','amenities', 'ask_price']
    main_listing = actual_house_selling.rename(columns={
        'market_price': 'ask_price',
        'occupant': 'occupant_id'
    })
    main_listing = main_listing[ask_df_columns]

    ask_df = ask_df.append(main_listing, ignore_index=True)

    # strangely, there's a row with nan value in location appearing
    # this chunk fixes that
    if any(ask_df['location'].apply(lambda loc: type(loc) != tuple)):
        # print('Missing location in ask_df, applying fix')
        ori_len = len(ask_df)
        ask_df = ask_df[~ask_df['location'].isna()]
        # print('Change in len', len(ask_df)-ori_len)
    return ask_df


# test run
# gen_asks()
# ask_df.sample(10)


def gen_bids(persons, houses, ask_df, bid_df):
    ''' phase 2 bid-ask
    1. Refresh bid_df pd.DataFrame()
    2. Generate subdf of persons who can and want to buy houses
    3. For each eligible person, iterate over ask, grow person_bids list of dict
    4. Merge 
    '''
    bid_df_columns = bid_df.columns.to_list(
    )  # ['location', 'bidder_id', 'utility', 'bid_price']

    # 1. Refresh bid_df pd.DataFrame()
    bid_df.drop(bid_df.index, inplace=True)  # drops all rows

    # 2. Screen viable bidders
    ## 2.1 Does not own a second house (can have 1 or 0 houses)
    COND_only_one_house = persons['house_selling'].isna(
    )  # NOTE: do not use `persons['house_selling'] == None` to check
    potential_buyers = persons[COND_only_one_house]

    ## 2.2 Random decide if want to seek or not
    COND_want_buy = potential_buyers['age'].apply(
        lambda runif: np.random.uniform()) <= PROBA_BUY
    eligible_and_seeking_buyers = potential_buyers[
        COND_want_buy]  # these are the eligible people who want to buy houses

    # 3. Each eligible buyer makes a bid for each house on sale
    list_of_bid_sets = []  # to be populated with df corr. to each person's bids

    ## 3.1 Define helper fn
    def _gen_bid_price(listing_row):
        max_bid_price = listing_row['max_bid_price']
        ask_price = listing_row['ask_price']
        if max_bid_price >= ask_price:
            surplus = max_bid_price - ask_price
            return ask_price + np.random.uniform() * surplus
        else:
            return max_bid_price

    ## 3.2 Iterate over buyers
    for idx, buyer in eligible_and_seeking_buyers.iterrows():
        buyer_view_of_ask_df = ask_df.copy()

        ###  3.2.1 Calculate each listing's utility to buyer
        buyer_view_of_ask_df['bidder_id'] = idx
        buyer_view_of_ask_df['utility_to_buyer'] = utility_function_vectorised(
            buyer, buyer_view_of_ask_df)
        # NOTE: utility_to_buyer is partial -- it only consider's a houses's general and locational utility and buyer idio

        ### 3.2.2 Calculate bid_price
        buyer_view_of_ask_df['max_bid_price'] = buyer['wealth'] - buyer[
            'utility'] + buyer_view_of_ask_df[
                'utility_to_buyer']  # TODO: double check if this is a good rule
        # NOTE: WEETS suspects above formula may be wrong since it does not compare the differential in utility DUE TO HOUSE only
        # test: what if utility to buyer is negative? Would you still bid (and spend money)?
        buyer_view_of_ask_df['max_bid_price'] = buyer_view_of_ask_df[
            'max_bid_price'].apply(lambda mbp: min(mbp, buyer['wealth']))
        # mbp must be capped at buyer's wealth
        buyer_view_of_ask_df['max_bid_price'] = buyer_view_of_ask_df[
            'max_bid_price'].apply(lambda mbp: max(0, mbp))
        # mbp must be non-negative

        bid_price = buyer_view_of_ask_df.apply(_gen_bid_price, axis=1)
        buyer_view_of_ask_df['bid_price'] = bid_price

        ### 3.2.3 Append specific columns of buyer_view_of_ask_df to list_of_bid_sets
        select_columns = [
            'location', 'bidder_id', 'utility_to_buyer', 'max_bid_price',
            'bid_price'
        ]
        list_of_bid_sets.append(buyer_view_of_ask_df[select_columns])

    # 4. Concatenate list of dataframes into one dataframe
    if list_of_bid_sets:  # possible that no bids take place
        bid_df = pd.concat(list_of_bid_sets)
    return bid_df


# bid_df = gen_bids()
# # print(bid_df['bidder_id'].nunique())
# bid_df.head()


def match_ask_bid(persons, houses, ask_df, bid_df):
    '''
    1. Create a container list to store dicts of info relating to bidding for each listing
    2. Iterate over listings in ask_df, find best bid - is successful match
    3. For each successful match
        1. Create and append dict of info relating to bids for the listing
        2. Remove all bids for same listing
        3. Remove all other bids by same bidder
        4. Update asker and bidder
    4. For each unsuccessful match
        1. Create and append dict of info relating to bids for the listing
        2. Remove all bids for same listing
    5. Make match_df
    '''
    # 1. Create a container list to store dicts of info relating to bidding for each listing
    list_of_matches = []  # contains info on winning bid

    # 2. Iterate over listings in ask_df, find best bid - is successful match
    for idx, listing in ask_df.iterrows():
        match_info_dict = {}  # stats for each listing match

        ## 2.1 Get general data
        listing_loc = listing['location']
        match_info_dict['location'] = listing_loc

        match_info_dict['ask_price'] = listing['ask_price']

        relevant_bids = bid_df[bid_df['location'] == listing_loc]
        match_info_dict['num_bids'] = len(relevant_bids)  # expect 0 or more

        highest_bid_value = relevant_bids['bid_price'].max()
        match_info_dict['highest_bid_value'] = highest_bid_value

        match_info_dict['mean_bid_value'] = relevant_bids['bid_price'].mean()

        # 3. Found winning bid(s)
        if highest_bid_value >= listing[
                'ask_price']:  # there exists a successful match

            ## 3.1 Create and append dict of info relating to bids for the listing
            ### 3.1.1 Check for ties among highest bid
            highest_bids = relevant_bids[relevant_bids['bid_price'] ==
                                         highest_bid_value]
            num_highest_bid = len(
                highest_bids)  # expect at least 1, rarely more
            assert num_highest_bid >= 1, 'ERR: num_highest_bid must be >= 1'

            ### 3.1.2 Get the winner
            winning_bid = highest_bids.sample(
                1)  # tie-breaker: randomly choose one highest bidder to win

            winning_bidder_id = winning_bid['bidder_id'].iloc[0]
            match_info_dict['winning_bidder_id'] = winning_bidder_id
            match_info_dict[
                'winning_bid_value'] = highest_bid_value  # obviously; stated explicitly as highest_bid_value may not win for the `else` case

            ### 3.1.3 Append match info
            list_of_matches.append(match_info_dict)

            ## 3.2 Remove all corresponding bids, 3.3 Remove all other bids by same bidder
            bid_df = bid_df.drop(relevant_bids.index, axis=0)
            bid_df = bid_df[~(bid_df['bidder_id'] == winning_bidder_id)]

            ## 3.4 Update asker and bidder
            asker_id = listing['occupant_id']

            ### 3.4.1 Update asker
            if type(asker_id) is str:  # if str, then not empty house
                persons['wealth'].loc[asker_id] += highest_bid_value
                persons['house_selling'].iloc[
                    asker_id] = np.NaN  # potential problem here?
                # TODO: check where to update 'utility' (person's simulation score) -- here or elsewhere?
                # ENSURE: asker['utility'] increase or stay the same

            ### 3.4.2 Update bidder
            winning_bidder = persons.loc[winning_bidder_id]
            persons['wealth'].loc[winning_bidder_id] -= highest_bid_value

            #### Additional updates for bidder if second house buyer
            if type(
                    winning_bidder['house_staying']
            ) is tuple:  # first house exists, buyer is buying second house
                persons['house_selling'].loc[winning_bidder_id] = winning_bidder[
                    'house_staying']  # set current house_staying to be house_selling
                houses['status'].loc[winning_bidder[
                    'house_staying']] = 'selling'  # set that same current house to 'selling' status
            persons['house_staying'].loc[winning_bidder_id] = listing_loc
            # TODO: check where to update 'utility' (person's simulation score) -- here or elsewhere?
            # ENSURE: asker['utility'] increase or stay the same

            ### 3.4.3 Update house
            houses['last_bought_price'].loc[listing_loc] = highest_bid_value
            houses['status'].loc[listing_loc] = 'occupied'
            # Note: for second house buyers, their first house's status has already been updated
            houses['occupant'].loc[listing_loc] = winning_bidder_id
            houses['last_updated'].loc[listing_loc] = 0
            # TODO: update houses['market_price'] at the end of each time step, somewhere else perhaps

        # 4. No successful match
        else:
            ## 4.1 Create and append dict of info relating to bids for the listing
            match_info_dict['winning_bidder_id'] = np.NaN
            match_info_dict['winning_bid_value'] = np.NaN
            list_of_matches.append(match_info_dict)

            ## 4.2 Remove all bids for same listing
            bid_df = bid_df.drop(relevant_bids.index, axis=0)

    # 5. Make match_df
    match_df = pd.DataFrame(list_of_matches)
    return match_df


# gen_asks()
# bid_df = gen_bids()
# match_df = match_ask_bid() # Note: changes bid_df each time it is called
# match_df.head(10)


def utility_general(house):
    '''
    Every person considers a house to have a certain utility.
    This is not based on personal perferences.
    '''
    utility_due_to_location = 2 / (1 + (house["location"][0] - 5.3)**2 +
                                   (house["location"][1] - 5.3)**2)
    return utility_due_to_location + house["amenities"]["fengshui"]


def utility_function(person, house):
    '''
    A person considers each house to have a different utility.
    This assigns an additional utility of each house based on personal preferences.
    '''
    utility_due_to_person = 1 / (
        1 +
        (house["location"][0] - person["idio"]["preferred_location"][0])**2 +
        (house["location"][1] - person["idio"]["preferred_location"][1])**2)
    return utility_general(house) + utility_due_to_person


### Weets' Vectorised Utility Functions (works with pd.Series) ###
# mere translation of above functions
# its quite hardcoded so not comfortable rofl
#
def utility_general_vectorised(house):
    '''
    Every person considers a house to have a certain utility.
    This is not based on personal perferences.
    '''
    utility_due_to_location = 2 / (
        1 + (house["location"].apply(lambda tup: tup[0]) - 5.3)**2 +
        (house["location"].apply(lambda tup: tup[1]) - 5.3)**2)
    return utility_due_to_location + house["amenities"].apply(
        lambda amen_dt: amen_dt["fengshui"])


def utility_function_vectorised(person, house):
    '''
    A person considers each house to have a different utility.
    This assigns an additional utility of each house based on personal preferences.
    Input
        person: a dict or pandas df row
    '''
    # print(house["location"])
    # print(house["location"].apply(lambda tup: tup[0]))

    xloc = (
        house["location"].apply(lambda tup: tup[0]) -
        person["idio"]["preferred_location"][0])
    yloc = (
        house["location"].apply(lambda tup: tup[1]) -
        person["idio"]["preferred_location"][1])

    utility_due_to_person = 1 / (1 + xloc**2 + yloc**2)
    return utility_general_vectorised(house) + utility_due_to_person