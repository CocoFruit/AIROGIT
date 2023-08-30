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

def main():

    old_directory = {'test_folder': ['test.py', {'test2_folder': ['test2.py']}]}
    new_directory = {'test_folder': ['test.py', {'test2_folder': ['test2.py', 'test3.py']}]}
    # file_system = {"test_folder": list_files_in_folder(r"C:\Users\parke\OneDrive\Documents\GitHub\AgentSyncScript\test_folder")}

    messages = [ {"role": "system", "content": '''You are an intelligent system that knows the past and present versions of files and directories'''} ]

    directory_diff_prompt = f"""
    Given the following directory, describe the differences between the two directories.
    Past Directory: {old_directory}
    Present Directory: {new_directory}
    """

    reply,messages = send_it(messages, directory_diff_prompt)


if __name__=="__main__":
    main()