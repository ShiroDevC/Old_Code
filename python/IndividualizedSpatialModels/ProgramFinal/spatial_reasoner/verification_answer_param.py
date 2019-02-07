'''Module for the verification methods, which are used when the model is built.
Created on 16.07.2018

@author: Christian Breu <breuch@web.de>, Julia Mertesdorf<julia.mertesdorf@web.de>
'''
from copy import deepcopy

from spatial_reasoner import low_level_functions_param as helper

#import parser_spatial_temporal as parser

from spatial_reasoner import modify_model_param as modify

PRINT_MODEL = False # zwischenloesung

#ANSWER = "NO ANSWER YET"


# ONLY USED IN SPATIAL
def verify_spatial(proposition, model):
    """
    Extracts the relation, subject and object from the proposition. Then
    searches the subj + obj in the model. Returns the model if the relation
    between the subj and obj is correctly represented in the model. Iterates
    through the relation and checks the corresponding subj and obj coordinates
    for the axis of the relation.
    e.g. for relation[0] = 1, checks if the subj_coords and obj_coords at the
    corresponding index do satisfy the relation.
    If the relation is 0 but the obj and subj coordinates are different,
    verification fails aswell.
    Returns None if the relation does not hold.
    """
    if PRINT_MODEL:
        print("call verify_spatial with prop, model: ", proposition, model)
    relation = proposition[1]
    subj = proposition[0]
    obj = proposition[2]
    subj_coords = helper.find_first_item(subj, [model])[0]
    obj_coords = helper.find_first_item(obj, [model])[0]
    if PRINT_MODEL:
        print("verify_spatial: subj_coords, obj_coords, relation",
              subj_coords, obj_coords, relation)
    # iterate through the relation and the coordinates of the objects.
    for index, value in enumerate(relation):
        # if the relation is != 0, check if the relation holds in this axis
        if (value > 0) and (subj_coords[index] <= obj_coords[index]):
            # if the subject coords are < than obj coords in rel axis, relation
            # does not hold!
            if PRINT_MODEL:
                print("verify_spatial: relation does not hold, return None")
            return None
        if (value < 0) and (subj_coords[index] >= obj_coords[index]):
            # the same for the opposite relation, this is the case when verify_temporal fails
            if PRINT_MODEL:
                print("verify_spatial: relation does not hold, return None")
            return None
        if (value == 0) and (subj_coords[index] != obj_coords[index]):
            # the items must not be at the same position!
            if PRINT_MODEL:
                print("verify_spatial: objects are on a different line in another axis ")
            return None
    if PRINT_MODEL:
        print("verify_spatial: succesfully verified, return the model")
    return model

# ONLY USED IN SPATIAL
def conflict(premises, model):
    """
    Finds all premises that are conflicting with the given model.
    Iterates over premises and parses them each. If the premises can't be
    parsed or the subject and the object are in the model, try to verify_temporal the
    premise(prop) with verify_spatial.
    If it can't be verified, add the premise(prop) to the result list of
    conflicted props. Returns a list of conflicting premises.
    """
    if PRINT_MODEL:
        print("conflict: prems, model: ", premises, model)
    if not premises:
        return None
    result_list = []
    #print("conflict with premises: ", premises)
    for prem in premises:
        prop = prem
        subj = prem[0]
        obj = prem[2]
        if PRINT_MODEL:
            print("conflict: subj, obj", subj, obj)
        #check if the premise can be parsed(should be always the case)
        # and the subject  and object are in the model.
        # call new_find_item with a list!!!
        if(prop is None) or ((helper.find_first_item(subj, [model]))
                             and (helper.find_first_item(obj, [model]))):
            #if subj + obj are in the model, try to verify_temporal. if verify_temporal
            # returns false, add the proposition to the conflicted props.
            if not verify_spatial(prop, model):
                if PRINT_MODEL:
                    print("conflicted premise in prems: with model", prop, model)
                result_list.append(prop)
    return result_list

