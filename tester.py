from openai import OpenAI
import time

key = "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"

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
    print(git_diff)

    messages = [ {"role": "system", "content": '''You are an intelligent system that receives a git diff for a project and you will create teh commit message.'''} ]

    summary_prompt = f"""Given the differences in a git repo named {name}, create a summary and description for the commit message. Use what you know about creating concise and accurate commit messages to create the message. 
    \nHere is a template for a commit message:\n {template}
    \n\nHere is the git diff:\n {git_diff}
    """

    reply,messages = send_it(messages, summary_prompt,model="gpt-3.5-turbo")
    reply = reply.strip().split("\n",1)
    title = reply[0].replace("Title:","").strip()
    body = reply[1].replace("Body:","").strip()

    return title,body   

def generate_commit_message(length):
    prompt = """generate a test git diff that follows this format that is about {length} characters long:

---
 demo.py | 11 ++++++++++-
 1 file changed, 10 insertions(+), 1 deletion(-)

diff --git a/demo.py b/demo.py
index 0899c6d..04211ae 100644
--- a/demo.py
+++ b/demo.py
@@ -101,7 +101,16 @@ def safe_b64decode(s):
     vd = b64encode(vd).decode()
     user.register(vd)
 
-logging.info(f"Looked up textgpt@icloud.com, got response: {user.lookup(['mailto:textgpt@icloud.com'])}")
+#logging.info(f"Looked up textgpt@icloud.com, got response: {user.lookup(['mailto:textgpt@icloud.com'])}")
+
+logging.info("Enter a username to look up, for example: mailto:textgpt@icloud.com")
+while True:
+    # Read a line from stdin
+    line = input("> ")
+    if line == "":
+        break
+    # Look up the username
+    logging.info(f"Looked up {line}, got response: {user.lookup([line])}")
 
 # Write config.json
 CONFIG["id"] = {"""
    reply,messages = send_it([{"role": "system", "content": '''You are an intelligent system that receives a git diff for a project and you will create teh commit message.'''}], prompt,model="gpt-3.5-turbo")
    return reply, len(reply)


def main():
    name = "test"
    template = open(r"C:\Users\parke\OneDrive\Documents\GitHub\AIROGIT\airogit\cola\config\commit_template.txt", "r").read()
    lengths = [2**i for i in range(13)]
    times = []
    # for i in range(13):
    #     git_diff = generate_commit_message(2**i)
        
    #     start = time.time()
    #     title,body = summarize_changes(name, git_diff, template)
    #     end = time.time()
    #     times.append(end-start)
        # print(f"Time to generate commit message: {end-start} seconds of length {2**i}")

    times = [2.7112035751342773, 1.32741379737854, 1.7484285831451416, 1.762526512145996, 1.424187421798706, 3.2897098064422607, 2.136672019958496, 1.853165626525879, 1.971144676208496, 2.4754979610443115, 1.9838175773620605, 2.3081977367401123, 1.2634811401367188]
    print("times:",times)
    import matplotlib.pyplot as plt
    import numpy as np

    plt.figure(figsize=(10, 6))
    plt.plot(lengths, times, marker='o', linestyle='-')
    # plt.xscale('log')
    # plt.yscale('log')
    plt.ylabel('Time (s)')
    plt.xlabel('Length of commit message')
    plt.title('Time to generate commit message')
    plt.grid(True)
    plt.show()

    

    # Define data

    



if __name__ == "__main__":
    main()