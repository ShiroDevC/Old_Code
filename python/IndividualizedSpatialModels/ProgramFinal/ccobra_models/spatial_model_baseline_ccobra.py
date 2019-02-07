'''
Module for the original spatial model to be used in the CCOBRA Framework.

@author: Christian Breu <breuch@web.de>
'''
from copy import deepcopy

import ccobra

from spatial_reasoner import main_module_param

class SpatialModelParam(ccobra.CCobraModel):
    """
    Model for the standard spatial model. To be compared with the individualizations
    in the framework. Does not use adapt or pretrain. all predictions will be made
    with the standard parameter assignment for the spatial model.
    """
    parameter_assignment = [[False, False, False, False, False, False],
                            [False, False, False, False, False]]

    def __init__(self, name='baseline spatial model'):
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
        # reset the parameters for the next participant
        self.parameter_assignment = [[False, False, False, False, False, False],
                                     [False, False, False, False, False]]

    def predict(self, item, **kwargs):
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
        Returns
        -------
        list(str)
            Single-choice relational response in list representation (e.g.,
            ['A', 'left', 'B']) or a verification relational response in Boolean
            representation.

        """
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
        return answer
