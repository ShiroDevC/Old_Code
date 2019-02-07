'''
Module for a individualized spatial model to be used in the CCOBRA Framework.
Each individualized model uses one or more individualizations implemented in the
modified spatial model.
This Module uses the 'premise three misinterpreted' and the 'premise two misinterpreted'
individualization.

@author: Christian Breu <breuch@web.de>
'''
from copy import deepcopy

import ccobra

from spatial_reasoner import main_module_param

class SpatialModelParam(ccobra.CCobraModel):
    """
    Model to test the premise three misinterpreted and premise two misinterpreted individualizations
    in combination. The individualizations can be activated and deactivated dynamically.
    The rating and prior values need to be over a specified threshold,
    to activate an individualization.
    The combination of both individualizations will be used like a new, single
    individualization and can therefore become activated independent from the
    other individualizations.
    """
    # list for the previously given answers by the model
    previous_model_ans = []
    # Variable for the parameter assignment for the spatial model
    parameter_assignment = [[False, False, False, False, False, False],
                            [False, False, False, False, False]]
    # rating value for the Premise3Understand individualisation
    ind_rating_prem3 = 0
    ind_rating_prior_prem3 = 0
    # rating for verbal memory
    ind_rating_prem2 = 0
    ind_rating_prior_prem2 = 0
    # rating for prem3Understand and VerbMem
    ind_rating_pr3pr2 = 0
    ind_rating_prior_pr3pr2 = 0

    def __init__(self, name='SpatialModelPrem3+2'):
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
        self.previous_model_ans = []
        # reset the parameters for the next participant
        self.parameter_assignment = [[False, False, False, False, False, False],
                                     [False, False, False, False, False]]
        self.ind_rating_prem3 = 0
        self.ind_rating_prem2 = 0
        #self.ind_rating_prior

    def predict(self, item, parameters=None, **kwargs):
        """ Generates a prediction based on a given task item.
        Can make a prediction with verify and single-choice tasks.
        The prediction will be made with the spatial model with individualizations.
        The spatial model takes a list of activation parameters. With these parameters,
        the spatial model will perform the task and return an appropriate answer.
        Depending on the task type, different answer types are returned(see below)
        Parameters
        ----------
        item : ccobra.data.Item
            Task item container. Holds information about the task, domain,
            response type and response choices.

        parameters : list
            The list with the activation values for all the individualizations
            in the model. (e.g., [[False, False, False, False, False, False],
            [False, False, False, False, False]]).

        Returns
        -------
        list(str)
            Single-choice relational response in list representation (e.g.,
            ['A', 'left', 'B']) or a verification relational response in Boolean
            representation.

        """
        if parameters is None: # no parameters were given, use the current general assignment.
            parameters = self.parameter_assignment
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
            # is different.
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
            answer = spatial_model.interpret_spatial2exp_parameters(rel_prob, deepcopy(parameters))
            # store the answer given by the model for later use in the adapt function.
            self.previous_model_ans.append(answer)
            return answer
        # for all verification problems the standard function will be called from the
        # spatial model. The format of the question premises is different, that's
        # why the conversion is different.
        rel_questions = deepcopy(item.choices[0]) # get the question premise
        for rel_pre in rel_questions:
            relation = rel_pre[0]
            rel_pre[0] = rel_pre[1]
            rel_pre[1] = relation
            rel_prob.append(rel_pre)
        answer = spatial_model.interpret_spatial_parameters(rel_prob, deepcopy(parameters))
        # store the answer given by the model for later use in the adapt function.
        self.previous_model_ans.append(answer)
        return answer

    def adapt(self, item, target, **kwargs):
        """This function will rate the effect of the individualizations used in the
        model on the current task. The individualizations will only be rated, if the
        answer given by the model and the participant is different. The model will
        make the previous prediction again with the activated individualization. If
        the answer is now the same as the participant answer, the rating will be increased.
        If the answer is still different, the rating will be decreased.
        After all individualzations are rated, they will be activaed or deactivated
        depending on their rating and their prior value, which is computed in the
        pretrain function. For the activation of an individualization, a threshold
        has to be passed( e.g. rating + x * prior >= threshold; where x is a multiplicator,
        to give the prior a certain weight)
        For each individualization and each experiment, the threshold, x and the
        gains of the rating(positive and negative) need to be optimized, to use
        the individualization only, and only if the model benefits from it.
        The combination of individualizations also have their own rating, prior and
        threshold to be activated separately from the other single individualizations.

        configurations for the experiments(for the combination):
            -figural: (2 * self.ind_rating_prior_pr3pr2) >= 1.1, gains +0.1/-0.1
            -premiseorder: (0.5 * self.ind_rating_prior_pr3pr2) >= 1.2, gains +0.1/-0.1
            -singlechoice: (2 * self.ind_rating_prior_pr3pr2) >= 1.0, gains +0.1/-0.1
        Parameters
        ----------
        item : ccobra.data.Item
            Task information container. Holds the task text, response type,
            response choices, etc.

        target : str
            True response given by the human reasoner.

        """
        # first of all, check if the answer was correct with regard to the participant answer
        if target != self.previous_model_ans[-1]:
            # compute the answer that the model would've given with the individualisation
            #### check what individualization produces which answer ####
            ans_ind_prem3 = self.predict(item, [[False, False, False, False, True, False],
                                                [False, False, False, False, False]])
            ans_ind_prem2 = self.predict(item, [[False, False, True, False, False, False],
                                                [False, False, False, False, False]])
            # Compute the answer with both individualizations combined.
            ans_ind_pr3pr2 = self.predict(item, [[False, False, True, False, True, False],
                                                 [False, False, False, False, False]])

            #### change the ratings of the individualizations ####
            # check if the answer would be correct now:
            ## Prem3Understand
            if ans_ind_prem3 == target:
                # now add something to the rating of the individualisation
                self.ind_rating_prem3 += 0.1
                #print("increase rating", self.ind_rating)
            else:
                # decrease the rating of the individualisaitons
                if self.ind_rating_prem3 >= 0.1:
                    #print("decrease rating")
                    self.ind_rating_prem3 -= 0.1
            ## VerbMem
            if ans_ind_prem2 == target:
                # now add something to the rating of the individualisation
                self.ind_rating_prem2 += 0.2
                #print("increase rating", self.ind_rating)
            else:
                # decrease the rating of the individualisaitons
                #print("should decrease")
                if self.ind_rating_prem2 >= 0.1:
                    #print("decrease rating", self.ind_rating)
                    self.ind_rating_prem2 -= 0.1
            ## Combination of Prem3 and VerbMem
            if ans_ind_pr3pr2 == target:
                #print("increase combo", self.ind_rating_pr3pr2)
                self.ind_rating_pr3pr2 += 0.1
            else:
                if self.ind_rating_pr3pr2 >= 0.1:
                    #print("decrease combo", self.ind_rating_pr3pr2)
                    self.ind_rating_pr3pr2 -= 0.1
            #### check which individualization should be activated ####
            # The inds will be checked separately to know which one of them should be active alone.
            # The combination is checked later   (2 * self.ind_rating_prior_prem2) >= 1.0
            ## Prem3
            if self.ind_rating_prem3 + (0.5 * self.ind_rating_prior_prem3) >= 1.0:
                #print("individualization activated")
                self.parameter_assignment[0][4] = True
            elif self.ind_rating_prem3 + (0.5 * self.ind_rating_prior_prem3) < 1:
                #print("deactivate individualization")
                self.parameter_assignment[0][4] = False
            ## Prem2
            """ not used, because this individualization interfered with the others
            if self.ind_rating_prem2 + (20 * self.ind_rating_prior_prem2) >= 0.5:
                #print("individualization activated")
                self.parameter_assignment[0][2] = True #= [[False, False, False, False, False, False], [True, False]]
            else:
                #print("deactivate individualization")
                self.parameter_assignment[0][2] = False # = [[False, False, False, False, False, False], [False, False]]
            ## combination
            """
            if self.ind_rating_pr3pr2 + (0.5 * self.ind_rating_prior_pr3pr2) >= 1.2:
                #print("combination activated")
                self.parameter_assignment[0][4] = True
                self.parameter_assignment[0][2] = True
            else:
                # check if both individualizations should be activated alone
                if self.parameter_assignment[0][4] and self.parameter_assignment[0][2]:
                    #print("just use one of the inds")
                    # since both indiviudalizations (should) have the same result, just use prem3
                    self.parameter_assignment[0][4] = True
                    self.parameter_assignment[0][2] = False

    def pre_train(self, dataset):
        """
        In the pre_train function, a prior value for all individualizations will
        be computed. The prior value represents, how often the corresponding
        individualization was able to correct the answer of the original model.
        This function works similarly to the adapt function, but the rating will
        be a counter for the corrected answers by the individualization, for each
        participant. An altered adapt function will be used to just use the rating
        as a counter. The rating_prior will be used as a global counter over all
        participants, since the rating(counter) is reseted for each participant.
        The pre_train function uses a given set of problems and answers for
        several participants. The prior will be computed using all these data,
        so it this a general pre tuning for the model.
        For the combinations the prior will be computed in the same way as for
        the single individualizations.

        Parameters
        ----------
        dataset : list(list(dict(str, object)))
            Training data for the model. List of participants which each
            contain lists of tasks represented as dictionaries with the
            corresponding task information (e.g., the item container and
            given response).

        """
        for participant_data in dataset:
            part_data = deepcopy(participant_data) # refresh working copy of problems etx.
            # reset the parameter assignment for each participant
            self.parameter_assignment = [[False, False, False, False, False, False],
                                         [False, False, False, False, False]]
            self.previous_model_ans = []
            for problem_data in part_data:
                prob_item = problem_data['item'] # the data of the problem
                prob_ans = problem_data['response'] # the response from the participant
                self.predict(prob_item) # predict the answer with the currect parameters
                # call adapt_prior to check if the individualization
                # can change the result to the better
                self.adapt_prior(prob_item, prob_ans)
            self.ind_rating_prior_prem3 += self.ind_rating_prem3
            self.ind_rating_prior_prem2 += self.ind_rating_prem2
            self.ind_rating_prior_pr3pr2 += self.ind_rating_pr3pr2
            self.ind_rating_prem3 = 0 # reset the rating counter
            self.ind_rating_prem2 = 0
            self.ind_rating_pr3pr2 = 0
        self.ind_rating_prior_prem3 /= (len(dataset) * len(part_data))
        self.ind_rating_prior_prem2 /= (len(dataset) * len(part_data))
        self.ind_rating_prior_pr3pr2 /= (len(dataset) * len(part_data))
        print("rating after pretrain: prem3, prem2, pr3pr2 ", self.ind_rating_prior_prem3,
              self.ind_rating_prior_prem2, self.ind_rating_prior_pr3pr2)

    def adapt_prior(self, item, target):
        """
        This adapt function only counts the times when the individualization
        lead to a better result than the baseline. In the pre_train function this
        function will be used. Changes the self.ind_rating, to be used in the
        pre_train function.
        All priors are normed like this, because they represent a percentual value.
        In the adapt function of the model, this prior value will be used to decide
        whether to activate an individualization or not.
        In this function, no individualization will be activated or deactivated.
        The prior for combinations is counted and computed just like the other
        individualizations.

        Parameters
        ----------
        item : ccobra.data.Item
            Task information container. Holds the task text, response type,
            response choices, etc.

        target : str
            True response given by the human reasoner.

        """
        # first of all, check if the answer was correct with regard to the participant answer
        if target != self.previous_model_ans[-1]:
            # compute the answer that the model would've given with the individualisation
            ans_ind_prem3 = self.predict(item, [[False, False, False, False, True, False],
                                                [False, False, False, False, False]])
            ans_ind_prem2 = self.predict(item, [[False, False, True, False, False, False],
                                                [False, False, False, False, False]])
            # Compute the answer with both individualizations combined.
            ans_ind_pr3pr2 = self.predict(item, [[False, False, True, False, True, False],
                                                 [False, False, False, False, False]])
            # check if the answer would be correct now:
            if ans_ind_prem3 == target:
                self.ind_rating_prem3 += 1
            if ans_ind_prem2 == target:
                self.ind_rating_prem2 += 1
            if ans_ind_pr3pr2 == target:
                self.ind_rating_pr3pr2 += 1
