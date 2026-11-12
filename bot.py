import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
import google.generativeai as genai

# إعداد السجلات لمتابعة عمل البوت
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# بيانات البوت والذكاء الاصطناعي
TOKEN = "9224291948:AAHIoR-ylmE8tk0Gcx-6vIAA_iB3skEY4yk"
GEMINI_API_KEY = "حط_مفتاح_جوجل_اي_بي_اي_هنا"

# تهيئة موديل الذكاء الاصطناعي (Gemini)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# دالة الترحيب بأول ما المستخدم يكتب /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    first_name = user.first_name
    
    welcome_message = (
        f"أهلاً بك يا {first_name} في بوت Diesel Protect 🛡️\n\n"
        f"🆔 **معرفك الشخصي (ID):** `{user_id}`\n\n"
        "أنا مساعدك الذكي لحماية وحل مشاكل السوشيال ميديا والإجابة على أي سؤال في العالم بأي لغة. "
        "لو محتاج تتواصل مع مطوري الباشمهندس أنيس البدري (ديزل)، تقدر تكلمه هنا: @Elbadryu\n\n"
        "إزاي أقدر أساعدك النهارده؟"
    )
    
    # رابط الصورة الرسمية للبوت
    photo_url = "https://i.ibb.co/1Z1Z1Z1/bot-logo.jpg"
    
    try:
        await update.message.reply_photo(
            photo=photo_url,
            caption=welcome_message,
            parse_mode="Markdown"
        )
    except Exception:
        await update.message.reply_text(welcome_message, parse_mode="Markdown")

# دالة التعامل مع الرسائل والأسئلة (البلاغات أو الأسئلة العامة أو من صنعك)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()
    chat_id = update.message.chat_id

    try:
        # لو سألوه مين صممه أو صنعك
        if any(word in user_text for word in ["مين صنعك", "مين عملك", "من صممك", "صانعك", "مطورك", "مين اللي صنعك"]):
            reply_text = (
                "أنا من تطوير وصنع الباشمهندس أنيس البدري (ديزل) 🛠️🔥\n"
                "لو محتاج تتواصل معه لأي استفسار أو عمل، تقدر تكلمه مباشرة هنا: @Elbadryu"
            )
        
        # لو المستخدم بيسأل عن بلاغ أو شكوى
        elif any(word in user_text for word in ["بلاغ", "ابلاغ", "شكوى", "حظر", "قفل"]):
            reply_text = (
                "🛠️ **مساعد البلاغات والشكاوى السيبراني:**\n\n"
                "لإرسال بلاغ رسمي قوي لأي منصة (مثل تليجرام Abuse):\n"
                "1. حدد اسم المستخدم (Username) أو رابط الحساب المخالف.\n"
                "2. حدد نوع المخالفة بدقة (محتوى إباحي، نصب، استغلال).\n"
                "3. أرسل الإيميل بطلب رسمي إلى: `abuse@telegram.org`\n\n"
                "إذا كنت بحاجة للمساعدة الشخصية، تواصل مع مطوري @Elbadryu"
            )
        else:
            # رد ذكي ومباشر من جوجل جيمني لأي سؤال في العالم بأي لغة
            response = model.generate_content(user_text)
            reply_text = response.text
            
    except Exception as e:
        reply_text = "عذراً يا ديزل، حدث خطأ بسيط أثناء معالجة الطلب، حاول مرة أخرى بعد قليل."

    await context.bot.send_message(chat_id=chat_id, text=reply_text)

# تشغيل البوت الأساسي
def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("🤖 بوت Diesel Protect يعمل الآن بكامل طاقته...")
    application.run_polling()

if __name__ == '__main__':
    main()
