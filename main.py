from modules.m_initialization import initialize
from simulation import simulate

persons, houses, ask_df, bid_df = initialize()
simulate(persons, houses, ask_df, bid_df)

print(persons.head())
