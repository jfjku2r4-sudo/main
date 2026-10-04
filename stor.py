import base64
from email.mime.text import MIMEText
import random
import re
import smtplib
from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from pywebio.session import *

# ==================== إعدادات المتجر العامة والعلامة المائية ====================
store_settings = {
    'store_name': '🛍️ المتجر الإلكتروني الشامل',
    'welcome_msg': 'مرحباً بك في متجرنا! نتمنى لك تجربة تسوق ممتعة.',
    'watermark_text': 'حقوق الطبع والتطوير © محمد عبد الله',
    'show_watermark': True,
    'free_shipping': False,
    'default_shipping_fee': 50,
    'smtp_email': 'your_email@gmail.com',
    'smtp_password': 'your_app_password',
    # إعدادات أزرار التواصل المتقدمة (الظهور، الأيقونات، الروابط)
    'contact_buttons': {
        'whatsapp': {
            'enabled': True,
            'title': '🟢 التواصل عبر واتساب',
            'val': '201000000000',
            'icon': 'https://cdn-icons-png.flaticon.com/512/3670/3670051.png',
            'bg_color': '#25D366',
        },
        'facebook': {
            'enabled': True,
            'title': '🔵 صفحة الفيسبوك',
            'val': 'https://facebook.com',
            'icon': 'https://cdn-icons-png.flaticon.com/512/5968/5968764.png',
            'bg_color': '#1877F2',
        },
        'messenger': {
            'enabled': True,
            'title': '⚡ التواصل عبر ماسنجر',
            'val': 'https://m.me',
            'icon': 'https://cdn-icons-png.flaticon.com/512/5968/5968771.png',
            'bg_color': '#0084FF',
        },
    },
}

# بيانات دخول الأدمن قابلة للتعديل والتحقق عبر الإيميل
admin_credentials = {
    'username': 'admin',
    'password': 'admin123',
    'email': 'admin_email@gmail.com',
}

# أسعار الشحن للمحافظات (ج.م)
shipping_rates = {
    'القاهرة': 30,
    'الجيزة': 35,
    'الإسكندرية': 45,
    'الدقهلية': 40,
    'الشرقية': 40,
    'القليوبية': 35,
    'الغربية': 40,
    'البحيرة': 45,
    'المنوفية': 40,
    'أسيوط': 60,
    'سوهاج': 65,
    'المنيا': 55,
    'بني سويف': 50,
    'بورسعيد': 45,
    'السويس': 45,
    'الإسماعيلية': 45,
    'كفر الشيخ': 45,
    'الفيوم': 50,
    'قنا': 70,
    'أسوان': 80,
    'دمياط': 45,
    'مطروح': 75,
    'البحر الأحمر': 85,
    'الوادي الجديد': 90,
    'شمال سيناء': 80,
    'جنوب سيناء': 85,
}

wallets_db = [
    {'id': 1, 'company': 'فودافون كاش (Vodafone Cash)', 'number': '01012345678'},
    {'id': 2, 'company': 'أورنج كاش (Orange Cash)', 'number': '01212345678'},
    {'id': 3, 'company': 'اتصالات كاش (Etisalat Cash)', 'number': '01112345678'},
    {'id': 4, 'company': 'إنستا باي (InstaPay)', 'number': 'user@instapay'},
]

egypt_governorates = {
    'القاهرة': [
        'مدينة نصر',
        'مصر الجديدة',
        'المعادي',
        'التجمع الخامس',
        'التجمع الأول',
        'شبرا',
        'وسط البلد',
        'حلوان',
        'الزمالك',
        'الرحاب',
        'مدينتي',
        'الشروق',
        'بدر',
        'المقطم',
        'القطامية',
        'عين شمس',
        'المرج',
        'الزيتون',
        'الوايلي',
    ],
    'الجيزة': [
        'الدقي',
        'المهندسين',
        'الهرم',
        'فيصل',
        '6 أكتوبر',
        'الشيخ زايد',
        'إمبابة',
        'العجوزة',
        'العمرانية',
        'البدرشين',
        'العياط',
        'أبو النمرس',
        'الصف',
        'أطفيح',
        'كرداسة',
        'أوسيم',
    ],
    'الإسكندرية': [
        'سموحة',
        'سيدي بشر',
        'المنتزه',
        'محرم بك',
        'العجمي',
        'العامرية',
        'ميامي',
        'جليم',
        'ستانلي',
        'كمب شيزار',
        'الجمارك',
        'برج العرب',
        'الشاطبي',
        'سيدي جابر',
    ],
    'الدقهلية': [
        'المنصورة',
        'طلخا',
        'ميت غمر',
        'دكرنس',
        'بلقاس',
        'شربين',
        'السنبلاوين',
        'منية النصر',
        'تمى الأمديد',
        'الجمالية',
        'المطرية',
        'منزلة',
        'نبروه',
        'أجا',
        'بني عبيد',
    ],
    'الشرقية': [
        'الزقازيق',
        'العاشر من رمضان',
        'بلبيس',
        'منيا القمح',
        'أبو حماد',
        'فاقوس',
        'ديرب نجم',
        'هيها',
        'أبو كبير',
        'كفر صقر',
        'أولاد صقر',
        'الحسينية',
        'صان الحجر',
        'مشتول السوق',
    ],
    'القليوبية': [
        'بنها',
        'شبرا الخيمة',
        'العبور',
        'قليوب',
        'الخانكة',
        'طوخ',
        'قناطر الخيرية',
        'كفر شكر',
        'شبين القناطر',
    ],
    'الغربية': [
        'طنطا',
        'المحلة الكبرى',
        'زفتى',
        'كفر الزيات',
        'بسيون',
        'سمنود',
        'قطور',
        'السنطة',
    ],
    'البحيرة': [
        'دمنهور',
        'كفر الدوار',
        'إيتاي البارود',
        'أبو حمص',
        'رشيد',
        'كوم حمادة',
        'حوش عيسى',
        'الدلنجات',
        'أبو المطامير',
        'رحمانية',
        'محمودية',
        'وادي النطرون',
    ],
    'المنوفية': [
        'شبين الكوم',
        'أشمون',
        'منوف',
        'قويسنا',
        'تلا',
        'الباجور',
        'شهداء',
        'السادات',
        'بركة السبع',
    ],
    'أسيوط': [
        'أسيوط',
        'ديروط',
        'القوصية',
        'أبنوب',
        'منفلوط',
        'أبو تيج',
        'الغنايم',
        'ساحل سليم',
        'البداري',
        'صدفا',
        'الفتح',
    ],
    'سوهاج': [
        'سوهاج',
        'أخميم',
        'جرجا',
        'طهطا',
        'البلينا',
        'المراغة',
        'منشأة',
        'دار السلام',
        'جهينة',
        'ساقلتة',
    ],
    'المنيا': [
        'المنيا',
        'ملوي',
        'بني مزار',
        'سمالوط',
        'أبو قرقاص',
        'متاي',
        'دير مواس',
        'عدوة',
    ],
    'بني سويف': [
        'بني سويف',
        'الواسطى',
        'ببا',
        'الفشن',
        'ناصر',
        'إهناسيا',
        'سمسطا',
    ],
    'بورسعيد': [
        'حي الشرق',
        'حي المناخ',
        'حي الزهور',
        'حي الضواحي',
        'حي العرب',
        'حي الجنوب',
        'بورفؤاد',
    ],
    'السويس': [
        'حي السويس',
        'حي الأربعين',
        'حي عتاقة',
        'حي فيصل',
        'حي الجناين',
    ],
    'الإسماعيلية': [
        'الإسماعيلية',
        'القنطرة شرق',
        'القنطرة غرب',
        'فايد',
        'أبو صوير',
        'القصاصين',
        'التل الكبير',
    ],
    'كفر الشيخ': [
        'كفر الشيخ',
        'دسوق',
        'فوّه',
        'مطوبس',
        'بلطيم',
        'سيدي سالم',
        'الرياض',
        'بيلا',
        'الحامول',
        'قلين',
    ],
    'الفيوم': ['الفيوم', 'سنورس', 'إطسا', 'طامية', 'أبشواي', 'يوسف الصديق'],
    'قنا': [
        'قنا',
        'الأقصر',
        'نجع حمادي',
        'قوص',
        'دشنا',
        'أبو تشت',
        'فرشوط',
        'نقادة',
        'قفط',
    ],
    'أسوان': ['أسوان', 'كوم أمبو', 'إدفو', 'نصر النوبة', 'دروا'],
    'دمياط': ['دمياط', 'رأس البر', 'فارسكور', 'الزرقا', 'كفر سعد', 'الروضة', 'السرو'],
    'مطروح': [
        'مرسى مطروح',
        'العلمين',
        'الضبعة',
        'سيوة',
        'الحمام',
        'النجيلة',
        'السلوم',
    ],
    'البحر الأحمر': [
        'الغردقة',
        'سفاجا',
        'القصير',
        'مرسى علم',
        'رأس غارب',
        'شلاتين',
        'حلايب',
    ],
    'الوادي الجديد': ['الخارجة', 'الداخلة', 'الفرافرة', 'بلاط', 'باريس'],
    'شمال سيناء': ['العريش', 'الشيخ زويد', 'رفح', 'بئر العبد', 'نخل', 'الحسنة'],
    'جنوب سيناء': [
        'شرم الشيخ',
        'دهب',
        'نويبع',
        'طابا',
        'طور سيناء',
        'رأس سدر',
        'سانت كاترين',
        'أبو رديس',
    ],
}

