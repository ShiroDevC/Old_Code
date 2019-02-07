'''
This module contains helper programs for the categorization and parameter
approach. Different categorizations were tested with this program, to find
the most promising categories for the actual categories model.

The parameter approach helper program has a new and and old version.
In the old version, the model was not build by the actual model for
convenience. Since the parameters need to be tested, the new, current version
uses the modified spatial model.

Created on 19.10.2018

@author: Christian Breu <breuch@web.de>
'''
from copy import deepcopy

from spatial_reasoner import main_module_param as model

# answers for only type3 questions, to compare them to the results of the program
PARTICIPANT_ANSWERS_TYPE3 = [
    [True, True, True, True, True, True, False, False, True, False, False, False, False], #KGSKUR
    [False, False, False, True, True, False, False, False, True, False, False, False, False],#LXUFLN
    [True, True, False, False, False, True, False, True, False, False, False, False, True], #ENWSAZ
    [False, True, True, True, False, True, True, False, True, False, True, True, True], #NNUPMA
    [True, False, True, True, True, True, False, True, False, False, False, False, False], # IEIRGN
    [False, False, True, False, True, False, False, False, True, False, False, True, False], #FEOKVU
    [True, True, True, True, True, False, False, False, False, False, False, False, True], #XHNLNR
    [True, False, True, True, True, True, False, False, True, False, False, False, False], #EOJQYJ
    [False, True, True, True, False, False, True, False, False, True, True, False, False], #VHHVGU
    [True, True, True, True, True, False, False, False, True, False, True, False, False,], #ELHJLV
    [True, True, False, True, True, True, False, False, False, False, False, False, True], # ASSXHN
    [True, False, True, True, True, False, False, False, False, True, False, True, False], #KTXJOY
    [True, True, True, True, True, True, True, False, False, False, False, False, False], #IVEVKT
    [True, True, True, True, False, True, False, False, True, False, False, False, False], #EOAQQH
    [True, False, True, False, True, True, False, False, False, False, False, True, False], #WEJBNU
    [True, True, True, True, True, False, True, False, False, False, False, False, False], #EQHJFM
    [True, True, False, True, True, False, False, True, False, False, False, False, False], #LRBGVD
    [False, True, True, False, True, True, True, True, True, False, True, False, True], #OPCKOC
    [True, False, False, False, True, True, False, False, False, False, False, False, False],#HXKROE
    [True, True, True, False, True, True, True, False, True, False, True, True, True], #ONEKCK
    [False, True, True, True, True, True, True, True, True, True, False, False, True], #BWBJBN
    [False, False, True, False, True, True, False, True, True, False, True, False, False], #THRJGF
    [True, True, True, True, True, True, False, False, False, False, False, False, False], #EJPXUT
    [False, True, True, True, True, True, True, False, False, False, False, False, False], #BFYKHC
    [True, True, True, True, True, False, False, True, True, False, True, False, True], #QULZXT
    [True, True, True, True, True, True, False, False, False, False, False, False, False], #PEXVVU
    [True, True, True, True, True, True, True, True, True, True, False, False, False], #DRUXYQ
    [True, True, True, True, True, True, False, False, False, True, False, False, True], #WLRLDD
    [True, True, False, False, True, False, False, True, True, False, False, True, True], #GIGSBG
    [True, False, True, True, False, True, False, False, True, True, True, False, False], #ZARPVY
    [True, True, False, True, True, False, False, False, False, False, False, True, False] #OAZMWE
    ]

