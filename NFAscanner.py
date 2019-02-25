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

class Stack:
    def __init__(self):
        self.elements = []
        self.size = 0

    def push(self, element):
        self.size += 1
        self.elements.append(element)

    def pop(self):
        self.size -= 1
        return self.elements.pop()

    def __len__(self):
        return self.size

    def __str__(self):
        return str(self.elements)



def concat(fa, char):
    out_fa = fa.copy()
    new_state = len(out_fa.Q)
    out_fa.Q.add(new_state)
    out_fa.Sigma.add(char)
    out_fa.delta[(list(out_fa.F)[0], char)] = {new_state}
    out_fa.F = {new_state}
    return out_fa


def star(fa):
    out_fa = fa.copy()
    new_start_state = len(out_fa.Q)
    new_end_state = len(out_fa.Q) + 1

    #set transition
    out_fa.delta[(new_start_state,"")] = {out_fa.q0, new_end_state}
    out_fa.delta[(list(out_fa.F)[0],"")] = {out_fa.q0, new_end_state}

    #update Q,q0,F
    out_fa.Q.add(new_start_state)
    out_fa.Q.add(new_end_state)
    out_fa.q0 = new_start_state
    out_fa.F = {new_end_state}
    return out_fa

def join(mainFA,joinFA):
    #re name subFA
    fa = mainFA.copy()
    subFA = joinFA.copy()
    num_state = len(fa.Q)
    subFA.Q = {i+num_state for i in subFA.Q}
    new_delta = {}

    #update delta of subFA
    for i in subFA.delta:
        new_delta[(i[0] + num_state, i[1])] = {j + num_state for j in subFA.delta[i]}
    subFA.delta = new_delta
    #update all attr of SubFA
    subFA.q0 += num_state
    subFA.F = {list(subFA.F)[0] + num_state}

    #join sigma and Q
    fa.Sigma = fa.Sigma | subFA.Sigma
    fa.Q = fa.Q | subFA.Q

    #connect transition
    fa.delta[(list(fa.F)[0], '')] = {subFA.q0} #add empty move to join 2 FA
    fa.delta = {**fa.delta, **subFA.delta} #combine dict
    fa.F = subFA.F #set new end
    return fa

def exclusiveOr(expr):
    exclusiveList = []
    temp = []
    for char in expr:
        if(char == '|'):
            exclusiveList.append(temp)
            temp = []
            continue
        temp.append(char)
    exclusiveList.append(temp)

    #build FA in each elements in list
    faList = []
    for expr in exclusiveList:
        faList.append(exprToFA(expr))

    counter = 1
    list_end_subFA = []
    fa = FA({0}, set(), {} , 0, {0})
    fa.delta[(fa.q0, '')] = set() #to prevent key error
    
    for sub_fa in faList:
        subFA = sub_fa.copy()
        subFA.Q = {i+counter for i in subFA.Q}
        new_delta = {}
        
        #update delta of subFA
        for i in subFA.delta:
            new_delta[(i[0] + counter, i[1])] = {list(subFA.delta[i])[0] + counter}
        subFA.delta = new_delta
        
        #update all attr of SubFA
        subFA.q0 += counter
        subFA.F = {list(subFA.F)[0] + counter}
        
        #join sigma and Q
        fa.Sigma = fa.Sigma | subFA.Sigma
        fa.Q = fa.Q | subFA.Q

        #connect transition
        fa.delta[(fa.q0, '')].add(subFA.q0) #add empty move to join 2 FA
        fa.delta = {**fa.delta, **subFA.delta} #combine dict
        list_end_subFA.append(list(subFA.F)[0]) #keep end state(s) 

        #update counter
        counter = len(fa.Q)
    #connect to same end state
    fa.Q.add(counter)
    for end in list_end_subFA: #set new end state
        fa.delta[(end,'')] = {counter}
    fa.F = {counter}

    return fa


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


