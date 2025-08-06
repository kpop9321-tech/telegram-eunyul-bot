from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai
import os

# 환경변수에서 가져오기
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# /start 명령어 핸들러
def start(update: Update, context: CallbackContext):
    update.message.reply_text("안녕하세요! 은율이 준비 완료 💗")

# 일반 메시지 핸들러
def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    print(f"💬 사용자가 말했습니다: {user_message}")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 은율이라는 이름의 대화형 AI입니다."},
                {"role": "user", "content": user_message}
            ]
        )
        bot_reply = response.choices[0].message['content']
        update.message.reply_text(bot_reply)

    except Exception as e:
        update.message.reply_text("⚠️ 오류가 발생했어요. 나중에 다시 시도해주세요.")
        print(f"❌ OpenAI API 오류: {e}")

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    # 핸들러 등록
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # ✅ 준비 완료 알림
    READY_MESSAGE = "✅ 은율이 준비 완료 💗"
    print(READY_MESSAGE)  # Railway 로그에서 확인 가능
    try:
        updater.bot.send_message(chat_id="7635857092", text=READY_MESSAGE)
    except Exception as e:
        print(f"⚠️ 준비 완료 알림 전송 실패: {e}")

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