# first 16 answers are type1, after that type2
PARTICIPANT_ANSWERS_TYPE12 = [
    [True, True, True, True, True, True, True, True, False, False, False,
     False, False, False, False, False, True, True, True, True, True, True,
     True, True, False, False, False, False, False, False, False, False], #KGSKUR
    [True, True, True, False, True, True, True, False, True, False, True,
     True, True, False, False, False, False, False, True, True, True, True,
     True, True, True, True, False, True, False, False, True, False], #LXUFLN
    [True, True, False, False, False, True, True, True, False, True, False,
     False, False, False, True, False, True, False, True, False, False, False, True,
     True, True, True, False, False, False, False, True, True], #ENWSAZ
    [False, True, True, True, False, True, True, True, True, True, False,
     True, True, False, False, True, True, True, True, False, True, False,
     True, True, True, True, False, False, True, True, False, False], #NNUPMA
    [True, True, True, True, True, True, True, True, False, False, False, False,
     False, False, False, False, True, True, True, True, False, True, True, True,
     False, False, False, False, False, False, False, False], #IEIRGN
    [False, False, True, False, True, True, True, True, True, False, False,
     False, True, False, True, False, False, True, False, False, False, True,
     False, False, True, False, True, True, True, False, True, True], #FEOKVU
    [True, True, True, True, True, True, True, True, True, False, False,
     False, False, False, False, False, True, False, True, True, True, True,
     True, True, True, True, False, False, True, False, False, False], #XHNLNR
    [True, False, True, True, True, True, True, True, True, False, False, False,
     True, True, False, False, False, True, True, True, True, True, True, True,
     False, False, True, False, False, False, False, False], #EOJQYJ
    [True, True, True, False, True, True, False, True, False, True, False, True,
     True, True, False, True, False, True, True, False, False, False, False,
     False, False, True, True, False, True, True, True, True], #VHHVGU
    [True, True, True, True, True, True, True, True, False, False, False, False,
     False, False, False, False, True, True, True, True, False, False, True,
     True, False, False, True, False, False, False, True, True], #ELHJLV
    [True, True, True, True, True, True, True, True, True, False, False, True,
     False, False, True, False, True, True, True, True, True, True, True, True,
     True, True, False, True, False, False, False, True], #ASSXHN
    [True, True, True, True, False, True, True, True, True, False, True, False,
     False, False, True, False, True, True, True, True, True, True, True, False,
     False, False, False, False, False, False, False, False], #KTXJOY
    [True, True, True, True, True, True, True, True, False, False, False, False,
     False, False, False, False, True, True, True, True, True, True, True, True,
     False, False, False, False, False, False, False, False], #IVEVKT
    [True, True, True, True, True, True, True, False, False, False, False, False,
     False, False, False, False, True, True, True, True, True, True, True, True,
     False, False, False, False, True, False, False, False], #EOAQQH
    [True, True, True, True, True, True, False, False, True, True, True, True,
     True, False, True, True, True, True, True, False, False, False, False,
     True, False, True, False, True, True, False, False, False], #WEJBNU
    [True, True, True, False, True, False, False, True, False, False, True, True,
     False, True, True, False, False, True, False, False, True, False, True, True,
     True, True, True, True, False, False, True, False], #EQHJFM
    [True, True, True, True, True, True, True, True, True, False, False, False,
     False, False, False, False, True, True, True, True, True, False, True, True,
     False, False, True, False, False, False, False, False], #LRBGVD
    [True, False, True, False, True, True, True, True, False, True, False, True,
     False, False, True, False, True, True, False, False, True, False, True,
     True, True, False, True, False, True, False, False, True], #OPCKOC
    [True, True, True, True, False, True, True, True, False, False, True, False, True,
     False, True, False, True, True, True, True, True, False, True, True, True, True,
     False, True, False, True, True, False], #HXKROE
    [True, False, True, True, False, True, True, True, False, True, False, True,
     False, False, False, False, True, True, True, False, True, False, False,
     False, True, True, False, True, False, False, False, False], #ONEKCK
    [True, False, False, True, True, False, True, False, False, True, True,
     True, True, True, False, True, True, True, False, True, True, False, False,
     True, True, True, True, True, False, False, False, False], #THRJGF
    [True, True, True, False, True, True, True, True, False, False, False, False,
     False, False, False, False, True, True, True, True, True, True, True, True,
     False, False, False, False, False, False, False, False], #EJPXUT
    [True, True, True, True, True, True, True, True, False, False, False, False,
     False, False, False, False, False, True, True, True, False, True, True,
     False, False, False, False, False, False, False, False, True], #BFYKHC
    [True, True, True, False, False, True, True, False, False, False, False, True,
     False, False, False, False, True, True, True, False, False, True, False,
     True, False, False, True, False, False, False, False, False], #QULZXT
    [True, True, True, True, True, True, True, True, False, False, True,
     False, False, False, False, True, True, True, True, True, True, True, True,
     True, False, False, True, False, False, False, False, False], #PEXVVU
    [False, True, True, False, True, True, True, True, True, False, False, True,
     False, False, False, True, True, False, True, True, True, True, False,
     False, False, False, True, False, False, True, False, False], #DRUXYQ
    [True, True, True, True, True, True, False, False, False, False, True, False,
     True, False, False, False, False, True, True, True, True, True, True, True,
     False, False, True, False, True, True, False, False], #WLRDLDD
    [False, False, True, False, True, False, False, True, False, True, False,
     True, False, False, True, True, True, False, False, False, False, True,
     True, False, False, True, True, False, True, True, False, True], #GIGSBG
    [False, False, False, True, True, True, False, True, False, True, False,
     True, True, False, True, False, True, False, False, True, True, False,
     False, False, False, False, True, True, True, True, True, False], #ZARPVY
    [True, True, True, True, True, True, True, True, False, False, False, False,
     False, False, False, False, True, True, True, True, True, False, True, True,
     False, False, False, True, False, False, False, False] #OAZMWE
    ]

#Ground Truth for all Problems from Type 3
GROUND_TRUTH3 = [True, True, True, True, True, True, False, False, False,
                 False, False, False, False]
# Premises are now coded as Object1, relation, Object2. Order is the same as PROBLEMS_TYPE3
# Problems of type3, startmod and combine contained
PROBLEMS_TYPE3 = [
    [["A", "L", "B"], ["C", "L", "D"], ["B", "L", "C"], ["A", "L", "D"]], #1 ID: 18
    [["C", "L", "D"], ["A", "L", "B"], ["B", "L", "C"], ["A", "L", "D"]], #1 ID: 21
    [["D", "R", "C"], ["B", "R", "A"], ["C", "R", "B"], ["A", "L", "D"]], #1 ID: 63
    [["A", "L", "B"], ["C", "L", "D"], ["B", "L", "C"], ["D", "R", "A"]], #1 ID: 66
    [["C", "L", "D"], ["A", "L", "B"], ["B", "L", "C"], ["D", "R", "A"]], #1 ID: 69
    [["D", "R", "C"], ["B", "R", "A"], ["C", "R", "B"], ["D", "R", "A"]], #1 ID: 111
    [["A", "L", "B"], ["C", "L", "D"], ["B", "L", "C"], ["D", "L", "A"]], #0 ID: 114
    [["C", "L", "D"], ["A", "L", "B"], ["B", "L", "C"], ["D", "L", "A"]], #0 ID: 117
    [["D", "R", "C"], ["B", "R", "A"], ["C", "R", "B"], ["D", "L", "A"]], #0 ID: 159
    [["A", "L", "B"], ["C", "L", "D"], ["B", "L", "C"], ["A", "R", "B"]], #0 ID: 162
    [["C", "L", "D"], ["A", "L", "B"], ["B", "L", "C"], ["A", "R", "B"]], #0 ID: 165
    [["B", "R", "A"], ["D", "R", "C"], ["B", "R", "C"], ["A", "R", "B"]], #0 ID: 204
    [["D", "R", "C"], ["B", "R", "A"], ["C", "R", "B"], ["A", "R", "B"]], #0 ID: 207
    ]
GROUND_TRUTH12 = [True, True, True, True, True, True, True, True, False, False, False,
                  False, False, False, False, False, True, True, True, True, True,
                  True, True, True, False, False, False, False, False, False, False, False]