products = [
    {
        'id': 1,
        'name': 'قميص قطني أنيق',
        'price': 250,
        'old_price': 350,
        'low_stock_limit': 3,
        'color_data': {
            'أبيض': {
                'images': [
                    'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800'
                ],
                'stock': 10,
            },
            'أسود': {
                'images': [
                    'https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=800'
                ],
                'stock': 2,
            },
            'أزرق': {
                'images': [
                    'https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=800'
                ],
                'stock': 5,
            },
        },
    },
    {
        'id': 2,
        'name': 'ساعة يد كلاسيكية',
        'price': 750,
        'old_price': 1000,
        'low_stock_limit': 2,
        'color_data': {
            'أسود': {
                'images': [
                    'https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800'
                ],
                'stock': 4,
            },
            'بني': {
                'images': [
                    'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=800'
                ],
                'stock': 1,
            },
        },
    },
]

users_db = {}
orders_db = []
cart = []
reset_codes_db = {}


# دالة التحقق من صحة رقم الهاتف
def validate_phone_number(phone_str):
    pattern = re.compile(r'^(010|011|012|015)\d{8}$')
    cleaned_phone = phone_str.strip().replace(' ', '')
    return bool(pattern.match(cleaned_phone))


# ==================== عرض وسائل التواصل بروابطه وأيقوناته المتخصصة ====================
def open_contact_dialog():
    btns = store_settings.get('contact_buttons', {})
    buttons_html = ''

    # زر الواتساب
    if btns.get('whatsapp', {}).get('enabled', True):
        wa_data = btns['whatsapp']
        wa_num = wa_data.get('val', '').strip()
        wa_link = f'https://wa.me/{wa_num}' if wa_num else '#'
        icon_img = f"<img src='{wa_data['icon']}' style='width:24px; height:24px; margin-left:8px; vertical-align:middle;'>"
        buttons_html += f"""
        <a href="{wa_link}" target="_blank" style="background-color: {wa_data['bg_color']}; color: white; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
            {icon_img} {wa_data['title']}
        </a>
        """

    # زر الفيسبوك
    if btns.get('facebook', {}).get('enabled', True):
        fb_data = btns['facebook']
        fb_link = fb_data.get('val', '#')
        icon_img = f"<img src='{fb_data['icon']}' style='width:24px; height:24px; margin-left:8px; vertical-align:middle;'>"
        buttons_html += f"""
        <a href="{fb_link}" target="_blank" style="background-color: {fb_data['bg_color']}; color: white; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
            {icon_img} {fb_data['title']}
        </a>
        """

    # زر الماسنجر
    if btns.get('messenger', {}).get('enabled', True):
        msg_data = btns['messenger']
        msg_link = msg_data.get('val', '#')
        icon_img = f"<img src='{msg_data['icon']}' style='width:24px; height:24px; margin-left:8px; vertical-align:middle;'>"
        buttons_html += f"""
        <a href="{msg_link}" target="_blank" style="background-color: {msg_data['bg_color']}; color: white; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
            {icon_img} {msg_data['title']}
        </a>
        """

    if not buttons_html:
        buttons_html = '<p style="color:red;">عفواً، لا توجد وسائل تواصل مفعّلة حالياً من قبل الإدارة.</p>'

    popup(
        '💬 وسائل التواصل مع الإدارة',
        [
            put_html(f"""
        <div style='text-align: center; padding: 10px;'>
            <p style='margin-bottom: 15px;'>اختر المنصة للتوجه إليها مباشرة:</p>
            <div style='display: flex; flex-direction: column;'>
                {buttons_html}
            </div>
        </div>
        """),
            put_button(
                'إغلاق', onclick=close_popup, color='secondary'
            ).style('margin-top: 15px;'),
        ],
    )


def render_watermark():
    if store_settings['show_watermark']:
        put_html(f"""
        <div onclick="WebIO.pushData('watermark_clicked', 'watermark_click_event')" 
             style='position: fixed; bottom: 10px; right: 10px; background: rgba(0,0,0,0.7); color: white; padding: 6px 14px; border-radius: 20px; font-size: 13px; z-index: 9999; cursor: pointer; user-select: none;'>
            {store_settings['watermark_text']} 💬
        </div>
        """)


# ==================== خدمة إرسال الإيميل التلقائي ====================
def send_email_message(to_email, subject, content):
    try:
        msg = MIMEText(content)
        msg['Subject'] = subject
        msg['From'] = store_settings['smtp_email']
        msg['To'] = to_email

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(
            store_settings['smtp_email'], store_settings['smtp_password']
        )
        server.sendmail(
            store_settings['smtp_email'], [to_email], msg.as_string()
        )
        server.quit()
        return True
    except Exception:
        return False


# ==================== الصفحة الرئيسية ====================
def App():
    current_session_user = eval_js('sessionStorage.getItem("logged_user")')
    current_role = eval_js('sessionStorage.getItem("logged_role")')

    if current_role == 'admin':
        return show_admin_dashboard()
    elif current_role == 'user' and current_session_user in users_db:
        if users_db[current_session_user].get('is_banned', False):
            run_js('sessionStorage.clear();')
            toast('⚠️ حسابك محظور من قبل الإدارة!', color='error', duration=10)
        elif users_db[current_session_user]['is_active']:
            return show_shop_page(current_session_user)

    clear()
    render_watermark()

    put_html(
        f"<center><h1"
        f" style='color:#2c3e50;'>{store_settings['store_name']}</h1></center>"
    )
    put_html(
        f"<center><p"
        f" style='color:#7f8c8d;'>{store_settings['welcome_msg']}</p></center>"
    )

    put_buttons(
        [
            {
                'label': '👤 دخول المتجر (مستخدم)',
                'value': 'user',
                'color': 'primary',
            },
            {'label': '⚙️ لوحة تحكم الأدمن', 'value': 'admin', 'color': 'dark'},
            {
                'label': '💬 التواصل مع الإدارة',
                'value': 'contact',
                'color': 'success',
            },
        ],
        onclick=lambda btn: (
            open_contact_dialog()
            if btn == 'contact'
            else (user_auth_flow() if btn == 'user' else admin_login())
        ),
    ).style('text-align: center; margin-top: 20px;')


