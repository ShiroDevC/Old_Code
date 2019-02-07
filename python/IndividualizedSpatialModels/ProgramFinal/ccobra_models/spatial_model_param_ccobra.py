'''
Module for the Spatial Model with Parameters to be used in the CCOBRA Framework.

@author: Christian Breu <breuch@web.de>
'''
from copy import deepcopy

import ccobra

from spatial_reasoner import low_level_functions_param as helper

from spatial_reasoner import main_module_param

class SpatialModelParam(ccobra.CCobraModel):
    """
    Model for the Spatial Model with parameters. The Model will call the main
    module of the spatial model to do predictions. Since this approach only uses
    up to 8 parameters, an other version of the interpret function of the spatial
    model is used.
    Only uses the adapt function. The pretrain function is not used.
    """
    # list to store all Problems and answers from the vp, contains tuples (problem, answer)
    previous_problems_ans = []
    # list for the previously given answers by the model
    previous_model_ans = []
    # Variable for the parameter assignment for the spatial model
    parameter_assignment = [[False, False, False, False, False, False], [False, False]]

    def __init__(self, name='SpatialModelParam'):
        """ Initializes the Model by calling the parent-class constructor
        and passing information about the name as well as supported domains
        and response-types.
        Each individualized model(except the categories model) can solve problems of
        the "verify" and "single-choice" type.

        Parameters
        ----------
        name : str
            Name of the model. Will be used as an identifier throughout the
            evaluation phase. Should be unique.

        """
        super(SpatialModelParam, self).__init__(
            name, ["spatial-relational"], ["verify", "single-choice"])

    def start_participant(self, **kwargs):
        """ Model initialization method. Used to setup the initial state of its
        datastructures, memory, etc.

        **Attention**: Should reset the internal state of the model.

        """
        #reset the collect problems/answers from the adapt function
        self.previous_problems_ans = []
        self.previous_model_ans = []
        # reset the parameters for the next participant
        self.parameter_assignment = [[False, False, False, False, False, False], [False, False]]

    def predict(self, item, **kwargs):
        """ Generates a prediction based on a given task item.
        Can make a prediction with verify and single-choice tasks.
        The current parameter assignment will be used for the prediction.
        Parameters
        ----------
        item : ccobra.data.Item
            Task item container. Holds information about the task, domain,
            response type and response choices.

        Returns
        -------
        list(str)
            Single-choice relational response in list representation (e.g.,
            ['A', 'left', 'B']) or a verification relational response in Boolean
            representation.

        """
        # initialize the spatial model
        spatial_model = main_module_param.MainModule()
        rel_prob = deepcopy(item.task) # get the problem premises
        # convert the premises to the form [A, relation, B] to be used by the spatial model
        for rel_prem in rel_prob:
            relation = rel_prem[0]
            rel_prem[0] = rel_prem[1]
            rel_prem[1] = relation
        # checks for the response type to choose an appropriate function from the
        # spatial model and a correct conversion of the question premise format.
        if item.response_type == "single-choice":
            # for single choice problems, the format of the question premises
            # is different than for the other problem_types.
            rel_questions = deepcopy(item.choices)
            for rel_pre in rel_questions:
                rel_pr = rel_pre[0] # unwrap the list of the actual premise
                relation = rel_pr[0]
                rel_pr[0] = rel_pr[1]
                rel_pr[1] = relation
                rel_pre = rel_pr
                rel_prob.append(rel_pr)
            # calls an apropriate function from the spatial model that will return
            # the given answer with the correct format for the evaluation in the framework.
            answer = spatial_model.interpret_spatial2exp_parameters(
                rel_prob, deepcopy(self.parameter_assignment))
            self.previous_model_ans.append(answer)
            return answer
        # for all verification problems the standard function will be called from the
        # spatial model. The format of the question premises is different, tha's
        # why the conversion is different aswell.
        rel_questions = deepcopy(item.choices[0]) # get the question premise
        #print("item choices: ", item.choices)
        for rel_pre in rel_questions:
            relation = rel_pre[0]
            rel_pre[0] = rel_pre[1]
            rel_pre[1] = relation
            rel_prob.append(rel_pre)
        answer = spatial_model.interpret_spatial_parameters_old(
            rel_prob, deepcopy(self.parameter_assignment))
        self.previous_model_ans.append(answer)
        return answer

    def adapt(self, item, target, **kwargs):
        """
        his function will collect all the given answers from the participant
        and the model to the corresponding problems, as well as the problems
        itself. If enough problems are collected, the best parameters will be
        searched. This process will be done again every 10 problems after that.
        For each answer from the model, that is different to the participant answer,
        the function will call the find_params function to find possible parameter
        assignments, that can correct the wrong prediction by the model for this
        problem.
        If there is no such problem, the function will call the find_params function
        with the current problem.
        The possible parameter assignments will then be evaluated with all collected
        problems. The parameter assignment(s) with the highest precision in predicting
        the participant answers will be stored.
        If the best assignment is more precise than a specified threshold, this
        assignment will be used for future predictions. If not, the standard
        assignment will be used.

        Parameters
        ----------
        item : ccobra.data.Item
            Task information container. Holds the task text, response type,
            response choices, etc.

        target : str
            True response given by the human reasoner.

        """
        # store the problem and the response from the participant
        self.previous_problems_ans.append((item, target))
        # check if there are enough collected data to find parameter assignments
        # maybe implement counter to reassign the parameters every n problems.
        if len(self.previous_problems_ans) >= 20 and (
                len(self.previous_problems_ans) % 10) == 0:
            #print("set new params", len(self.previous_problems_ans))
            # find a parameter assignment based on the results of these problems
            #First find a problem where the answer of the participant was
            # different to the models answer. If the answer is the same, no
            # meaningful parameter assignment can be found(only parameters to
            # answer the problems correctly, which isn't needed.
            params = None
            current_top_param = []
            current_top_prec = 0
            # check for each answer from the model
            for i, prev_ans in enumerate(self.previous_model_ans):
                if prev_ans != self.previous_problems_ans[i][1]:
                    params = self.find_params(deepcopy(
                        self.previous_problems_ans[i][0]),
                                              deepcopy(self.previous_problems_ans[i][1]))
                    top_params = self.compute_compare_answers(
                        params, deepcopy(self.previous_problems_ans))
                    if top_params[1] > current_top_prec:
                        current_top_param = top_params[0][0] # store the current best parameters
                        current_top_prec = top_params[1] # store the current best precision.
            if not params: #if no pronlem was found where the answer was different
                params = self.find_params(
                    deepcopy(item), deepcopy(target))
                top_params = self.compute_compare_answers(
                    params, deepcopy(self.previous_problems_ans))
                if not top_params[0]:
                    current_top_param = top_params[0][0]
                    current_top_prec = top_params[1]
            if current_top_prec > 0.8: # check if the best parameter assignment is above a threshold
                self.parameter_assignment = current_top_param
            else:
                print("use no parameters")
                self.parameter_assignment = [
                    [False, False, False, False, False, False], [False, False]]

    @staticmethod
    def find_params(problem, answer):
        """
        This function finds all possible parameters to get the given result with
        a given problem. The function will iterate over all possible parameter assignments
        and will store all assignments that result in the specified answer. This list will
        be returned. The answer needs to be a boolean value.
        Parameters
        ----------
        problem : list
            contains all premise lists of the task

        answer : bool
            True response given by the human reasoner.
        """
        spatial_model = SpatialModelParam() # initiate the spatial model
        matching_params = []
        i = 0
        # iterates over all possible variable assignments
        while i < 64:
            prob = deepcopy(problem) # problem = item
            b_num = format(i, '06b')
            params = [[bool(int(b_num[0])), bool(int(b_num[1])), bool(int(b_num[2])),
                       bool(int(b_num[3])), bool(int(b_num[4])), bool(int(b_num[5]))],
                      [False, False]]
            # check if the result with these parameters is the same as answer
            para = deepcopy(params)
            spatial_model.parameter_assignment = para # set the parameter assignment to use predict
            prediction = spatial_model.predict(prob)
            if prediction == answer:
                matching_params.append(params)
            elif prob.response_type == "single-choice":
                if helper.list_equal(prediction, answer):
                    matching_params.append(params)
            i += 1
        return matching_params # returns all lists of parameter values that did match

    @staticmethod
    def compute_compare_answers(params, problems):
        """
        Computes all answers for each of the given parameters with the given problems.
        After the answers for one parameter list is computed, the results will be directly
        evaluated with respect to the precision of the participant prediction.
        The currently best parameter assignment will be stored. After all parameter
        assignments are processed, the best one will  be returned.
        Parameters
        ----------
        params : list
             contains parameter assigment lists(of bools)

        problems : list
            list of problems(list containing the premises)
        Returns
        ---------
        bestparam: tuple
            tuple containing the best parameter and the accuracy of it. (e.g.
            (parameter assignment, accuracy))
        """
        #answers_list = [] # list for the lists of results
        spatial_model = SpatialModelParam() # initiate the spatial model
        best_param = [[], 0] # the tuple contains the parameter(s) with the best accuracy
        for param in params:
            correct_answers = 0 # results for each parameter and all problems
            # now directly check if the answer is the same as the given answer from the data?
            probs = deepcopy(problems)
            for problem in probs: # problem is now just a tuple with the item and the answer
                spatial_model.parameter_assignment = deepcopy(param)
                answer = spatial_model.predict(problem[0]) # problem = (item, vp_answer)
                if answer == problem[1]:
                    correct_answers += 1
            # determine how accurate the parameters were
            acc_val = float(correct_answers) / len(problems)
            if acc_val >= best_param[1]: # check if the current parameter is better
                best_param[1] = acc_val # new accuracy threshold
                best_param[0].append(param)
        # reset the parameters
        spatial_model.parameter_assignment = [
            [False, False, False, False, False, False], [False, False]]
        # returns tuple with the accuracy aswell
        # return the best parameter assignment(or one of the best)
        return (best_param[0], best_param[1])
