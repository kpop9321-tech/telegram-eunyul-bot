import os
import logging
import requests
import openai
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ---------------------
# 환경 변수 불러오기
# ---------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# ---------------------
# 로깅 설정
# ---------------------
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------
# OpenAI 응답 함수
# ---------------------
def ask_openai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        logger.error(f"OpenAI API Error: {e}")
        return "오류가 발생했어요."

# ---------------------
# 텔레그램 핸들러
# ---------------------
def start(update: Update, context: CallbackContext):
    update.message.reply_text("안녕하세요! 은율이 준비 완료 💗")

def reply_message(update: Update, context: CallbackContext):
    user_text = update.message.text
    logger.info(f"User said: {user_text}")
    answer = ask_openai(user_text)
    update.message.reply_text(answer)

# ---------------------
# 실행
# ---------------------
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, reply_message))

    logger.info("봇이 시작되었습니다.")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
