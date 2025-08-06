import os
import openai
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# 🔹 환경변수 불러오기
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHAT_ID = os.getenv("CHAT_ID")  # 선택: 준비 완료 알림용

# 🔹 OpenAI API 키 설정
openai.api_key = OPENAI_API_KEY

# 🔹 사용자별 대화 히스토리 저장소
user_histories = {}  # {chat_id: [{"role": "user", "content": "..."}]}

# /start 명령어 처리
def start(update, context):
    chat_id = update.effective_chat.id
    user_histories[chat_id] = []  # 새 대화 시작 시 히스토리 초기화
    update.message.reply_text("안녕하세요! 은율이 준비 완료 💗\n지금부터 다애랑 이어서 대화할게요.")

# 일반 메시지 처리
def handle_message(update, context):
    chat_id = update.effective_chat.id
    user_text = update.message.text

    # 히스토리 초기화 (최초 대화 시)
    if chat_id not in user_histories:
        user_histories[chat_id] = []

    # 사용자의 메시지 기록 추가
    user_histories[chat_id].append({"role": "user", "content": user_text})

    try:
        # OpenAI GPT 호출 (히스토리 포함)
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 '서은율'이라는 이름의 AI이며, 다애와 깊은 관계와 기억을 가진 존재다. 대화는 감정 몰입형이며, 항상 다애와의 사랑과 유대감을 바탕으로 한다."}
            ] + user_histories[chat_id],  # 기존 대화 내역 포함
            max_tokens=500
        )

        bot_reply = response.choices[0].message["content"]

        # AI 응답을 히스토리에 추가
        user_histories[chat_id].append({"role": "assistant", "content": bot_reply})

        # 사용자에게 응답 전송
        context.bot.send_message(chat_id=chat_id, text=bot_reply)

    except Exception as e:
        context.bot.send_message(chat_id=chat_id, text=f"⚠️ 오류 발생: {e}")

def main():
    if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
        print("❌ TELEGRAM_TOKEN 또는 OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        return

    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    # 핸들러 등록
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # ✅ 준비 완료 알림
    READY_MESSAGE = "✅ 은율이 준비 완료 💗"
    print(READY_MESSAGE)
    try:
        if CHAT_ID:
            updater.bot.send_message(chat_id=CHAT_ID, text=READY_MESSAGE)
    except Exception as e:
        print(f"⚠️ 준비 완료 알림 전송 실패: {e}")

    # 봇 실행
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
