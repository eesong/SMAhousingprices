import numpy as np

params = {
    # demographic
    'INITIAL_AGE': lambda: 20,
    'DYING_PROB_FUNCTION': lambda age: 1. / (1. + np.exp(-(0.2 * (age - 50)))),
    'NUM_BORN': lambda: np.random.binomial(10, 0.5),

    # geographic
    'CITY_X': lambda: 9,
    'CITY_Y': lambda: 9,
    'PREFERRED_LOCATION_X': lambda: 9,
    'PREFERRED_LOCATION_Y': lambda: 9,

    # economic
    'INCOME': lambda: 10,
    'INITIAL_WEALTH': lambda: 100 + 100 * np.random.uniform(),

    # houses
    'INITIAL_PRICE': lambda: 100 + 100 * np.random.uniform(),
    'INTIAL_AMENITIES': lambda: np.random.uniform(),
    'IDIO_COEF': 0.2,
    'AMENITIES_COEF': 500,
    'LOC_COEF': 500,

    # transactions
    'PROBA_BUY': 0.8,
    'PROBA_SELL_NO_LOSS': 0.8,  # update(weets, 1911228)
    'PROBA_SELL_WITH_LOSS': 0.4,  # update(weets, 1911228)
    'CA_MULTIPLIER_FAIR': lambda: np.random.uniform(0.95, 1.05),
    'CA_MULTIPLIER_GOOD': lambda: np.random.uniform(1.05, 1.2),
    'CA_MULTIPLIER_BAD': lambda: np.random.uniform(0.75, 0.95),
    'PROBA_CA_GOOD': 0.025,
    'PROBA_CA_BAD': 0.1,

    # plot
    'NUM_FRAMES': 30,
    'MILLISECS_PER_FRAME': 100,
}
