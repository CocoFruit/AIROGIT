import openai
import os

def list_files_in_folder(folder_path):
    current = []
    with os.scandir(folder_path) as entries:
        for entry in entries:
            if not entry.name.startswith('.'):  # Exclude hidden files/folders
                if entry.is_file():
                    current.append(entry.name)
                    print("File:", entry.name)
                elif entry.is_dir():
                    current.append({entry.name: list_files_in_folder(entry.path)})
                    print("Directory:", entry.name)
    return current

def get_all_contents(folder_path):
    current = {}
    with os.scandir(folder_path) as entries:
        for entry in entries:
            if not entry.name.startswith('.'):  # Exclude hidden files/folders
                if entry.is_file():
                    with open(entry.path, 'r') as f:
                        current[entry.path] = f.read()
    return current

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

def summarize_changes(old_directory,new_directory,verbose=False):
    summary = ""

    messages = [ {"role": "system", "content": '''You are an intelligent system that knows the past and present versions of files and directories'''} ]

    ## Directory Differences ##

    if verbose:
        print("listing out directory")

    old_directory = list_files_in_folder(old_directory)
    new_directory = list_files_in_folder(new_directory)


    directory_diff_prompt = f"""
    Given the following before and after of a directory, describe the difference between the before and after. Describe it in a format like this: "file a was added to folder b. file c was deleted from folder f"
    Past Directory: {old_directory}
    Present Directory: {new_directory}
    """

    if verbose:
        print("Generating ai directory differences")

    reply,messages = send_it(messages, directory_diff_prompt)

    summary += reply

    print("summary:",summary)
    print("-"*20)

    ## File Differences ##

    if verbose:
        print("listing out files")

    old_files = get_all_contents(r"C:\Users\parke\OneDrive\Documents\GitHub\AgentSyncScript\practice_old")
    new_files = get_all_contents(r"C:\Users\parke\OneDrive\Documents\GitHub\AgentSyncScript\practice_new")

    file_diff_prompt = lambda old_file, new_file: f"""
    Given the following before and after of a file, describe the differences between them. 
    This is an example: "a line was added to main.py to print the name of the file"
    Now, describe the difference between the following versions:
    Past Version: {old_file[1]}  
    Present Version: {new_file[1]}
    """

    if verbose:
        print("Generating ai file differences")

    for file in new_files:
        file_name = file.split("\\")[-1]

        if verbose:
            print(f"Generating ai file difference for {file}")

        try:
            old_file = (file_name,old_files[file])
        except KeyError:
            old_file = (file_name, f"the file {file} did not exist in the past")

        new_file = (file_name,new_files[file])

        if old_file[1] == new_file[1]:
            reply = f"the file {file_name} did not change"
            if verbose:
                print(f"{file_name}: No change")
        else:
            reply,messages = send_it(messages, file_diff_prompt(old_file, new_file))

        summary +=f"\n{new_file[0]}: {reply}"

        print("summary:",summary)
        print("-"*20)


    ## Summary ##

    if verbose:
        print("Generating ai summary")
        print("Summary:",summary)

    summary_prompt = """
    Given the following summary of the before and after of a programming project, describe the difference between the before and after. Describe it in a format well suited for a commit message with a summary line and a description line. The summary line should be a short description of the change. The description line should be a longer description of the change. No code should be in the summary or description. They should be able to be read by a human to understand the change. 
    Summary: {summary}
    """

    reply,messages = send_it(messages, summary_prompt.format(summary=summary))
    
    return reply,messages

def main():
    old = r"C:\Users\parke\OneDrive\Documents\GitHub\AgentSyncScript\practice_old"
    new = r"C:\Users\parke\OneDrive\Documents\GitHub\AgentSyncScript\practice_new"

    summary = summarize_changes(old,new,verbose=True)[0]
    print(summary)
if __name__=="__main__":
    main()