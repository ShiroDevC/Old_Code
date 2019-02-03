'''
Main Module for the individualized spatial Model. The previously contained temporal
model is not usable with this module.

@author: Christian Breu <breuch@web.de>
'''

from copy import deepcopy

import random

import unittest

import model_construction_param as construct

import low_level_functions_param as helper

import verification_answer_param as ver_ans

# GLOBAL VARIABLES

# Global variable capacity illustrating the working memory (how many different models can be
# kept in the working memory). Is usually set to 4.
CAPACITY = 4

# Two global variables enabling function-prints. Mainly used for debugging purposes.
PRINT_PARSING = False # global variable for whether to print parsing process or not

PRINT_MODEL = False # global variable for whether to print model construction process or not.

PRINT_INDIVIDUAL = False # global variable for whether to print all active individualizations.

class MainModule:
    """
    Main module for the individualized spatial model. The interpret function now
    takes a set of parameters, which have an effect on the outcome of the problem
    processing. The general functionality of the spatial model is still the same,
    but the input needs to be converted to fit the interpret function. The spatial
    model can now process two problem types. The verification task type was already
    implemented in the original version(only give answer True/False).
    Now the single choice task type can be processed as well. The model will choose
    the correct answer from a given set of answer choices.

    Old Documentation of the spatial model:
    Main module of the Spatial Model. This Class contains the high-level functions
    like "process_problem_spatial" which the user can call on a specific problem set.
    Moreover, it contains the different "interpret" and "decide" - functions for each the Spatial
    and the Temporal Model, which are called depending on whether
    "process_problem spatial " was called.

    Spatial Model Documentation:
    This version is semantical (almost) equal to the space5 lisp program from 1989.
    In this version the program can be called with interpret_spatial(problem) or
    process_problem_spatial(n, problems), with n as the number of the problem in the given
    set of problems.

    Quick description of the program:
    First it goes through all given PREMISES, parses them and adds them to
    the current model or creates a new one. Premises can also combine two exising
    models when both items of a premise are in different models.
    If The two items from a premise are in the same model, the program will
    check if this premise holds in the model. If yes, tries to falsify and
    if no, tries to verify the premise an the given model. In order to do this,
    the program takes the last added premise(which triggered verify) and tries
    to make it hold in the model. If there is a model that satisfies the premise,
    it will be added to a list of PREMISES that always have to hold. Now it will
    iteratively check if there are conflicts in the current model(that is changed
    every time when a premise is made true f.i.) and then try to make them true
    in the model. If there are no more conficting PREMISES, the program will
    return the new model. If there is a premise that cannot be satisfied in the
    model, the program will terminate with the opposite result(e.g. if a certain
    premise cannot be made false in the model, it is verified. If it can be made
    false, the previous model might be wrong/false.
    There is only one order for verifying the conflicting PREMISES that occur,
    so there are different models with a different outcome probably left out.
    """

