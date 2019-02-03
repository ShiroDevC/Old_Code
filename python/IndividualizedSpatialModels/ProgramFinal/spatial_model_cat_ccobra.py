'''
Module for the spatial model with categories to be used in the CCOBRA Framework.
This Module will implement the categorization approach.

@author: Christian Breu <breuch@web.de>
'''
from copy import deepcopy

import ccobra

import main_module_param

class SpatialModelParam(ccobra.CCobraModel):
    """
    Model to test the categorization approach. This model will search for differences
    between certain categories of problems. If there is a big difference between
    the results of two categories, the model will activate certain parameters for
    the spatial model. In some cases, the problem will be modified before it will
    be processed by the spatial model, to simulate individualizations.
    Categories:
        problem type3: problem start with A/B or  C/D; R/L as the task relation..
        problem type2: task relation == problem relation/task relation != problem relation.
        problem type1: problem start with A/B or C/D.

    """
    # list to store all Problems and answers from the vp, contains tuples (problem, answer)
    previous_problems_ans = []
    # variables to store the problems in their corresponding type list. preparation for
    # the evaluation of the categories within the problem types.
    problem_type1 = []
    problem_type2 = []
    problem_type3 = []
    # list to store all the problemtype numbers from the processed problems, will be used in adapt
    # to know what problem type the current problem belongs to.
    previous_problem_type = []
    # list for the correct answers of the problems.
    previous_correct_ans = []
    # variable for the individualizations triggered by the categories analysis
    # The parameters are split up between the problem types. each problem type
    # has its own param list.
    # cat1(A or D first/aufbaurichtung) cat2(task+question have same relation)
    # cat3(A or D first/aufbaurichtung); (L or R relation in task)
    # parameters for problem type 1, 2 and 3 in order.
    cat_params = [[False, False, False], [False, False], [False, False, False, False]]
    # Variable for the parameter assignment for the spatial model
    parameter_assignment = [[False, False, False, False, False, False], [False, False]]

    def __init__(self, name='SpatialModelCat'):
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
        # initializes the spatial model and the parameter settings

    def start_participant(self, **kwargs):
        """ Model initialization method. Used to setup the initial state of its
        datastructures, memory, etc.

        **Attention**: Should reset the internal state of the model.

        """
        #reset the collect problems/answers from the adapt function
        self.problem_type1 = []
        self.problem_type2 = []
        self.problem_type3 = []
        self.previous_problem_type = []
        # list for the correct answers of the problems.
        self.previous_correct_ans = []
        self.previous_problems_ans = []
        # reset the parameters for the next participant
        self.cat_params = [[False, False, False], [False, False], [False, False, False, False]]
        self.parameter_assignment = [[False, False, False, False, False, False], [False, False]]

    def predict(self, item, **kwargs):
        """ Generates a prediction based on a given task item.
        Can make a prediction with verify and single-choice tasks.
        The predict function will use the category parameters only for the problems
        of the 'premiseorder' data. For each of the three problem types, the
        corresponding active individualizations will be applied on the problem
        or used in the spatial model when processing the problems. There is a
        parameter to trigger the inversion of the answer given by the model as
        well. This will not affect the way the model is build.
        The answers for the processed problems will be stored for later use in the
        adapt function.
        Parameters
        ----------
        item : ccobra.data.Item
            Task item container. Holds information about the task, domain,
            response type and response choices.

        Returns
        -------
        list(str)
            Single-choice relational response in list representation (e.g.,
            ['All', 'managers', 'clerks']).

        """
        # variable to make the model answer wrong/invert the answer
        invert_ans = False
        # initialize the spatial model
        spatial_model = main_module_param.MainModule()
        rel_prob = self.convert_premises(deepcopy(item.task)) # get the problem premises
        #print("item task: ", rel_prob)
        # convert the premises to the form [A, relation, B] to be used by the spatial
        #print("converted item task: ", rel_prob)
        # checks for the response type to choose an appropriate function from the
        # spatial model and a correct conversion of the question premise format.
        if item.response_type == "single-choice": # No change for single-choice problems
            # the categorization cannot be used for single choice problems
            print("problem cannot be processed by categories model")
            return None
        ##### Problem conversion #####
        # for all verification problems the standard function will be called from the
        # spatial model. The format of the question premises is different, tha's
        # why the conversion is different aswell.
        rel_questions = deepcopy(item.choices[0]) # get the question premise
        for rel_pre in rel_questions:
            relation = rel_pre[0]
            rel_pre[0] = rel_pre[1]
            rel_pre[1] = relation
            rel_prob.append(rel_pre)
        ##### Categorization/decide which cat_param to use ######
        # parameters for problem type 1, 2 and 3 in order.
        if len(item.choices) == 1 and len(rel_prob) == 4:
            # determine the problemtype
            # check for problemtype 3; if the 3rd premise contains C and B, it has to be type 3
            if (rel_prob[2][0] == "B" and rel_prob[2][2] == "C") or (
                    rel_prob[2][0] == "C" and rel_prob[2][2] == "B"):
                self.previous_problem_type.append(3)
                # check for the parameters activated by the categorization
                if self.cat_params[2][0]:
                    # A or D first category; combine should be done wrong!
                    # change the 3rd premise in the problem/ other option:
                    # activate the corresponding parameter of the model
                    # check if the first premise contains A/B or D/C!
                    if (rel_prob[0][0] == "D" and rel_prob[0][2] == "C") or (
                            rel_prob[0][0] == "C" and rel_prob[0][2] == "D"):
                        # combination should be wrong then
                        # invert the relation of the third premise to
                        # change the combination process
                        rel_prob[3] = self.invert_premise(rel_prob[3])
                elif self.cat_params[2][3]:
                    invert_ans = True
                elif self.cat_params[2][1]:
                    # the relation of the task premises should be inverted
                    # to generate wrong results.
                    # this is only if the L relation is worse than the
                    # R relation, invert the L into R
                    if rel_prob[0][1] == "L": #check if the relation is L
                        #print("used cat3 param2")
                        rel_prob[0][1] = "Right"
                        rel_prob[1][1] = "Right"
                        rel_prob[2][1] = "Right"
                elif self.cat_params[2][2]:
                    # the relation of the task premises should be
                    # inverted to generate wrong results.
                    # this is only if the R relation is worse than
                    # the L relation, invert the R into L
                    if rel_prob[0][1] == "R": #check if the relation is R
                        #print("used cat3 param3")
                        rel_prob[0][1] = "Left"
                        rel_prob[1][1] = "Left"
                        rel_prob[2][1] = "Left"
            # check for problemtype 2; if the first premise contains
            # C and B, it has to be type 2
            elif (rel_prob[0][0] == "B" and rel_prob[0][2] == "C") or (
                    rel_prob[0][0] == "C" and rel_prob[0][2] == "B"):
                self.previous_problem_type.append(2)
                # check for the parameters activated by the categorization
                # if the relation of task and question is not the same and
                # the answers are wrong then invert the relation of the
                # question premise, since one of the two different relations
                # lead to a mistake in understanding the premises.
                if self.cat_params[1][0]:
                    # if activated, simply invert question relation
                    if rel_prob[0][1] != rel_prob[3][1]: # check if the relations are different
                        rel_prob[3] = self.invert_premise(rel_prob[3])
                elif self.cat_params[1][1]:
                    invert_ans = True
            else: # Since the problem is not type 3 and 2, it has to be type 1
                self.previous_problem_type.append(1)
                # check for the parameters activated by the categorization
                # if the problem starts with A/B, the results are sometimes better
                # this parameter inverts the relations of the task, if
                # activated and model starts with C/D. The second parameter
                # is the same the other way around with A/B being worse than C/D.
                if self.cat_params[0][0]: # if the ab category is better than the cd category
                    if (rel_prob[0][0] == "C" and rel_prob[0][2] == "D"
                       ) or (rel_prob[0][0] == "D" and rel_prob[0][2] == "C"):
                        # first premise has d and c in it, invert the
                        # relations of the task premises to change the result
                        rel_prob = self.invert_premises(rel_prob)
                elif self.cat_params[0][1]:
                    # The other way around for the first category. If the
                    # vp can solve problems better with C/D as the first
                    # premise and has problems with A/B.
                    # also activates the parameter to change the combination.
                    if (rel_prob[0][0] == "A" and rel_prob[0][2] == "B"
                       ) or (rel_prob[0][0] == "B" and rel_prob[0][2] == "A"):
                        # invert the relations of the premises,
                        # this way the answer will be changed as well
                        rel_prob = self.invert_premises(rel_prob)
                elif self.cat_params[0][2]:
                    invert_ans = True
            answer = spatial_model.interpret_spatial_parameters(
                rel_prob, deepcopy(self.parameter_assignment))
            self.previous_correct_ans.append(answer) # store the given answer
            if invert_ans:
                return not answer
            return answer

    def adapt(self, item, target, **kwargs):
        """
        This function will collect all the given answers from the participant
        and the model to the corresponding problems, as well as the problems
        itself. If enough problems are collected, the categorization will be done.
        For the categorization, each problem type has an own problem list, where
        the previous problems are collected. If there are enough problems in a
        problem type list, the categorization for this specific category will
        be processed.

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
        correct_answer = self.previous_correct_ans[-1] # retrieve the correct answer
        problem_type = self.previous_problem_type[-1]
        if problem_type == 1:
            # add problem, answer and correct answer
            self.problem_type1.append([item, target, correct_answer])
        elif problem_type == 2:
            self.problem_type2.append([item, target, correct_answer])
        else:
            self.problem_type3.append([item, target, correct_answer])
        # check if there are enough collected data to do the categorization
        if len(self.previous_problems_ans) >= 25:
            # with 25 there are enough problems to judge properly
            # check all the categorie's lists and then set the cat_params accordingly
            if len(self.problem_type1) >= 9:
                self.categorize_type1()
            if len(self.problem_type2) >= 9:
                self.categorize_type2()
            if len(self.problem_type3) >= 9:
                self.categorize_type3_1()

    def categorize_type3_1(self):
        """
        Implements the first categorization of type 3 problems.
        The problems will be split up into two lists for each category.
        The problems with A and B in the first premise are in the first list, the
        other problems are in the second list.
        The lists will then be evaluated with regard to their precision. Since the
        list only contain the answers of the participants, the correctness of the
        given participant will be checked. If the participant makes a lot of errors
        in a certain category or problem type, the corresponding parameters are
        set to be used in the predict function.
        """
        #print("categorize type3")
        ab_cat = [] # category for the problems that start with a/b
        cd_cat = [] # category for the problems that start with c/d
        for prob_ans in self.problem_type3:
            rel_prob = self.convert_premises(deepcopy(prob_ans[0].task)) # get the problem premise
            #print("converted prob", rel_prob)
            # check if the first premise contains A and B
            if (rel_prob[0][0] == "B" and rel_prob[0][2] == "A") or (
                    rel_prob[0][0] == "A" and rel_prob[0][2] == "B"):
                ab_cat.append(prob_ans) #in this list only the answer and correct answer matter
            else: cd_cat.append(prob_ans) # if the problem doesn't start with A/B, it's D/C.
        ab_precision = self.evaluate_cat(ab_cat)
        cd_precision = self.evaluate_cat(cd_cat)
        overall_precision = self.evaluate_cat(ab_cat + cd_cat)
        if ab_precision >= 0 and cd_precision >= 0:
            if overall_precision <= 0.3:
                self.cat_params[2][3] = True
            elif ab_precision - cd_precision >= 0.6 and overall_precision <= 0.8:
                # set the first parameter for the third category to true.
                self.cat_params[2][0] = True
            elif cd_precision - ab_precision >= 0.6 and overall_precision <= 0.8:
                # set the first parameter for the third category to true.
                self.cat_params[2][0] = True

    def categorize_type3_2(self):
        """
        Implements the second categorization of type 3 problems.
        The problems will be split up into two lists for each category.
        The problems with the right relation in the task premises are in the
        first list, the other problems are in the second list.
        The lists will then be evaluated with regard to their precision. Since the
        list only contain the answers of the participants, the correctness of the
        given participant will be checked. If the participant makes a lot of errors
        in a certain category or problem type, the corresponding parameters are
        set to be used in the predict function.
        """
        #print("categorize type3 category 2")
        r_cat = [] # category for the problems with right
        l_cat = [] # category for the problems with left
        for prob_ans in self.problem_type3:
            rel_prob = self.convert_premises(deepcopy(prob_ans[0].task)) # get the problem premise
            # check if the first premise contains A and B
            if rel_prob[0][1] == "Right":
                r_cat.append(prob_ans) #in this list only the answer and correct answer matter
            else: l_cat.append(prob_ans) # if the problem doesn't start with A/B, it's D/C.
        r_precision = self.evaluate_cat(r_cat)
        l_precision = self.evaluate_cat(l_cat)
        overall_precision = self.evaluate_cat(r_cat + l_cat)
        #print("overall precision", overall_precision)
        if r_precision >= 0 and l_precision >= 0:
            if overall_precision <= 0.3:
                self.cat_params[2][3] = True
            elif r_precision - l_precision >= 0.6 and overall_precision <= 0.8:
                self.cat_params[2][1] = True # r is better than l
            elif l_precision - r_precision >= 0.6 and overall_precision <= 0.8:
                self.cat_params[2][2] = True # l is better than r
    def categorize_type2(self):
        """
        Implements the categorization of type 2 problems.
        The problems will be split up into two lists for each category.
        The problems with same task relation and question relation are in the
        first list, the other problems are in the second list.
        The lists will then be evaluated with regard to their precision. Since the
        list only contain the answers of the participants, the correctness of the
        given participant will be checked. If the participant makes a lot of errors
        in a certain category or problem type, the corresponding parameters are
        set to be used in the predict function.
        """
        same_cat = [] # categorylist for the problems, where the task rel != question rel.
        dif_cat = []# categorylist for the problems, where the task rel == question rel.
        for prob_ans in self.problem_type2:
            rel_prob = self.convert_premises(deepcopy(prob_ans[0].task)) # get the problem premise
            # check if the two relations are the same
            if rel_prob[0][1] == prob_ans[0].choices[0][0][0]:
                same_cat.append(prob_ans)
            else:
                dif_cat.append(prob_ans)
        same_precision = self.evaluate_cat(same_cat)
        dif_precision = self.evaluate_cat(dif_cat)
        overall_precision = self.evaluate_cat(same_cat + dif_cat)
        if same_precision >= 0 and dif_precision >= 0:
            if overall_precision <= 0.30:
                self.cat_params[1][1] = True
            elif same_precision - dif_precision >= 0.6 and overall_precision <= 0.7:
                self.cat_params[1][0] = True # set the parameter for the second category to true.
            elif dif_precision - same_precision >= 0.6 and overall_precision <= 0.7:
                self.cat_params[1][0] = True # set the parameter for the second category to true.

    def categorize_type1(self):
        """
        Implements the categorization of type 1 problems.
        The problems will be split up into two lists for each category.
        The problems with A and B in the first premise are in the first list, the
        other problems are in the second list.
        The lists will then be evaluated with regard to their precision. Since the
        list only contain the answers of the participants, the correctness of the
        given participant will be checked. If the participant makes a lot of errors
        in a certain category or problem type, the corresponding parameters are
        set to be used in the predict function.
        """
        ab_cat = [] # category for the problems that start with a/b
        cd_cat = [] # category for the problems that start with c/d
        for prob_ans in self.problem_type1:
            rel_prob = self.convert_premises(deepcopy(prob_ans[0].task)) # get the problem premise
            # check if the first premise contains A and B
            if (rel_prob[0][0] == "B" and rel_prob[0][2] == "A") or (
                    rel_prob[0][0] == "A" and rel_prob[0][2] == "B"):
                ab_cat.append(prob_ans) #in this list only the answer and correct answer matter
            else: cd_cat.append(prob_ans)
        ab_precision = self.evaluate_cat(ab_cat)
        cd_precision = self.evaluate_cat(cd_cat)
        overall_precision = self.evaluate_cat(ab_cat + cd_cat)
        if ab_precision >= 0 and cd_precision >= 0:
            if overall_precision <= 0.30:
                self.cat_params[0][2] = True
            elif ab_precision - cd_precision >= 0.6 and overall_precision <= 0.8:
                self.cat_params[0][0] = True # set the parameter for the first(1) category to true.
            elif cd_precision - ab_precision >= 0.6 and overall_precision <= 0.8:
                self.cat_params[0][1] = True # set the parameter for the first(2) category to true.

    @staticmethod
    def evaluate_cat(category_list):
        """
        Checks the answers to all the given problems in the category.
        Parameters
        ----------
        category_list: list
            contains lists of the form [problem, answer, correct_anser] as list item.
        Returns
            the precision value of the participant in this category as float
        """
        if not category_list:
            return -1 # return a special value if there is no problem in the category_list
        precision_counter = 0.0
        for prob in category_list:
            if prob[1] == prob[2]:
                precision_counter += 1
        return precision_counter / len(category_list) # compute precision value

    @staticmethod
    def convert_premises(premises):
        """
        Converts all premises in the given list into a format that the spatial model can use.
        Parameters
        ----------
        premises: list
            contains premises represented as lists.
        Returns
            the premise list with the premises in the correct format for the
            spatial model.
        """
        for rel_prem in premises:
            relation = rel_prem[0]
            rel_prem[0] = rel_prem[1]
            rel_prem[1] = relation
        return premises


    def invert_premises(self, premises):
        """
        Converts all relations of the given premise list. The premises have to be
        converted to the format (object1 relatoin object2) before.
        Parameters
        ----------
        premises: list
            contains premises represented as lists.
        Returns
            the list of premises with inverted relation.
        """
        for rel_prob in premises:
            rel_prob = self.invert_premise(rel_prob)
        return premises

    @staticmethod
    def invert_premise(rel_prob):
        """
        inverts the relation of the given premise
        Parameters
        ----------
        premise: list
            contains the first object, the relation and the second object.
            (e.g. [object1, relation, object2])
        Returns
            the premise with the inverted relation.
        *Caution*: Only inverts Left and Right, not other relations.
        """
        if rel_prob[1] == "Right":
            rel_prob[1] = "Left"
        elif rel_prob[1] == "Left":
            rel_prob[1] = "Right"
        return rel_prob
