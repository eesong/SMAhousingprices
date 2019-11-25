# # demographic
# migration_base_age = 20
# DEATH_RATE = 0.05  #deprecated? cant see where it was called
# death_coef = 0.2
# birth_n, birth_p = 10, 0.2

# # geographic
# city_x, city_y = 7, 9

# # economic
# income_mu, income_sigma = 10, 5
# wealth_mu, wealth_sigma = 300, 10

# # houses
# initialization_price_mu, initialization_price_sigma = 300, 10
# fengshui_mu, fengshui_sigma = 1, .1

# # transactions
# PROBA_SELL, PROBA_BUY = 0.4, 0.8

params = {
    # demographic
    'migration_base_age': 20,
    'DEATH_RATE': 0.05,  #deprecated? cant see where it was called
    'death_coef': 0.2,
    'birth_n': 10,
    'birth_p': 0.2,

    # geographic
    'city_x': 7,
    'city_y': 9,

    # economic
    'income_mu': 10,
    'income_sigma': 5,
    'wealth_mu': 300,
    'wealth_sigma': 10,

    # houses
    'initialization_price_mu': 300,
    'initialization_price_sigma': 10,
    'fengshui_mu': 1,
    'fengshui_sigma': .1,

    # transactions
    'PROBA_SELL': 0.4,
    'PROBA_BUY': 0.8,
}