# ---------------------------- SPATIAL MODEL FUNCTIONS --------------------------------------------

    def interpret_spatial_parameters(self, prem, parameters):
        """
        *This function can only be used for verification tasks*
        New version of interpret_spatial. does not use the parser.
        Parameters contains all the parameters to decide which individualisation
        should be activated or not. Checks position (20, 20, 20) to get the answer
        to the problem, when there is one.
        Returns only the answer and doesn't print the model.
        The answer will be false, when at least one question premise couldn't be
        verified.
        There are 11 parameters with a boolean value. The first 6 parameters are
        for understanding the premise and for correctly building the model in
        the 3 steps. Parameter 1,3,5 are for understanding the premises. Parameter
        2,4,6 are for model_start/insert/combine. The 7th parameter is for the
        verbal memory usage. The 8th parameter is for the usage of the guessing.
        Parameters consists of 2 lists, the first one is for the model construction and
        the second one is for other parameters.
        The last three parameters are for alternative combine, alternative insert and
        modify intial model.
        The Parameters for "premise build correctly", at index 1,3 and 5 of the
        original parameters were not used by the recent models except for the
        parameters approach model.
        Parameters:
        ------------
        parameters: list
            Parameters need to have the form: [[Bool, Bool, Bool, Bool, Bool, Bool],
            [Bool, Bool, Bool, Bool, Bool]]
            The first 6 are premise x understood and premise x correctly build(for
            1 < x < 3) the last 5 are for: verbal memory, guessing, preferred
            model(use makefalse), alt_insert, alt_combine
        Returns:
        -----------
        answer: bool
            Returns the boolean value of the anwer for all verification problems
        """
        #first check whether the problem should be solved by another method(guessing/verbal memory)
        if parameters[1][0]: # check for verbal memory
            if PRINT_INDIVIDUAL:
                print("verbal memory use")
            if prem[-1][0] in ["A", "B", "C", "D"]:
                #print("check with verbal memory")
                return self.verbal_memory(prem[:-1], prem[-1])
            if len(prem) == 8:
                #the problem is from the trees experiment
                verb_premises = prem[:4] # the first 4 premises are for the task
                for q_prem in prem[4:]: #iterate over all question premises
                    #print("check premise: ", q_prem, "with ", verb_premises)
                    if not self.verbal_memory(verb_premises, q_prem):
                        return False # at least one of the premises does not hold
                return True # no premise could be falsified with the verb. memory.
        #check for guessing
        if parameters[1][1]:
            if PRINT_INDIVIDUAL:
                print("guessing with question: ", prem[-1])
            # the standard modell NOTE: ONlY FOR CERTAIN DATA!!!!
            # checks if the question premise is about  A,B,C or D
            if prem[-1][0] in ["A", "B", "C", "D"]:
                # the standard model for certain types of experiments.
                model1 = {(0, 0, 0): 'A', (1, 0, 0): 'B', (2, 0, 0): 'C', (3, 0, 0): 'D'}
                prem[-1][1] = self.parse_relation(prem[-1])
                if ver_ans.verify_spatial(prem[-1], model1) is not None:
                    return True # the question premise holds in the standard model
                return False
            #real guessing for the second experiment(trees/fruits)
            #+print("guessing for second experiment: verify")
            if random.randint(1, 10) < 5:
                return True
            return False
        # no Parser
        mods = []  # list of models
        all_mods = []
        answer = None # The answer that will be returned at the end
        # iterate over the list of PREMISES, return models when done
        for pre_ in prem:
            if PRINT_MODEL:
                print(pre_, "premise")
            #premise = pars.parse(pre_)  # the currently parsed premise
            pre_[1] = self.parse_relation(pre_) # convert the relation into a tupel
            if PRINT_MODEL:
                print("parsed premise: ", pre_)
            #print(parameters[0][:2])
        for pre_ in prem:
            mods = self.decide_spatial(pre_, mods, prem, parameters[0][:2],
                                       parameters[1][2:]) # New! add other parameters
            parameters[0] = parameters[0][2:]
            #print(parameters[0])
            if mods[0].get((20, 20, 20)) == "T" and answer is not False:
                answer = True # The answer for the problem can only become True,
                # if no previous verify returned a negative value.
            elif mods[0].get((20, 20, 20)) == "F":
                answer = False
            #only preparation to print a model
            #mods[0] = helper.normalize_coords(mods[0])
            #mods[0] = modify.shrink_dict(mods[0])
            # list for all models
            all_mods.append(deepcopy(mods[0]))
            if PRINT_MODEL:
                print("current models after decide_spatial: ", mods)
        # print out models in the list.
        if PRINT_MODEL:
            print("list of all resulting Models")
            print(all_mods)
        return answer # return only the answer, not the model(s)

    def interpret_spatial2exp_parameters(self, prem, parameters):
        """
        *Only for singel choiceproblems.*
        In this experiment, the participants had to choose an answer so the
        return value of the interpret function can't be True or False. The function
        returns the first question premise that evaluates to true in verify.
        There are 11 parameters with a boolean value. The first 6 parameters are
        for understanding the premise and for correctly building the model in
        the 3 steps. Parameter 1,3,5 are for understanding the premises. Parameter
        2,4,6 are for model_start/insert/combine. The 7th parameter is for the
        verbal memory usage. The 8th parameter is for the usage of the guessing.
        Parameters consists of 2 lists, the first one is for the model construction and
        the second one is for other parameters.
        The last three parameters are for alternative combine, alternative insert and
        modify intial model.
        The Parameters for "premise build correctly", at index 1,3 and 5 of the
        original parameters were not used by the recent models except for the
        parameters approach model.
        Parameters:
        ------------
        parameters: list
            Parameters need to have the form: [[Bool, Bool, Bool, Bool, Bool, Bool],
            [Bool, Bool, Bool, Bool, Bool]]
            The first 6 are premise x understood and premise x correctly build(for
            1 < x < 3) the last 5 are for: verbal memory, guessing, preferred
            model(use makefalse), alt_insert, alt_combine
        Returns:
        -----------
        answer: list
            Returns the answer premise for the given problem
        """
        #first check whether the problem should be solved by another method(guessing/verbal memory)
        if parameters[1][0]: # check for verbal memory
            if PRINT_INDIVIDUAL:
                print("verbal memory use")
            question_prem = prem[2:]
            model_prem = prem[:2]
            for q_p in question_prem:
                for m_p in model_prem:
                    # check if the two lists are the same
                    if q_p[0] == m_p[0] and q_p[1] == m_p[1] and q_p[2] == m_p[2]:
                        #print("found the answer in the premises")
                        ans_rel = m_p[1]
                        m_p[1] = m_p[0]
                        m_p[0] = ans_rel
                        #print("answer with verbal: ", [m_p])
                        return [m_p]
            # the premise could'nt be found, guess an answer.
            possible_ans = prem[-8:]
            #print(possible_ans, "possible answers for guessing")
            rand = random.randint(0, 7)
            ans = possible_ans[rand]
            ans_rel = ans[1]
            ans[1] = ans[0]
            ans[0] = ans_rel
            #print("answer with verb: ", [ans])
            return [ans]
        #check for guessing
        if parameters[1][1]:
            if PRINT_INDIVIDUAL:
                print("guessing with question: ", prem)
            possible_ans = prem[-8:]
            #print(possible_ans, "possible answers for guessing")
            rand = random.randint(0, 7)
            ans = possible_ans[rand]
            ans_rel = ans[1]
            ans[1] = ans[0]
            ans[0] = ans_rel
            #print("answer with guessing: ", [ans])
            return [ans]
        # no Parser
        mods = []  # list of models
        all_mods = []
        answer = None # The answer that will be returned at the end
        # iterate over the list of PREMISES, return models when done
        prems = deepcopy(prem)
        for pre_ in prems:
            if PRINT_MODEL:
                print(pre_, "premise")
            pre_[1] = self.parse_relation(pre_) # convert the relation into a tupel
            if PRINT_MODEL:
                print("parsed premise: ", pre_)
        for pre_ in prem:
            pr_ = deepcopy(pre_)
            pr_[1] = self.parse_relation(pr_) # convert the relation into a tupel
            mods = self.decide_spatial(pr_, mods, prems, parameters[0][:2], parameters[1][2:])
            parameters[0] = parameters[0][2:]
            #print(parameters[0])
            if mods[0].get((20, 20, 20)) == "T" and answer is None:
                answer = pre_ # this question premise was verified as true and therefore
                # is the correct answer based on this model
            # list for all models
            all_mods.append(deepcopy(mods[0]))
            if PRINT_MODEL:
                print("current models after decide_spatial: ", mods)
        # print out models in the list.
        if PRINT_MODEL:
            print("list of all resulting Models")
            print(all_mods)
        if answer is None:
            possible_ans = prem[-8:]
            rand = random.randint(0, 7)
            answer = possible_ans[rand]
        # re-format the answer to fit ccobra evaluation
        ans_rel = answer[1]
        answer[1] = answer[0]
        answer[0] = ans_rel
        # the answer has to fit the format of the ccobra evaluation
        return [answer] # return only the answer, not the model(s)

    def interpret_spatial_parameters_old(self, prem, parameters):
        """
        *only used by parameters model*
        The old version of interpret spatial parameters. To be used by the models
        that do still use all 8 original parameters.
        New version of interpret_spatial. does not use the parser.
        The parameters parameter contains all the parameters to decide which individualisation
        should be activated or not. Checks position (20, 20, 20) to get the answer, when there
        is one. Returns only the answer and doesn't print the model. The answer will be false,
        when at least one question premise couldn't be verified.
        There are 8 parameters with a boolean value. The first 6 parameters are for understanding
        the premise and for correctly building the model in the 3 steps. Parameter 1,3,5 are for
        understanding the premises. Parameter 2,4,6 are for model_start/insert/combine. The 7th
        parameter is for the verbal memory usage. The last parameter is for the usage of the
        guessing. Parameters consists of 2 lists, the first one is for the model construction and
        the second one is for other parameters.
        Parameters:
        ------------
        parameters: list
            Parameters need to have the form: [[Bool, Bool, Bool, Bool, Bool, Bool],
            [Bool, Bool]]
            The first 6 are premise x understood and premise x correctly build(for
            1 < x < 3) the last 5 are for: verbal memory, guessing, preferred
            model(use makefalse), alt_insert, alt_combine
        Returns:
        -----------
        answer: bool
            Returns the boolean value of the anwer for all verification problems
        """
        #first check whether the problem should be solved by another method(guessing/verbal memory)
        if parameters[1][0]: # check for verbal memory
            if PRINT_INDIVIDUAL:
                print("verbal memory use")
            if prem[-1][0] in ["A", "B", "C", "D"]:
                #print("check with verbal memory")
                return self.verbal_memory(prem[:-1], prem[-1])
            if len(prem) == 8:
                #the problem is from the trees experiment
                verb_premises = prem[:4] # the first 4 premises are for the task
                for q_prem in prem[4:]: #iterate over all question premises
                    print("check premise: ", q_prem, "with ", verb_premises)
                    if not self.verbal_memory(verb_premises, q_prem):
                        return False # at least one of the premises does not hold
                return True # no premise could be falsified with the verb. memory.
        #check for guessing
        if parameters[1][1]:
            if PRINT_INDIVIDUAL:
                print("guessing with question: ", prem[-1])
            # the standard modell NOTE: ONlY FOR CERTAIN DATA!!!!
            # checks if the question premise is about  A,B,C or D
            if prem[-1][0] in ["A", "B", "C", "D"]:
                # the standard model for certain types of experiments.
                model1 = {(0, 0, 0): 'A', (1, 0, 0): 'B', (2, 0, 0): 'C', (3, 0, 0): 'D'}
                prem[-1][1] = self.parse_relation(prem[-1])
                if ver_ans.verify_spatial(prem[-1], model1) is not None:
                    return True # the question premise holds in the standard model
                return False
            #real guessing for the second experiment(trees/fruits)
            print("guessing for second experiment: verify")
            if random.randint(1, 10) < 5:
                return True
            return False
        # no Parser
        mods = []  # list of models
        all_mods = []
        answer = None # The answer that will be returned at the end
        # iterate over the list of PREMISES, return models when done
        for pre_ in prem:
            if PRINT_MODEL:
                print(pre_, "premise")
            #premise = pars.parse(pre_)  # the currently parsed premise
            pre_[1] = self.parse_relation(pre_) # convert the relation into a tupel
            if PRINT_MODEL:
                print("parsed premise: ", pre_)
            #print(parameters[0][:2])
        for pre_ in prem:
            mods = self.decide_spatial(pre_, mods, prem, parameters[0][:2])
            parameters[0] = parameters[0][2:]
            #print(parameters[0])
            if mods[0].get((20, 20, 20)) == "T" and answer is not False:
                answer = True # The answer for the problem can only become True,
                # if no previous verify returned a negative value.
            elif mods[0].get((20, 20, 20)) == "F":
                answer = False
            # list for all models
            all_mods.append(deepcopy(mods[0]))
            if PRINT_MODEL:
                print("current models after decide_spatial: ", mods)
        # print out models in the list.
        if PRINT_MODEL:
            print("list of all resulting Models")
            print(all_mods)
        return answer # return only the answer, not the model(s)

    def verbal_memory(self, premises, question):
        """checks if the question can be answered by only knowing all premises. Iterates
        through a given list of premises and checks if both elements from the question
        are contained in each premise. If such a premise can be found, an answer can be
        returned based on the information in the premise. If no such premise can be found,
        returns false as the answer.
        """
        for prem in premises:
            if question[0] in prem and question[2] in prem:
                # now compute the answer
                if question[1] == prem[1]:
                    # relation is equal
                    if question[0] == prem[0] and question[2] == prem[2]:
                        return True #the exact same premise to the question exists.
                    return False # prem has information contrary to the question
                if question[1] != prem[1]:
                    #relation is not the same, check if the premise and question is inverted
                    q_rel = self.parse_relation(question)
                    p_rel = self.parse_relation(prem)
                    #print("check for inverted relations with: ", q_rel, p_rel)
                    if (helper.list_equal(helper.invert_relation(q_rel), p_rel) and (
                            question[2] == prem[0] and question[0] == prem[2])):
                        return True
                    return False # prem has information contrary to the question
        return False # no premise could be found which contains the information to answer

    @staticmethod
    def parse_relation(premise):
        """ 3-tuple really needed?
        Function that only parses a given Relation into a 3 tuple of
        coordinates that represent the direction of the relation.
        """
        relation_string = premise[1].split("-") # split the relation(for the 3rd experiment)
        relation = [0, 0, 0]
        # adds the directions represented by the relation(or relation parts)
        # only checks for the first letter L to also get the "Left" relation.
        for relation_p in relation_string:
            relation_part = relation_p.lower() # to be able to process all kinds of premises
            if relation_part[0] == "l" or relation_part == "west":
                relation[0] -= 1
            elif relation_part[0] == "r" or relation_part == "east":
                relation[0] += 1
            elif relation_part == "north":
                relation[1] += 1
            elif relation_part == "south":
                relation[1] -= 1
        return (relation[0], relation[1], relation[2]) # return the resulting relation as a tuple

    def alt_insert(self, coordinates, relation, object1, model):
        """alternative version of the insert function. In this insert, the object
        to be inserted will be placed at the exact position of coordinates+relation.
        The other objects in the axis of the relation will be moved accordingly.

        Example: Model AB with premise A L C -> ACB
        So B is the moved in the x axis by the relation.
        """
        # create new model to later insert all objects with the fixed coordinates.
        new_model = {}
        # find out in which dimension the objects need to be moved
        # works also for two dimensional models and two dimensional relations
        if relation[0] != 0:
            dimension_index = 0 # variable to know which dimension is important later
        elif relation[1] != 0:
            dimension_index = 1
        else:
            dimension_index = 2
        # first, move all objects by the relation from coordinates onwards
        for coord in model.keys():
            # iterate over the coordinates to check, wheter to  move the object or not.
            if relation[dimension_index] > 0:
                # the relation is positive, search for bigger values than the coordinates
                if coord[dimension_index] > coordinates[dimension_index]:
                    # the object needs to be moved in the corresponding dimension with the relation
                    new_coord = helper.tuple_add(coord, relation)
                    new_model[new_coord] = deepcopy(model[coord])
                    #print("new_coord at index", new_coord, "relation at index: ", relation)
                else:
                    # copy the object to the new model normaly
                    new_model[coord] = deepcopy(model[coord])
            elif relation[dimension_index] < 0:
                # the relation is positive, search for bigger values than the coordinates
                if coord[dimension_index] < coordinates[dimension_index]:
                    # the object needs to be moved in the corresponding dimension with the relation
                    new_coord = helper.tuple_add(coord, relation)
                    new_model[new_coord] = deepcopy(model[coord])
                    #print("new_coord at index", new_coord, "relation at index: ", relation)
                    new_model[new_coord] = deepcopy(model[coord])
                else:
                    # copy the object to the new model normaly
                    new_model[coord] = deepcopy(model[coord])
        new_obj_co = helper.tuple_add(coordinates, relation)
        new_model[new_obj_co] = object1 # add the actual object to insert
        return new_model

    def decide_spatial(self, proposition, models, premises, params,
                       alt_params=[False, False, False]):
        """
        Modifications: relation/subject/object are directly retrieved. Always calls
        choose_function with pref_mod = True, to use the preferred model.
        takes the parsed premise and the list of current models.
        extracts the subject and object of the premise, then checks if they
        can be found in any model.
        deletes the models from the models list, if they contain the subj. or obj.
        calls helper function choose_function_spatial to decide_spatial what should
        be done depending on the
        premise and the current models.(see documentation of ddci for more detail)
        returns list of current models as a result of choose_function_spatial.
        """
        # check if alt_params is not None
        if len(alt_params) < 3:
            #print("wrong input, the second parameter list has to have 5 elements!")
            alt_params = [False, False, False]
        relation = proposition[1]
        subject = proposition[0]
        object1 = proposition[2]
        s_co = None
        o_co = None
        subj_mod = None
        obj_mod = None
        param = None
        # check if the premise is understood correctly:
        #print(params)
        if params:
            if params[0]: #if this error should be activated
                if PRINT_INDIVIDUAL:
                    print("param premise not understood")
                relation = helper.invert_relation(relation) # inverts the premise
            param = params[1] # cut out the first element of the list(parameter used)
            #print("second parameter for decide:", param)
        if PRINT_MODEL:
            print("call decide_spatial with rel-subj-obj:", relation, subject, object1)
        # retrieve the subject and the object from the models
        subj_co_mod = helper.find_first_item(subject, models)
        if subj_co_mod is not None:
            s_co = subj_co_mod[0]
            subj_mod = subj_co_mod[1]
        obj_co_mod = helper.find_first_item(object1, models)
        if obj_co_mod is not None:
            o_co = obj_co_mod[0]
            obj_mod = obj_co_mod[1]
        if subj_mod in models:
            models.remove(subj_mod)
        if obj_mod in models:
            models.remove(obj_mod)
        #print("s_co and o_co:", s_co, o_co)
        if not models:
            # always uses just the preffered model to give the answer!
            return [self.choose_function_spatial(proposition, s_co, o_co, relation, subject,
                                                 object1, subj_mod, obj_mod,
                                                 premises, param, alt_params)]

        models.insert(0, self.choose_function_spatial(proposition, s_co, o_co, relation,
                                                      subject, object1, subj_mod, obj_mod,
                                                      premises, param, alt_params))
        return models

    def choose_function_spatial(self, proposition, s_co, o_co, relation, subject,
                                object1, subj_mod, obj_mod, premises, param,
                                alt_params):
        """
        Modifications: add "T" or "F" to the model at a certain position to be able
        to retrieve the answer later on without changing the return type of the function.
        takes a premise(proposition), subject-and object coordinates, a subject and
        an object and their models in which they are contained.
        deletes the models from the models list, if they contain the subj. or obj.
        creates a new model if the subj. and obj. both aren't in any model.
        if one of them is in a model, add the new item to the corresponding model.
        if they both are in the same model, verify the model. depending on the
        result of that, calls make_true or make_false to find counterexamples.
        The paramater pref_mod decides, whether the model will be further inspected
        after the first verify with the given question premise. If pref_mod is set
        to true, the model will not be further inspected and the answer will be
        given based on the preferred model alone.
        """
        if s_co is not None:
            if o_co is not None:
                # whole premise already in model, check if everything holds
                if subj_mod == obj_mod:
                    if PRINT_MODEL:
                        print("verify, whether subj. and obj. are in same model")
                    # verify returns the model in case the premise holds
                    if ver_ans.verify_spatial(proposition, subj_mod) is not None:
                        if PRINT_MODEL:
                            print("verify returns true, the premise holds")
                        # try to make falsify the result
                        if alt_params[0]:
                            #print("try make false")
                            return ver_ans.make_false(proposition, subj_mod, premises)
                        #print("valid(pref_mod)")
                        subj_mod[(20, 20, 20)] = "T" #add The T(true) as the answer to the model
                        # in the interpret function, this position will be checked.
                        return subj_mod # return True if the model does not try to falsify
                    # try to make all PREMISES hold
                    if PRINT_MODEL:
                        print("verify returns false, the premise is invalid")
                    if alt_params[0]:
                        #print("try make tue", proposition)
                        return ver_ans.make_true(proposition, subj_mod, premises)
                    #print("incorrect(pref_mod)")
                    subj_mod[(20, 20, 20)] = "F" # add The F(false) as the answer to the model
                    return subj_mod # return false beacause the model does not try to verify
                # subj and obj both already exist, but in different models
                if PRINT_MODEL:
                    print("combine")
                # if the parameter is active, invert the relation before the combination
                # to simulate an error when combining the two models.
                if param:
                    if PRINT_INDIVIDUAL:
                        print("param combine")
                    relation = helper.invert_relation(relation)
                comb_model = construct.combine(relation, s_co, o_co,
                                               helper.normalize_coords(subj_mod),
                                               helper.normalize_coords(obj_mod))
                if alt_params[2]:
                    # ONLY premiseorder problems can use this, so it
                    # is made just for these problems!
                    #print("swap the 2nd and 3rd object in the model after combine", comb_model)
                    comb_model = helper.normalize_coords(comb_model)
                    obj1 = comb_model[(1, 0, 0)]
                    comb_model[(1, 0, 0)] = comb_model[(2, 0, 0)]
                    comb_model[(2, 0, 0)] = obj1
                    #print("swapped model: ", comb_model)
                return comb_model
            if PRINT_MODEL:
                print("add object to the model")
                # convert relation because the object is added
                print("relation before convert: ", relation, "after convert: ",
                      helper.convert(relation))
            # if the parameter is active, invert the relation before the insert
            # to simulate an error when adding a new object
            if param:
                if PRINT_INDIVIDUAL:
                    print("param add item")
                relation = helper.invert_relation(relation)
            if alt_params[1]:
                # use the alternative version of insert
                #print("alt insert")
                return self.alt_insert(s_co, helper.convert(relation), object1, subj_mod)
            return construct.add_item(s_co, helper.convert(relation), object1, subj_mod)
        # object != Null but subject doesn't exist at this point
        if o_co is not None:
            if PRINT_MODEL:
                print("add subject to the model")
            # if the parameter is active, invert the relation before the insert
            # to simulate an error when adding a new object
            if param:
                relation = helper.invert_relation(relation)
            if alt_params[1]:
                # use the alternative version of insert
                #print("alt insert")
                return self.alt_insert(o_co, relation, subject, obj_mod)
            return construct.add_item(o_co, relation, subject, obj_mod)
        # sub and ob doesn't exist at the moment
        if PRINT_MODEL:
            print("startmod")
        # if the parameter is active, invert the relation before startmod
        if param:
            if PRINT_INDIVIDUAL:
                print("param add item")
            relation = helper.invert_relation(relation)
        return construct.startmod(relation, subject, object1)

