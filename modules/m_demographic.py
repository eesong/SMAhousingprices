import secrets  # python 3.6 necessary
import random
import numpy as np
import pandas as pd  # we try not to depend on pandas, to better translate later?
from copy import deepcopy
from initialization_params import *


def aging(persons, houses, verbose=False):  # change this a function of age
    persons["age"] += 1
    persons["wealth"] += persons["income"]
    houses["last_updated"] += 1


def dying_prob_function(age):
    return 1. / (1. + np.exp(-(death_coef * (age - 50))))


def dying(persons, houses, verbose=False):  # change this a function of age
    persons_id_dead = []
    for person_id in persons.index:
        if np.random.uniform() < dying_prob_function(
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


def birth(persons, houses, verbose=False):
    born = np.random.binomial(birth_n, birth_p)
    for _ in range(born):
        persons.loc[secrets.token_hex(4)] = generate_person()


def generate_person():
    person = {
        "age": migration_base_age,
        "income": np.random.normal(income_mu, income_sigma, 1)[0],
        "wealth": np.random.normal(wealth_mu, wealth_sigma, 1)[0],
        "house_staying": np.NaN,
        "house_selling": np.NaN,
        "utility":
            0,  # WEETS: utility here is person's 'score'. Every decision person makes must immediately result in increase of 0 or more, never decrease.
        "idio": {
            "preferred_location": (np.random.normal(city_x, 0.1, 1)[0],
                                   np.random.normal(city_y, 0.1, 1)[0])
        }
    }
    return person