# ==================== تسجيل وتفعيل الحسابات ونظام نسيت كلمة السر ====================
def user_auth_flow():
    clear()
    render_watermark()
    put_html('<center><h3>بوابة حسابات المستخدمين</h3></center>')

    put_buttons(
        [
            {
                'label': '✨ تسجيل حساب جديد',
                'value': 'new',
                'color': 'success',
            },
            {
                'label': '🔑 تسجيل دخول لحساب حالي',
                'value': 'login',
                'color': 'info',
            },
            {
                'label': '❓ نسيت كلمة السر',
                'value': 'forgot',
                'color': 'warning',
            },
            {'label': '🔙 العودة للرئيسية', 'value': 'back', 'color': 'secondary'},
        ],
        onclick=handle_auth_action,
    )


def handle_auth_action(btn_val):
    if btn_val == 'back':
        return App()

    if btn_val == 'new':
        data = input_group('إنشاء حساب جديد', [
            input('اسم المستخدم الجديد', name='user', required=True),
            input(
                'البريد الإلكتروني (Gmail)',
                name='email',
                type=TEXT,
                required=True,
            ),
            input(
                'كلمة السر (6 أحرف/أرقام على الأقل)',
                name='pass',
                type=PASSWORD,
                required=True,
            ),
        ])

        if len(data['pass']) < 6:
            toast(
                'كلمة السر يجب أن تكون 6 أحرف أو أرقام على الأقل!',
                color='error',
                duration=10,
            )
            return user_auth_flow()

        if data['user'] in users_db:
            toast('اسم المستخدم هذا مسجل بالفعل!', color='error', duration=10)
            return user_auth_flow()

        generated_code = str(random.randint(100000, 999999))

        users_db[data['user']] = {
            'pass': data['pass'],
            'email': data['email'],
            'code': generated_code,
            'is_active': False,
            'is_banned': False,
        }

        sent = send_email_message(
            data['email'],
            f"كود تفعيل الحساب - {store_settings['store_name']}",
            f'كود التفعيل الخاص بك هو: {generated_code}',
        )

        if sent:
            toast(
                f"تم إرسال كود التفعيل تلقائياً إلى بريدك ({data['email']})!",
                color='success',
                duration=10,
            )
        else:
            toast(
                f'تعذر الإرسال الآلي. كود التفعيل التجريبي هو: ({generated_code})',
                color='info',
                duration=10,
            )

        prompt_verification_code(data['user'])

    elif btn_val == 'login':
        data = input_group('تسجيل الدخول', [
            input('اسم المستخدم', name='user', required=True),
            input('كلمة السر', name='pass', type=PASSWORD, required=True),
        ])

        if (
            data['user'] not in users_db
            or users_db[data['user']]['pass'] != data['pass']
        ):
            toast(
                'اسم المستخدم أو كلمة السر غير صحيحة!',
                color='error',
                duration=10,
            )
            return user_auth_flow()

        if users_db[data['user']].get('is_banned', False):
            toast(
                '🚫 هذا الحساب محظور من استخدام الموقع بواسطة الإدارة!',
                color='error',
                duration=10,
            )
            return user_auth_flow()

        if not users_db[data['user']]['is_active']:
            toast(
                'حسابك في انتظار التفعيل! جاري تحويلك لإدخال كود التفعيل...',
                color='warning',
                duration=10,
            )
            return prompt_verification_code(data['user'])

        run_js(
            f'sessionStorage.setItem("logged_user", "{data["user"]}");'
            ' sessionStorage.setItem("logged_role", "user");'
        )
        toast(f"أهلاً بك مجدداً {data['user']}!", color='success', duration=10)
        show_shop_page(data['user'])

    elif btn_val == 'forgot':
        forgot_password_flow('user')


def resend_code_action(username):
    user_info = users_db.get(username)
    if user_info:
        new_code = str(random.randint(100000, 999999))
        user_info['code'] = new_code
        sent = send_email_message(
            user_info['email'],
            f"إعادة إرسال كود التفعيل - {store_settings['store_name']}",
            f'كود التفعيل الجديد الخاص بك هو: {new_code}',
        )

        if sent:
            toast(
                f"تمت إعادة إرسال كود التفعيل بنجاح إلى ({user_info['email']})!",
                color='success',
                duration=10,
            )
        else:
            toast(
                f'تعذر الإرسال الآلي. كود التفعيل الجديد التجريبي هو:'
                f' ({new_code})',
                color='info',
                duration=10,
            )
    prompt_verification_code(username)


def forgot_password_flow(target_role='user'):
    clear()
    render_watermark()
    put_html('<h3>🔑 استعادة كلمة السر</h3>')

    if target_role == 'user':
        username = input('أدخل اسم المستخدم الخاص بك:', required=True)
        if username not in users_db:
            toast('اسم المستخدم هذا غير موجود لدينا!', color='error', duration=10)
            return user_auth_flow()

        if users_db[username].get('is_banned', False):
            toast(
                '🚫 هذا الحساب محظور من قبل الإدارة ولا يمكن استعادة كلمة'
                ' السر!',
                color='error',
                duration=10,
            )
            return user_auth_flow()

        user_email = users_db[username]['email']
    else:
        username = admin_credentials['username']
        user_email = admin_credentials['email']

    reset_code = str(random.randint(100000, 999999))
    reset_codes_db[username] = reset_code

    sent = send_email_message(
        user_email,
        f"كود إعادة ضبط كلمة السر - {store_settings['store_name']}",
        f'كود إعادة ضبط كلمة السر الخاص بك هو: {reset_code}',
    )

    if sent:
        toast(
            f'تم إرسال كود إعادة الضبط تلقائياً إلى بريدك ({user_email})!',
            color='success',
            duration=10,
        )
    else:
        toast(
            f'تعذر إرسال الإيميل تلقائياً. كودك هو: ({reset_code})',
            color='info',
            duration=10,
        )

    code_in = input(
        f'أدخل كود إعادة الضبط المرسل لـ ({user_email}):', required=True
    )

    if code_in.strip() == reset_codes_db.get(username):
        new_pass = input(
            'أدخل كلمة السر الجديدة:', type=PASSWORD, required=True
        )
        if len(new_pass) < 6:
            toast(
                'كلمة السر يجب أن تكون 6 أحرف/أرقام على الأقل!',
                color='error',
                duration=10,
            )
            return forgot_password_flow(target_role)

        if target_role == 'user':
            users_db[username]['pass'] = new_pass
            toast(
                'تم تغيير كلمة السر بنجاح! يمكنك الآن تسجيل الدخول.',
                color='success',
                duration=10,
            )
            user_auth_flow()
        else:
            admin_credentials['password'] = new_pass
            toast('تم تغيير كلمة سر الأدمن بنجاح!', color='success', duration=10)
            admin_login()
    else:
        toast('كود إعادة الضبط خاطئ!', color='error', duration=10)
        App()