#-----------------------------Experimental Problem Set(figural effect)--------------------------
#figural effect: the order/arrangement of l and r relations in the premises.
# For easier encoding the Temporal Parser will be used, since there is parsing for
# the letters A,B etc. The relation before will be L = left. after will resemble R = right.

EXP_PROBLEMS_FIG = [
    [["the", "A", "happens", "before", "the", "B"],  # incorrect
     ["the", "B", "happens", "before", "the", "C"],  #ID: 13
     ["the", "A", "happens", "after", "the", "C"]], # result:incorrect
    [["the", "B", "happens", "after", "the", "A"],  # incorrect
     ["the", "C", "happens", "after", "the", "B"],  #ID: 12
     ["the", "C", "happens", "before", "the", "A"]], # result:incorrect
    [["the", "B", "happens", "after", "the", "A"],  # incorrect
     ["the", "B", "happens", "before", "the", "C"],  #ID: 15
     ["the", "A", "happens", "after", "the", "C"]], # result:incorrect
    [["the", "B", "happens", "after", "the", "A"],  # valid
     ["the", "B", "happens", "before", "the", "C"],  #ID: 7
     ["the", "C", "happens", "after", "the", "A"]], # result:valid
    [["the", "A", "happens", "before", "the", "B"],  # valid
     ["the", "B", "happens", "before", "the", "C"],  #ID: 1
     ["the", "A", "happens", "before", "the", "C"]], # result:valid
    [["the", "A", "happens", "before", "the", "B"],  # valid
     ["the", "C", "happens", "after", "the", "B"],  #ID: 2
     ["the", "A", "happens", "before", "the", "C"]], # result:valid
    [["the", "B", "happens", "after", "the", "A"],  # incorrect
     ["the", "C", "happens", "after", "the", "B"],  #ID: 16
     ["the", "A", "happens", "after", "the", "C"]], # result:incorrect
    [["the", "B", "happens", "after", "the", "A"],  # valid
     ["the", "C", "happens", "after", "the", "B"],  #ID: 8
     ["the", "C", "happens", "after", "the", "A"]], # result:valid
    [["the", "A", "happens", "before", "the", "B"],  # incorrect
     ["the", "B", "happens", "before", "the", "C"],  #ID: 9
     ["the", "C", "happens", "before", "the", "A"]], # result:incorrect
    [["the", "A", "happens", "before", "the", "B"],  # valid
     ["the", "B", "happens", "before", "the", "C"],  #ID: 5
     ["the", "C", "happens", "after", "the", "A"]], # result:valid
    [["the", "A", "happens", "before", "the", "B"],  # incorrect
     ["the", "C", "happens", "after", "the", "B"],  #ID: 14
     ["the", "A", "happens", "after", "the", "C"]], # result:incorrect
    [["the", "A", "happens", "before", "the", "B"],  # valid
     ["the", "C", "happens", "after", "the", "B"],  #ID: 6
     ["the", "C", "happens", "after", "the", "A"]], # result:valid
    [["the", "A", "happens", "before", "the", "B"],  # incorrect
     ["the", "C", "happens", "after", "the", "B"],  #ID: 10
     ["the", "C", "happens", "before", "the", "A"]], # result:incorrect
    [["the", "B", "happens", "after", "the", "A"],  # valid
     ["the", "C", "happens", "after", "the", "B"],  #ID: 4
     ["the", "A", "happens", "before", "the", "C"]], # result:valid
    [["the", "B", "happens", "after", "the", "A"],  # incorrect
     ["the", "B", "happens", "before", "the", "C"],  #ID: 11
     ["the", "C", "happens", "before", "the", "A"]], # result:incorrect
    [["the", "B", "happens", "after", "the", "A"],  # valid
     ["the", "B", "happens", "before", "the", "C"],  #ID: 3
     ["the", "A", "happens", "before", "the", "C"]], # result:valid
    ]

