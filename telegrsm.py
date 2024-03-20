import telebot

TOKEN ='6792117338:AAGWKJEU5B0iw1AO43BsxXXd3_tZmtn2z44'

CHAT_ID =[5867382409,1844173274]

# Initialize the bot outside the function
bot = telebot.TeleBot(TOKEN)

def send_message():
    message = "emergency"
    for i in CHAT_ID:
        bot.send_message(i, message)

# Call the function to send the message
send_message()
