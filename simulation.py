from modules.m_demographic import aging, birth, dying
from modules.m_transaction import gen_asks, gen_bids, match_ask_bid


def simulate(params, persons, houses, ask_df, bid_df):
    aging(params, persons, houses)
    birth(params, persons, houses)
    dying(params, persons, houses)
    ask_df = gen_asks(params, persons, houses, ask_df)
    bid_df = gen_bids(params, persons, houses, ask_df, bid_df)
    match_df = match_ask_bid(params, persons, houses, ask_df, bid_df)