# ----------------------------SPATIAL REASONING PROBLEM SETS ------------------------------------

COMBO_PROBLEMS = [
    [["the", "square", "is", "behind", "the", "circle"],#combo 1
     ["the", "cross", "is", "in", "front", "of", "the", "triangle"],
     ["the", "square", "is", "on", "the", "left", "of", "the", "cross"]],
    #composition problem 2
    [["the", "circle", "is", "in", "front", "of", "the", "square"],
     ["the", "triangle", "is", "behind", "the", "cross"],
     ["the", "cross", "is", "on", "the", "right", "of", "the", "square"]],
    #combo3
    [["the", "square", "is", "behind", "the", "circle"],
     ["the", "triangle", "is", "behind", "the", "cross"],
     ["the", "cross", "is", "on", "the", "left", "of", "the", "square"]],
    #combo 4
    [["the", "square", "is", "behind", "the", "circle"],
     ["the", "triangle", "is", "behind", "the", "cross"],
     ["the", "line", "is", "above", "the", "triangle"],
     ["the", "cross", "is", "on", "the", "left", "of", "the", "square"]]]

####Problems that require a deductive Conlusion####
#(correct: 1, 2, 3, 4, 5, 6 (for 5 and 6 only checked important indermediate results)
DEDUCTIVE_PROBLEMS = [#deductive conclusion 1
    [["the", "circle", "is", "on", "the", "right", "of", "the", "square"],
     ["the", "triangle", "is", "on", "the", "left", "of", "the", "circle"],
     ["the", "cross", "is", "in", "front", "of", "the", "triangle"],
     ["the", "line", "is", "in", "front", "of", "the", "circle"],
     ["the", "cross", "is", "on", "the", "left", "of", "the", "line"]],
    #deductive conlcusions prob 2
    [["the", "cross", "is", "in", "front", "of", "the", "circle"],
     ["the", "circle", "is", "in", "front", "of", "the", "triangle"],
     ["the", "cross", "is", "in", "front", "of", "the", "triangle"]],
    #ded 3
    [["the", "square", "is", "on", "the", "right", "of", "the", "circle"],
     ["the", "circle", "is", "on", "the", "right", "of", "the", "triangle"],
     ["the", "square", "is", "on", "the", "right", "of", "the", "triangle"]],
    #ded 4
    [["the", "square", "is", "on", "the", "right", "of", "the", "circle"],
     ["the", "triangle", "is", "on", "the", "left", "of", "the", "circle"],
     ["the", "square", "is", "on", "the", "right", "of", "the", "triangle"]],
    #ded5
    [["the", "square", "is", "on", "the", "right", "of", "the", "circle"],
     ["the", "cross", "is", "in", "front", "of", "the", "triangle"],
     ["the", "triangle", "is", "on", "the", "left", "of", "the", "square"],
     ["the", "square", "is", "behind", "the", "line"],
     ["the", "line", "is", "on", "the", "right", "of", "the", "cross"]],
    #ded6
    [["the", "triangle", "is", "on", "the", "right", "of", "the", "square"],
     ["the", "circle", "is", "in", "front", "of", "the", "square"],
     ["the", "cross", "is", "on", "the", "left", "of", "the", "square"],
     ["the", "line", "is", "in", "front", "of", "the", "cross"],
     ["the", "line", "is", "on", "the", "right", "of", "the", "ell"],
     ["the", "star", "is", "in", "front", "of", "the", "ell"],
     ["the", "circle", "is", "on", "the", "left", "of", "the", "vee"],
     ["the", "ess", "is", "in", "front", "of", "the", "vee"],
     ["the", "star", "is", "on", "the", "left", "of", "the", "ess"]]]

