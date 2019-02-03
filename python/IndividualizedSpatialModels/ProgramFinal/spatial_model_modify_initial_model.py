'''
Module for a individualized spatial model to be used in the CCOBRA Framework.
Each individualized model uses one or more individualizations implemented in the
modified spatial model.
This Module uses the 'modify initial model' individualization.

@author: Christian Breu <breuch@web.de>
'''
from copy import deepcopy

import ccobra

import main_module_param


class SpatialModelParam(ccobra.CCobraModel):
    """
    Model to test the individualization, which is responsible for the modification
    of the initially build model. If the individualization is active, the model
    will be modified in order to further verify the initial conclusion made with
    the initital model. The individualization can be activated in the adapt function.
    The individualization can be activated and deactivated dynamically. The rating
    and prior values need to be over a specified threshold, to activate the
    individualization.
    """
    # list for the previously given answers by the model
    previous_model_ans = []
    # Variable for the parameter assignment for the spatial model
    parameter_assignment = [[False, False, False, False, False, False],
                            [False, False, False, False, False]]
    # rating value for the individualization
    ind_rating = 0
    # prior of the individualization
    ind_rating_prior = 0

    def __init__(self, name='SpatialModelModify'):
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
        Resets the  individualization's rating, activation and the stored problem answers.

        **Attention**: Should reset the internal state of the model.

        """
        # reset the stored answers of the spatial model for each participant
        self.previous_model_ans = []
        # reset the parameters for the next participant
        self.parameter_assignment = [[False, False, False, False, False, False],
                                     [False, False, False, False, False]]
        # reset the rating of the individualization.
        self.ind_rating = 0

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

        configurations for the experiments:
            -premiseorder: (20 * self.ind_rating_prior) >= 0.8, gains +0.2/-0.1
            -figural: no configuration possible/no gains
            -verification: (10 * self.ind_rating_prior) >= 0.8, gain +0.2/-0.1
            -singlechoice:
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
            ans_ind = self.predict(item, [[False, False, False, False, False, False],
                                          [False, False, True, False, False]])
            # check if the answer would be correct now:
            if ans_ind == target:
                # now add something to the rating of the individualisation
                self.ind_rating += 0.2
                #print("increase rating", self.ind_rating)
            else:
                # decrease the rating of the individualisaitons
                if self.ind_rating >= 0.1:
                    #print("decrease rating", self.ind_rating)
                    self.ind_rating -= 0.1
            if self.ind_rating + (20 * self.ind_rating_prior) >= 0.8:
                #print("individualization activated")
                self.parameter_assignment[1][2] = True
            else:
                #print("deactivate individualization")
                self.parameter_assignment[1][2] = False

    def pre_train(self, dataset):
        """
        In the pre_train function, a prior value for all individualizations will
        be computed. The prior value represents, how often the corresponding
        individualization was able to correct the answer of the original model.
        This function works similarily to the adapt function, but the rating will
        be a counter for the corrected answers by the individualization, for each
        participant. An altered adapt function will be used to just use the rating
        as a counter. The rating_prior will be used as a global counter over all
        participants, since the rating(counter) is reseted for each participant.
        The pre_train function uses a given set of problems and answers for
        several participants. The prior will be computed using all these data,
        so it this a general pre tuning for the model.

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
            self.ind_rating_prior += self.ind_rating
            self.ind_rating = 0 # reset the rating counter
        self.ind_rating_prior /= (len(dataset) * len(part_data))
        print("rating after pretrain ", self.ind_rating_prior)

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
            ans_ind = self.predict(item, [[False, False, False, False, False, False],
                                          [False, False, True, False, False]])
            # check if the answer would be correct now:
            if ans_ind == target:
                # now add something to the rating of the individualisation
                self.ind_rating += 1
