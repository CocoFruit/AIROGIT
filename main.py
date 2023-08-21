# Python Version: 3.10.7
import openai

def main():
    openai.api_key = "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"

    agent_creator = lambda task:f"""
    Your job is to break tasks down into sub tasks. each subtask should have an agent that does it. 
    Give the agents a name like "leader" or "task creator" or "researcher". 
    Your output should be a json file and each agent should have a detailed description on what it should do.
    Decompose this task into subtasks and agents: {task}"""


    task = input("User: ")

    if task:
        pass 

    # messages = [ {"role": "system", "content": "You are a intelligent assistant."} ]




    # while True:
    #     message = input("User : ")
    #     if message:
    #         messages.append(
    #             {"role": "user", "content": message},
    #         )
    #         chat = openai.ChatCompletion.create(
    #             model="gpt-3.5-turbo", messages=messages
    #         )
    #     reply = chat.choices[0].message.content
    #     print(f"ChatGPT: {reply}")
    
    #     messages.append({"role": "assistant", "content": reply})

if __name__=="__main__":
    main()