####indeterminate propblems#### all correct
INDETERMINATE_PROBLEMS = [#indeterminate 1, true
    [["the", "circle", "is", "on", "the", "right", "of", "the", "square"],
     ["the", "triangle", "is", "on", "the", "left", "of", "the", "circle"],
     ["the", "cross", "is", "in", "front", "of", "the", "triangle"],
     ["the", "line", "is", "in", "front", "of", "the", "square"],
     ["the", "cross", "is", "on", "the", "left", "of", "the", "line"]],
    #indeterminate2, false
    [["the", "triangle", "is", "on", "the", "right", "of", "the", "square"],
     ["the", "circle", "is", "in", "front", "of", "the", "square"],
     ["the", "cross", "is", "on", "the", "left", "of", "the", "triangle"],
     ["the", "line", "is", "in", "front", "of", "the", "cross"],
     ["the", "line", "is", "on", "the", "right", "of", "the", "ell"],
     ["the", "star", "is", "in", "front", "of", "the", "ell"],
     ["the", "circle", "is", "on", "the", "left", "of", "the", "vee"],
     ["the", "ess", "is", "in", "front", "of", "the", "vee"],
     ["the", "star", "is", "on", "the", "right", "of", "the", "ess"]],
    #indeterminate 3, false
    [["the", "square", "is", "on", "the", "right", "of", "the", "circle"],
     ["the", "triangle", "is", "on", "the", "left", "of", "the", "square"],
     ["the", "triangle", "is", "on", "the", "right", "of", "the", "circle"]],
    #indeterminate 4, false
    [["the", "square", "is", "on", "the", "right", "of", "the", "circle"],
     ["the", "triangle", "is", "on", "the", "left", "of", "the", "square"],
     ["the", "cross", "is", "in", "front", "of", "the", "triangle"],
     ["the", "line", "is", "in", "front", "of", "the", "circle"],
     ["the", "cross", "is", "on", "the", "right", "of", "the", "line"]],
    #indeterminate 5, false
    [["the", "square", "is", "on", "the", "right", "of", "the", "circle"],
     ["the", "triangle", "is", "on", "the", "left", "of", "the", "square"],
     ["the", "cross", "is", "in", "front", "of", "the", "triangle"],
     ["the", "line", "is", "in", "front", "of", "the", "circle"],
     ["the", "triangle", "is", "on", "the", "right", "of", "the", "circle"]],
    #indeterminate 6, false
    [["the", "circle", "is", "on", "the", "right", "of", "the", "square"],
     ["the", "triangle", "is", "on", "the", "left", "of", "the", "circle"],
     ["the", "cross", "is", "in", "front", "of", "the", "triangle"],
     ["the", "line", "is", "in", "front", "of", "the", "square"],
     ["the", "cross", "is", "on", "the", "right", "of", "the", "line"]],]

