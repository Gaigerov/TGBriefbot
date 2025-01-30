from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import smtplib
from email.mime.text import MIMEText

# Функция для отправки email
def send_email(subject, body):
    sender_email = "000"  # Укажите ваш email на Mail.ru
    sender_password = "000"  # Укажите ваш пароль от почты Mail.ru
    receiver_email = "000@mail.ru"  # Адрес получателя (можно оставить тот же)

    # Создаем сообщение
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        # Подключаемся к серверу Mail.ru
        with smtplib.SMTP_SSL('smtp.mail.ru', 465) as server:  # Используем SSL
            server.login(sender_email, sender_password)  # Логинимся
            server.send_message(msg)  # Отправляем сообщение
        print("Email отправлен успешно!")
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте! Я помогу вам заполнить бриф на застройку.\n"
        "Введите /brief, чтобы начать."
    )

# Начало заполнения брифа
async def brief(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()  # Очищаем данные пользователя
    await update.message.reply_text("Как вас зовут?")
    context.user_data['step'] = 'name'  # Устанавливаем текущий шаг

# Обработка ответов пользователя
async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get('step')

    if step == 'name':
        context.user_data['name'] = update.message.text
        
        # Инлайн-кнопки для выбора типа застройки
        keyboard = [
            [InlineKeyboardButton("Остров", callback_data='Остров')],
            [InlineKeyboardButton("Полуостров", callback_data='Полуостров')],
            [InlineKeyboardButton("Линейный", callback_data='Линейный')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Какой тип застройки вас интересует?", reply_markup=reply_markup)
        context.user_data['step'] = 'project_type'
    
    elif step == 'budget':
        context.user_data['budget'] = update.message.text
        await update.message.reply_text("Пожалуйста, укажите контактное лицо для связи (номер телефона).")
        context.user_data['step'] = 'contact'
    
    elif step == 'contact':
        context.user_data['contact'] = update.message.text
        await update.message.reply_text("Спасибо за заполнение брифа! Мы свяжемся с вами.")

        # Формируем данные для отправки на email с рамками
        email_body = (
            "==============================\n"
            f"Имя: {context.user_data['name']}\n"
            f"Тип застройки: {context.user_data['project_type']}\n"
            f"Бюджет: {context.user_data['budget']}\n"
            f"Контакт для связи: {context.user_data['contact']}\n"
            "==============================\n"
        )
        
        # Отправка данных на email
        send_email("Новый бриф на застройку", email_body)

        # Очистка данных пользователя после завершения
        context.user_data.clear()

# Обработка нажатий на инлайн-кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Подтверждаем нажатие кнопки

    context.user_data['project_type'] = query.data  # Сохраняем выбранный тип застройки
    await query.edit_message_text(text=f"Вы выбрали тип застройки: {query.data}. Укажите ваш бюджет.")
    
    context.user_data['step'] = 'budget'  # Переходим к следующему шагу


# Главная функция запуска бота
def main():
    app = ApplicationBuilder().token('TOKEN').build()

    # Обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("brief", brief))

    # Обработчик сообщений (ответы на вопросы)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))

    # Обработчик нажатий на инлайн-кнопки
    app.add_handler(CallbackQueryHandler(button_handler))

    # Запуск бота
    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()