def prompt_verification_code(username):
    clear()
    render_watermark()
    put_html(f'<h3>تفعيل حساب العميل: ({username})</h3>')
    put_text(
        'أدخل كود التفعيل المكون من 6 أرقام المرسل تلقائياً إلى Gmail'
        f" ({users_db[username]['email']}):"
    )

    code_in = input('كود التفعيل:', required=True)
    if code_in.strip() == users_db[username]['code']:
        users_db[username]['is_active'] = True
        run_js(
            f'sessionStorage.setItem("logged_user", "{username}");'
            ' sessionStorage.setItem("logged_role", "user");'
        )
        toast('تم تفعيل حسابك بنجاح!', color='success', duration=10)
        show_shop_page(username)
    else:
        toast('كود التفعيل خاطئ!', color='error', duration=10)
        put_buttons(
            [
                {
                    'label': '🔄 إعادة إرسال الكود',
                    'value': 'resend',
                    'color': 'info',
                },
                {'label': 'إعادة المحاولة', 'value': 'retry', 'color': 'warning'},
                {
                    'label': '🔙 العودة للرئيسية',
                    'value': 'back',
                    'color': 'secondary',
                },
            ],
            onclick=lambda b: (
                resend_code_action(username)
                if b == 'resend'
                else (prompt_verification_code(username) if b == 'retry' else App())
            ),
        )


# ==================== صفحة المتجر وتكبير الصور والخصومات ====================
def show_shop_page(current_user):
    if users_db.get(current_user, {}).get('is_banned', False):
        run_js('sessionStorage.clear();')
        toast('🚫 تم حظر حسابك من قبل الإدارة!', color='error', duration=10)
        return App()

    clear()
    render_watermark()

    put_html(f"""
    <div style='background:#eef2f3; padding:15px; border-radius:8px; display:flex; justify-content:space-between; align-items:center;'>
        <div><b>{store_settings['store_name']}</b> | العميل: <span style='color:#2980b9;'>{current_user}</span></div>
    </div>
    """)

    put_buttons(
        [
            {
                'label': '✏ تعديل الحساب',
                'value': 'edit_acc',
                'color': 'warning',
            },
            {
                'label': '📦 تتبع طلباتي',
                'value': 'track_orders',
                'color': 'info',
            },
            {
                'label': f'🛒 سلة الشراء ({len(cart)})',
                'value': 'view_cart',
                'color': 'success',
            },
            {'label': '💬 تواصل معنا', 'value': 'contact', 'color': 'primary'},
            {'label': '🚪 تسجيل الخروج', 'value': 'logout', 'color': 'danger'},
        ],
        onclick=lambda btn: (
            open_contact_dialog()
            if btn == 'contact'
            else handle_user_menu(btn, current_user)
        ),
    )

    put_html(f"<center><h2>{store_settings['welcome_msg']}</h2></center>")

    if not products:
        put_text('لا توجد منتجات متاحة حالياً.')
        return

    cards = []
    for p in products:
        colors_available = list(p['color_data'].keys())
        first_color = colors_available[0]
        first_img = p['color_data'][first_color]['images'][0]

        price_html = (
            f"<span style='color:green; font-weight:bold;"
            f" font-size:18px;'>{p['price']} ج.م</span>"
        )
        if p.get('old_price') and p['old_price'] > p['price']:
            price_html += (
                f" <span style='text-decoration: line-through; color: #888;"
                f" font-size: 14px; margin-right: 8px;'>{p['old_price']}"
                ' ج.م</span>'
            )
            discount_pct = int(
                ((p['old_price'] - p['price']) / p['old_price']) * 100
            )
            price_html += (
                f" <span style='background:red; color:white; padding:2px 6px;"
                f" border-radius:10px; font-size:12px;'>خصم {discount_pct}%</span>"
            )

        cards.append([
            put_html(
                f"<center><img src='{first_img}' style='width:140px;"
                " height:140px; object-fit:cover;"
                " border-radius:8px;'></center>"
            ),
            put_text(p['name']).style('font-weight:bold; font-size:16px;'),
            put_html(price_html),
            put_button(
                'معاينة الألوان وتكبير الصور 🛒',
                onclick=lambda prod=p: open_add_to_cart_dialog(
                    prod, current_user
                ),
                color='primary',
            ),
        ])

    put_grid(cards, cell_width='280px', cell_height='auto')


def open_large_image(url):
    popup('🔍 معاينة الصورة مكبرة', [
        put_html(
            f"<center><img src='{url}' style='max-width:100%; max-height:500px;"
            " border-radius:10px;'></center>"
        ),
        put_button('إغلاق', onclick=close_popup, color='secondary'),
    ])


def open_add_to_cart_dialog(product, current_user):
    colors = list(product['color_data'].keys())

    data = input_group(f"اختر تفاصيل {product['name']}", [
        select(
            'اختر اللون لتظهر لك الصور والمخزون الخاص به:',
            colors,
            name='color',
        ),
        input(
            'حدد الكمية المطلوب شراءها:', type=NUMBER, value=1, name='qty'
        ),
    ])

    selected_color = data['color']
    selected_qty = data['qty']

    color_info = product['color_data'][selected_color]
    available_stock = color_info['stock']

    if selected_qty is None or selected_qty < 1:
        toast('يرجى تحديد كمية صحيحة!', color='error', duration=10)
        return

    if selected_qty > available_stock:
        toast(
            f'عفواً، الكمية المتاحة في المخزن لهذا اللون هي ({available_stock})'
            ' فقط!',
            color='error',
            duration=10,
        )
        return

    imgs = color_info['images']
    img_elements = [
        put_button(
            'عرض مكبر 🔍',
            onclick=lambda u=url: open_large_image(u),
            color='light',
        )
        for url in imgs
    ]

    popup(f'صور اللون ({selected_color}) ومعاينة الشراء', [
        put_html(
            f"<center><img src='{imgs[0]}' style='width:220px; height:220px;"
            " object-fit:cover; border-radius:10px;'></center>"
        ),
        put_row(img_elements),
        put_text(f"المنتج: {product['name']}"),
        put_text(
            f'اللون: {selected_color} | المتوفر في المخزن: {available_stock}'
            ' قطعة'
        ),
        put_text(f'الكمية المطلوبة: {selected_qty}'),
        put_text(f"الإجمالي الجزئي: {product['price'] * selected_qty} ج.م"),
        put_button(
            'تأكيد الإضافة للسلة 🛒',
            onclick=lambda: [
                cart.append({
                    'product_id': product['id'],
                    'name': product['name'],
                    'price': product['price'],
                    'color': selected_color,
                    'qty': selected_qty,
                    'subtotal': product['price'] * selected_qty,
                }),
                toast('تمت الإضافة للسلة بنجاح!', color='success', duration=10),
                close_popup(),
                show_shop_page(current_user),
            ],
            color='success',
        ),
        put_button('🔙 إغلاق والعودة', onclick=close_popup, color='danger'),
    ])


def handle_user_menu(btn_val, current_user):
    if btn_val == 'edit_acc':
        change_user_credentials(current_user)
    elif btn_val == 'track_orders':
        show_user_order_tracking(current_user)
    elif btn_val == 'view_cart':
        checkout_flow(current_user)
    elif btn_val == 'logout':
        run_js('sessionStorage.clear(); location.reload();')


def change_user_credentials(current_user):
    data = input_group('تحديث بيانات الحساب', [
        input(
            'اسم المستخدم الجديد',
            name='new_user',
            value=current_user,
            required=True,
        ),
        input(
            'كلمة السر الجديدة', name='new_pass', type=PASSWORD, required=True
        ),
    ])

    if len(data['new_pass']) < 6:
        toast('كلمة السر يجب أن لا تقل عن 6 أحرف!', color='error', duration=10)
        return

    for o in orders_db:
        if o['user'] == current_user:
            o['user'] = data['new_user']

    old_data = users_db.pop(current_user)
    users_db[data['new_user']] = {
        'pass': data['new_pass'],
        'email': old_data['email'],
        'code': old_data['code'],
        'is_active': old_data['is_active'],
        'is_banned': old_data.get('is_banned', False),
    }

    run_js(f'sessionStorage.setItem("logged_user", "{data["new_user"]}");')
    toast('تم تحديث البيانات بنجاح!', color='success', duration=10)
    show_shop_page(data['new_user'])


