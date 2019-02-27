from NFA import *

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
    return out_fa.copy()


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
    return out_fa.copy()

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
    return fa.copy()

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
            new_delta[(i[0] + counter, i[1])] = {j + counter for j in subFA.delta[i]}
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

    return fa.copy()


#simple expr to FA (convert sub expr to sub fa)
def exprToFA(expr_list):
    fa = FA({0}, set(), {} , 0, {0})
    if('*' in expr_list):
        return star(expr_list[0])
    elif('|' in expr_list):
        return exclusiveOr(expr_list)
    
    for char in expr_list:
        if(type(char) == type(FA())):
            fa = join(fa,char)
        else:
            fa = concat(fa, char)
    return fa.copy()


# get NFA from regex_expr
def getFA(regex_expr):
    regex_expr = '('+ regex_expr + ')'
#    print("original regex  :  " + regex_expr)

    #pre process (to mange * ,change char* to (char)*)
    temp_regex_expr = ""
    for i in range(len(regex_expr)):
        if(regex_expr[i] == '*' and regex_expr[i-1] != ')'):
            temp_regex_expr = temp_regex_expr[0:-1]
            temp_regex_expr += '(' + regex_expr[i-1] +')*'
        else:
            temp_regex_expr += regex_expr[i]
    regex_expr = temp_regex_expr
#    print("Pre-process regex  :  " + regex_expr)
    
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
            fa = exprToFA(expr_temp)
            if(len(stack) != 0):
                stack.push(fa)
#            print(root_ref + "  :  " + str(expr_temp))
            expr_temp = []
            sub_num += 1

        elif(expr[index] == '*'): #case '*'
            char = stack.pop()
            expr_temp = [char] + expr_temp + ['*']
            sub_fa["FA(" + str(sub_num) + ')'] = expr_temp
            root_ref = "FA(" + str(sub_num) + ')'
            fa = exprToFA(expr_temp)
            stack.push(fa)
#            print(root_ref + "  :  " + str(expr_temp))
            expr_temp = []
            sub_num += 1
            
        else:
            stack.push(expr[index])
        index += 1
    return exprToFA(sub_fa[root_ref]).copy()

##def tokenize(faList, string):
##    acceptList = []
##    rejectedList = []
##    tokenizeList = []
##    temp = string[0]
##    #push start accept fa
##    for fa in faList:
##        if(fa.accept(temp)):
##            acceptList.append(fa)
##            
##    #loop find token
##    temp_list = acceptList.copy()
##    rejected = None
##    for i in range(1, len(string),1):
##        char = string[i]
##        temp += char #string for token
##        for j in range(len(acceptList)):
##            if(acceptList[j] in rejectedList):
##                continue
##            if(acceptList[j].accept(temp) == False):
##                rejectedList.append(acceptList[j])
##            #reset to current point and continue tokenize the least of string
##            if(len(rejectedList) == len(acceptList)):
##                tokenizeList.append((rejected.name, temp[0:-1]))
##                temp_list = []
##                #update acceptList
##                for fa in faList:
##                    if(fa.accept(string[i])):
##                        temp_list.append(fa)
##                rejectedList = []
##                temp = string[i]
##        acceptList = temp_list.copy()
##    for fa in faList:
##        if(fa.accept(temp) == True):
##            tokenizeList.append((fa.name,temp))
##                                
##    return tokenizeList

def foo(lt = []):
    lt.append(5)
    out = lt.copy()
    lt.clear()
    return out.copy()

#tokenize recursively
def tokenize(fa_list, string, output_reference):
    if(string == ""):
        return
    fa_check_list = []
    #init checker
    for fa in fa_list:
        fa_check_list.append([fa, -1])
        
    #check start
    for i in range(len(string)):
        for fa in fa_check_list:
            if(fa[0].accept(string[:i+1])):
                fa[1] = i

    Max = -1
    Max_fa = None
    #get recognized part
    for fa in fa_check_list:
        if(Max <= fa[1]):
            Max= fa[1]
            Max_fa = fa

    if(Max == -1):
        tokenize(fa_list, string[Max+2:], output_reference)
        return
    output_reference.append((Max_fa[0].name, string[:Max+1]))
    tokenize(fa_list, string[Max+1:], output_reference)


#change to read from file
int_fa = getFA("(0|1|2|3|4|5|6|7|8|9)|(1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*")
int_nfa = NFA(int_fa.Q, int_fa.Sigma, int_fa.delta, int_fa.q0, int_fa.F)
int_nfa.name = "t_integer"

float_fa = getFA("(0|1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*.|.(0|1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*|(0|1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*.(0|1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*")
float_nfa = NFA(float_fa.Q, float_fa.Sigma, float_fa.delta, float_fa.q0, float_fa.F)
float_nfa.name = "t_decimal"

l_fa = getFA("(A|B)*")
l_nfa = NFA(l_fa.Q, l_fa.Sigma, l_fa.delta, l_fa.q0, l_fa.F)
l_nfa.name = "upper_case"

u_fa = getFA("(a|b)*")
u_nfa = NFA(u_fa.Q, u_fa.Sigma, u_fa.delta, u_fa.q0, u_fa.F)
u_nfa.name = "lower_case"

##output = []
##input_string = "123.1234567890"
##tokenize([int_nfa, float_nfa], input_string , output) #token by refence (recursively)
##print("input string : " , input_string)
##print(output)


output = []
input_string = "AAAbbbb"
tokenize([l_nfa, u_nfa], input_string , output) #token by refence (recursively)
print("input string : " , input_string)
print(output)