# Problems of type 1 and 2, startmod and insert contained
PROBLEMS_TYPE12 = [
    # Typ 1
    [["A", "L", "B"], ["B", "L", "C"], ["C", "L", "D"], ["A", "L", "D"]], #1 ID: 17
    [["C", "L", "D"], ["B", "L", "C"], ["A", "L", "B"], ["A", "L", "D"]], #1 ID: 22
    [["B", "R", "A"], ["C", "R", "B"], ["D", "R", "C"], ["A", "L", "D"]], #1 ID: 59
    [["D", "R", "C"], ["C", "R", "B"], ["B", "R", "A"], ["A", "L", "D"]], #1 ID: 64
    [["A", "L", "B"], ["B", "L", "C"], ["C", "L", "D"], ["D", "R", "A"]], #1 ID: 65
    [["C", "L", "D"], ["B", "L", "C"], ["A", "L", "B"], ["D", "R", "A"]], #1 ID: 70
    [["B", "R", "A"], ["C", "R", "B"], ["D", "R", "C"], ["D", "R", "A"]], #1 ID: 107
    [["D", "R", "C"], ["C", "R", "B"], ["B", "R", "A"], ["D", "R", "A"]], #1 ID: 112
    [["A", "L", "B"], ["B", "L", "C"], ["C", "L", "D"], ["D", "L", "A"]], #0 ID: 113
    [["C", "L", "D"], ["B", "L", "C"], ["A", "L", "B"], ["D", "L", "A"]], #0 ID: 118
    [["B", "R", "A"], ["C", "R", "B"], ["D", "R", "C"], ["D", "L", "A"]], #0 ID: 155
    [["D", "R", "C"], ["C", "R", "B"], ["B", "R", "A"], ["D", "L", "A"]], #0 ID: 160
    [["A", "L", "B"], ["B", "L", "C"], ["C", "L", "D"], ["A", "R", "B"]], #0 ID: 161
    [["C", "L", "D"], ["B", "L", "C"], ["A", "L", "B"], ["A", "R", "B"]], #0 ID: 166
    [["B", "R", "A"], ["C", "R", "B"], ["D", "R", "C"], ["A", "R", "B"]], #0 ID: 203
    [["D", "R", "C"], ["C", "R", "B"], ["B", "R", "A"], ["A", "R", "B"]], #0 ID: 208

    # Typ 2
    [["B", "L", "C"], ["A", "L", "B"], ["C", "L", "D"], ["A", "L", "D"]], #1 ID: 19
    [["B", "L", "C"], ["C", "L", "D"], ["A", "L", "B"], ["A", "L", "D"]], #1 ID: 20
    [["C", "R", "B"], ["B", "R", "A"], ["D", "R", "C"], ["A", "L", "D"]], #1 ID: 61
    [["C", "R", "B"], ["D", "R", "C"], ["B", "R", "A"], ["A", "L", "D"]], #1 ID: 62
    [["B", "L", "C"], ["A", "L", "B"], ["C", "L", "D"], ["D", "R", "A"]], #1 ID: 67
    [["B", "L", "C"], ["C", "L", "D"], ["A", "L", "B"], ["D", "R", "A"]], #1 ID: 68
    [["C", "R", "B"], ["B", "R", "A"], ["D", "R", "C"], ["D", "R", "A"]], #1 ID: 109
    [["C", "R", "B"], ["D", "R", "C"], ["B", "R", "A"], ["D", "R", "A"]], #1 ID: 110
    [["B", "L", "C"], ["A", "L", "B"], ["C", "L", "D"], ["D", "L", "A"]], #0 ID: 115
    [["B", "L", "C"], ["C", "L", "D"], ["A", "L", "B"], ["D", "L", "A"]], #0 ID: 116
    [["C", "R", "B"], ["B", "R", "A"], ["D", "R", "C"], ["D", "L", "A"]], #0 ID: 157
    [["C", "R", "B"], ["D", "R", "C"], ["B", "R", "A"], ["D", "L", "A"]], #0 ID: 158
    [["B", "L", "C"], ["A", "L", "B"], ["C", "L", "D"], ["A", "R", "B"]], #0 ID: 163
    [["B", "L", "C"], ["C", "L", "D"], ["A", "L", "B"], ["A", "R", "B"]], #0 ID: 164
    [["C", "R", "B"], ["B", "R", "A"], ["D", "R", "C"], ["A", "R", "B"]], #0 ID: 205
    [["C", "R", "B"], ["D", "R", "C"], ["B", "R", "A"], ["A", "R", "B"]], #0 ID: 206
    ]

#---------------------------------------------------------------------------------
#################Categories approach##########################
#---------------------------------------------------------------------------------

######## Categories for the tasks       ############
#All 4 Categories for type3 tasks: 3AD, 3AB, 3CD, 3CB
# has all indices of the tasks/answers in the category
CAT_TYPE31 = [[0, 3, 6], [9, 11], [1, 2, 4, 5, 7, 8], [10, 12]]
# All 4 Categories for type3 tasks: 3A1, 3A0, 3C1, 3C0
# New Approach with the categories
CAT_TYPE32 = [[0, 6, 11], [3, 9], [1, 5, 7, 12], [2, 4, 8, 10]]
# New approach: categories: 3AR,3AL,3CR,3CL
CAT_TYPE33 = [[3, 11], [0, 6, 9], [2, 5, 8, 12], [1, 4, 7, 10]]
# New approach: categories: 3R1,3R0,3L1,3L0
CAT_TYPE34 = [[5, 11, 12], [2, 8], [0, 1, 6, 7], [3, 4, 9, 10]]


