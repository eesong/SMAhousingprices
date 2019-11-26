import secrets  # python 3.6 necessary
import random
import numpy as np
import pandas as pd  # we try not to depend on pandas, to better translate later?
from copy import deepcopy


def aging(params, persons, houses,
          verbose=False):  # change this a function of age
    persons["age"] += 1
    persons["wealth"] += persons["income"]
    houses["last_updated"] += 1


def dying(params, persons, houses,
          verbose=False):  # change this a function of age
    DYING_PROB_FUNCTION = params['DYING_PROB_FUNCTION']

    persons_id_dead = []
    for person_id in persons.index:
        if np.random.uniform() < DYING_PROB_FUNCTION(
                persons.loc[person_id, "age"]):
            if verbose:
                print(person_id, " died")
            dead_person = persons.loc[person_id]
            if dead_person["house_staying"] != None:
                if verbose:
                    print("vacated ", dead_person["house_staying"])
                houses.loc[dead_person["house_staying"], "status"] = "empty"
                houses.loc[dead_person["house_staying"], "occupant"] = None
                houses.loc[dead_person["house_selling"], "status"] = "empty"
                houses.loc[dead_person["house_selling"], "occupant"] = None
            persons_id_dead.append(person_id)
    persons.drop(persons_id_dead, inplace=True)


def birth(params, persons, houses, verbose=False):
    NUM_BORN = params['NUM_BORN']

    born = NUM_BORN()
    for _ in range(born):
        persons.loc[secrets.token_hex(4)] = generate_person(params)


def generate_person(params):
    INITIAL_AGE = params['INITIAL_AGE']
    INCOME = params['INCOME']
    INITIAL_WEALTH = params['INITIAL_WEALTH']
    PREFERRED_LOCATION_X, PREFERRED_LOCATION_Y = params[
        'PREFERRED_LOCATION_X'], params['PREFERRED_LOCATION_Y']

    person = {
        "age": INITIAL_AGE(),
        "income": INCOME(),
        "wealth": INITIAL_WEALTH(),
        "house_staying": np.NaN,
        "house_selling": np.NaN,
        "utility":
            0,  # WEETS: utility here is the utility of the current staying house to the person. It will be swapped for the utility of the new house if this person buys new house.
        # the true 'score' of a person is wealth + utility
        'preferred_location_x': PREFERRED_LOCATION_X(),  # UPDATE(weets, 191125)
        'preferred_location_y':
            PREFERRED_LOCATION_Y()  # UPDATE(weets, 191125)
    }
    return person