####problems with inconsistent PREMISES#### all correct
INCONSISTENT_PROBLEMS = [
    #incons 1
    [["the", "square", "is", "on", "the", "left", "of", "the", "circle"],
     ["the", "cross", "is", "in", "front", "of", "the", "square"],
     ["the", "triangle", "is", "on", "the", "right", "of", "the", "circle"],
     ["the", "triangle", "is", "behind", "the", "line"],
     ["the", "line", "is", "on", "the", "left", "of", "the", "cross"]],
    #incons2
    [["the", "square", "is", "in", "front", "of", "the", "circle"],
     ["the", "triangle", "is", "behind", "the", "circle"],
     ["the", "triangle", "is", "in", "front", "of", "the", "square"]],
    #incons 3
    [["the", "triangle", "is", "on", "the", "right", "of", "the", "square"],
     ["the", "circle", "is", "in", "front", "of", "the", "square"],
     ["the", "cross", "is", "on", "the", "left", "of", "the", "square"],
     ["the", "line", "is", "in", "front", "of", "the", "cross"],
     ["the", "line", "is", "on", "the", "right", "of", "the", "ell"],
     ["the", "star", "is", "in", "front", "of", "the", "ell"],
     ["the", "circle", "is", "on", "the", "left", "of", "the", "vee"],
     ["the", "ess", "is", "in", "front", "of", "the", "vee"],
     ["the", "star", "is", "on", "the", "right", "of", "the", "ess"]]]

