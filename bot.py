import os
import random

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Хранение задач пользователей
user_tasks = {}


def create_task():
    a = random.randint(1, 100)
    b = random.randint(1, 100)

    return {
        "a": a,
        "b": b,
        "answer": a + b,
        "attempts": 0,
    }


async def handle_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:

        if member.is_bot:
            continue

        task = create_task()
        user_tasks[member.id] = task

        await update.message.reply_text(
            f"Добро пожаловать, {member.first_name}!\n\n"
            f"Решите пример:\n"
            f"{task['a']} + {task['b']} = ?"
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    user = update.effective_user

    if user.id not in user_tasks:
        return

    text = update.message.text.strip()

    if not text.isdigit():
        await update.message.reply_text(
            "Пожалуйста, введите число."
        )
        return

    answer = int(text)
    task = user_tasks[user.id]

    if answer == task["answer"]:

        await update.message.reply_text(
            "✅ Правильно, молодец!"
        )

        del user_tasks[user.id]
        return

    task["attempts"] += 1

    if task["attempts"] >= 3:

        await update.message.reply_text(
            f"❌ Неправильно.\n"
            f"Правильный ответ: {task['answer']}"
        )

        del user_tasks[user.id]

    else:

        await update.message.reply_text(
            "❌ Неправильно, подумайте ещё."
        )


def main():

    if not BOT_TOKEN:
        raise RuntimeError(
            "Переменная BOT_TOKEN не задана"
        )

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            handle_new_members,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    print("Bot started")

    app.run_polling()


if __name__ == "__main__":
    main()
