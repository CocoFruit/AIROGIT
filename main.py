# Python Version: 3.10.7
import openai



def main():
    openai.api_key = "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"

    messages = [ {"role": "system", "content": '''You are an intelligent system that describes 
                  programming problems in a step-by-step way'''} ]


    print("Reading Prompt...")

    with open("problem.txt", "r") as f:
        problem = f.read()

    explainer_prompt = """
    Describe this competitive programming problem in a step-by-step way such that it can be solved with ease and precision.
    You should understand the problem and present the description as an outline to the solution. Be as specific as possible.
    Problem: {problem}
    """

    solver_prompt = """
    Given the following problem as well as an explanation of the problem, write a program that solves this competitive programming problem.
    Do so in a way that works well and don't worry about efficiency. Do the problem in Python. Respond with the code and only the code.

    Problem: {problem}

    Explanation: {explanation}
    """

    ##--Explaining--##

    messages.append(
        {"role": "assistant", "content": explainer_prompt.format(problem=problem)},
    )
    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )

    print("Explaining...")

    reply = chat.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})

    explination = reply

    with open("explanation.txt", "w") as f:
        f.write(explination)

    # print(f"Explainer: {reply}")


    ##--Solving--##

    print("Solving...")
    
    messages.append(
        {"role": "assistant", "content": solver_prompt.format(problem=problem, explanation=explination)},
    )
    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )

    reply = chat.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})

    solution = reply

    with open("solution.py", "w") as f:
        f.write(reply)

    # print(f"Solver: {solution}")

    print("Done!")

if __name__=="__main__":
    main()