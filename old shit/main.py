# Python Version: 3.10.7
import openai

openai.api_key = "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"

def send_it(messages, prompt):
    messages.append(
        {"role": "assistant", "content": prompt},
    )

    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )

    reply = chat.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})

    return reply, messages

def single_layer(problem):
    messages = [ {"role": "system", "content": '''You are an intelligent system that describes
    programming problems in a step-by-step way'''} ]

    # solver_prompt = """
    # Given the following problem, write a program that solves this competitive programming problem.
    # Do so in a way that works well and don't worry about efficiency unless the problem says to do so. 
    # Do the problem in Python. Respond with the code and only the code.

    # Problem: {problem}
    # """

    solver_prompt = """
    given a problem, do the competitive programming question. return ONLY the python code. 

    problem: {problem}
    """

    solution,messages = send_it(messages, solver_prompt.format(problem=problem))

    with open(r"single_layer\solution.py", "w") as f:
        f.write(solution)

def dual_layer(problem):
    messages = [ {"role": "system", "content": '''You are an intelligent system that describes 
    programming problems in a step-by-step way such that an ai with extensive knowledge of programming could solve it'''} ] 

    explainer_prompt = """
    Describe this competitive programming problem in a step-by-step way such that it can be solved with ease and precision.
    You should understand the problem and present the description as an outline to the solution. Be as specific as possible.
    Problem: {problem}
    """

    # solver_prompt = """
    # Given the following problem as well as an explanation of the problem, write a program that solves this competitive programming problem.
    # Do so in a way that works well and don't worry about efficiency unless the problem says to do so.
    # Do the problem in Python. Respond with the code and only the code.

    # Problem: {problem}

    # Explanation: {explanation}
    # """

    solver_prompt = """
    given a problem and explination, do the competitive programming question. return ONLY the python code. 
    
    problem: {problem}
    explination: {explanation}
    """

    explination,messages = send_it(messages, explainer_prompt.format(problem=problem))

    with open(r"dual_layer\explanation.txt", "w") as f:
        f.write(explination)

    messages = [ {"role": "system", "content": '''You are an intelligent system that solves
    programming problems.'''} ]

    solution,messages = send_it(messages, solver_prompt.format(problem=problem, explanation=explination))

    with open("dual_layer\\solution.py", "w") as f:
        f.write(solution)
    
def main():
    print("Reading Prompt...")

    with open("problem.txt", "r") as f:
        problem = f.read()

    print("Solving With Single Layer...")
    single_layer(problem)

    print("Solving With Dual Layer...")
    dual_layer(problem)

    print("Done!")

if __name__=="__main__":
    main()