#All 4 Categories for type2 tasks: 22D, 22B, 23D, 23B
# has all indices of the tasks/answers in the category
CAT_TYPE21 = [[17, 18, 21, 22, 25, 26], [29, 30], [16, 19, 20, 23, 24, 27], [28, 31]]
# All 4 Categories for type3 tasks: 2A1, 2A0, 2D1, 2D0
CAT_TYPE22 = [[16, 22, 24, 30], [18, 20, 26, 28], [17, 23, 25, 31], [19, 21, 27, 29]]
# new approach: categories: 21R,21L,20R,20L
CAT_TYPE23 = [[22, 23, 30, 31], [16, 17, 24, 25], [18, 19, 26, 27], [20, 21, 28, 29]]
#All 4 Categories for type1 tasks: 11D, 11B, 10D, 10B
# has all indices of the tasks/answers in the category
CAT_TYPE11 = [[1, 2, 5, 6, 9, 10], [13, 14], [0, 3, 4, 7, 8, 11], [12, 15]]
# All 4 Categories for type3 tasks: 1A1, 1A0, 1C1, 1C0
CAT_TYPE12 = [[0, 6, 8, 14], [2, 4, 10, 12], [1, 7, 9, 15], [3, 5, 11, 13]]
# All 4 Categories for type3 tasks: 11A,11C,10A,10C
CAT_TYPE13 = [[2, 6, 10, 14], [1, 5, 9, 13], [0, 4, 8, 12], [3, 7, 11, 15]]

########## task categories ###########

def evaluate_cats(participant12, participant3, cat1, cat2, cat3):
    """Evaltuates the answers of the given participant with the ground truth.
    For each of the given Categories, iterates over each list and checks the
    participant answers with the ground truth at the specified indices in the
    category list. The distinction into 3 categories is for the task types, within
    those task type categories there are 4 sub categories. The full answer Set of
    the participant is needed.(First Version of categories, 1.11)
    In addition to the evaluation, the function also stores all correct and wrong
    problem's ids into a correct and an incorrect problems list. The structure
    corresponds to the precision values list, so the i-th element is for the i-th
    participant. There is a list for each category and instead of the precision value,
    there are the correct and incorrect lists.
    The function returns a tuple (precision values per category, correct/wrong answers per cat)
    """
    result_prob_ans = [] # list for all correct and wrong problems for each vp, like result_all_cat
    result_all_cat = [] #the complete results of 12 values for all 12 categories
    # category for type 1 problems
    result_cat = [] # list for results of one category
    result_ans_cat = [] #correct + incorrect problem ids for a category
    for cat in cat1:
        sub_cat_correct = 0# counter for correct answers
        cor_inc = [[], []]# list for all correct/incorrect ans
        for i in cat: #all indices in the current subcategory
            #print("answer: ", )
            if participant12[i] == GROUND_TRUTH12[i]:
                sub_cat_correct += 1
                cor_inc[0].append(i) #add the id to the correct answers list
            else: cor_inc[1].append(i) #add it to incorrect answers list
        sub_cat_correct /= len(cat)
        result_cat.append(round(sub_cat_correct, 2))
        result_ans_cat.append(cor_inc) #add all correct/incorrect probs to cat_list
    result_all_cat.append(result_cat)
    result_prob_ans.append(result_ans_cat)
    # category for type 2 problems
    # Reset the lists!
    result_cat = []
    result_ans_cat = [] #correct + incorrect problem ids for a category
    for cat in cat2:
        sub_cat_correct = 0
        cor_inc = [[], []]# list for all correct/incorrect ans
        for i in cat: #all indices in the current subcategory
            if participant12[i] == GROUND_TRUTH12[i]:
                sub_cat_correct += 1
                cor_inc[0].append(i) #add the id to the correct answers list
            else: cor_inc[1].append(i) #add it to incorrect answers list
        sub_cat_correct /= len(cat)
        result_cat.append(round(sub_cat_correct, 2))
        result_ans_cat.append(cor_inc) #add all correct/incorrect probs to cat_list
    result_all_cat.append(result_cat)
    result_prob_ans.append(result_ans_cat)
    # Category 3; Reset lists
    result_cat = []
    result_ans_cat = [] #correct + incorrect problem ids for a category
    for cat in cat3:
        sub_cat_correct = 0
        cor_inc = [[], []]# list for all correct/incorrect ans
        for i in cat: #all indices in the current subcategory
            if participant3[i] == GROUND_TRUTH3[i]:
                sub_cat_correct += 1
                cor_inc[0].append(i) #add the id to the correct answers list
            else: cor_inc[1].append(i) #add it to incorrect answers list
        sub_cat_correct /= len(cat)
        result_cat.append(round(sub_cat_correct, 2))
        result_ans_cat.append(cor_inc) #add all correct/incorrect probs to cat_list
    result_all_cat.append(result_cat)
    result_prob_ans.append(result_ans_cat)
    return (result_all_cat, result_prob_ans)

def evaluate_all_cats(cat1, cat2, cat3):
    """Evaluates all participants in the 3 given categories. calls evaluate_cat
    for all participants. Returns a tuple which contains a list of all evaluation results
    and a list of all correct/wrong answers for all those evaluation results. One Element of
    this list corresponds to one participant with 12 results. Prints out all results
    for all the participants. Returns a tuple with the list of all precision values for
    the categories for all participant and with the list of all correct/wrong answers for problems
    when the precision is not 1.0 or 0.0.
    """
    all_res = [] # list for the results of all vp
    all_corr = [] # list for all the correct/incorrect problems wich are returned by evaluate cats
    print("Type1: 11A,11C,10A,10C |Type2: 2A1,2A0,2D1,2D0 |Type3: 3A1,3A0,3C1,3C0")
    #iterate over all vps
    for i, vp_ in enumerate(PARTICIPANT_ANSWERS_TYPE12):
        vp_res = evaluate_cats(vp_, PARTICIPANT_ANSWERS_TYPE3[i], cat1, cat2, cat3)
        all_res.append(vp_res[0])
        all_corr.append(vp_res[1])
        #print(vp_res[0])
    return (all_res, all_corr)

def check_all_categories(all_vp_precision, all_cor_inc):
    """Function that calls check_categories on all participants and prints the answer
    precision along with the category check results for the categories that aren't
    completely correct/wrong. Returns the list of all results from check_categories for
    all participant precisions that were given. Has to be called with the result of
    evaluate_all_cats. The results will be printed aswell.
    """
    all_cat_check = [] #result list for all category checks
    # iterates over the vp_precision and the corresponding list of correct/incorrect problems ids
    for i, vp_prec in enumerate(all_vp_precision):
        cat_check = check_categories(vp_prec, all_cor_inc[i])
        print(i, "id ", vp_prec)
        print(i, "id ", cat_check)
        all_cat_check.append(cat_check)
    return all_cat_check

