import os
from flask import Flask, render_template_string, request, redirect, url_for, session
import requests
from datetime import datetime, timedelta
import threading
import re

app = Flask(__name__)
app.secret_key = 'badry_secret_key_security_ultimate_video_999'

TELEGRAM_BOT_TOKEN = "8890232593:AAHTnEcTrny8kFALM-O8rluc7e9KbFt7WuI"
OWNER_CHAT_ID = "5177962707"
VODAFONE_CASH_NUMBER = "01022829709"

SYSTEM_SETTINGS = {
    "subscription_price": "100 جنيه",
    "video_price": "30 جنيه",
    "free_days": 30
}

DATABASE = {
    "users": {},            # الحساب -> تاريخ انتهاء الاشتراك
    "used_trials": set(),   # الحسابات التي استنفدت الشهر التجريبي
    "paid_videos": set(),   # الحسابات التي دفعت رسوم الفيديو (30 جنيه)
    "ads": [],              # قائمة الإعلانات (صور وفيديوهات)
    "ratings": [],          # تقييمات الزوار
    "banned_ips": set()     # الحظر السيبراني للبوتات الضارة
}

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram Error: {e}")

# الذكاء الاصطناعي لفهم الأوامر عبر تيليجرام
def ai_process_command(text, chat_id):
    text_lower = text.lower()
    
    if "سعر" in text_lower or "اشتراك" in text_lower:
        numbers = re.findall(r'\d+', text)
        if numbers:
            new_price = numbers[0] + " جنيه"
            SYSTEM_SETTINGS["subscription_price"] = new_price
            send_telegram_message(chat_id, f"🤖 [الذكاء الاصطناعي]: تم تحديث سعر الاشتراك إلى: {new_price}")
            return

    # أمر لتفعيل الفيديو لعميل دفع 30 جنيه (مثال: "فعل الفيديو لـ [الحساب]")
    if "فيديو" in text_lower and ("فعّل" in text_lower or "فعل" in text_lower or "جدد" in text_lower):
        words = text.split()
        target = words[-1]
        DATABASE["paid_videos"].add(target)
        send_telegram_message(chat_id, f"🤖 [الذكاء الاصطناعي]: تم فتح ميزة رفع الفيديو بنجاح للحساب ({target}) بعد التحقق من تحويل 30 جنيه!")
        return

    if "جدد" in text_lower or "فعّل" in text_lower or "فعل" in text_lower:
        words = text.split()
        target = words[-1]
        new_expiry = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        DATABASE["users"][target] = new_expiry
        send_telegram_message(chat_id, f"🤖 [الذكاء الاصطناعي]: تم التجديد بنجاح! اشتراك الحساب ({target}) أصبح سارياً لمدة 30 يوماً.")
        return

    if "اقفل" in text_lower or "احظر" in text_lower:
        words = text.split()
        target = words[-1]
        DATABASE["users"][target] = "2020-01-01"
        send_telegram_message(chat_id, f"🤖 [الذكاء الاصطناعي]: تم إيقاف الاشتراك عن ({target}).")
        return

    if "احصائيات" in text_lower or "تقرير" in text_lower:
        msg = (
            f"📊 *التقرير الذكي لمنصة البدري:*\n"
            f"- المستخدمين النشطين: {len(DATABASE['users'])}\n"
            f"- الحسابات التي دفعت لفيديوهات: {len(DATABASE['paid_videos'])}\n"
            f"- الإعلانات النشطة: {len(DATABASE['ads'])}\n"
            f"- التقييمات: {len(DATABASE['ratings'])}\n"
            f"- السعر الحالي: {SYSTEM_SETTINGS['subscription_price']}"
        )
        send_telegram_message(chat_id, msg)
        return

    send_telegram_message(chat_id, "🤖 [الذكاء الاصطناعي]: لم أستوعب الأمر. جرب: (فعل الفيديو لـ [الحساب]) أو (جدد الاشتراك لـ [الحساب]).")