# ==================== تتبع الطلبات وإمكانية الإلغاء ====================
def show_user_order_tracking(current_user):
    user_orders = [o for o in orders_db if o['user'] == current_user]

    if not user_orders:
        popup('تتبع الطلبات', [
            put_text(
                f'مرحباً {current_user}، لم يسبق لك تقديم طلبات حتى الآن!'
            ),
            put_button(
                '🔙 العودة للمتجر', onclick=close_popup, color='secondary'
            ),
        ])
        return

    table = [[
        'رقم الطلب',
        'سعر المنتجات',
        'الشحن',
        'الإجمالي الكلي',
        'عنوان التوصيل',
        'الحالة',
        'الإجراء',
    ]]
    for o in user_orders:
        cancel_btn = 'غير متاح'
        if o['status'] == 'قيد المراجعة ⏳':
            cancel_btn = put_button(
                '❌ إلغاء الطلب',
                onclick=lambda order_ref=o: cancel_user_order(
                    order_ref, current_user
                ),
                color='danger',
            )

        table.append([
            f"#{o['order_id']}",
            f"{o['subtotal']} ج.م",
            f"{o['shipping_fee']} ج.م",
            f"{o['total']} ج.م",
            o['address'],
            o['status'],
            cancel_btn,
        ])

    popup(f'سجل طلبات الحساب ({current_user})', [
        put_table(table),
        put_button('🔙 العودة للمتجر', onclick=close_popup, color='secondary'),
    ])


def cancel_user_order(order, current_user):
    for item in order['items']:
        p_id = item['product_id']
        p_color = item['color']
        p_qty = item['qty']

        for p in products:
            if p['id'] == p_id and p_color in p['color_data']:
                p['color_data'][p_color]['stock'] += p_qty

    order['status'] = 'تم إلغاء الطلب من قبل العميل ❌'
    toast(
        'تم إلغاء الطلب وإرجاع المنتجات إلى المخزن تلقائياً!',
        color='info',
        duration=10,
    )
    close_popup()
    show_user_order_tracking(current_user)


# ==================== إتمام الشراء مع التحقق الحقيقي من رقم الهاتف ====================
def checkout_flow(current_user):
    if not cart:
        popup('سلة الشراء فارغة', [
            put_text('لم تقم بإضافة أي منتج حتى الآن!'),
            put_button(
                '🔙 العودة للمتجر', onclick=close_popup, color='secondary'
            ),
        ])
        return

    subtotal_price = sum(item['subtotal'] for item in cart)

    selected_gov = select(
        'اختر المحافظة المصرية:', list(egypt_governorates.keys())
    )
    selected_center = select(
        f'اختر المركز / الحي في ({selected_gov}):',
        egypt_governorates[selected_gov],
    )

    shipping_fee = (
        0
        if store_settings['free_shipping']
        else shipping_rates.get(
            selected_gov, store_settings['default_shipping_fee']
        )
    )
    total_price = subtotal_price + shipping_fee

    shipping_info = input_group(
        f'تفاصيل التوصيل (مصاريف الشحن: {shipping_fee} ج.م)',
        [
            input(
                'الشارع ورقم المبنى والشقة بالتفصيل',
                name='street',
                required=True,
            ),
            input(
                'رقم الهاتف المصري للتواصل (مثال: 01012345678)',
                name='phone',
                type=TEXT,
                required=True,
            ),
        ],
    )

    # التحقق من أن رقم الهاتف حقيقي ومكون من 11 رقمًا يتبع الشبكات المصرية
    if not validate_phone_number(shipping_info['phone']):
        toast(
            '⚠️ يرجى إدخال رقم هاتف مصري صحيح يتكون من 11 رقمًا (يبدأ بـ 010 أو'
            ' 011 أو 012 أو 015)!',
            color='error',
            duration=10,
        )
        return checkout_flow(current_user)

    full_address = (
        f'محافظة {selected_gov} - مركز/حي {selected_center} -'
        f" {shipping_info['street']}"
    )
    pay_choice = select(
        'طريقة الدفع الفضلى:',
        ['الدفع عند الاستلام (COD)', 'المحفظة الإلكترونية'],
    )

    wallet_company_selected = 'N/A'
    receipt_b64 = None

    if pay_choice == 'المحفظة الإلكترونية':
        if not wallets_db:
            toast(
                'لا توجد محافظ مسجلة حالياً، تم التحويل للدفع عند الاستلام.',
                color='warning',
                duration=10,
            )
            pay_choice = 'الدفع عند الاستلام (COD)'
        else:
            wallet_options = [
                f"{w['company']} (رقم: {w['number']})" for w in wallets_db
            ]
            chosen_w_str = select(
                'اختر المحفظة المراد التحويل إليها:', wallet_options
            )

            for w in wallets_db:
                if w['company'] in chosen_w_str:
                    wallet_company_selected = w['company']
                    break

            receipt_file = file_upload(
                'إرفاق صورة إيصال التحويل (ضروري):', accept='image/*'
            )
            if receipt_file:
                receipt_b64 = f"data:image/png;base64,{base64.b64encode(receipt_file['content']).decode('utf-8')}"

    for item in cart:
        p_id = item['product_id']
        p_color = item['color']
        p_qty = item['qty']

        for p in products:
            if p['id'] == p_id and p_color in p['color_data']:
                p['color_data'][p_color]['stock'] -= p_qty

    order_data = {
        'order_id': len(orders_db) + 1001,
        'user': current_user,
        'phone': shipping_info['phone'],
        'address': full_address,
        'payment_method': pay_choice,
        'wallet_company': wallet_company_selected,
        'receipt_img': receipt_b64,
        'items': list(cart),
        'subtotal': subtotal_price,
        'shipping_fee': shipping_fee,
        'total': total_price,
        'status': 'قيد المراجعة ⏳',
    }

    orders_db.append(order_data)
    cart.clear()

    popup('تم استلام الطلب! 🎉', [
        put_text(f"رقم الطلب: #{order_data['order_id']}"),
        put_text(f'سعر المنتجات: {subtotal_price} ج.م'),
        put_text(f'تكلفة الشحن: {shipping_fee} ج.م'),
        put_text(f'الإجمالي النهائي: {total_price} ج.م'),
        put_text(f"الحالة: {order_data['status']}"),
        put_button(
            '🔙 متابعة التسوق (رجوع)',
            onclick=lambda: [close_popup(), show_shop_page(current_user)],
            color='primary',
        ),
    ])


# ==================== لوحة تحكم الأدمن وحظر الحسابات ====================
def admin_login():
    clear()
    render_watermark()
    put_html('<h3>تسجيل دخول الأدمن</h3>')

    put_buttons(
        [
            {'label': '🔑 دخول الأدمن', 'value': 'login', 'color': 'dark'},
            {
                'label': '❓ نسيت كلمة سر الأدمن',
                'value': 'forgot',
                'color': 'warning',
            },
            {'label': '🔙 العودة للرئيسية', 'value': 'back', 'color': 'secondary'},
        ],
        onclick=lambda b: (
            forgot_password_flow('admin')
            if b == 'forgot'
            else (App() if b == 'back' else process_admin_login())
        ),
    )


def process_admin_login():
    data = input_group('بيانات أدمن النظام', [
        input('اسم الأدمن', name='user', required=True),
        input('كلمة السر', name='pass', type=PASSWORD, required=True),
    ])

    if (
        data['user'] != admin_credentials['username']
        or data['pass'] != admin_credentials['password']
    ):
        toast('بيانات الأدمن غير صحيحة!', color='error', duration=10)
        return admin_login()

    run_js('sessionStorage.setItem("logged_role", "admin");')
    show_admin_dashboard()