# ONLY USED IN SPATIAL
def conflict_props(propositions, model):
    """
    Returns list of conflicted propositions in model. Works similiar to the
    conflict method, but it uses a list of already parsed propositions.
    Also uses verify_spatial to check for conflicted propositions.
    """
    if PRINT_MODEL:
        print("conflict_props with prop, model: ", propositions, model)
    if propositions is None:
        return None
    conflict_list = []
    for prop in propositions:
        if not verify_spatial(prop, model):
            conflict_list.append(prop)
    return conflict_list

# ONLY USED IN SPATIAL
def make(prop_list, fix_props, model, premises):
    """
    Iterates over the given prop-list and tries to make the props true by
    calling switch. If the resulting model is not None, switch was able to
    create a model in which prop holds. If thats the case, add the prop to
    the fix_props that should always hold. If the result of switch is None,
    return None, it is not possible to create a model with all props = true
    with this prop_list. After each iteration through the prop_list, set the
    prop_list to all the conflicting props in the current model.
    If there are no conflicts, return the model.
    """
    if PRINT_MODEL:
        print("make with prop_list, fix_props, model, premises", prop_list,
              fix_props, model, premises)
    while prop_list:
        #first, iterate over the prop list and call switch on the props
        for prop in prop_list:#for each proposition, call switch and change the model with this
            model = switch(prop, fix_props, model)
            # if switch could make the prop hold in the model, add it to the fix props
            if model is not None:
                if PRINT_MODEL:
                    print("make: switch worked, insert prop into fix-props")
                fix_props.insert(0, prop)
            else: return None#returns None, if the model becomes None
        #when all the props are through, check if there are any conflicts in the new model.
        #if there are no conflicts, the loop is over
        prop_list = conflict(premises, model)
        if PRINT_MODEL:
            print("current prop_list after conflict:", prop_list)
    return model

# ONLY USED IN SPATIAL
def remove_prem(proposition, premises):
    """
    Iterates over all the premises and returns a list of the premises
    without the given proposition(premise). Adds premises to the result
    list if they aren't equal to the proposition.
    """
    if((premises is None) or (not premises)):
        return None#return None if the premises list is empty or None
    result = []
    #print("remove prem with proposition, premises: ", proposition, premises)
    for prem in premises:
        #add premises != proposition in order to remove proposition from the list.
        if not helper.list_equal(proposition, prem):
            result.append(prem)
    return result

# ONLY USED IN SPATIAL
def make_false(proposition, model, premises):
    """
    Tries to make the model hold with a negated relation from the premise.
    If this is possible, the proposition is falsified. If not, the premise
    is valid in the model. The original model is returned with a statement.
    """
    if PRINT_MODEL:
        print("make-false with prop: ", proposition)
    prems = remove_prem(proposition, premises)
    prop = deepcopy(proposition)
    prop[1] = helper.invert_relation(prop[1])#negate the proposition
    #print("call make with the negated premise: ", prop)
    new_mod = make([prop], [prop], model, deepcopy(prems))
    if (new_mod is not None) and (verify_spatial(prop, new_mod)):
        #print("could be made incorrect")
        #print("model + premise that holds now: ", prop, new_mod)
        model[(20, 20, 20)] = "F" #add The T(true) as the answer to the model
        return model
    #print("valid")
    model[(20, 20, 20)] = "T" #add The T(true) as the answer to the model
    return model

# ONLY USED IN SPATIAL
def make_true(proposition, model, premises):
    """
    Tries to find a way to make the proposition hold in model.
    Modifies the model in different ways to see if the proposition and all
    the other premises do hold then. If this suceeds, returns the new model.
    Calls make to modify the model.
    """
    if PRINT_MODEL:
        print("make true with premise, model: ", proposition, model)
    prems = remove_prem(proposition, premises)
    new_mod = make([proposition], [proposition], model, deepcopy(prems))
    if (new_mod is not None) and (verify_spatial(proposition, new_mod)):
        #print("could be made valid")
        new_mod[(20, 20, 20)] = "T" #add The T(true) as the answer to the model
        return new_mod
    #print("incorrect")
    model[(20, 20, 20)] = "F" #add The T(true) as the answer to the model
    return model

