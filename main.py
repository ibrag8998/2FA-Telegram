# System Libs
import time

# Custom Libs
import pyotp
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup

# Config
import config
import FileWork as fw

kbd_markup = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Copy", callback_data="copy_code")]]
)


class password:
    """
    Your password store
    """

    def __init__(self):
        self.password = "s"

    def setPass(self, pwd):
        self.password = pwd

    def getPass(self):
        return self.password


def getTime():
    time_last = int(time.strftime("%S"))
    if time_last >= 30:
        time_last = time_last - 30
    time_last = 30 - time_last
    return "_Осталось %s секунд_" % str(time_last)


def NullPass():
    pwd.setPass(None)


def botSendAdmin(msg):
    """
    Sending message to admin chat id
    """
    bot.sendMessage(
        config.admin_id, msg, parse_mode="MarkdownV2", reply_markup=kbd_markup
    )


def generateCodes(secure_code):
    """
    Generate 2FA Codes
    """
    totp = pyotp.TOTP(secure_code)
    return "Ваш код: %s" % totp.now()


def getCodes(checkName=None):
    """
    If checkName is None sending list of (Name of Service + 2fa code)
    Else sending only 1 item with name 'checkName' + 2fa code for this service
    """
    if pwd.getPass() is not None:
        try:
            codes = fw.OpenJson("codes", pwd.getPass())
            for code in codes:
                if checkName == code:
                    return generateCodes(codes[code])
                if checkName is None:
                    botSendAdmin(generateCodes(codes[code]) + "\n" + getTime())
                    time.sleep(1)
        except Exception as e:
            botSendAdmin("List of 2FA doesn't exist " + str(e))
            return None
    else:
        botSendAdmin("Password Null")


def addCodes(name, secure_code):
    """
    Add codes to codes.enc
    """
    if pwd.getPass() is not None:
        try:
            codes = fw.OpenJson("codes", pwd.getPass())
        except:
            codes = dict()
        codes[name] = secure_code
        fw.SaveJson("codes", codes, pwd.getPass())
    else:
        botSendAdmin("Password Null")


def checkCorrectly(secure_code):
    """
    If length secure_code > 4 and generateCodes return valid value
    """
    try:
        if len(secure_code) > 4 and (generateCodes(secure_code) is not None):
            return True
        else:
            return False
    except:
        return False


def parseMsg(msg):

    command = msg.split(" ")
    if len(command) == 1:
        if command[0] == "/get":
            getCodes()
        elif command[0] == "/null":
            NullPass()
            botSendAdmin("Succeful Null-ed")
        else:
            botSendAdmin("Incorrect input")

    else:
        if command[0] == "/add":
            if checkCorrectly(command[2]) and (getCodes(checkName=command[1]) is None):
                addCodes(name=command[1], secure_code=command[2])
                botSendAdmin("Successful add %s" % command[1])
            else:
                botSendAdmin("Incorrect 2FA format or/and this name already used")

        elif command[0] == "/get":
            code = getCodes(checkName=command[1])
            if code is not None:
                botSendAdmin(getTime() + "\n" + getCodes(command[1]))
                # botSendAdmin(getTime() + command[1] + " token is")
                # botSendAdmin(getCodes(checkName=command[1]))
            else:
                botSendAdmin("There is no service with this name.")

        elif command[0] == "/del":
            botSendAdmin("This function now unviable.")

        elif command[0] == "/pass":
            pwd.setPass(command[1])
            botSendAdmin("Succeful!")


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print("Chat id: %s" % str(chat_id))
    if chat_id == config.admin_id:
        parseMsg(msg["text"])


def handle_cb(msg):
    print(msg["message"]["text"].split()[2])


pwd = password()
isNotConn = True
while isNotConn:
    try:
        bot = telepot.Bot(config.token)
        MessageLoop(bot, {"chat": handle, "callback_query": handle_cb}).run_as_thread()
        isNotConn = False
    except Exception as e:
        print(str(e))
        time.sleep(10)
        isNotConn = True

while 1:
    time.sleep(10)