def check_categories(vp_precision, cor_inc_probs):
    """Function to check all precision values for a given participant. vp_precision
    is the result of the evaluate_cats function. Checks each precision value. If a
    value is not 1.0 or 0.0, the function will find out which of the problems are
    correct and incorrect(out of the given list). Then those correct and incorrect
    problems will be compared.
    Returns a list of all different premise's ids(0 or 1, see compare_problems).
    """
    diff_list = [] #all differences of the categories
    #first, iterate over the vp_precision list(over the categories)
    for i, cat_precision in enumerate(vp_precision):
        cats_diff = [] # differences list for each category, to make result more readable
        cor_inc_cat = cor_inc_probs[i] # all correct/wrong problems for this category
        problem_type3 = False # for later use when comparing the problems
        if i == 2: # change the problem type to 3, if the category is type3
            problem_type3 = True
        for k, prec_val in enumerate(cat_precision): # iterate over the precision values of category
            diff = [] #dummy list, if there is no difference, the list will be empty
            # this is for the readability of the resulting list.
            if prec_val not in (1.0, 0.0): #check if the precision is <1 and > 0
                # now compare the correct/wrong answers of this category
                #print("prec_val", prec_val)
                corr_inc_ans = cor_inc_cat[k]
                #print("correct/incorrect ids:", corr_inc_ans, "index of the category:", k, i)
                # call compare problems to get all differences for a given category
                corr_probs = fetch_problems(problem_type3, corr_inc_ans[0])
                inc_probs = fetch_problems(problem_type3, corr_inc_ans[1])
                diff = compare_problems(corr_probs, inc_probs)
            cats_diff.append(diff)
        diff_list.append(cats_diff)
    return diff_list

def fetch_problems(problem_type3, id_list):
    """helper function. Fetches all problems of the given type with the ids in the list.
    """
    fetched_problems = []
    if problem_type3:
        for id_ in id_list:
            fetched_problems.append(PROBLEMS_TYPE3[id_])
    else:
        for i in id_list:
            fetched_problems.append(PROBLEMS_TYPE12[i])
    return fetched_problems

def compare_problems(correct_probs, incorrect_probs):
    """Function that encodes all the premises of the given problems into their
    relation(l or r) by calling the encode_problemfunction.
    Then those encoded problems are compared. If two corresponding premises are
    not the same, the index of the premise(0 = premises 1-3; 1 = question premise)
    will be added to the result list.
    """
    differences_list = [] #list for all the indices where the encodings are different
    enc_cor_probs = [] #list for encoded problems to be compared later.
    enc_inc_probs = []
    for prob in correct_probs:#encode correct problems
        enc_cor_probs.append(encode_problem_rel(prob))
    for prob in incorrect_probs:#encode incorrect problems
        enc_inc_probs.append(encode_problem_rel(prob))
    # now compare all correctly answered problems with all wrong answered problems
    # iterate through all correct problems and compares them with all the incorrect ones
    # if there is a difference, the index of the difference will be added to the differences_list.
    for cor_prob in enc_cor_probs:
        for inc_prob in enc_inc_probs:
            for i, prem in enumerate(cor_prob): #iterate over the two problems to be checked
                if prem != inc_prob[i]: #check if there is a difference in the premises
                    differences_list.append(i)
    return differences_list

def encode_problem_rel(problem):
    """Function that takes a problem and returns a list with two relations. The first
    one resembles the relation 1-3, the second relation is the question relation.
    The premises will be encoded by the relation that they contain. There may be
    other possible encodings for the premises.
    """
    encoded_prob = []
    encoded_prob.append(problem[0][1])
    encoded_prob.append(problem[3][1])
    return encoded_prob

#---------------------------------------------------------------------------------
############ Parameters approach ############
#---------------------------------------------------------------------------------

def answer_question(model1, question):
    """Function returns True if the question premise holds in the model1 an False
    if it doesn't. First searches the two objects from the question and checks their
    coordinates. The answer will be given based on the relation of the question and
    the two objects in the question.
    Only checks for right and left relations(but 2-dimensional can be implemented).
    """
    obj1_coords = (0, 0)
    obj2_coords = (0, 0)
    for item in model1.items():
        # if one of the objects is found in the model1, take it's coordinates.
        if item[1] == question[0]:
            obj1_coords = item[0]
        elif item[1] == question[2]:
            obj2_coords = item[0]
    if (question[1] == "R" and obj1_coords[0] > obj2_coords[0]) or (
            question[1] == "L" and obj1_coords[0] < obj2_coords[0]):
        return True # the relation is r and the x coords are bigger -> correct
    return False # relation not satisfied

def understand_premise(premise, premise_correct=True):
    """Unnötig???
    Function returns the inverted premise, if parameter premise_correct is False.
    """
    pre = premise.copy()
    if not premise_correct:
        return invert_premise(pre)
    return pre

def invert_premise(premise):
    """returns the inverted premise.
    """
    pre = premise.copy()
    if pre[1] == "L":
        pre[1] = "R"
    elif pre[1] == "R":
        pre[1] = "L"
    return pre

def model_start(premise, modelstart_correct=True):
    """Creates a new Model with the given premise according to the relation
    between the objects. If the parameter modelstart_correct is False, the
    relation of the premise will be inverted. This simulates an error of the model1
    creation.
    Returns the model1 created with the given premise and correctness parameter.
    """
    # check if there should be an error, and if yes, inverts the relation.
    if not modelstart_correct:
        premise = invert_premise(premise)
    model1 = {} # create an empty dictionary for the model1
    if premise[1] == "L":
        # add the first object to the left of the second object
        model1[(0, 0)] = premise[0]
        model1[(1, 0)] = premise[2]
    elif premise[1] == "R":
        # add the first object to the right of the second object
        model1[(0, 0)] = premise[2]
        model1[(1, 0)] = premise[0]
    return model1

