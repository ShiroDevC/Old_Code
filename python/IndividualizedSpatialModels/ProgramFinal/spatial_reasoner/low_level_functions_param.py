'''Module for low level helper functions.
Created on 16.07.2018

@author: Christian Breu <breuch@web.de>, Julia Mertesdorf<julia.mertesdorf@web.de>
'''

PRINT_MODEL = False # zwischenloesung

import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d


def invert_relation(relation):
    """inverts all values of numbers in the given relation 3-tuple
    """
    return (relation[0] *-1, relation[1] *-1, relation[2] *-1)

def list_equal(list1, list2):
    """Compares two given lists. If one item in the two lists is different,
    the function returns false. If all items ate equal, returns True.
    """
    for i, item in enumerate(list1):
        if item != list2[i]:
            return False
    return True

# ---------------------------- FUNCTIONS FOR FINDING ITEMS IN MODELS ------------------------------

# USED BY BOTH MODELS (CAUTION! TEMPORAL VERSION HAS 2 LINES MORE; SEE ABOVE!)

def find_first_item(item, models):
    """
    new version of find item with dictionary (replaces find_first_item, finders, finds,
    eq_or_inc and check_member of v.1)
    Searches an item in all the models given as a dictionary.
    Iterates over all models and checks if the item is in one of them.
    Function works for both when the value is a list of items or when the
    value itself is a single item.
    Returns a list with a tuple of the coordinates of the item and the model
    where the item was found in. if it couldn´t be found, returns None.
    """
    if PRINT_MODEL:
        print("Function call - find_first_item", item, "in models", models)
    if not models:
        return None
    if not isinstance(models, list):
        models = [models]
    for model in models:
        #need to check if the model is None!!
        if model is not None:
            #checks if the item is in the current model, and if yes, where
            coordinates = [key for key, val in model.items() if item in val]
            if coordinates == []:
                coordinates = [key for key, val in model.items() if item == val] # NEW FOR TEMPORAL
            if coordinates != []:
                #return the coordinates and the corresponding model when item found
                if PRINT_MODEL:
                    print("find_first_item returns:", coordinates[0])
                return [coordinates[0], model]
    if PRINT_MODEL:
        print("new find itm failed, nothing found")
    return None


# ---------------------------- GENERAL LOW LEVEL FUNCTIONS ----------------------------------------

# USED BY BOTH MODELS (CAUTION! LISTS OR TUPEL AS RETURNS?)

def convert(relation):
    """OK [102]
    Function inverts all numbers in relation, changing positive numbers
    to negative numbers and vice versa, leaving the 0´s unchanged.
    """
    if relation is None:
        return None
    neg_rel = [-x for x in relation]
    return neg_rel

# USED BY BOTH MODELS (CAUTION! LISTS OR TUPEL AS RETURNS?)

def get_relation(proposition):
    """[73]
    Returns the relation as a list of ints from the given premise
    """
    relation_string = proposition[0]
    if PRINT_MODEL:
        print("get_relation: ", proposition)
    if isinstance(relation_string, list):
        # print("refln: relation is already a list")
        # the relation has already been converted
        return relation_string
    # re-format the string into a list for coordinate use
    relation_string = relation_string.strip('(')
    relation_string = relation_string.strip(')')
    relation = relation_string.split()
    relation = [int(relation[0]), int(relation[1]), int(relation[2])]
    return relation

# USED BY BOTH MODELS (CAUTION WRAPPER FOR TEMPORAL!)

def get_subject(proposition):
    """[74]
    Returns the subject of a given proposition
    """
    return proposition[1][0]

# USED BY BOTH MODELS (CAUTION WRAPPER FOR TEMPORAL!)

def get_object(proposition):
    """[75]
    Returns the object of a given proposition
    """
    return proposition[2][0]

# USED BY BOTH MODELS (CAUTION WRAPPER FOR TEMPORAL!)

def tuple_add(tuple1, tuple2):
    """
    new version of list_add, used for dictionaries.
    Adds all single elements of the tuples. Returns the tuple of the sums.
    Returns None if the tuples do not have the same length.
    """
    if (not tuple1) or (not tuple2) or (len(tuple1) != len(tuple2)):
        return None
    return (tuple1[0] + tuple2[0], tuple1[1] + tuple2[1], tuple1[2] + tuple2[2])

