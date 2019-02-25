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


if __name__ == "__main__":
#    regex_expr = "12*2"
#    regex_expr = "1(12*3|11)12(14)*"
#    regex_expr = "(0|1|2|3|4|5|6|7|8|9)|(1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*"
#    regex_expr = "(0|1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*.|.(0|1|2|3|4|5|6||8|9)(0|1|2|3|4|5|6|7|8|9)*|(0|1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*.(0|1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*"
#    regex_expr = "(123)12"
    regex_expr = "(12*333)*5(1|2)"

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
            expr_temp = []
            sub_num += 1

        elif(expr[index] == '*'): #case '*'
            char = stack.pop()
            expr_temp = [char] + expr_temp + ['*']
            
            sub_fa["FA(" + str(sub_num) + ')'] = expr_temp
            root_ref = "FA(" + str(sub_num) + ')'
            stack.push(root_ref)
            expr_temp = []
            sub_num += 1
            
        else:
            stack.push(expr[index])
        index += 1



#test system
    print("Sub NFA references  :  " + str(sub_fa))
    print("Root NFA  :  " + root_ref)
    
    
