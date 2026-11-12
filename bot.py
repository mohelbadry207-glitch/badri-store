import os
import json
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

# إعدادات السجل
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# التوكن والآي دي الخاص بك يا بدري
TOKEN = "9274836401:AAEMaB6auOfZzlBNab1tEBI9PziRiRzWn_k"
ADMIN_ID = 5177962707
DEVELOPER_NAME = "البدري (الديزل)"

DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def get_group_file(chat_id):
    return os.path.join(DATA_DIR, f"{chat_id}.json")

def load_group_data(chat_id):
    file_path = get_group_file(chat_id)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "rules": "أهلاً بك! يرجى الالتزام بقوانين المجموعة والاحترام المتبادل.",
        # كلمات محظورة افتراضية (شتائم أو طلبات رصيد وشحاتة واستخفاف دم)
        "banned_words": [
            "شحن", "رصيد", "مجانا", "مجاني", "ثغرة", "فلوس", "كاش", 
            "عايز رصيد", "محتاج رصيد", "تحويل", "vodafone"
        ],
        "custom_replies": {
            "السلام عليكم": "وعليكم السلام ورحمة الله وبركاته يا هلا بيك!",
            "ازيك": "الحمد لله يا غالي كله تمام، أنت اخبارك ايه؟",
            "منور": "ده نورك يا بدري، تسلم لي!"
        }
    }

def save_group_data(chat_id, data):
    file_path = get_group_file(chat_id)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 1. أمر البدء
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id == ADMIN_ID:
        welcome_text = f"أهلاً بيك يا زعيمنا ومطورنا البشمهندس {DEVELOPER_NAME} 🚀\nالبوت حارس الجروب يعمل بكامل طاقته!"
    else:
        welcome_text = (
            f"أهلاً بيك يا {user.first_name} في مجموعتنا! 🤖\n"
            f"🔹 مبرمج ومطور هذا البوت هو: **{DEVELOPER_NAME}**\n"
            "⚠️ تنبيه: الجروب محمي بنظام ذكي، أي شتيمة، سبام، أو طلب رصيد وشحاتة يعرض صاحبها للحظر الفوري."
        )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

# 2. الرد الفوري لو حد سأل عن المطور
async def developer_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text.lower()
    dev_keywords = ["مين مطورك", "من مطورك", "مين صانعك", "من صانعك", "مين اللي عملك", "مطورك مين", "صانعك مين"]
    if any(keyword in text for keyword in dev_keywords):
        await update.message.reply_text(
            f"المطور وصانع هذا البوت هو العبقري **{DEVELOPER_NAME}** 🛠🔥\n"
            f"معرف المطور (ID): `{ADMIN_ID}`",
            parse_mode="Markdown"
        )

# 3. عرض القوانين
async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    data = load_group_data(chat_id)
    await update.message.reply_text(f"📌 قوانين المجموعة:\n\n{data.get('rules')}")

# 4. إضافة كلمة ممنوعة جديدة (للمطور فقط)
async def add_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("❌ عذراً، هذا الأمر للمطور (البدري) فقط.")
        return
        
    if not context.args:
        await update.message.reply_text("⚠️ اكتب الكلمة المراد حظرها. مثال:\n`/addword كلمة`", parse_mode="Markdown")
        return

    word = context.args[0].lower()
    chat_id = update.effective_chat.id
    data = load_group_data(chat_id)
    
    if word not in data["banned_words"]:
        data["banned_words"].append(word)
        save_group_data(chat_id, data)
        await update.message.reply_text(f"✅ تم إضافة الكلمة (`{word}`) لقائمة الحظر الفوري بنجاح.", parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠️ هذه الكلمة موجودة مسبقاً في قائمة الحظر.")

# 5. النظام الذكي والحازم لمراقبة الرسائل (طرد وحظر فوري للمخالفين)
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    chat = update.effective_chat
    user = update.effective_user
    text = update.message.text.lower()
    chat_id = chat.id
    
    # فحص سؤال المطوّر
    dev_keywords = ["مين مطورك", "من مطورك", "مين صانعك", "من صانعك", "مين اللي عملك", "مطورك مين", "صانعك مين"]
    if any(keyword in text for keyword in dev_keywords):
        await update.message.reply_text(
            f"المطور وصانع هذا البوت هو العبقري **{DEVELOPER_NAME}** 🛠🔥\n"
            f"معرف المطور (ID): `{ADMIN_ID}`",
            parse_mode="Markdown"
        )
        return

    data = load_group_data(chat_id)

    # التحقق من الجروب وتطبيق الحظر
    if chat.type in ["group", "supergroup"]:
        try:
            member = await chat.get_member(user.id)
            # استثناء المشرفين والمالك من الحظر
            if member.status in ["creator", "administrator"] or user.id == ADMIN_ID:
                return
        except Exception:
            pass

        # فحص الكلمات المحظورة (شتائم، طلبات رصيد، استخفاف دم ومحاولات نصب)
        banned_words = data.get("banned_words", [])
        for word in banned_words:
            if word in text:
                try:
                    # 1. حذف الرسالة المخالفة فوراً
                    await update.message.delete()
                    # 2. طرد أو حظر العضو نهائياً من الجروب
                    await chat.ban_member(user.id)
                    # 3. إرسال تنذير للجروب
                    await chat.send_message(
                        f"🚨 تم طرد وحظر العضو {user.first_name} نهائياً!\n"
                        f"السبب: محاولة إرسال محتوى مخالف، سبام، أو طلبات رصيد ممنوعة."
                    )
                except Exception as e:
                    # لو البوت مأخذش صلاحيات كافية (مشرف)
                    await chat.send_message(f"⚠️ تنبيه: العضو حاول نشر محتوى مخالف، لكن تأكد من منح البوت صلاحية (حظر الأعضاء).")
                return

    # الردود التلقائية العادية لو الرسالة سليمة
    custom_replies = data.get("custom_replies", {})
    for key, response in custom_replies.items():
        if key in text:
            await update.message.reply_text(response)
            return

    # لو في الخاص
    if chat.type == "private":
        await update.message.reply_text(f"أنا الحارس الشخصي لبوت البشمهندس {DEVELOPer_NAME}! تحت أمرك يا غالي.")

# تشغيل البوت
def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rules", rules))
    application.add_handler(CommandHandler("addword", add_word))
    
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_messages))

    print("🤖 بوت الحراسة الذكي يعمل الآن بكفاءة صارمة...")
    application.run_polling()

if __name__ == "__main__":
    main()
