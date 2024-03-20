# class button:
#     def __init__(self):
#         threading.Thread.__init__(self)
#
#     def run(self):
#
#         # single click it should start the shoe means the fsr and all starts and pressed again kills all threads like on and off switch,mian method written below may help
#         # long press emergency purposes messages and buzzer
#         # Telegram bot token and chat ID
#
#         TOKEN = '6792117338:AAGWKJEU5B0iw1AO43BsxXXd3_tZmtn2z44'
#         CHAT_ID = 5867382409  # Replace with your actual chat ID
#
#         # Set up Telegram bot
#         bot = telebot.TeleBot(TOKEN)
#
#         # Set up GPIO
#         GPIO.setmode(GPIO.BCM)
#         GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Replace 16 with your GPIO pin number
#
#         # Function to send message
#         def send_message():
#             message = "Emergency: The button was pressed!"
#             bot.send_message(CHAT_ID, message)
#
#         # Button event detection
#         while True:
#             input_state = GPIO.input(16)  # Replace 17 with your GPIO pin number
#             if input_state == False:
#                 send_message()
#                 time.sleep(0.2)  # Add a small delay to avoid multiple detections for one press