# USED BY BOTH MODELS
def dict_dimensions(dict1):
    """
    Determines the dimensions of a model in dictionary form.
    Returns a tuple with the max values of indices from the coords.
    """
    x_dim = []
    y_dim = []
    z_dim = []
    for (i, j, k) in dict1.keys():
        y_dim.append(j)
        x_dim.append(i)
        z_dim.append(k)
    # add 1 to actually get the size of the model.
    return tuple([max(x_dim)+1, max(y_dim)+1, max(z_dim)+1])

# USED BY BOTH MODELS
def dict_mins(dict1):
    """
    Determines the minima of all coordinates. returns the minima for the 3
    axes separately. Returns a tuple with min x, y and z
    """
    x_dim = []
    y_dim = []
    z_dim = []
    for (i, j, k) in dict1.keys():
        y_dim.append(j)
        x_dim.append(i)
        z_dim.append(k)
    # add 1 to actually get the size of the model.
    return tuple([min(x_dim), min(y_dim), min(z_dim)])

# USED BY BOTH MODELS
def normalize_coords(model):
    """
    Function which normalizes a given model (dictionary) to get a model with only
    positive coordinates.
    Function takes the minimum of the 3 coordinate components. For each of them,
    shift all coordinates to make the smallest number 0(if the minimum is
    smaller than 0 only). Returns the normalized model.
    e.g. shifts the items at (1, 1, 0) and (-1, 2, 0) to (2, 1, 0) and (0, 2, 0)
    """
    if PRINT_MODEL:
        print("normalize model with model: ", model)
    min_coords = dict_mins(model) # get all minima of the coordinates
    shift_vals = [0, 0, 0] # a list for the values by which the coords will be shifted.
    if min_coords[0] < 0: # shift all x coordinates by the absolute value of the minimum.
        shift_vals[0] = abs(min_coords[0])
    if min_coords[1] < 0:
        shift_vals[1] = abs(min_coords[1])
    if min_coords[2] < 0:
        shift_vals[2] = abs(min_coords[2])
    # iterate through the model and copy the items into another dict with updated coordinates.
    shifted_model = {}
    for (x_co, y_co, z_co), value in model.items():
        shifted_model[x_co + shift_vals[0], y_co + shift_vals[1], z_co + shift_vals[2]] = value
    if PRINT_MODEL:
        print("normalized model: ", shifted_model)
    return shifted_model


# ONLY USED BY SPATIAL MODEL (AUFWEITEN AUF TEMPORAL?)
def print_models(model_list):
    """
    Prints all models in a given model_list the way they should look.
    Uses matplotlib scatterplot.
    """
    plt.ioff()
    fig = plt.figure()
    model_objects = {'[]':'s', 'V': '^', 'O': 'o', 'I': '|', '+': 'X',
                     'L': '$L$', 'A': '$A$','B': '$B$','C': '$C$','D': '$D$',
                     '^': '$V$', '*': '*', 'S': '$S$'}
    # compute the square root from the number of elements and then adjust the
    # size for the grid to fit the number of models.
    rows_cols = int(np.sqrt(len(model_list))+0.5)+1
    #print("rows_cols ", rows_cols)
    # iterate through the models
    for index, model in enumerate(model_list):
        ax_ = fig.add_subplot(rows_cols, rows_cols, index+1, projection='3d')
        ax_.set_xlabel('X-Axis')
        ax_.set_ylabel('Y-Axis')
        ax_.set_zlabel('Z-Axis')
        for (x_co, y_co, z_co), value in model.items():
            if isinstance(value, list):
                #model_obj = ''
                for item in value:
                    ax_.scatter(x_co, y_co, z_co, s=50, marker=model_objects[item])
                    ax_.annotate("test", (x_co, y_co))

                # print("double item found in model:", model_obj)
            else:
                ax_.scatter(x_co, y_co, z_co, s=40, marker=model_objects[value])
    # print an asnwer or sth. like that
    #fig.text(.5, .05, answer, ha='center')
    fig.text(.5, .05, "all created models in their creation order", ha='center')
    plt.show()
