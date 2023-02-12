from flask import Flask, request
import time
from typing import List
import os
import openai
import telebot
import random
import string
import datetime
import nltk
from nltk.tokenize import word_tokenize

secret = "c8c288d0-6d7c-49b7-8b3e-2644fb6f589c"
bot = telebot.TeleBot('5920358297:AAH24s97cxlnx7WsUqA1tZ9RnHWS9lcmFpw', threaded=False)
openai.api_key = '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'

GPT3Model = 'text-davinci-003'
CurieModel = 'text-curie-001'
BabbageModel = 'text-babbage-001'
AdaModel = 'text-ada-001'
directory = 'https://www.pythonanywhere.com/user/Gagutuun/files/home/Gagutuun/mysite'
selected_model = 'text-davinci-003'
conversation_history = {}
current_chat = {}
conversation_all = {}
keywords_history = {}
chat_creator = {}
model_engine = {
    'text-davinci-003': GPT3Model,
    'text-curie-001': CurieModel,
    'text-babbage-001': BabbageModel,
    'text-ada-001': AdaModel
}

bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url="https://Gagutuun.pythonanywhere.com/{}".format(secret))

app = Flask(__name__)

@app.route('/{}'.format(secret), methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    print("Message")
    return "ok", 200


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(chat_id=message.chat.id, text="Welcome to my bot! Here are the available commands:")
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = telebot.types.KeyboardButton('/newchat')
    itembtn2 = telebot.types.KeyboardButton('/reset')
    itembtn3 = telebot.types.KeyboardButton('/delete')
    itembtn4 = telebot.types.KeyboardButton('/showchats')
    itembtn5 = telebot.types.KeyboardButton('/save')
    itembtn6 = telebot.types.KeyboardButton('/load')
    itembtn7 = telebot.types.KeyboardButton('/changemodel')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7)
    bot.send_message(chat_id=message.chat.id, text="Please select a command:", reply_markup=markup)

# Handle incoming messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    last_message_by_user = True
    text = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id
    if chat_id not in current_chat:
        current_chat[chat_id] = None

    # Creating new chat
    if '/newchat' in text.lower():
        new_chat_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        conversation_history[new_chat_id] = []
        conversation_all[new_chat_id] = []
        keywords_history[new_chat_id] = []
        current_chat[chat_id] = new_chat_id
        chat_creator[new_chat_id] = user_id
        bot.send_message(chat_id=chat_id, text = f"New chat created with id: {new_chat_id}.")

    elif '/changemodel' in text.lower():
        keyboard = telebot.types.InlineKeyboardMarkup()
        for model in model_engine:
            callback_button = telebot.types.InlineKeyboardButton(model, callback_data=model)
            keyboard.add(callback_button)
        bot.send_message(message.chat.id, "Select a model:", reply_markup=keyboard)

    # Reset context of conversation
    elif '/reset' in text.lower():
        if current_chat[chat_id]:
            if chat_creator[current_chat[chat_id]] == user_id:
                conversation_history[current_chat[chat_id]] = []
                keywords_history[current_chat[chat_id]] = []
                bot.send_message(chat_id=chat_id, text = "Conversation history has been reset.")
            else:
                bot.send_message(chat_id=chat_id, text = "You are not authorized to reset this chat.")
        else:
            bot.send_message(chat_id=chat_id, text = "No chat selected. Please create a new chat or switch to an existing one.")

    # Show all extists chats
    elif '/showchats' in text.lower():
        user_id = message.from_user.id
        user_chats = []
        for chat_id, creator in chat_creator.items():
            if creator == user_id:
                user_chats.append(chat_id)
        if user_chats:
            reply_markup = telebot.types.InlineKeyboardMarkup()
            for chat in user_chats:
                reply_markup.add(telebot.types.InlineKeyboardButton(chat, callback_data=chat))
            bot.send_message(chat_id=message.chat.id, text = "Choose a chat to switch to:", reply_markup=reply_markup)
        else:
            bot.send_message(chat_id=message.chat.id, text = "You have not created any chats.")


    # Save converstaion in txt doc and delete active chat
    elif '/save' in text.lower():
        if current_chat[chat_id]:
            conversation_all[current_chat[chat_id]].append(text)
            current_time = datetime.datetime.now().strftime("%Y-%m-%dTIME%H-%M-%S")
            filename = f"{current_chat[chat_id]}-{current_time}.txt"
            with open(filename, 'w') as f:
                for i,line in enumerate(conversation_all[current_chat[chat_id]]):
                    if last_message_by_user == True:
                        f.write("User: "+line + '\n')
                        last_message_by_user = False
                    else:
                        f.write("Bot: "+line + '\n')
                        last_message_by_user = True
            bot.send_message(chat_id=chat_id, text = f"Conversation history of chat {current_chat[chat_id]} saved to file {filename}.")
            if current_chat[chat_id] in conversation_all:
                del conversation_history[current_chat[chat_id]]
                del conversation_all[current_chat[chat_id]]
                del current_chat[chat_id]
                current_chat[chat_id] = None
                bot.send_message(chat_id=chat_id, text = f"Active chat was deleted.")

    elif '/load' in text.lower():
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton("Upload file", callback_data="upload_file")
        markup.add(btn)
        bot.send_message(message.chat.id, "Please select a file to upload:", reply_markup=markup)

    elif '/delete' in text.lower():
        current_chat_id = current_chat[chat_id]
        if current_chat_id in chat_creator:
            if chat_creator[current_chat_id] == user_id:
                del conversation_history[current_chat_id]
                del conversation_all[current_chat_id]
                del keywords_history[current_chat_id]
                del chat_creator[current_chat_id]
                bot.send_message(chat_id=chat_id, text=f"Chat with id {current_chat_id} deleted.")
            else:
                bot.send_message(chat_id=chat_id, text="You are not the creator of this chat and cannot delete it.")
        else:
            bot.send_message(chat_id=chat_id, text="Invalid chat ID or chat no longer exists.")


    else:
        if current_chat[chat_id]:
            keywords = extract_keywords(text)
            keywords_history[current_chat[chat_id]].extend(keywords)
            print(keywords_history[current_chat[chat_id]])
            conversation_history[current_chat[chat_id]].append(text)
            conversation_all[current_chat[chat_id]].append(text)
            prompt = text + " (" + " ".join(keywords_history[current_chat[chat_id]]) + ")"
            print(prompt)
            bot.send_chat_action(message.chat.id, 'typing') # send the "typing" action
            response = openai.Completion.create(
                model=selected_model,
                prompt=prompt,
                temperature=0.5,
                max_tokens=3000,
                top_p=1,
                frequency_penalty=1,
                presence_penalty=1
            )
            print(selected_model)
            response_text = response.choices[0].text.strip()
            keywords_fromBot = extract_keywords(response_text)
            keywords_history[current_chat[chat_id]].extend(keywords_fromBot)
            # append the bot's response to the conversation history
            conversation_all[current_chat[chat_id]].append(response_text)
            bot.send_message(chat_id=chat_id, text=response.choices[0].text)
            last_message_by_user = True
        else:
            bot.send_message(chat_id=chat_id, text = "I don't understand you")