def model_insert(premise, mod, modelinsert_correct=True):
    """ToDo: Test schreiben
    Problem: what should happen if both items are not in the model1?
    Adds an object to a given model1, according to the relation given in the
    premise. Returns the model1 with the inserted object.
    If the first element of the premise is already in the model1, the relation needs
    to be inverted, because object1 is then e.g. to the right of object2. This
    means that a correct place for object2 will be to the left of object1. If it
    is the other way around, the relation must not be inverted.
    """
    model1 = mod.copy()
    # if the insert is not correct, the premise relation will be inverted.
    if not modelinsert_correct:
        premise = invert_premise(premise)
    # check if the first or second object of the premise is already in the model1.
    if premise[0] in model1.values():
        # the first element is in the model1; now find a correct place for the second.
        premise = invert_premise(premise) # invert the premise to search correctly.
        for item in model1.items():
            if item[1] == premise[0]:
                coords = item[0]
                # add the second object according to the premise
                # search the first free spot to add the item in dictionary
                free_coords = find_insert_spot(premise[1], model1, coords)
                model1[free_coords] = premise[2] # now add the object to the model1
                break
    elif premise[2] in model1.values():
        for item in model1.items():
            if item[1] == premise[2]:
                coords = item[0]
                free_coords = find_insert_spot(premise[1], model1, coords)
                model1[free_coords] = premise[0] # now add the object to the model1
                break
    else:
        print(model1, "premise", premise)
        print("none of the items in the premise could be found")
    return model1

def find_insert_spot(relation, model1, coordinates):
    """helper function for the model_insert function.
    iterates over the x or y axis to find the first free coordinates in the model1
    to satisfy the relation that is given. The function starts with the given coordinates
    which should be the coordinates of the item already in the model1.
    """
    rel_valx = 0 # the value to iterate in the model1 into a certain direction.
    rel_valy = 0 # the value to iterate in the model1 into a certain direction.
    if relation == "R": # go to the right
        rel_valx = 1
    elif relation == "L": # go to the left
        rel_valx = -1
    ### NOT NEEDED ATM ###
    elif relation == "A": # needs to be added to y-coordinates, above
        rel_valy = 1
    elif relation == "U": # "under"
        rel_valy = -1
    ### ####
    coord_x = coordinates[0] + rel_valx
    coord_y = coordinates[1] + rel_valy
    while (coord_x, coord_y) in model1:
        coord_x += rel_valx
        coord_y += rel_valy
    return (coord_x, coord_y)

def model_combine(premise, model1, model2, combine_correct=True):
    """Caution: only applicable for certain problems!(see inline comment below)
    Combines two models with the given premise. If the combine_correct parameter
    is false, the premise will be inverted, which will result in a wrong combination
    of the two models.
    Checks if the first item is in the first or second model. Depending on in which
    model the first object of the premise is, one of the two models will be added
    to the other one. All items of the model that will be added to the other model,
    will have an offset for their coordinates. The offset is usually the upper bound
    of the coordinates in the other model. In this case for one-dimensional problems
    and a specified model size, the simple offset of 2 or -2 can be used.
    """
    if not combine_correct:
        #print("invert premise combine")
        premise = invert_premise(premise)
    if premise[0] in model1.values() and premise[2] in model2.values():
        if premise[1] == "L": # add model2 to the right of model1
        # add all items from model2 to model1 with a specified offset
        # This offset will be 2 or -2 depending on the relation
        # Caution: this only works for models with the size 2 -> only these problems!!!
            for item in model2.items():
                # new coordinates with offset = 2
                coordinates = (item[0][0] + 2, item[0][1])
                model1[coordinates] = item[1] # add the item to model1
        elif premise[1] == "R": # add model2 to the left of model1
            for item in model2.items():
                # new coordinates with offset = -2
                coordinates = (item[0][0] - 2, item[0][1])
                model1[coordinates] = item[1] # add the item to model1
    # the other way around
    elif premise[2] in model1.values() and premise[0] in model2.values():
        if premise[1] == "L": # add model2 to the left of model1
            for item in model2.items():
                # new coordinates with offset = 2
                coordinates = (item[0][0] - 2, item[0][1])
                model1[coordinates] = item[1] # add the item to model1
        elif premise[1] == "R": # add model2 to the right of model1
            for item in model2.items():
                # new coordinates with offset = -2
                coordinates = (item[0][0] + 2, item[0][1])
                model1[coordinates] = item[1] # add the item to model1
    return model1

def verbal_memory(premises, question):
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
                    return True
                return False # prem has information contrary to the question
            if question[1] != prem[1]:
                #relation is not the same, check if the premise and question is inverted
                if question[2] == prem[0] and question[0] == prem[2]:
                    return True
                return False # prem has information contrary to the question
    return False # no premise could be found which contains the information to answer

def process_problem_type3(problem, error_param):
    """Function gets a problem as a list of premises and error parameters as a
    list of boolean values. The function calls all functions to process the task
    and uses the error parameters to compute an answer. All premises that will be
    used in the method will be first processed by understand_premise to check whether
    the premise should be inverted or not. Returns an answer to the problem as a boolean value.
    """
    prob = problem.copy()
    #process the first premise by calling understand premise and model_start
    model1 = model_start(understand_premise(prob[0], error_param[0]), error_param[1])
    #print(model1)
    # processes the second premise just like the first one(starts new model)
    model2 = model_start(understand_premise(prob[1], error_param[2]), error_param[3])
    #print(model2)
    # combine the previous models
    model3 = model_combine(understand_premise(prob[2], error_param[4]),
                           model1, model2, error_param[5])
    #print(model3)
    if error_param[6]:
        return verbal_memory(prob[:3], prob[3])
    return answer_question(model3, prob[3])

