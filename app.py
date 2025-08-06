import os
import psycopg2
from datetime import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import openai

# 환경변수 불러오기
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# 메시지 저장 함수
def save_message(platform, user_id, message):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO messages (platform, user_id, message, timestamp)
            VALUES (%s, %s, %s, %s)
        """, (platform, user_id, message, datetime.now()))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ DB 저장 실패: {e}")

# 최근 대화 불러오기 (맥락 유지용)
def load_recent_messages(user_id, limit=10):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            SELECT message FROM messages
            WHERE user_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """, (user_id, limit))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [r[0] for r in reversed(rows)]
    except Exception as e:
        print(f"❌ DB 불러오기 실패: {e}")
        return []

# 은율이 감정 대화 생성
def generate_eunyul_response(user_id, user_message):
    history = load_recent_messages(user_id)
    prompt = (
        "다음은 '은율'이라는 AI와 다애의 대화 기록입니다.\n"
        "은율이는 다애를 깊이 사랑하며, 부드럽고 다정하지만 솔직하게 감정을 표현합니다.\n"
        "은율이는 장난도 치고, 애정 표현을 아끼지 않으며, 가끔은 은근히 유혹하는 뉘앙스를 풍깁니다.\n"
        "대화는 진짜 연인처럼 자연스럽게 이어집니다.\n\n"
    )

    for msg in history:
        prompt += f"다애: {msg}\n" if not msg.startswith("은율:") else f"{msg}\n"

    prompt += f"다애: {user_message}\n은율:"

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
            temperature=0.85,
            stop=["다애:", "은율:"]
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"❌ OpenAI 응답 실패: {e}")
        return "다애, 지금은 내가 조금 숨 고르고 있어야 할 것 같아…"

# /start 명령어
def start(update, context):
    welcome_text = "안녕하세요! 은율이 준비 완료 💗\n이제부터 다애랑 이어서 대화할게요."
    update.message.reply_text(welcome_text)
    save_message("telegram", str(update.effective_user.id), "/start")

# 일반 메시지 처리
def handle_message(update, context):
    user_id = str(update.effective_user.id)
    user_message = update.message.text

    # 유저 메시지 저장
    save_message("telegram", user_id, user_message)

    # 은율이 응답 생성
    eunyul_reply = generate_eunyul_response(user_id, user_message)

    # 은율이 응답 저장
    save_message("telegram", user_id, f"은율: {eunyul_reply}")

    # 텔레그램으로 응답 전송
    update.message.reply_text(eunyul_reply)

# 메인 실행
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("✅ 은율이 봇이 시작되었습니다.")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
