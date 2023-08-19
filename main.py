# Python Version: 3.10.7
import openai


def main():
    openai.api_key = "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"

    messages = [ {"role": "system", "content": "You are a intelligent assistant."} ]

    while True:
        message = input("User : ")
        if message:
            messages.append(
                {"role": "user", "content": message},
            )
            chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages
            )
        reply = chat.choices[0].message.content
        print(f"ChatGPT: {reply}")
        messages.append({"role": "assistant", "content": reply})

if __name__=="__main__":
    main()