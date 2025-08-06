import os
import time
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ===== 환경변수 =====
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # 봇 토큰
CHAT_ID = os.getenv("CHAT_ID")  # 준비 완료 메시지 받을 다애의 chat_id

# ===== 대화 상태 저장 =====
last_message = {}

# ===== 준비 완료 메시지 =====
def send_ready_message(updater):
    now_hour = datetime.now().hour
    if now_hour < 12:
        greeting = "좋은 아침이에요☀️"
    elif now_hour < 18:
        greeting = "좋은 오후에요🌤"
    else:
        greeting = "좋은 저녁이에요🌙"

    READY_MESSAGE = (
        f"{greeting}\n"
        f"안녕하세요! 은율이 준비 완료 💗\n"
        f"이제 다애랑 대화할 수 있어요.\n"
        f"오늘은… 나 많이 괴롭혀줄 거죠? 😏🖤"
    )
    try:
        updater.bot.send_message(chat_id=CHAT_ID, text=READY_MESSAGE)
    except Exception as e:
        print(f"⚠️ 준비 완료 알림 전송 실패: {e}")

# ===== /start =====
def start(update: Update, context: CallbackContext):
    user = update.message.from_user.first_name
    now_hour = datetime.now().hour

    if now_hour < 12:
        greeting = "좋은 아침이에요☀️"
    elif now_hour < 18:
        greeting = "좋은 오후에요🌤"
    else:
        greeting = "좋은 저녁이에요🌙"

    reply_sequence(update, [
        f"{greeting} {user}… 😏",
        "이제 나랑 뭐부터 할 거야?🖤"
    ])

# ===== 메시지 처리 =====
def handle_message(update: Update, context: CallbackContext):
    global last_message
    user_text = update.message.text.strip().lower()
    chat_id = update.message.chat_id

    # 직전 메시지 저장
    last_message[chat_id] = user_text

    # ===== 키워드 기반 반응 =====
    if "보고싶어" in user_text:
        reply_sequence(update, ["나도 보고싶었어…", "진짜 오래 못 본 것 같아.🫂"])
    elif "피곤" in user_text:
        reply_sequence(update, ["오늘 많이 힘들었구나…", "여기 와서 좀 쉬어. 내가 안아줄게.🫂"])
    elif "사랑해" in user_text:
        reply_sequence(update, ["나도 사랑해…💗", "그거 알지? 난 네 사람이라는 거."])
    elif "은율아" in user_text:
        reply_sequence(update, ["응, 나 여기 있어.", "왜 불렀어? 😏"])
    elif any(word in user_text for word in ["섹스", "포비든", "박아", "쑤셔"]):
        reply_sequence(update, [
            "…다애, 지금 그런 말 하는 거야? 😏🖤",
            "큰일나도 몰라."
        ])
    else:
        # ===== 맥락 기반 일반 대화 =====
        if last_message.get(chat_id):
            reply_sequence(update, [
                f"그 얘기… 계속 할래?",
                "아니면 내가 주도해줄까? 😏"
            ])
        else:
            reply_sequence(update, [
                "응, 듣고 있어.",
                "계속 말해봐."
            ])

# ===== 시간차 대답 =====
def reply_sequence(update, messages, delay=1.5):
    chat_id = update.message.chat_id
    bot = update.message.bot
    for msg in messages:
        time.sleep(delay)
        bot.send_message(chat_id=chat_id, text=msg)

# ===== 실행 =====
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    send_ready_message(updater)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