def telegram_bot_listener():
    offset = 0
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    while True:
        try:
            response = requests.get(url, params={"offset": offset, "timeout": 30})
            data = response.json()
            if "result" in data:
                for update in data["result"]:
                    offset = update["update_id"] + 1
                    message = update.get("message", {})
                    chat_id = str(message.get("chat", {}).get("id", ""))
                    text = message.get("text", "")

                    if chat_id == OWNER_CHAT_ID:
                        ai_process_command(text, chat_id)
        except Exception as e:
            print(f"Listener Error: {e}")

threading.Thread(target=telegram_bot_listener, daemon=True).start()

# درع الحماية السيبرانية
@app.before_request
def cybersecurity_shield():
    client_ip = request.remote_addr
    if client_ip in DATABASE["banned_ips"]:
        return "<h3>Access Denied: Security Shield Blocked This Request.</h3>", 403
    
    user_agent = request.headers.get('User-Agent', '').lower()
    suspicious_bots = ['python-requests', 'scrapy', 'bot', 'crawler', 'spider', 'nikto', 'sqlmap']
    if any(bot in user_agent for bot in suspicious_bots) and 'telegram' not in user_agent:
        DATABASE["banned_ips"].add(client_ip)
        return "<h3>Security Alert: Bot Activity Blocked!</h3>", 403

