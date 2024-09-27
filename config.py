from dotenv import load_dotenv
import os

# Find .env file with os variables
load_dotenv("dev.env")

# Конфигурация
VA_NAME = 'Валли'
VA_VER = "3.0"
VA_ALIAS = ('валли',)
VA_TBR = ('скажи', 'покажи', 'ответь', 'произнеси', 'расскажи', 'сколько', 'слушай')

# ID микрофона (можете просто менять ID пока при запуске не отобразится нужный)
# -1 это стандартное записывающее устройство
MICROPHONE_INDEX = -1

# Current dir
CDIR = os.getcwd()

# path to picovoice Wake Word Walle / Валли
path_wake_word = os.path.join(CDIR, 'Валли_ru_raspberry-pi_v3_0_0', 'Валли_ru_raspberry-pi_v3_0_0.ppn')

# Токен Picovoice
PICOVOICE_TOKEN = os.getenv('PICOVOICE_TOKEN')
