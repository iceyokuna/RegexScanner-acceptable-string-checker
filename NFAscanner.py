class FA:
    def __init__(self, Q = {0}, Sigma = set(), delta = {}, q0 = 0, F = {0}):
        self.Q = Q
        self.Sigma = Sigma
        self.delta = delta
        self.q0 = q0
        self.F = F

    def copy(self):
        return FA(self.Q.copy(), self.Sigma.copy(), self.delta.copy(), self.q0, self.F.copy())
    
    def show(self):
        print('\n-----------------------------')
        print("Q = ", self.Q) 
        print("Sigma = ", self.Sigma)
        print("delta = ", self.delta)
        print("q0 = ", self.q0)
        print("F = ", self.F)
        print('-----------------------------\n')


def concat(fa, char):
    out_fa = FA(fa.Q, fa.Sigma, fa.delta , fa.q0, fa.F)
    new_state = len(out_fa.Q)
    out_fa.Q.add(new_state)
    out_fa.Sigma.add(char)
    out_fa.delta[(list(out_fa.F)[0], char)] = {new_state}
    out_fa.F = {new_state}
    return out_fa


def star(fa):
    out_fa = FA(fa.Q, fa.Sigma, fa.delta , fa.q0, fa.F)
    new_start_state = len(FA.Q)
    new_end_state = len(FA.Q) + 1

    #set transition
    FA.delta[(new_start_state,"")] = {FA.q0, new_end_state}
    FA.delta[(list(FA.F)[0],"")] = {FA.q0, new_end_state}

    #update Q,q0,F
    FA.Q.add(new_start_state)
    FA.Q.add(new_end_state)
    FA.q0 = new_start_state
    FA.F = {new_end_state}
    return FA

def join(FA,subFA):
    #re name subFA 
    num_state = len(FA.Q)
    subFA.Q = {i+num_state for i in subFA.Q}
    new_delta = {}
    
    for i in subFA.delta:
        new_delta[(i[0] + num_state, i[1])] = {list(subFA.delta[i])[0] + num_state}
    subFA.delta = new_delta
    
    subFA.q0 += num_state
    subFA.F = {list(subFA.F)[0] + num_state}
    FA.Sigma = FA.Sigma | subFA.Sigma
    FA.Q = FA.Q | subFA.Q

    #connect transition
    FA.delta[(list(FA.F)[0], '')] = subFA.q0
    FA.delta = {**FA.delta, **subFA.delta}
    FA.F = subFA.F
    return FA

def exclusiveOr(FA, expr):
    exclusiveList = []
    temp = []
    for char in expr:
        if(char == '|'):
            exclusiveList.append(temp)
            temp = []
            continue
        temp.append(char)
    exclusiveList.append(temp)
    print(exclusiveList)
    #build FA in each elements in list
    #merge to 1 fa

#simple expr to FA (convert sub expr to sub fa)
def exprToFA(expr_list):
    fa = FA({0}, set(), {} , 0, {0})
    if('*' in expr_list):
        return star(expr_list[0])
    elif('|' in expr_list):
        return exclusiveOr(fa, expr_list)
    
    for char in expr_list:
        if(type(char) == type(FA())):
            fa = join(fa,char)
        else:
            fa = concat(fa, char)
    return fa
    
#TEST_CONCAT
##expr = ['a','a','b']
##fa = FA()
##for char in expr:
##    concat(fa, char)
##fa.show()

#TEST_STAR *
##fa = FA({0, 1, 2, 3}, {'a', 'b'}, {(0, 'a'): {1}, (1, 'a'): {2}, (2, 'b'): {3}}, 0, {3})
##star(fa)
##fa.show()

#TEST_JOIN
##expr = ['a','a','b']
##expr2 = ['a']
##fa = FA({0}, set(), {} , 0, {0})
##fa2 = FA({0}, set(), {} , 0, {0})
##
##for char in expr:
##    concat(fa, char)
##for char in expr2:
##    concat(fa2, char)
##    
##fa = join(fa,fa2)
##
##fa.show()


#TEST ALL 1
##expr = ['a','b']
##expr2 = ['c','c']
##
##fa = FA()
##
##for char in expr:
##    concat(fa, char)
##star(fa)
##
##for char in expr2:
##    concat(fa, char)
##    
##fa.show()

#TEST ALL 2
##expr = ['a','b']
##expr2 = ['c','c']
##
##fa = FA({0}, set(), {} , 0, {0})
##fa2 = FA({0}, set(), {} , 0, {0})
##
##for char in expr:
##    concat(fa, char)
##star(fa)
##
##for char in expr2:
##    concat(fa2, char)
##
##fa = join(fa,fa2)
##    
##fa.show()

#TEST ExclusiveOR (tokenize)
##fa = FA({0}, set(), {} , 0, {0})
##expr = ['a','s','|','b','c','|','c','c']
##exclusiveOr(fa, expr)

#TEST construct FA from sub expr
expr = ['a','b','c']
fa = exprToFA(expr)
fa.show()
fa2 = exprToFA([fa,'*'])
fa2.show()
fa.show()