def process_problem_type1(problem, error_param):
    """Function gets a problem as a list of premises and error parameters as a
    list of boolean values. The function calls all functions to process the task
    and uses the error parameters to compute an answer. All premises that will be
    used in the method will be first processed by understand_premise to check whether
    the premise should be inverted or not. Returns an answer to the problem as a boolean value.
    """
    prob = problem.copy()
    #process the first premise by calling understand premise and model_start
    model1 = model_start(understand_premise(prob[0], error_param[0]), error_param[1])
    #print(model1)
    # the second premise will lead to an insert function
    model2 = model_insert(understand_premise(prob[1], error_param[2]), model1, error_param[3])
    #print(model2)
    # the third premise will also lead to an insert
    model3 = model_insert(understand_premise(prob[2], error_param[4]), model2, error_param[5])
    #print(model3)
    if error_param[6]:
        return verbal_memory(prob[:3], prob[3])
    return answer_question(model3, prob[3])

def process_problem(problem_type3, problem, error_param):
    """calls process_problem_type1 or process_problem_type3 according to the problem_type3
    boolean value. Returns the result from the function that was called.
    """
    # checks if the problem should be solved, by guessing(use same model regardless of problem)
    if error_param[7]:
        model1 = {(0, 0): 'A', (1, 0): 'B', (2, 0): 'C', (3, 0): 'D'}
        return answer_question(model1, problem[3])
    if problem_type3:
        return process_problem_type3(problem, error_param)
    return process_problem_type1(problem, error_param)

###########find parameters  ####################################

def find_params_old(problem_type3, problem, answer):
    """This function finds all possible parameters to get the given result with
    a given problem. The function will iterate over all possible parameter assignments
    and will store all assignments that result in the specified answer. This list will
    be returned. The answer needs to be a boolean value.
    """
    matching_params = []
    i = 0
    # iterates over all 128 possible variable assignments
    while i < 256:
        b_num = format(i, '08b')
        #print(b_num)
        #print("bool", bool(int(b_num[0])))
        params = [bool(int(b_num[0])), bool(int(b_num[1])), bool(int(b_num[2])),
                  bool(int(b_num[3])), bool(int(b_num[4])), bool(int(b_num[5])),
                  bool(int(b_num[6])), bool(int(b_num[7]))]
        # check if the result with these parameters is the same as answer
        if process_problem(problem_type3, problem, params) == answer:
            #print(answer, params)
            matching_params.append(params)
        i += 1
    #print("matching params len", len(matching_params[0]))
    return matching_params # returns all lists of parameter values that did match
    #print(matching_params[0])

def find_params(problem, answer):
    """New version: uses the modified spatial model. Doesn't need the problemtype
    parameter anymore.
    This function finds all possible parameters to get the given result with
    a given problem. The function will iterate over all possible parameter assignments
    and will store all assignments that result in the specified answer. This list will
    be returned. The answer needs to be a boolean value.
    """
    spatial_model = model.MainModule() # initiate the spatial model
    matching_params = []
    i = 0
    # iterates over all 128 possible variable assignments
    while i < 256:
        prob = deepcopy(problem)
        b_num = format(i, '08b')
        #print(b_num)
        #print("bool", bool(int(b_num[0])))
        params = [[bool(int(b_num[0])), bool(int(b_num[1])), bool(int(b_num[2])),
                   bool(int(b_num[3])), bool(int(b_num[4])), bool(int(b_num[5]))],
                  [bool(int(b_num[6])), bool(int(b_num[7]))]]
        # check if the result with these parameters is the same as answer
        para = deepcopy(params)
        if spatial_model.interpret_spatial_parameters(prob, para) == answer:
            #print(answer, params)
            matching_params.append(params)
        i += 1
        #print(problem, "problem after interpret spatial")
    #print("matching params len", len(matching_params[0]))
    return matching_params # returns all lists of parameter values that did match
    #print(matching_params[0])

def compute_answers_old(problem_type3, params):
    """
    Function computes all answers to the given list of parameters. The parameters
    list contains lists of boolean values. problem_type3 decides from which problem set
    the answers will be computed. There needs to be a distinction between the problem
    types because there are two different procedures for them in the program.
    returns a list of lists which contains the respective answers for the problems
    with the parameter assignments. The index of the answers will be in sync with the
    params list to acces them later on.
    """
    answers_list = [] # list for the lists of results
    if problem_type3: #iterate over type 3 problems
        for param in enumerate(params):
            answers = [] # results for each parameter and all problems
            for problem in PROBLEMS_TYPE3:
                answers.append(process_problem_type3(problem, param))
            answers_list.append(answers) # make sure the list is in correct order
    else: # iterate over type1+2 problems
        for param in enumerate(params):
            answers = [] # results for each parameter and all problems
            for problem in PROBLEMS_TYPE12:
                answers.append(process_problem_type1(problem, param))
            answers_list.append(answers) # make sure the list is in correct order
    return answers_list # returns all answers for all parameters

def compute_answers(params, problems):
    """New version: doesn't need the problem type, but a given list of problems.
    Function computes all answers to the given list of parameters. The parameters
    list contains lists of boolean values. problem_type3 decides from which problem set
    the answers will be computed. There needs to be a distinction between the problem
    types because there are two different procedures for them in the program.
    returns a list of lists which contains the respective answers for the problems
    with the parameter assignments. The index of the answers will be in sync with the
    params list to acces them later on.
    """
    answers_list = [] # list for the lists of results
    spatial_model = model.MainModule() # initiate the spatial model
    for param in enumerate(params):
        answers = [] # results for each parameter and all problems
        for problem in problems:
            answers.append(spatial_model.interpret_spatial_parameters(deepcopy(problem), param))
        answers_list.append(answers) # make sure the list is in correct order
    return answers_list # returns all answers for all parameters

def compare_vp_params(vp_results, params_results):
    """Iterates through all the lists of answers for the parameters in the list.
    Then the function iterates through the vp_results and the results for the respective
    parameter. Returns a list of accuracy values for each param in the list.
    """
    acc_list = []
    for par in params_results:
        acc = 0 # accuracy, computed with the number of items and the number of equal items
        for i, vp_res in enumerate(vp_results):
            if vp_res == par[i]:
                acc += 1
        acc_list.append(round(acc/len(vp_results), 2))
    return acc_list