def show_admin_dashboard():
    clear()
    render_watermark()
    put_html('<center><h1>⚙️ لوحة تحكم الإدارة الشاملة</h1></center>')

    low_stock_alerts = []
    for p in products:
        limit = p.get('low_stock_limit', 3)
        for c_name, c_info in p['color_data'].items():
            if c_info['stock'] <= limit:
                low_stock_alerts.append(
                    f"• المنتج: <b>{p['name']}</b> | اللون: <b>{c_name}</b> |"
                    f" المتبقي: <span style='color:red;"
                    f" font-weight:bold;'>{c_info['stock']} قطع</span> (حد"
                    f' التنبيه: {limit})'
                )

    if low_stock_alerts:
        alerts_html = '<br>'.join(low_stock_alerts)
        put_html(f"""
        <div style='background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 8px; border: 1px solid #f5c6cb; margin-bottom: 20px;'>
            <h4 style='margin-top:0;'>⚠️ إشعار تحذيري: منتجات كادت أن تنفد من المخزن!</h4>
            {alerts_html}
        </div>
        """)

    total_sales = sum(
        o['total'] for o in orders_db if 'إلغاء' not in o['status']
    )
    put_grid([[
        put_info(f'👥 المشتركين: {len(users_db)}'),
        put_info(f'📦 الطلبات: {len(orders_db)}'),
        put_success(f'💰 المبيعات: {total_sales} ج.م'),
    ]])

    put_html('<hr>')

    put_buttons(
        [
            {
                'label': '🔐 تغيير بيانات دخول الأدمن وإيميله',
                'value': 'change_admin_creds',
                'color': 'danger',
            },
            {
                'label': '💧 إدارة العلامة المائية ووسائل التواصل الأزرار والصور',
                'value': 'edit_watermark',
                'color': 'info',
            },
            {
                'label': '📧 إدارة الحسابات، التفعيل، وحظر المستخدمين',
                'value': 'manage_users_codes',
                'color': 'success',
            },
            {
                'label': '🎨 تعديل اسم المتجر والرسالة الترحيبية',
                'value': 'edit_store_info',
                'color': 'dark',
            },
            {
                'label': '🚚 إعدادات الشحن وأسعار المحافظات',
                'value': 'shipping_settings',
                'color': 'warning',
            },
            {
                'label': '📦 إدارة ومعالجة الطلبات',
                'value': 'orders',
                'color': 'primary',
            },
            {
                'label': '🛍️ تعديل المنتجات والمخزون والخصومات',
                'value': 'manage_prods',
                'color': 'secondary',
            },
            {
                'label': '💳 تعديل وحذف المحافظ الإلكترونية',
                'value': 'manage_wallets',
                'color': 'light',
            },
            {
                'label': '🚪 الخروج للرئيسية',
                'value': 'logout',
                'color': 'danger',
            },
        ],
        onclick=handle_admin_menu,
    )


def handle_admin_menu(btn_val):
    if btn_val == 'change_admin_creds':
        data = input_group('تغيير اسم وكلمة سر وإيميل الأدمن', [
            input(
                'اسم الأدمن الجديد:',
                value=admin_credentials['username'],
                name='new_username',
                required=True,
            ),
            input(
                'البريد الإلكتروني للأدمن (لاستعادة الباسورد):',
                value=admin_credentials['email'],
                name='new_email',
                required=True,
            ),
            input(
                'كلمة السر الجديدة:',
                type=PASSWORD,
                name='new_password',
                required=True,
            ),
        ])
        admin_credentials['username'] = data['new_username']
        admin_credentials['email'] = data['new_email']
        admin_credentials['password'] = data['new_password']
        toast('تم تحديث بيانات الأدمن بنجاح!', color='success', duration=10)
        show_admin_dashboard()

    elif btn_val == 'edit_watermark':
        btns = store_settings['contact_buttons']

        data = input_group('إدارة العلامة المائية وأزرار التواصل والتصاميم', [
            input(
                'نص العلامة المائية الجديدة:',
                value=store_settings['watermark_text'],
                name='wm_text',
                required=True,
            ),
            select(
                'إظهار العلامة المائية على الموقع؟',
                ['نعم', 'لا'],
                name='show_wm',
            ),
            # التحكم بزر الواتساب
            select(
                'إظهار زر الواتساب للمستخدمين؟',
                ['نعم', 'لا'],
                name='wa_show',
                value='نعم' if btns['whatsapp']['enabled'] else 'لا',
            ),
            input(
                'عنوان زر الواتساب:',
                value=btns['whatsapp']['title'],
                name='wa_title',
            ),
            input(
                'رقم الواتساب (مع كود الدولة مثل 201000000000):',
                value=btns['whatsapp']['val'],
                name='wa_val',
            ),
            input(
                'رابط أيقونة/صورة الواتساب:',
                value=btns['whatsapp']['icon'],
                name='wa_icon',
            ),
            # التحكم بزر الفيسبوك
            select(
                'إظهار زر الفيسبوك للمستخدمين؟',
                ['نعم', 'لا'],
                name='fb_show',
                value='نعم' if btns['facebook']['enabled'] else 'لا',
            ),
            input(
                'عنوان زر الفيسبوك:',
                value=btns['facebook']['title'],
                name='fb_title',
            ),
            input(
                'رابط صفحة الفيسبوك الكامل:',
                value=btns['facebook']['val'],
                name='fb_val',
            ),
            input(
                'رابط أيقونة/صورة الفيسبوك:',
                value=btns['facebook']['icon'],
                name='fb_icon',
            ),
            # التحكم بزر الماسنجر
            select(
                'إظهار زر الماسنجر للمستخدمين؟',
                ['نعم', 'لا'],
                name='msg_show',
                value='نعم' if btns['messenger']['enabled'] else 'لا',
            ),
            input(
                'عنوان زر الماسنجر:',
                value=btns['messenger']['title'],
                name='msg_title',
            ),
            input(
                'رابط الماسنجر (مثل https://m.me/username):',
                value=btns['messenger']['val'],
                name='msg_val',
            ),
            input(
                'رابط أيقونة/صورة الماسنجر:',
                value=btns['messenger']['icon'],
                name='msg_icon',
            ),
        ])

        store_settings['watermark_text'] = data['wm_text']
        store_settings['show_watermark'] = data['show_wm'] == 'نعم'

        # تحديث بيانات أزرار التواصل
        btns['whatsapp']['enabled'] = data['wa_show'] == 'نعم'
        btns['whatsapp']['title'] = data['wa_title']
        btns['whatsapp']['val'] = data['wa_val']
        btns['whatsapp']['icon'] = data['wa_icon']

        btns['facebook']['enabled'] = data['fb_show'] == 'نعم'
        btns['facebook']['title'] = data['fb_title']
        btns['facebook']['val'] = data['fb_val']
        btns['facebook']['icon'] = data['fb_icon']

        btns['messenger']['enabled'] = data['msg_show'] == 'نعم'
        btns['messenger']['title'] = data['msg_title']
        btns['messenger']['val'] = data['msg_val']
        btns['messenger']['icon'] = data['msg_icon']

        toast(
            'تم تعديل العلامة المائية وأزرار التواصل وإيقوناتها بنجاح!',
            color='success',
            duration=10,
        )
        show_admin_dashboard()

    elif btn_val == 'manage_users_codes':
        show_manage_users_codes()

    elif btn_val == 'edit_store_info':
        data = input_group('تعديل هوية المتجر', [
            input(
                'اسم المتجر الإلكتروني',
                name='name',
                value=store_settings['store_name'],
                required=True,
            ),
            textarea(
                'الرسالة الترحيبية',
                name='welcome',
                value=store_settings['welcome_msg'],
                required=True,
            ),
        ])
        store_settings['store_name'] = data['name']
        store_settings['welcome_msg'] = data['welcome']
        toast('تم تحديث معلومات المتجر بنجاح!', color='success', duration=10)
        show_admin_dashboard()

    elif btn_val == 'shipping_settings':
        show_shipping_management()

    elif btn_val == 'orders':
        show_admin_orders_management()

    elif btn_val == 'manage_prods':
        show_manage_products()

    elif btn_val == 'manage_wallets':
        show_manage_wallets()

    elif btn_val == 'logout':
        run_js('sessionStorage.clear(); location.reload();')