# ---------------------------- UNIT TESTS ------------------------------------------------------

class Tests(unittest.TestCase):
    """Unittest class for newly implemented functions.
    """
    def test_parse_relation(self):
        """Tests the correctness of the conversion of the relation.
        """
        model = MainModule()
        self.assertEqual(model.parse_relation(["A", "north", "B"]),
                         (0, 1, 0))
        self.assertEqual(model.parse_relation(["A", "south", "B"]),
                         (0, -1, 0))
        self.assertEqual(model.parse_relation(["A", "east", "B"]),
                         (1, 0, 0))
        self.assertEqual(model.parse_relation(["A", "west", "B"]),
                         (-1, 0, 0))
        self.assertEqual(model.parse_relation(["A", "left", "B"]),
                         (-1, 0, 0))
        self.assertEqual(model.parse_relation(["A", "right", "B"]),
                         (1, 0, 0))
        self.assertEqual(model.parse_relation(["A", "south-west", "B"]),
                         (-1, -1, 0))
        self.assertEqual(model.parse_relation(["A", "north-east", "B"]),
                         (1, 1, 0))

    def test_verbal_memory(self):
        """Tests the verbal memory function.
        """
        model = MainModule()
        task_premises = [["B", "R", "A"], ["C", "R", "A"], ["D", "R", "C"]]
        question_premise = ["A", "L", "D"]
        self.assertEqual(model.verbal_memory(task_premises, question_premise), False)
        task_premises = [["B", "R", "A"], ["C", "R", "A"], ["C", "L", "D"], ["A", "L", "D"]]
        self.assertEqual(model.verbal_memory(task_premises, question_premise), True)

    def test_altinsert(self):
        """Tests the alternative insertion
        """
        model = MainModule()
        test_model = {(0, 0, 0) : "A", (1, 0, 0) : "B"}
        alt_mod = model.alt_insert((1, 0, 0), (-1, 0, 0), "new", test_model)
        correct_mod = {(0, 0, 0) : "new", (1, 0, 0) : "B", (-1, 0, 0) : "A"}
        self.assertEqual(alt_mod, correct_mod)