# get NFA from regex_expr
def getFA(regex_expr):
    regex_expr = '('+ regex_expr + ')'
    print("original regex  :  " + regex_expr)

    #pre process (to mange * ,change char* to (char)*)
    temp_regex_expr = ""
    for i in range(len(regex_expr)):
        if(regex_expr[i] == '*' and regex_expr[i-1] != ')'):
            temp_regex_expr = temp_regex_expr[0:-1]
            temp_regex_expr += '(' + regex_expr[i-1] +')*'
        else:
            temp_regex_expr += regex_expr[i]
    regex_expr = temp_regex_expr
    print("Pre-process regex  :  " + regex_expr)
    
    #change regex to list of char in order to insert sub FA (FA object references)
    expr = list(regex_expr) #read char by char O(n)

    #dict of sub FA references
    sub_fa = {}

    stack = Stack()
    sub_num = 1 #sub number postfix reference
    index = 1
    stack.push(expr[0]) #push '('
    expr_temp = []
    char = ''
    root_ref = '' #when process is end, this variable will be the root FA reference(whole NFA)

    while(len(stack) != 0):
        if(expr[index] == ')'):  #case  ')'
            char = stack.pop()
            while(char != '('):
                expr_temp = [char] + expr_temp
                char = stack.pop()
                
            sub_fa["FA(" + str(sub_num) + ')'] = expr_temp
            root_ref = "FA(" + str(sub_num) + ')'
            if(len(stack) != 0):
                stack.push(root_ref)
            print(expr_temp)
            expr_temp = []
            sub_num += 1

        elif(expr[index] == '*'): #case '*'
            char = stack.pop()
            expr_temp = [char] + expr_temp + ['*']
            sub_fa["FA(" + str(sub_num) + ')'] = expr_temp
            root_ref = "FA(" + str(sub_num) + ')'
            stack.push(root_ref)
            print(expr_temp)
            expr_temp = []
            sub_num += 1
            
        else:
            stack.push(expr[index])
        index += 1
    return sub_fa
    
#########################TEST_CONCAT
##expr = ['a','a','b']
##fa = FA()
##for char in expr:
##    concat(fa, char)
##fa.show()

#########################TEST_STAR *
##fa = FA({0, 1, 2, 3}, {'a', 'b'}, {(0, 'a'): {1}, (1, 'a'): {2}, (2, 'b'): {3}}, 0, {3})
##star(fa)
##fa.show()

#########################TEST_JOIN (aab)(a)
##expr = ['a','a','b']
##expr2 = ['a']
##fa = FA({0}, set(), {} , 0, {0})
##fa2 = FA({0}, set(), {} , 0, {0})
##
##for char in expr:
##    fa = concat(fa, char)
##for char in expr2:
##    fa2 = concat(fa2, char)
##fa.show()
##fa2.show()
##
##fa = join(fa,fa2)
##
##fa.show()


###########################TEST ALL 1
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

###########################TEST ALL 2
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

###########################TEST ExclusiveOR (tokenize)
##expr = ['a','s','|','b','c','|','c','c']
##exclusiveOr(expr)


###########################TEST construct FA from sub expr -> (abc)* #correct
##expr = ['a','b','c']
##fa = exprToFA(expr)
##fa.show()
##fa2 = exprToFA([fa,'*'])
##fa2.show()


###########################TEST construct FA from sub expr -> (ab)(cc) #correct
##expr = ['a','b']
##expr2 = ['c','c']
##fa = exprToFA(expr)
##fa.show()
##fa2 = exprToFA(expr2)
##fa2.show()
##fa3 = exprToFA([fa,fa2])
###((ab)(cc))*
##fa3.show()
##fa4 = exprToFA([fa3,'*'])
##fa4.show()


###########################TEST ExclusiveOR (aa|bb|)  #correct
##fa = exprToFA(['a'])
##expr = ['a','a','|','b','b']
##out_fa = exclusiveOr(expr)
##out_fa.show()

###########################TEST ExclusiveOR (12*2)  #correct
##expr = ['2']
##fa = exprToFA(expr)
##fa.show()
##
##expr2 = [fa,'*']
##fa2 = exprToFA(expr2)
##fa2.show()
##
##expr3 = ['1',fa2,'2']
##fa3 = exprToFA(expr3)
##fa3.show()

###########################REGEX
regex_expr = "12*2"
#    regex_expr = "1(12*3|11)12(14)*"
#    regex_expr = "(0|1|2|3|4|5|6|7|8|9)|(1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*"
#    regex_expr = "(0|1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*.|.(0|1|2|3|4|5|6||8|9)(0|1|2|3|4|5|6|7|8|9)*|(0|1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*.(0|1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*"
#    regex_expr = "(123)12"
#    regex_expr = "(12*333)*5(1|2)"
fa = getFA(regex_expr)
print(fa)
