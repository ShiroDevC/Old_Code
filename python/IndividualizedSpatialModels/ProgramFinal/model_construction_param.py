'''
Created on 16.07.2018

@author: Christian Breu <breuch@web.de>, Julia Mertesdorf<julia.mertesdorf@web.de>

STATUS: Funktionsaufrufe müssen evtl geupdatet werden
'''

import copy

import low_level_functions_param as helper


PRINT_BACKTRACK = False


# ---------------------------- FUNCTIONS FOR MODEL CONSTRUCTION -----------------------------------

# USED BY BOTH MODELS
def startmod(relation, subj, obj):
    """
    Function constructs a new model out of a given subject, object and relation from a
    premise. It creates an empty dictionary, then adds the object and the subject of the
    proposition as a new dictionary entry with "add_item" (was add_it in v.1).
    Returns the resulting Model.
    """
    if PRINT_BACKTRACK:
        print("startmod with rel,sub, obj:", relation, subj, obj)
    model = {(0, 0, 0): obj} # add the obj to the origin directly
    # put subject at appropriate relation to object
    model = add_item((0, 0, 0), relation, subj, model)
    if PRINT_BACKTRACK:
        print("startmod: Full startmodel with object and subject is:", model)
    return model

# USED BY BOTH MODELS (CAUTION! ONLY TEMPORAL NEEDS THE COPY! BUT WORKS FOR SPATIAL THAT WAY)
def add_item(coordinates, relation, item, model):
    """
    New version of add_item + add_it
    Function adds the given item to the model by using the coordinates and the relation
    (relation and coordinates need to be tuples). Adds the relation to the coordinates
    in order to get the real coordinates that the item should have in the model by calling
    tuple_add.
    If the relation is (0, 0, 0), gets the item at the target coordinates, if there is
    an element, and concatenates item and this element. If the slot is still empty, the item
    is simply inserted at this slot and afterwards the model is returned.
    If the relation wasn´t (0, 0, 0), search for the first empty slot (by adding the relation
    to the target coordinates until a free slot is reached), and insert the item.
    """
    target_coords = helper.tuple_add(coordinates, relation) # NOT IN TEMPORAL
    if PRINT_BACKTRACK:
        print("add_item: coords:", coordinates, "rel", relation, "--> target",
              target_coords, "item", item, "mod", model)
    if relation == (0, 0, 0):
        # check if there is already an object at the given coords.
        if model.get(target_coords) is not None:
            if isinstance(model.get(target_coords),list):
                model_item = model.get(target_coords)
                model_item.append(item)
                item = model_item
            else:
                item = [item, model.get(target_coords)] # add the item to the already existing one
        model[target_coords] = item                 # add the item to the model at the coords
        return model
    # check if there is another object at the current coords.
    while model.get(target_coords) is not None:
        # search the first free spot in the correlating axis in the model.
        # add the relation to coords until a free spot is found.
        target_coords = helper.tuple_add(target_coords, relation)
    if PRINT_BACKTRACK:
        print("add the item at coords:, ", item, target_coords)
    model2 = copy.deepcopy(model) # NEW FOR TEMPORAL
    model2[target_coords] = item # add the item to the model
    return model2