@bot.callback_query_handler(func=lambda call: call.data in conversation_history)
def handle_callback(call):
    if call.data in conversation_history:
        if chat_creator[call.data] == call.from_user.id:
            current_chat[call.message.chat.id] = call.data
            bot.send_message(chat_id=call.message.chat.id, text=f"Switched to chat with id: {call.data}.")
        else:
            bot.send_message(chat_id=call.message.chat.id, text="You are not the creator of this chat.")
    else:
        bot.send_message(chat_id=call.message.chat.id, text="Invalid chat ID or chat no longer exists.")


@bot.callback_query_handler(func=lambda call: call.data in model_engine)
def callback_inline(call):
        global selected_model
        if call.data in model_engine:
            selected_model = model_engine[call.data]
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Selected model: {}".format(selected_model))

@bot.callback_query_handler(func=lambda call: call.data == "commands")
def handle_commands(call):
    bot.send_message(call.message.chat.id, "Here are the available commands:\n/newchat - create a new chat\n/switchchat - switch to an existing chat\n/reset - reset the current chat's history\n/showchats - show existing chats\n/save - save the current chat's history to a file\n/load - load a saved chat's history from a file\n/commands - show this menu")

@bot.callback_query_handler(func=lambda call: call.data == "upload_file")
def upload_file(call):
    bot.send_message(call.message.chat.id, "Upload a file to continue.")
    bot.register_next_step_handler(call.message, process_file)

def process_file(message):
    if message.content_type == 'document':
        chat_id = message.chat.id
        file_info = bot.get_file(message.document.file_id)
        file = bot.download_file(file_info.file_path)
        filename = file_info.file_path.split('/')[-1]
        if filename.endswith('.txt'):
            with open(filename, 'wb') as f:
                f.write(file)
            with open(filename, 'r') as f:
                lines = f.readlines()
                conversation_history[current_chat[chat_id]] = []
                conversation_all[current_chat[chat_id]] = []
                last_message_by_user = True
                for line in lines:
                    if "User:" in line:
                        conversation_history[current_chat[chat_id]].append(line.replace("User: ",""))
                        conversation_all[current_chat[chat_id]].append(line.replace("User: ",""))
                        last_message_by_user = True
                    else:
                        conversation_history[current_chat[chat_id]].append(line.replace("Bot: ",""))
                        conversation_all[current_chat[chat_id]].append(line.replace("Bot: ",""))
                        last_message_by_user = False
                bot.send_message(chat_id=chat_id, text = f"Loaded conversation from file: {filename}")
            os.remove(filename)
        else:
            bot.send_message(chat_id=chat_id, text = "error")


def extract_keywords(text: str) -> List[str]:
    words = word_tokenize(text)
    tagged_words = nltk.pos_tag(words)
    keywords = [word for word, pos in tagged_words if pos in ['NN', 'NNS', 'NNP', 'NNPS']]
    return keywords

if __name__ == '__main__':
  bot.polling(none_stop=True)