def compare_all_vp(vp_list, params_results):
    """Function calls compare_vp_params for all participants in the vp_list.
    The results of these function calls are all summed together(element-wise).
    The parameters with the aggregated score will be returned as a list.
    """
    agg_results = [0] * (len(params_results)+1) # list for the aggregated results for each param
    all_vp_res = []
    vp_l = vp_list.copy()
    # first iterate over the vps and get all compare results in a list
    for vp_ in vp_l:
        result_vp = compare_vp_params(vp_, params_results)
        all_vp_res.append(result_vp)
        #now iterate over the result list and aggregate all results.
        for i, param_res in enumerate(result_vp):
            agg_results[i] += param_res
    percent_res = []
    for ag_ in agg_results:
        ag_ = ag_/len(vp_l)
        percent_res.append(ag_)
    return percent_res

def find_n_max_vals(list_, num):
    """Function searches the num-biggest values of a given list of numbers.
    Returns the num maximas list and the index list wrapped up in a list.
    """
    li_ = list_.copy()
    max_vals = [] #the values
    max_ind = []# the index of the value, can be used to get the param
    while num > 0:
        max_val = max(li_)
        max_id = li_.index(max_val)
        max_vals.append(max_val)
        max_ind.append(max_id)
        li_[max_id] = 0 #better than deleting
        num -= 1 # count down
    return [max_vals, max_ind]

def find_params_prob_vp_old(problemtype_3, problem, participant, answer, print_params):
    """*old version, only used in this module, this function will call the old
    versions of the functions*
    Finds the best parameter assigment for a given problem an participant.
    The Parameter assignments need to result in the same value as the given
    answer Boolean value. If print_params is set to true, the best parameter assignments
    will be printed with their id. The id of an assignment is only for representation, this
    is not the real binary number that is represented with the assigment.
    Returns these parameter list and their ids and prints all assignments and their ids.
    """
    if print_params:
        print("problem: ", problem, "vp_ans: ", answer)
    params = find_params_old(problemtype_3, problem, answer)
    answers = compute_answers_old(problemtype_3, params)
    comp_res = compare_vp_params(participant, answers)
    max_ind = find_n_max_vals(comp_res, 20)
    if print_params:
        print("max ids", max_ind[1])
        print("max values", max_ind[0])
        for id_ in max_ind[1]:
            print(params[id_], "id:", id_)
    return [params, max_ind[1]]

def find_params_prob_vp(problem, problems, participant, answer, print_params):
    """Finds the best parameter assignment for a given problem and participant.
    The Parameter assignments need to result in the same value as the given
    answer Boolean value. All parameter assignments that match the given result
    will be tested by compare_vp_params with the answers for all the problems with
    the parameters. The assignments with the best result in this evaluation are returned.
    If print_params is set to true, the best parameter assignments
    will be printed with their id. The id of an assignment is only for representation, this
    is not the real binary number that is represented with the assigment.
    Returns the top 20 parameter list and their ids and prints them.
    """
    if print_params:
        print("problem: ", problem, "vp_ans: ", answer)
    params = find_params(problem, answer)
    answers = compute_answers(params, problems) #compute the answers to any set of given problems
    comp_res = compare_vp_params(participant, answers)
    print(comp_res)
    max_ind = find_n_max_vals(comp_res, 20) #finds the top 20 parameter assignments
    if print_params:
        print("max ids", max_ind[1])
        print("max values", max_ind[0])
        for id_ in max_ind[1]:
            print(params[id_], "id:", id_)
    return [params, max_ind[1]]

def find_params_all_prob_vp_old(problemtype_3, problems, participant, print_all_params):
    """Finds the best parameter assignments for a given participant for all Problems.
    The Function will run find_params_prob_vp for every problem in the given problems
    list with the corresponding answer list given with participant.
    according to the problem number, the answer that the participant gave will be taken
    from the participant answer list.
    """
    #problems = problems_list.copy()
    all_params = [] # list for all parameter assignments
    all_ids = [] # all ids of the best parameters, for later use
    # first iterate over the problems and call find_params_prob_vp on each prob
    for i, prob in enumerate(problems):
        vp_ans = participant[i] # get the answer for this problem
        param_id = find_params_prob_vp(problemtype_3, prob, participant, vp_ans, print_all_params)
        all_params.append(param_id[0])
        all_ids.append(param_id[1])

def find_params_all_prob_vp(problems, participant, print_all_params):
    """Finds the best parameter assignments for a given participant for all Problems.
    The Function will run find_params_prob_vp for every problem in the given problems
    list with the corresponding answer list given with participant.
    according to the problem number, the answer that the participant gave will be taken
    from the participant answer list.
    """
    #problems = problems_list.copy()
    all_params = [] # list for all parameter assignments
    all_ids = [] # all ids of the best parameters, for later use
    # first iterate over the problems and call find_params_prob_vp on each prob
    for i, prob in enumerate(problems):
        vp_ans = participant[i] # get the answer for this problem
        param_id = find_params_prob_vp(prob, problems, participant, vp_ans, print_all_params)
        all_params.append(param_id[0])
        all_ids.append(param_id[1])
    return [all_params, all_ids]

def main():
    """
    Main-function.
    calls all relevant functions
    """
    #### categorization ####
    # usage of the categorization helperprogram
    #prec_result = evaluate_all_cats(CAT_TYPE13, CAT_TYPE23, CAT_TYPE32)
    #check_all_categories(prec_result[0], prec_result[1])
    #### find parameters usage ####
    #all_params = find_params_all_prob_vp(True, PROBLEMS_TYPE3,
    #                                     PARTICIPANT_ANSWERS_TYPE3[5], True)
    #all_params = find_params_all_prob_vp(PROBLEMS_TYPE12, PARTICIPANT_ANSWERS_TYPE12[4], True)

    #params = find_params_prob_vp(PROBLEMS_TYPE3[2], PROBLEMS_TYPE3,
    #                             PARTICIPANT_ANSWERS_TYPE3[3], True, True)
    #params = find_params(PROBLEMS_TYPE3[9], False)

if __name__ == '__main__':
    main()
