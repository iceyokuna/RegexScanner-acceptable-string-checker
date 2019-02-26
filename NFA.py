class NFA:
  def __init__(self, Q, Sigma, delta, q0, F):
    self.name = ""
    self.Q = Q          # set of states
    self.Sigma = Sigma  # alphabet (set of input characters)
    self.delta = delta  # transition function
    self.q0 = q0        # starting state
    self.F = F          # set of accepting states

    # add missing transitions
    Q.add('err')
    for q in Q:       # for each state
      for c in Sigma: # for each character
        if (q,c) not in delta:
          delta[(q,c)] = {'err'}

  def setName(self, name):
    self.name = name

  def closure(self, q):
    working_set = {q}
    reached = set()
    while len(working_set) > 0:
      q = working_set.pop()
      reached.add(q)

      # if there is an empty string transition
      if (q,'') in self.delta:
        # add all next state candidates to the working set if they are not reached
        working_set = working_set.union({next_state for next_state in self.delta[(q,'')] if next_state not in reached})
    return reached

  def accept(self, string):
    for c in string:
      if(c not in self.Sigma):
        return False
    current_states = self.closure(self.q0)    # start from closure of the starting state
    for c in string:
      next_states = set()                     # possible next state
      for q in current_states:
      # delta(state, c) -> set of states
        for next_state in self.delta[(q,c)]:
          closure_next_state = self.closure(next_state)
          next_states = next_states.union(closure_next_state)
      current_states = next_states
    return any(q in self.F for q in current_states)
    
'''
  # NFA to DFA
  def convert_to_DFA(self):
    Q_DFA = set()
    delta_DFA = dict()

    q0_DFA = tuple(sorted(list(self.closure(self.q0))))
    
    working_set = {q0_DFA}
    while len(working_set) > 0:
      current_states = working_set.pop()
      Q_DFA.add(current_states)
      for c in self.Sigma:
        next_states = set()                     # possible next state
        for q in current_states:
        # delta(state, c) -> set of states
          for next_state in self.delta[(q,c)]:
            closure_next_state = self.closure(next_state)
            next_states = next_states.union(closure_next_state)
        newstate = tuple(sorted([s for s in next_states if s != 'err']))
        if newstate not in Q_DFA:
          working_set.add(newstate)
        delta_DFA[(current_states,c)] = newstate

    F_DFA = set(q for q in Q_DFA if any(qf in q for qf in self.F))

    return DFA(Q_DFA, Sigma, delta_DFA, q0_DFA, F_DFA)
'''