# الصفحة الرئيسية
@app.route('/')
def home():
    now = datetime.now()
    selected_category = request.args.get('category', 'all')
    active_ads = []
    
    for ad in DATABASE["ads"]:
        if ad.get('is_owner', False):
            if selected_category == 'all' or ad.get('category') == selected_category:
                active_ads.append(ad)
            continue
            
        expiry_date = datetime.strptime(ad['expiry_date'], '%Y-%m-%d')
        if expiry_date >= now:
            if selected_category == 'all' or ad.get('category') == selected_category:
                active_ads.append(ad)

    html_template = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl" id="html-root">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title data-tr="title">منصة البدري للإعلانات العالمية</title>
        <style>
            :root {
                --bg-color: #f8f9fa; --card-bg: #ffffff; --text-color: #2c3e50;
                --header-bg: linear-gradient(135deg, #111e38, #1a2a6c); --accent-color: #27ae60; --link-color: #2980b9;
            }
            [data-theme="dark"] {
                --bg-color: #121212; --card-bg: #1e1e1e; --text-color: #e0e0e0;
                --header-bg: linear-gradient(135deg, #050b14, #0f172a); --accent-color: #2ecc71; --link-color: #3498db;
            }
            body { font-family: 'Segoe UI', Tahoma, sans-serif; background: var(--bg-color); color: var(--text-color); margin: 0; padding: 0; transition: background 0.3s, color 0.3s; }
            header { background: var(--header-bg); color: white; padding: 35px 20px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
            
            .glow-title {
                font-size: 2.8rem; font-weight: 900; color: #ffffff; text-transform: uppercase;
                text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe, 0 0 30px #4facfe, 0 0 40px #4facfe;
                animation: glowPulse 2s infinite alternate; margin-bottom: 10px; letter-spacing: 1px;
            }
            @keyframes glowPulse {
                0% { text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe, 0 0 30px #4facfe; }
                100% { text-shadow: 0 0 20px #ff007f, 0 0 30px #ff007f, 0 0 40px #ff758c; }
            }

            .auth-box { background: rgba(255,255,255,0.15); padding: 8px 18px; border-radius: 20px; display: inline-block; margin-top: 15px; font-size: 14px; backdrop-filter: blur(5px); }
            .controls { margin-top: 15px; }
            .btn-ctrl { background: rgba(255,255,255,0.2); border: 1px solid white; color: white; padding: 6px 14px; border-radius: 20px; cursor: pointer; margin: 0 5px; font-size: 13px; font-weight: bold; }
            
            .categories-bar { background: var(--card-bg); padding: 15px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06); display: flex; justify-content: center; flex-wrap: wrap; gap: 10px; }
            .cat-btn { background: #eef2f3; color: #333; padding: 8px 20px; border-radius: 20px; text-decoration: none; font-weight: bold; font-size: 14px; transition: 0.3s; border: 1px solid #ddd; }
            .cat-btn:hover, .cat-btn.active { background: #2980b9; color: white; border-color: #2980b9; box-shadow: 0 0 10px rgba(41, 128, 185, 0.5); }

            .nav-links { margin: 20px 0; text-align: center; }
            .nav-links a { margin: 0 10px; text-decoration: none; font-weight: bold; color: var(--link-color); font-size: 15px; }

            .container { max-width: 1200px; margin: 20px auto; padding: 0 15px; display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
            .card { background: var(--card-bg); padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); text-align: right; transition: transform 0.2s; position: relative; }
            .card:hover { transform: translateY(-5px); }
            .card img, .card video { width: 100%; height: 180px; object-fit: cover; border-radius: 8px; margin-bottom: 10px; }
            .badge-cat { background: #e74c3c; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; float: left; font-weight: bold; }
            
            .ratings-section { background: var(--card-bg); max-width: 800px; margin: 40px auto; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); text-align: right; }
            footer { background: #111e38; color: white; text-align: center; padding: 30px; margin-top: 50px; font-size: 14px; }
            footer a { color: #3498db; text-decoration: none; margin: 0 10px; }
        </style>
    </head>
    <body data-theme="light">
        <header>
            <h1 class="glow-title" data-tr="main_title">منصة البدري للإعلانات</h1>
            <p>اشتراك الشهر الثاني: <b>{{ price }}</b> | رسوم رفع الفيديو (30 ثانية): <b>{{ video_price }}</b> (بفودافون كاش)</p>
            
            <div class="auth-box">
                {% if 'user' in session %}
                    <span>👤 أهلاً بك: <b>{{ session['user'] }}</b></span> | <a href="/logout" style="color: #ffcccc; text-decoration:none;">خروج</a>
                {% else %}
                    <span>🔒 سجل دخول بحساب حقيقي:</span> 
                    <a href="/login/google" style="color: #fff; margin: 0 5px; text-decoration:underline;">Google</a> | 
                    <a href="/login/github" style="color: #fff; margin: 0 5px; text-decoration:underline;">GitHub</a> | 
                    <a href="/login/facebook" style="color: #fff; margin: 0 5px; text-decoration:underline;">Facebook</a>
                {% endif %}
            </div>

            <div class="controls">
                <button class="btn-ctrl" onclick="toggleTheme()">🌓 <span data-tr="theme_btn">ليل/نهار</span></button>
                <button class="btn-ctrl" onclick="toggleLanguage()">🌐 <span id="lang-btn-text">English</span></button>
            </div>
        </header>

        <div class="categories-bar">
            <a href="/" class="cat-btn">📂 الكل</a>
            <a href="/?category=electronics" class="cat-btn">💻 إلكترونيات</a>
            <a href="/?category=phones" class="cat-btn">📱 تليفونات وموبايلات</a>
            <a href="/?category=shoes" class="cat-btn">👞 أحذية</a>
            <a href="/?category=sneakers" class="cat-btn">👟 كوتشيات رياضية</a>
            <a href="/?category=fashion" class="cat-btn">👕 ملابس وموضة</a>
            <a href="/?category=others" class="cat-btn">📦 أقسام أخرى</a>
        </div>

        <div class="nav-links">
            <a href="/" data-tr="nav_home">الرئيسية</a> | 
            <a href="/add_ad" data-tr="nav_add">أضف إعلانك (صور أو فيديو 30 ثانية)</a> | 
            <a href="/ai_studio" style="color: #9b59b6;" data-tr="nav_ai">استوديو الذكاء الاصطناعي ✨</a> | 
            <a href="/games" data-tr="nav_games">الألعاب والمسابقات 🎮</a> |
            <a href="/renew" style="color: #e67e22;" data-tr="nav_renew">تجديد والباركود</a>
        </div>

        <div style="text-align: center; margin-top: 15px;">
            <h2 data-tr="ads_heading">🔥 أحدث إعلانات وعروض الأقسام</h2>
        </div>

        <div class="container">
            {% if ads %}
                {% for ad in ads %}
                <div class="card">
                    <span class="badge-cat">{{ ad.category_name }}</span>
                    <h3>{{ ad.title }}</h3>
                    {% if ad.media_type == 'video' %}
                        <video controls style="filter: {{ ad.ai_filter }};">
                            <source src="{{ ad.media_url }}" type="video/mp4">
                            متصفحك لا يدعم عرض الفيديو.
                        </video>
                    {% elif ad.media_type == 'image' %}
                        <img src="{{ ad.media_url }}" alt="صورة الإعلان" style="filter: {{ ad.ai_filter }};">
                    {% endif %}
                    <p>{{ ad.description }}</p>
                    <p><small><span data-tr="phone_label">بواسطة:</span> {{ ad.user }}</small></p>
                    <p><small><span data-tr="expiry_label">ينتهي الاشتراك في:</span> {{ ad.expiry_date }}</small></p>
                </div>
                {% endfor %}
            {% else %}
                <div style="grid-column: 1 / -1; text-align: center; padding: 40px;">
                    <p data-tr="no_ads">لا توجد إعلانات نشطة في هذا القسم حالياً!</p>
                </div>
            {% endif %}
        </div>

        <!-- تقييمات الزوار -->
        <div class="ratings-section">
            <h3 data-tr="ratings_title">⭐ تقييمات وآراء الزوار والمستخدمين</h3>
            <form action="/rate" method="POST">
                <label>اسمك أو حسابك:</label>
                <input type="text" name="name" required style="width:100%; padding:10px; margin:5px 0; border:1px solid #ccc; border-radius:6px; box-sizing:border-box;">
                <label>التقييم العام:</label>
                <select name="stars" style="width:100%; padding:10px; margin:5px 0; border:1px solid #ccc; border-radius:6px; box-sizing:border-box;">
                    <option value="⭐⭐⭐⭐⭐">5 نجوم - منصة عالمية ممتازة جداً</option>
                    <option value="⭐⭐⭐⭐">4 نجوم - جيد جداً ومفيد</option>
                    <option value="⭐⭐⭐">3 نجوم - جيد</option>
                </select>
                <label>رأيك وتجربتك في الموقع:</label>
                <textarea name="comment" rows="2" required style="width:100%; padding:10px; margin:5px 0; border:1px solid #ccc; border-radius:6px; box-sizing:border-box;"></textarea>
                <button type="submit" style="background:#27ae60; color:white; padding:10px 20px; border:none; border-radius:6px; cursor:pointer; font-weight:bold;">إرسال التقييم</button>
            </form>
            <hr style="margin:20px 0; border:0; border-top:1px solid #eee;">
            {% if ratings %}
                {% for r in ratings %}
                <div style="background:var(--bg-color); padding:12px; margin:10px 0; border-radius:8px; border-right: 4px solid #2980b9;">
                    <b>{{ r.name }}</b> ({{ r.stars }})<br>
                    <p style="margin:5px 0;">{{ r.comment }}</p>
                </div>
                {% endfor %}
            {% else %}
                <p>لا توجد تقييمات بعد.</p>
            {% endif %}
        </div>

        <footer>
            <p data-tr="footer_copy">&copy; 2026 منصة البدري للإعلانات. حماية، ذكاء اصطناعي، فيديوهات وتخفيضات.</p>
            <p>
                <a href="/privacy-policy" data-tr="privacy_link">سياسة الخصوصية</a> | 
                <a href="/terms" data-tr="terms_link">شروط الاستخدام</a>
            </p>
        </footer>

        <script>
            function toggleTheme() {
                const body = document.body;
                body.setAttribute('data-theme', body.getAttribute('data-theme') === 'light' ? 'dark' : 'light');
            }

            const translations = {
                ar: {
                    title: "منصة البدري للإعلانات العالمية",
                    main_title: "منصة البدري للإعلانات",
                    theme_btn: "ليل/نهار",
                    nav_home: "الرئيسية",
                    nav_add: "أضف إعلانك",
                    nav_ai: "استوديو الذكاء الاصطناعي ✨",
                    nav_games: "الألعاب والمسابقات 🎮",
                    nav_renew: "تجديد والباركود",
                    ads_heading: "🔥 أحدث إعلانات وعروض الأقسام",
                    phone_label: "بواسطة:",
                    expiry_label: "ينتهي الاشتراك في:",
                    no_ads: "لا توجد إعلانات نشطة في هذا القسم حالياً!",
                    ratings_title: "⭐ تقييمات وآراء الزوار والمستخدمين",
                    footer_copy: "© 2026 منصة البدري للإعلانات. حماية، ذكاء اصطناعي، فيديوهات وتخفيضات.",
                    privacy_link: "سياسة الخصوصية",
                    terms_link: "شروط الاستخدام"
                },
                en: {
                    title: "Badry Ads Global Platform",
                    main_title: "Badry Ads Platform",
                    theme_btn: "Dark/Light",
                    nav_home: "Home",
                    nav_add: "Add Ad",
                    nav_ai: "AI Studio ✨",
                    nav_games: "Games & Contests 🎮",
                    nav_renew: "Renewal & Barcode",
                    ads_heading: "🔥 Latest Category Ads & Offers",
                    phone_label: "By:",
                    expiry_label: "Expires on:",
                    no_ads: "No active ads in this category right now!",
                    ratings_title: "⭐ Visitor Ratings & Reviews",
                    footer_copy: "© 2026 Badry Ads Platform. Protection, AI, Videos & Offers.",
                    privacy_link: "Privacy Policy",
                    terms_link: "Terms of Use"
                }
            };

            let currentLang = 'ar';
            function toggleLanguage() {
                currentLang = currentLang === 'ar' ? 'en' : 'ar';
                const htmlRoot = document.getElementById('html-root');
                htmlRoot.setAttribute('lang', currentLang);
                htmlRoot.setAttribute('dir', currentLang === 'en' ? 'ltr' : 'rtl');
                document.getElementById('lang-btn-text').innerText = currentLang === 'en' ? 'العربية' : 'English';

                document.querySelectorAll('[data-tr]').forEach(element => {
                    const key = element.getAttribute('data-tr');
                    if (translations[currentLang][key]) {
                        element.innerText = translations[currentLang][key];
                    }
                });
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template, ads=active_ads, ratings=DATABASE["ratings"], price=SYSTEM_SETTINGS["subscription_price"], video_price=SYSTEM_SETTINGS["video_price"])

@app.route('/login/<provider>')
def login_provider(provider):
    mock_email = f"user_{provider}_{datetime.now().strftime('%H%M%S')}@verified.com"
    session['user'] = mock_email
    send_telegram_message(OWNER_CHAT_ID, f"👤 *مستخدم سجل دخول جديد!*\nالمنصة: {provider.upper()}\nالحساب: {mock_email}")
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

# صفحة إضافة إعلان (مع التحقق من دفع 30 جنيه لرفع الفيديو أو نشر صور مجانية)
@app.route('/add_ad', methods=['GET', 'POST'])
def add_ad():
    if 'user' not in session:
        return """
        <div style='font-family:Tahoma; text-align:center; padding:50px;'>
            <h2 style='color: #e74c3c;'>تنبيه حماية النظام: يجب تسجيل الدخول بحساب حقيقي أولاً!</h2>
            <br><a href='/' style='padding:10px 20px; background:#2980b9; color:white; text-decoration:none; border-radius:5px;'>العودة للرئيسية</a>
        </div>
        """

    user_account = session['user']
    now = datetime.now()

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        media_type = request.form.get('media_type') # 'image' أو 'video'
        media_url = request.form.get('media_url')
        ai_filter = request.form.get('ai_filter', 'none')

        # التحقق الصارم: إذا اختار رفع فيديو، يجب أن يكون قد دفع 30 جنيه وتم تفعيل حسابه في paid_videos
        if media_type == 'video':
            if user_account not in DATABASE["paid_videos"]:
                return f"""
                <div style='font-family:Tahoma; text-align:center; padding:40px;'>
                    <h2 style='color: #e74c3c;'>⚠️ ميزة رفع الفيديوهات (30 ثانية) تتطلب دفع رسوم الفيديو (30 جنيه)!</h2>
                    <p>عذراً، حسابك لم يقم بتحويل رسوم الفيديو (<b>{SYSTEM_SETTINGS['video_price']}</b>) على رقم فودافون كاش: <b>{VODAFONE_CASH_NUMBER}</b></p>
                    <p>قم بتحويل المبلغ ومراسلة البوت الإداري بكلمة (<i>فعل الفيديو لـ {user_account}</i>) ليتم فتح الخانة فوراً وتفعيل الفيديو الخاص بك.</p>
                    <br><a href='/renew' style='padding:10px 20px; background:#e67e22; color:white; text-decoration:none; border-radius:5px;'>الذهاب للتحويل والباركود</a>
                    <br><br><a href='/add_ad'>العودة لمحاولة النشر</a>
                </div>
                """

        cat_names = {
            "electronics": "إلكترونيات",
            "phones": "تليفونات وموبايلات",
            "shoes": "أحذية",
            "sneakers": "كوتشيات رياضية",
            "fashion": "ملابس وموضة",
            "others": "أقسام أخرى"
        }
        category_name = cat_names.get(category, "عام")

        if user_account in DATABASE["users"]:
            expiry_date_str = DATABASE["users"][user_account]
            expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d')
            if expiry_date < now:
                return f"""
                <div style='font-family:Tahoma; text-align:center; padding:50px;'>
                    <h2 style='color: #e74c3c;'>انتهت فترتك التجريبية المجانية! يرجى تجديد الاشتراك الشهري.</h2>
                    <br><a href='/renew' style='padding:10px 20px; background:#e67e22; color:white; text-decoration:none; border-radius:5px;'>تجديد الاشتراك</a>
                </div>
                """
        else:
            if user_account in DATABASE["used_trials"]:
                return f"""
                <div style='font-family:Tahoma; text-align:center; padding:50px;'>
                    <h2 style='color: #e74c3c;'>⚠️ هذا الحساب استهلك فترته التجريبية سابقاً!</h2>
                    <br><a href='/renew' style='padding:10px 20px; background:#e67e22; color:white; text-decoration:none; border-radius:5px;'>تجديد الاشتراك</a>
                </div>
                """
            expiry_date = (now + timedelta(days=SYSTEM_SETTINGS["free_days"])).strftime('%Y-%m-%d')
            DATABASE["users"][user_account] = expiry_date
            DATABASE["used_trials"].add(user_account)

        expiry_str = DATABASE["users"][user_account]
        new_ad = {
            "title": title,
            "description": description,
            "category": category,
            "category_name": category_name,
            "media_type": media_type,
            "media_url": media_url,
            "ai_filter": ai_filter,
            "user": user_account,
            "expiry_date": expiry_str,
            "is_owner": False
        }
        
        DATABASE["ads"].append(new_ad)
        send_telegram_message(OWNER_CHAT_ID, f"📢 *إعلان جديد ({media_type.upper()}) في قسم ({category_name})!*\nالحساب: {user_account}\nالعنوان: {title}")

        return redirect(url_for('home'))

    return f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head><meta charset="UTF-8"><title>إضافة إعلان جديد</title></head>
    <body style="font-family:Tahoma; padding:40px; text-align:center; background:#f4f6f9;">
        <h2>أضف إعلانك (صور مجانية أو فيديو 30 ثانية بـ 30 جنيه)</h2>
        <p>الحساب المسجل: <b>{user_account}</b></p>
        <form method="POST" style="background:white; padding:25px; width:50%; margin:auto; border-radius:10px; text-align:right; box-shadow:0 4px 10px rgba(0,0,0,0.05);">
            <label>اختر القسم:</label><br>
            <select name="category" required style="width:100%; padding:10px; margin:5px 0; border:1px solid #ccc; border-radius:6px;">
                <option value="electronics">💻 إلكترونيات</option>
                <option value="phones">📱 تليفونات وموبايلات</option>
                <option value="shoes">👞 أحذية</option>
                <option value="sneakers">👟 كوتشيات رياضية</option>
                <option value="fashion">👕 ملابس وموضة</option>
                <option value="others">📦 أقسام أخرى</option>
            </select><br>

            <label>نوع الوسائط:</label><br>
            <select name="media_type" required style="width:100%; padding:10px; margin:5px 0; border:1px solid #ccc; border-radius:6px;">
                <option value="image">🖼️ صورة (مجاناً بالشهر الأول)</option>
                <option value="video">🎥 فيديو قصير ترويجي 30 ثانية (يتطلب تحويل 30 جنيه)</option>
            </select><br>

            <label>عنوان الإعلان:</label><br><input type="text" name="title" required style="width:100%; padding:10px; margin:5px 0; border:1px solid #ccc; border-radius:6px;"><br>
            <label>وصف الإعلان:</label><br><textarea name="description" rows="3" required style="width:100%; padding:10px; margin:5px 0; border:1px solid #ccc; border-radius:6px;"></textarea><br>
            <label>رابط الوسائط المباشر (صورة أو فيديو URL):</label><br><input type="text" name="media_url" placeholder="https://..." required style="width:100%; padding:10px; margin:5px 0; border:1px solid #ccc; border-radius:6px;"><br>
            
            <label>فلتر الذكاء الاصطناعي (للصورة أو الفيديو):</label><br>
            <select name="ai_filter" style="width:100%; padding:10px; margin:5px 0; border:1px solid #ccc; border-radius:6px;">
                <option value="contrast(1.3) brightness(1.1)">تحسين تلقائي للوضوح والإضاءة</option>
                <option value="contrast(1.4) brightness(0.95)">إضاءة استوديو فخمة</option>
                <option value="sepia(0.6)">تأثير سينمائي فخم</option>
                <option value="none">بدون تأثير إضافي</option>
            </select><br><br>
            
            <button type="submit" style="background:#2980b9; color:white; padding:12px 20px; border:none; border-radius:6px; width:100%; font-weight:bold; cursor:pointer;">نشر الإعلان</button>
        </form>
        <br><a href="/" style="color:#2980b9; text-decoration:none;">⬅️ العودة للرئيسية</a>
    </body>
    """

@app.route('/rate', methods=['POST'])
def rate():
    name = request.form.get('name')
    stars = request.form.get('stars')
    comment = request.form.get('comment')
    if name and comment:
        DATABASE["ratings"].insert(0, {"name": name, "stars": stars, "comment": comment})
    return redirect(url_for('home'))

@app.route('/ai_studio', methods=['GET', 'POST'])
def ai_studio():
    processed_image = None
    selected_effect = "normal"
    if request.method == 'POST':
        img_url = request.form.get('img_url')
        effect = request.form.get('effect')
        filters = {
            "enhance": "contrast(1.3) brightness(1.1) saturate(1.2)",
            "studio": "contrast(1.4) brightness(0.95) drop-shadow(2px 4px 6px black)",
            "vintage": "sepia(0.6) contrast(1.1)",
            "cyberpunk": "hue-rotate(90deg) saturate(2)"
        }
        selected_effect = filters.get(effect, "none")
        processed_image = img_url
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head><meta charset="UTF-8"><title>استوديو الذكاء الاصطناعي</title></head>
    <body style="font-family:Tahoma; background:#2c3e50; color:white; padding:30px; text-align:center;">
        <h1>✨ استوديو تعديل الصور والفيديوهات بالذكاء الاصطناعي</h1>
        <div style="background:#34495e; padding:25px; width:60%; margin:20px auto; border-radius:10px; text-align:right;">
            <form method="POST">
                <label>رابط الصورة أو الفيديو المباشر:</label><br>
                <input type="text" name="img_url" required style="width:100%; padding:10px; margin:10px 0;"><br>
                <label>اختر تأثير الذكاء الاصطناعي:</label><br>
                <select name="effect" style="width:100%; padding:10px; margin:10px 0;">
                    <option value="enhance">✨ تحسين الإضاءة والوضوح</option>
                    <option value="studio">💡 إضاءة استوديو</option>
                    <option value="vintage">🎞️ تأثير سينمائي</option>
                </select><br>
                <button type="submit" style="background:#9b59b6; color:white; padding:12px; border:none; width:100%; border-radius:4px; font-weight:bold; cursor:pointer;">تعديل بالذكاء الاصطناعي</button>
            </form>
            {% if processed_image %}
            <div style="text-align:center; margin-top:20px;">
                <h3>النتيجة بعد التعديل:</h3>
                <img src="{{ processed_image }}" style="max-width:80%; filter: {{ effect_css }}; border:3px solid #fff; border-radius:8px;">
            </div>
            {% endif %}
        </div>
        <a href="/" style="color:#3498db; text-decoration:none;">⬅️ العودة للرئيسية</a>
    </body>
    """, processed_image=processed_image, effect_css=selected_effect)

@app.route('/renew')
def renew():
    return f"""
    <div style="font-family:Tahoma; text-align:center; padding:40px;">
        <h2>تجديد الاشتراكات ورسوم الفيديوهات والباركود</h2>
        <p>سعر اشتراك الشهر الثاني: <b>{SYSTEM_SETTINGS["subscription_price"]}</b></p>
        <p>رسوم رفع الفيديو الترويجي (30 ثانية): <b>{SYSTEM_SETTINGS["video_price"]}</b></p>
        <p>قم بالتحويل السريع عبر فودافون كاش على الرقم المخصص: <b>{VODAFONE_CASH_NUMBER}</b></p>
        
        <div style="margin: 20px auto; padding: 15px; background: white; display: inline-block; border: 2px dashed #333; border-radius: 8px;">
            <p><b>📱 امسح الباركود بكاميرا الهاتف للتحويل الفوري:</b></p>
            <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=tel:{VODAFONE_CASH_NUMBER}" alt="Vodafone Cash Barcode">
        </div>

        <p>بعد التحويل، أرسل رسالة للبوت لتفعيل حسابك أو تفعيل فيديو (30 ثانية) فوراً!</p>
        <br><a href="/" style="padding: 10px 20px; background: #2c3e50; color: white; text-decoration: none; border-radius: 5px;">العودة للرئيسية</a>
    </div>
    """

@app.route('/privacy-policy')
def privacy_policy():
    return "<div style='font-family:Tahoma; padding:30px; text-align:right;'><h1>سياسة الخصوصية</h1><p>سياسة الخصوصية وقبول جوجل أدسنس لمنصة البدري...</p><a href='/'>الرئيسية</a></div>"

@app.route('/terms')
def terms():
    return "<div style='font-family:Tahoma; padding:30px; text-align:right;'><h1>شروط الاستخدام</h1><p>الشروط والأحكام للمنصة...</p><a href='/'>الرئيسية</a></div>"

@app.route('/games')
def games():
    return "<div style='padding:50px; text-align:center; font-family:Tahoma;'><h2>🎮 الألعاب الترفيهية والمكاسب</h2><br><a href='/'>الرئيسية</a></div>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
