from modules.m_demographic import aging, birth, dying
from modules.m_transaction import gen_asks, gen_bids, match_ask_bid


def simulate(persons, houses, ask_df, bid_df):
    aging(persons, houses)
    birth(persons, houses)
    dying(persons, houses)
    ask_df = gen_asks(persons, houses, ask_df)
    bid_df = gen_bids(persons, houses, ask_df, bid_df)
    match_df = match_ask_bid(persons, houses, ask_df, bid_df)