# ==================== إدارة الحسابات والطلبات والمنتجات والمحافظ والحظر ====================
def show_manage_users_codes():
    clear()
    render_watermark()
    put_html('<h3>📧 إدارة كود التفعيل وحظر حسابات المستخدمين</h3>')

    if not users_db:
        put_text('لا توجد حسابات مسجلة بعد.')
    else:
        for u, u_info in users_db.items():
            status_str = (
                'مفعل ✅' if u_info['is_active'] else 'في انتظار التفعيل ⏳'
            )
            ban_str = (
                "<span style='color:red; font-weight:bold;'>محظور 🚫</span>"
                if u_info.get('is_banned', False)
                else "<span style='color:green;'>نشط 👍</span>"
            )

            put_html(f"""
            <div style='border:1px solid #ccc; padding:10px; border-radius:5px; margin-bottom:10px;'>
                <b>اسم المستخدم:</b> {u} | <b>البريد (Gmail):</b> {u_info['email']}<br>
                <b>كود التفعيل الحالي:</b> <span style='color:red; font-weight:bold;'>{u_info['code']}</span> | <b>الحالة:</b> {status_str} | <b>حالة الحظر:</b> {ban_str}
            </div>
            """)

            ban_btn_label = (
                f'🔓 فك الحظر عن ({u})'
                if u_info.get('is_banned', False)
                else f'🚫 حظر حساب ({u})'
            )
            ban_btn_color = (
                'secondary' if u_info.get('is_banned', False) else 'danger'
            )

            put_buttons(
                [
                    {
                        'label': f'📧 إرسال كود التفعيل لـ ({u})',
                        'value': f'send_{u}',
                        'color': 'primary',
                    },
                    {
                        'label': f'✅ تفعيل الحساب مباشر لـ ({u})',
                        'value': f'activate_{u}',
                        'color': 'success',
                    },
                    {
                        'label': ban_btn_label,
                        'value': f'ban_{u}',
                        'color': ban_btn_color,
                    },
                ],
                onclick=lambda btn, user_ref=u: handle_user_code_action(
                    btn, user_ref
                ),
            )
            put_html('<br>')

    put_button(
        '🔙 العودة للوحة التحكم',
        onclick=show_admin_dashboard,
        color='secondary',
    )


def handle_user_code_action(btn_val, username):
    u_info = users_db[username]
    if btn_val.startswith('send_'):
        sent = send_email_message(
            u_info['email'],
            f"كود التفعيل - {store_settings['store_name']}",
            f"كود التفعيل الخاص بك هو: {u_info['code']}",
        )
        if sent:
            toast(
                f"تم إرسال كود التفعيل ({u_info['code']}) بنجاح إلى البريد"
                f" {u_info['email']}!",
                color='success',
                duration=10,
            )
        else:
            toast(
                f"كود التفعيل لـ {username} هو ({u_info['code']}). (يمكنك"
                ' تزويده بالعميل يدويًا).',
                color='info',
                duration=10,
            )

    elif btn_val.startswith('activate_'):
        u_info['is_active'] = True
        toast(
            f'تم تفعيل حساب العميل {username} مباشرة!',
            color='success',
            duration=10,
        )
        show_manage_users_codes()

    elif btn_val.startswith('ban_'):
        u_info['is_banned'] = not u_info.get('is_banned', False)
        status_msg = (
            'تم حظر الحساب بنجاح!'
            if u_info['is_banned']
            else 'تم فك الحظر عن الحساب بنجاح!'
        )
        toast(
            f'{status_msg} لـ ({username})',
            color='warning' if u_info['is_banned'] else 'success',
            duration=10,
        )
        show_manage_users_codes()


def show_shipping_management():
    clear()
    render_watermark()
    put_html('<h3>🚚 إدارة الشحن والتوصيل للمحافظات</h3>')

    is_free = select('حالة الشحن العام:', [
        'الشحن بمبلغ محدد حسب المحافظة',
        'شحن مجاني لجميع المناطق',
    ])
    store_settings['free_shipping'] = is_free == 'شحن مجاني لجميع المناطق'

    if not store_settings['free_shipping']:
        selected_gov = select(
            'اختر المحافظة لتعديل سعر الشحن لها:', list(shipping_rates.keys())
        )
        new_rate = input(
            f'سعر الشحن لـ ({selected_gov}):',
            type=NUMBER,
            value=shipping_rates[selected_gov],
            required=True,
        )
        shipping_rates[selected_gov] = new_rate
        toast(
            f'تم تعديل سعر شحن {selected_gov} إلى {new_rate} ج.م!',
            color='success',
            duration=10,
        )

    put_button(
        '🔙 العودة للوحة التحكم',
        onclick=show_admin_dashboard,
        color='secondary',
    )


def show_manage_products():
    clear()
    render_watermark()
    put_html('<h3>🛍️ إدارة المنتجات والمخزون والخصومات</h3>')

    put_buttons(
        [
            {
                'label': '➕ إضافة منتج جديد',
                'value': 'add_prod',
                'color': 'success',
            },
            {
                'label': '🔙 العودة للوحة التحكم',
                'value': 'back',
                'color': 'secondary',
            },
        ],
        onclick=lambda btn: (
            add_new_product_dialog()
            if btn == 'add_prod'
            else show_admin_dashboard()
        ),
    )
    put_html('<hr>')

    if not products:
        put_text(
            'لا توجد منتجات حالياً. يمكنك استخدام الزر أعلاه لإضافة منتج جديد.'
        )
        return

    for p in products:
        stock_summary = ', '.join([
            f"{c}: {info['stock']} قطعة" for c, info in p['color_data'].items()
        ])
        old_p_str = (
            f"{p['old_price']} ج.م" if p.get('old_price') else 'لا يوجد خصم'
        )

        put_html(f"""
        <div style='border:1px solid #ccc; padding:12px; border-radius:6px; margin-bottom:10px; background:#fafafa;'>
            <b>المنتج:</b> {p['name']} | <b>السعر الحالى:</b> {p['price']} ج.م | <b>السعر القديم:</b> {old_p_str}<br>
            <b>حد تحذير المخزون:</b> {p.get('low_stock_limit', 3)} قطع<br>
            <b>تفاصيل المخزون للألوان:</b> {stock_summary}
        </div>
        """)
        put_buttons(
            [
                {
                    'label': f"✏️ تعديل بيانات ومخزون {p['name']}",
                    'value': f"edit_{p['id']}",
                    'color': 'warning',
                },
                {
                    'label': f"🗑️️ حذف {p['name']}",
                    'value': f"del_{p['id']}",
                    'color': 'danger',
                },
            ],
            onclick=lambda btn, prod=p: process_product_action(btn, prod),
        )
        put_html('<br>')