# ---------------------------- MAIN FUNCTION ------------------------------------------------------
def main():
    """
    Main-function.
    """
    #spatial_model = MainModule()
    """

    print(spatial_model.interpret_spatial_parameters([["B", "R", "A"], ["C", "R", "A"],
                                                      ["D", "R", "C"], ["C", "L", "D"]],
                                                      [[False, False, False, False,
                                                        False, False], [False, False,
                                                        False, True, False]]))

    print(spatial_model.interpret_spatial_parameters(
    [["plum tree", "West", "apricot tree"],["lime tree", "West", "plum tree"],
    ["plum tree", "West", "kiwi tree"], ["kiwi tree", "West", "fig tree"],
    ["lime tree", "West", "apricot tree"], ["apricot tree", "West", "plum tree"],
    ["apricot tree", "West", "kiwi tree"], ["kiwi tree", "West", "fig tree"]],
    [[False, False, False, False, False, False], [False, False, False, False, False]]))

    print(spatial_model.interpret_spatial_parameters(
    [["plum tree", "West", "apricot tree"],["lime tree", "West", "plum tree"],
    ["plum tree", "West", "kiwi tree"], ["kiwi tree", "West", "fig tree"],
    ["lime tree", "West", "apricot tree"], ["plum tree", "West", "kiwi tree"],
    ["apricot tree", "West", "kiwi tree"], ["kiwi tree", "West", "fig tree"]],
    [[False, False, False, False, False, False], [False, False]]))
    #["lime tree", "West", "apricot tree"], ["apricot tree", "West", "plum tree"],
    """

if __name__ == "__main__":
    main()
    unittest.main()
