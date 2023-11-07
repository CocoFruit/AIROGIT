from openai import OpenAI
import yaml
import os

# print directory
# Get the directory where your Python script is located
script_directory = os.path.dirname(os.path.abspath(__file__))

# Define the path to the desired file relative to the script directory
desired_file_path = os.path.join(script_directory, "config", "config.yaml")

# Open the file with the desired path
with open(desired_file_path, "r") as f:
    # Your code to work with the file goes here
    config = yaml.safe_load(f)

key = config.get("openai",{}).get("gpt-api-key")

if key is None:
    raise Exception("Please add your openai api key to config/config.yaml")

client = OpenAI(api_key=key)

def send_it(messages, prompt,model="gpt-3.5-turbo"):
    messages.append(
        {"role": "assistant", "content": prompt},
    )

    response = client.chat.completions.create(
        messages=messages,
        model = model
    )

    reply = response.choices[0].message.content
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