import numpy as np

params = {
    # demographic
    'INITIAL_AGE': lambda: 20,
    'DYING_PROB_FUNCTION': lambda age: 1. / (1. + np.exp(-(0.2 * (age - 50)))),
    'NUM_BORN': lambda: np.random.binomial(10, 0.5),

    # geographic
    'CITY_X': lambda: 5.3,
    'CITY_Y': lambda: 5.3,
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
    'PROBA_SELL': 0.8,
    'PROBA_BUY': 0.8,

    # plot
    'NUM_FRAMES': 20,
    'MILLISECS_PER_FRAME': 100,
}
