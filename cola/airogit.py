import openai
import os

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

def summarize_changes(name, git_diff, template, verbose=False):
    messages = [ {"role": "system", "content": '''You are an intelligent system that knows the past and present versions of files and directories'''} ]

    summary_prompt = f"""Given the differences in a git repo named {name}, create a summary and description for the commit message. Use what you know about creating concise and accurate commit messages to create the message. 
    \nHere is a template for a commit message:\n {template}
    \n\nHere is the git diff:\n {git_diff}
    """

    reply,messages = send_it(messages, summary_prompt)
    reply = reply.strip().split("\n",1)
    title = reply[0].replace("Title:","").strip()
    body = reply[1].replace("Body:","").strip()

    return title,body   