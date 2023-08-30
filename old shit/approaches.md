# Different Approaches #

## Single Layer ##
1. Agent 1:
    - input: Problem
    - output: Solution **END**

## Dual Layer ##
1. Agent 1: 
    - input: Problem 
    - output: Explination
2. Agent 2:
    - input: Problem, Explination
    - output: Solution **END**

## Dual Layer With Oracle ##
1. Agent 1:
    - input: Problem, Oracle Solution
    - output: Explination
2. Agent 2:
    - input: Problem, Explination
    - output: Solution **END**

## 8 Layer ##

1. Agent 1: 
    - input: Problem
    - output: Explination
2. Agent 2: 
    - input Problem, Explination
    - output: Sub Problems
# Agent 2.x: Explain the subproblems
# Agent 3.x: Solve the subproblems
# Agent 4: Combine the subproblems
# Agent 5: Explain the solution without context of the problem
# Agent 6: Explain the solution with context of the problem
# Agent 7: Compare agent 5 and 6 and explain the difference
# Agent 8: If they don't match, fix the solution