# USED BY BOTH MODELS
def combine(relation, s_co, o_co, subj_mod, obj_mod): # same as SPATIAL
    """
    New version of combine with dictionaries.
    Function combines the subject model and the object model in a way that the relation
    between the subject and the object is satisfied.
    Calls dimensions_n_orig to find out what the new dimensions and origins
    need to be. Then the coordinates of all objects in both models are
    shifted according to the new dimensions.
    returns the combined model.
    """
    if PRINT_BACKTRACK:
        print("function call - combine with rel", relation, "s_co", s_co, "o_co", o_co,
              "subj_mod", subj_mod, "and obj_mod", obj_mod)
    # use the dimension to determine the size of the models
    sub_dims = helper.dict_dimensions(subj_mod)
    obj_dims = helper.dict_dimensions(obj_mod)
    tmp = find_new_origin_dict(relation, sub_dims, obj_dims, s_co, o_co)
    if PRINT_BACKTRACK:
        print("Combine: Dimensions of new model is (find_new_origin_dict): ", tmp)
    # find out by which delta the origin needs to be shifted
    new_sub_orig = [y[0] for y in tmp] # build the new origins from sub and obj
    new_obj_orig = [z[1] for z in tmp]
    if PRINT_BACKTRACK:
        print("new origins of subj is:", new_sub_orig, "new origins of obj is:", new_obj_orig)
    # update the coordinates on both models.
    new_subj_mod = shift_origin_dict(subj_mod, new_sub_orig)
    new_obj_mod = shift_origin_dict(obj_mod, new_obj_orig)
    if PRINT_BACKTRACK:
        print("Combine: after origin update, subj is: ", new_subj_mod, "obj is", new_obj_mod)
    # just put the two dicts together to get the full combined model
    new_subj_mod.update(new_obj_mod)
    if PRINT_BACKTRACK:
        print("Combine: combined model is: ", new_subj_mod)
    return new_subj_mod

# USED BY BOTH MODELS
def find_new_origin_dict(relation, sub_dims, obj_dims, s_co, o_co):
    """
    New version for dimensions_n_orig, only returns new origins.
    Iterates through the relation and coordinates of the two
    models. Returns a list of 3 lists consisting of the subject and
    the object new origin.
    If the relation of an axis is > 0: add the object dimension to the
    subject-origin part.
    -> because the subject is right or in front of the object and hence need
    to have the origin value of the obj aswell.
    If the relation is < 0: add the subject dimension to the object-origin part.
    if the relation is 0 at a certain point, call ortho (with the coordinates of sub+obj)
    and add the result of ortho to the result.
    """
    if PRINT_BACKTRACK:
        print("Function call - dimensions_n_orig with rel", relation, "s_dims", sub_dims,
              "o_dims", obj_dims, "s_co", s_co, "o_co", o_co)
    if not relation:
        return None
    result_list = []
    for count, value in enumerate(relation):
        if value > 0:
            # the subject needs a new origin
            result_list.append([obj_dims[count], 0])
        elif value < 0:
            #the object needs a new origin.
            result_list.append([0, sub_dims[count]])
        else:
            result_list.append(ortho(s_co[count], o_co[count]))
    if PRINT_BACKTRACK:
        print("dimensions_n_orig: returnList is:", result_list)
    return result_list

# USED BY BOTH MODELS
def ortho(sub_cord, obj_cord): # same as spatial # Doc anpassen
    """
    new version of orhto method. returns new origins for subj + obj.
    Takes coordinate components.

    Function returns a list with the new dimensions for the combined array, the new
    subject origin and the new object origin component.
    If the subject coordinates are bigger than the object coordinates,
    new dimensions will be set to the subject coordinates and the
    object_array dimensions - object coordinates. The subject will become
    the new origin, so add 0 for subject_origin. The object origin will
    become subject coordinates - object coordinates (the offset of the two
    elements).
    if the object coordinates are bigger, it works the other way around.
    if the array dimensions from the subject model are bigger then the dims
    from the obj_mod, use the subject dims.
    """
    if PRINT_BACKTRACK:
        print("Function call - ortho with sub_cord", sub_cord, "obj_cord", obj_cord)
    if sub_cord > obj_cord:
        return [0, (sub_cord - obj_cord)]
    if sub_cord < obj_cord:
        return [(obj_cord - sub_cord), 0]
    return [0, 0]

# USED BY BOTH MODELS
def shift_origin_dict(dictionary1, origin_list):
    """
    New version of "new_origin" used for dictionaries.
    Shifts all coordinates of the elements in the model by the number given in origin_list.
    Returns the model with all items shifted according to new origin.
    """
    new_dict = {}
    for (x_co, y_co, z_co) in dictionary1.keys():
        new_dict[x_co+origin_list[0], y_co+origin_list[1], z_co+origin_list[2]
                ] = dictionary1[(x_co, y_co, z_co)]
    return new_dict