# ONLY USED IN SPATIAL
def negate_prop(proposition):
    """
    Negates relation-part of the proposition and returns the changed proposition.
    (before --> after, after --> before, while --> while).
    """
    #proposition needs to be List!
    relation = proposition[1]
    proposition[0] = helper.convert(relation)
    if PRINT_MODEL:
        print("negate prop: ", proposition)
    return proposition

# ONLY USED IN SPATIAL
def switch(new_prop, fix_props, model):
    """
    new version of switch for dictionaries.
    First, tries to swap the object and subject if the relation is the
    opposite of the required relation.(find_rel_prop will return the
    relation between the subj and object.)
    Calls swap with the subject and the object. Checks if the resulting
    model has any conflicts, if not returns it. If there were any conflicts,
    set the new_mod to the result of move with the subject.
    move will change the position of the subject to make the premise true in
    the model. Returns new_mod if conflict-free.
    After that it tries the same thing with moving the object.
    If nothing works, returns None
    """
    if PRINT_MODEL:
        print("switch with new_prop, fixprops, model: ", new_prop, fix_props, model)
    relation = new_prop[1]
    # just use the string of the item
    subj = new_prop[0]
    obj = new_prop[2]
    # call new_find_item with a list!!!
    s_coord = helper.find_first_item(subj, [model])[0] # s_coord + o_coord are tuples
    o_coord = helper.find_first_item(obj, [model])[0]# only get the coordinates
    # check if the relation of subj and obj is converse to the relation of the proposition.
    if find_rel_prop(s_coord, o_coord) == helper.convert(relation):
        # only if first condition holds, try to swap the items.
        new_mod = modify.swap(subj, s_coord, obj, o_coord, model)
        if PRINT_MODEL:
            print("switch: model, new_mod after swap:", model, new_mod)
        if new_mod is not None:
            # if there are now conflicting props in the new model, return it
            if not conflict_props(fix_props, new_mod):
                if PRINT_MODEL:
                    print("no conflicts found in the model")
                return new_mod
            if PRINT_MODEL:
                print("model + new_model after swap+conflict:", model, new_mod)
    # move the subject and check if there are any conflicting propositions
    new_mod = modify.move(subj, s_coord, relation, o_coord, model)
    if PRINT_MODEL:
        print("new_mod after move: ", new_mod)
    # revise condition!!!
    if new_mod and (new_mod is not None) and not conflict_props(fix_props, new_mod):
        return new_mod
    if PRINT_MODEL:
        print("model + new_model after move subject:", model, new_mod)
    # move the subject and check if there are any conflicting props
    new_mod = modify.move(obj, o_coord, helper.convert(relation), s_coord, model)
    if PRINT_MODEL:
        print("new_mod after move: ", new_mod)
    if (new_mod is not None) and not conflict_props(fix_props, new_mod):
        return new_mod
    return None  # nothing worked

# ONLY USED IN SPATIAL
def find_rel_prop(s_coords, o_coords):
    """
    Returns the normalized difference of the subject and object coordinates.
    The normalization is the semantic relation between the two coordinates.
    Calls list_substract with the two coordinate lists and normalizes the
    result.
    Example: for s_coords = [2, 0, 1] and o_coords = [0, 0, 1]
    returns [1, 0, 0]
    """
    if PRINT_MODEL:
        print("find rel prop with s_coords, o_coords: ", s_coords, o_coords)
    vector = list_substract(s_coords, o_coords)
    return normalize(vector)

def normalize(vector):
    """
    Normalizes each element of the given list to 1 for positive values and
    -1 for negative values.
    """
    if PRINT_MODEL:
        print("normalize vector: ", vector)
    for count, value in enumerate(vector):
        if value > 0:
            vector[count] = 1
        elif value < 0:
            vector[count] = -1
        else: vector[count] = 0
    if PRINT_MODEL:
        print("normalized vector: ", vector)
    return vector

# ONLY USED IN SPATIAL
def list_substract(list1, list2):
    """OK [52]
    Returns list1 where each element is substracted by the corresponding
    list2 element. Returns None if the lenght of the lists is not the same.
    """
    if not list1:
        return None
    result_list = []
    if len(list1) != len(list2):
        #print("list substract with lists of different length!!, abort")
        return None
    for count, value in enumerate(list1):
        result_list.append(value - list2[count])
    return result_list