def add_new_product_dialog():
    p_name = input('اسم المنتج الجديد:', required=True)
    p_price = input('السعر بعد الخصم (ج.م):', type=NUMBER, required=True)
    p_old_price = input(
        'السعر القديم قبل الخصم (اكتب 0 إن لم يوجد خصم):',
        type=NUMBER,
        value=0,
    )
    p_limit = input(
        'حد التنبيه عند انخفاض المخزن إلى:',
        type=NUMBER,
        value=3,
        required=True,
    )

    color_data_dict = {}
    colors_count = input(
        'كم عدد الألوان المتاحة لهذا المنتج؟',
        type=NUMBER,
        value=1,
        required=True,
    )

    for i in range(colors_count):
        c_name = input(f'اسم اللون رقم ({i+1}):', required=True)
        c_stock = input(
            f'الكمية المتاحة في المخزن للون ({c_name}):',
            type=NUMBER,
            value=10,
            required=True,
        )
        c_urls = textarea(
            f'روابط الصور للون ({c_name}) - كل رابط في سطر:', required=True
        )

        color_data_dict[c_name] = {
            'images': [u.strip() for u in c_urls.split('\n') if u.strip()],
            'stock': c_stock,
        }

    products.append({
        'id': len(products) + 1,
        'name': p_name,
        'price': p_price,
        'old_price': p_old_price if p_old_price > 0 else None,
        'low_stock_limit': p_limit,
        'color_data': color_data_dict,
    })
    toast('تم إضافة المنتج والمخزون بنجاح!', color='success', duration=10)
    show_manage_products()


def process_product_action(btn_val, product):
    if btn_val.startswith('del_'):
        products.remove(product)
        toast('تم حذف المنتج!', color='success', duration=10)
        show_manage_products()
    elif btn_val.startswith('edit_'):
        new_name = input(
            'اسم المنتج الجديد:', value=product['name'], required=True
        )
        new_price = input(
            'السعر الحالي (ج.م):',
            type=NUMBER,
            value=product['price'],
            required=True,
        )
        new_old_price = input(
            'السعر القديم (أدخل 0 لإلغاء الخصم):',
            type=NUMBER,
            value=product.get('old_price') or 0,
        )
        new_limit = input(
            'حد التنبيه عند انخفاض المخزون:',
            type=NUMBER,
            value=product.get('low_stock_limit', 3),
            required=True,
        )

        for c_name, c_info in product['color_data'].items():
            new_st = input(
                f'تحديث الكمية للون ({c_name}) في المخزن:',
                type=NUMBER,
                value=c_info['stock'],
                required=True,
            )
            c_info['stock'] = new_st

        product['name'] = new_name
        product['price'] = new_price
        product['old_price'] = new_old_price if new_old_price > 0 else None
        product['low_stock_limit'] = new_limit

        toast(
            'تم تحديث المنتج والخصم والمخزون بنجاح!',
            color='success',
            duration=10,
        )
        show_manage_products()


def show_manage_wallets():
    clear()
    render_watermark()
    put_html('<h3>💳 إدارة المحافظ الإلكترونية</h3>')
    if wallets_db:
        for w in wallets_db:
            put_html(
                f"<b>الشركة:</b> {w['company']} | <b>الرقم:</b> {w['number']}<br>"
            )
            put_buttons(
                [
                    {
                        'label': '✏ تعديل',
                        'value': f"edit_{w['id']}",
                        'color': 'warning',
                    },
                    {
                        'label': '🗑️ حذف',
                        'value': f"del_{w['id']}",
                        'color': 'danger',
                    },
                ],
                onclick=lambda btn, wallet=w: process_wallet_action(
                    btn, wallet
                ),
            )
            put_html('<br>')

    put_button(
        '➕ إضافة محفظة جديدة', onclick=add_new_wallet_dialog, color='success'
    )
    put_button(
        '🔙 العودة للوحة التحكم',
        onclick=show_admin_dashboard,
        color='secondary',
    )


def add_new_wallet_dialog():
    new_w = input_group('إضافة محفظة', [
        input('اسم الشركة', name='company', required=True),
        input('رقم المحفظة', name='number', required=True),
    ])
    wallets_db.append({
        'id': len(wallets_db) + 1,
        'company': new_w['company'],
        'number': new_w['number'],
    })
    toast('تمت الإضافة بنجاح!', color='success', duration=10)
    show_manage_wallets()


def process_wallet_action(btn_val, wallet):
    if btn_val.startswith('del_'):
        wallets_db.remove(wallet)
        toast('تم الحذف بنجاح!', color='success', duration=10)
        show_manage_wallets()
    elif btn_val.startswith('edit_'):
        data = input_group('تعديل المحفظة', [
            input(
                'اسم الشركة',
                name='company',
                value=wallet['company'],
                required=True,
            ),
            input(
                'رقم المحفظة',
                name='number',
                value=wallet['number'],
                required=True,
            ),
        ])
        wallet['company'] = data['company']
        wallet['number'] = data['number']
        toast('تم التعديل بنجاح!', color='success', duration=10)
        show_manage_wallets()


def show_admin_orders_management():
    clear()
    render_watermark()
    put_html('<h3>📦 سجل الطلبات والتفاصيل الشاملة</h3>')
    if not orders_db:
        put_text('لا توجد طلبات واردة حالياً.')
        put_button(
            '🔙 العودة للوحة التحكم',
            onclick=show_admin_dashboard,
            color='secondary',
        )
        return

    for o in orders_db:
        items_details = [
            f"• {itm['name']} | اللون: {itm['color']} | الكمية: {itm['qty']} |"
            f" السعر الجزئي: {itm['subtotal']} ج.م"
            for itm in o['items']
        ]
        items_str = '<br>'.join(items_details)

        receipt_html = 'بدون إيصال'
        if o['receipt_img']:
            receipt_html = (
                f"<a href='{o['receipt_img']}' target='_blank'><img"
                f" src='{o['receipt_img']}' width='80' height='80'"
                " style='object-fit:cover; border-radius:5px;'> (عرض"
                ' الإيصال)</a>'
            )

        put_html(f"""
        <div style='border:1px solid #ccc; background:#fdfdfd; padding:15px; border-radius:8px; margin-bottom:15px;'>
            <b>رقم الطلب:</b> #{o['order_id']} | <b>العميل:</b> {o['user']} | <b>الهاتف:</b> {o['phone']}<br>
            <b>العنوان:</b> {o['address']}<br>
            <b>سعر المنتجات:</b> {o['subtotal']} ج.م | <b>الشحن:</b> {o['shipping_fee']} ج.م | <b>الإجمالي الكلي:</b> <span style='color:green; font-weight:bold;'>{o['total']} ج.م</span><br>
            <b>طريقة الدفع:</b> {o['payment_method']} ({o['wallet_company']})<br>
            <b>إيصال التحويل:</b> {receipt_html}<br>
            <hr>
            <b>المنتجات:</b><br>{items_str}<br>
            <hr>
            <b>الحالة الحالية:</b> <span style='color:blue;'>{o['status']}</span>
        </div>
        """)

        put_button(
            f"تحديث حالة الطلب #{o['order_id']} ✏",
            onclick=lambda order_ref=o: update_order_status(order_ref),
            color='warning',
        )
        put_html('<br><br>')

    put_button(
        '🔙 العودة للوحة التحكم',
        onclick=show_admin_dashboard,
        color='secondary',
    )


def update_order_status(order):
    status_choice = select(
        f"اختر الحالة الجديدة للطلب #{order['order_id']}:",
        [
            'قيد المراجعة ⏳',
            'جاري التحضير والتجهيز 🛠',
            'تم الشحن وفي الطريق للعميل 🚚',
            'تم التوصيل بنجاح ✅',
            'تم إلغاء الطلب ❌',
        ],
    )

    if status_choice == 'تم إلغاء الطلب ❌' and 'إلغاء' not in order['status']:
        for item in order['items']:
            p_id = item['product_id']
            p_color = item['color']
            p_qty = item['qty']
            for p in products:
                if p['id'] == p_id and p_color in p['color_data']:
                    p['color_data'][p_color]['stock'] += p_qty

    order['status'] = status_choice
    toast(
        f'تم تحديث حالة الطلب إلى ({status_choice})!',
        color='success',
        duration=10,
    )
    show_admin_orders_management()


if __name__ == '__main__':
    start_server(App, port=8000, debug=True)
