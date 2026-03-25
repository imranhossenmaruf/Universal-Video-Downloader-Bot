import os
import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, InlineQueryHandler
import yt_dlp
from uuid import uuid4

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

DOWNLOAD_DIR = 'downloads'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# --- ল্যাঙ্গুয়েজ ডাটাবেস (নমুনা হিসেবে ৩টি দেওয়া হলো, আপনি ২০টি যোগ করতে পারবেন) ---
LANG_DATA = {
    'en': {
        'start': "🔗 Send me a link to a post on Instagram, YouTube, TikTok, etc. — in a few seconds, the photo, text, or video will be yours!",
        'menu_btn': 'Menu',
        'options_head': '📥 My options:',
        'sub': '⭐️ Subscription: not active',
        'add_bot': '➕ Add a bot to the chat',
        'invite': '✉️ Invite a friend',
        'search_btn': '🔍 Search For Another video',
        'lang_btn': '🌐 Language',
        'support': '🛠 Support',
        'buy': '💎 Buy Subscription',
        'hide': '❌ Hide'
    },
    'bn': {
        'start': "🔗 আমাকে ইনস্টাগ্রাম, ইউটিউব বা টিকটক লিঙ্ক পাঠান — কয়েক সেকেন্ডের মধ্যে ভিডিওটি আপনার হবে!",
        'menu_btn': 'মেনু',
        'options_head': '📥 আমার অপশনসমূহ:',
        'sub': '⭐️ সাবস্ক্রিপশন: সচল নয়',
        'add_bot': '➕ বটে গ্রুপে যুক্ত করুন',
        'invite': '✉️ বন্ধুকে ইনভাইট করুন',
        'search_btn': '🔍 অন্য ভিডিও সার্চ করুন',
        'lang_btn': '🌐 ভাষা পরিবর্তন',
        'support': '🛠 সাপোর্ট',
        'buy': '💎 সাবস্ক্রিপশন কিনুন',
        'hide': '❌ হাইড করুন'
    }
}

# ডিফল্ট ভাষা সেট করা (User specific database থাকলে ভালো হয়, এখানে গ্লোবাল রাখা হয়েছে)
current_lang = 'en'

def get_text(key):
    return LANG_DATA.get(current_lang, LANG_DATA['en']).get(key)

# --- Functions ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    inline_keyboard = [
        [InlineKeyboardButton(f"✨ {get_text('add_bot')} ✨", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton(f"🔍 {get_text('search_btn')}", switch_inline_query_current_chat="")],
        [InlineKeyboardButton(f"✉️ {get_text('invite')}", url=f"https://t.me/share/url?url=https://t.me/{context.bot.username}")]
    ]
    # বাটন বড় দেখানোর জন্য ইমোজি এবং স্পেস ব্যবহার করা হয়েছে
    inline_markup = InlineKeyboardMarkup(inline_keyboard)
    
    reply_markup = ReplyKeyboardMarkup([[get_text('menu_btn')]], resize_keyboard=True)

    await update.message.reply_text(get_text('start'), reply_markup=inline_markup)

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_details = (
        f"{get_text('options_head')}\n\n"
        "▫️ Instagram | Pinterest | Tiktok\n"
        "▫️ Twitter (X) | Vk | Reddit\n"
        "▫️ Twitch | Vimeo | Ok | Tumblr\n"
        "▫️ Soundcloud | Spotify | Apple Music\n\n"
        f"{get_text('sub')}"
    )

    options_keyboard = [
        [InlineKeyboardButton(f"✨ {get_text('add_bot')} ✨", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton(f"🌐 {get_text('lang_btn')}", callback_data="show_languages"), InlineKeyboardButton(f"🛠 {get_text('support')}", url="https://t.me/IH_Maruf")],
        [InlineKeyboardButton(f"✉️ {get_text('invite')}", url=f"https://t.me/share/url?url=https://t.me/{context.bot.username}")],
        [InlineKeyboardButton(f"💎 {get_text('buy')}", callback_data="buy"), InlineKeyboardButton(f"❌ {get_text('hide')}", callback_data="hide")]
    ]
    await update.message.reply_text(menu_details, reply_markup=InlineKeyboardMarkup(options_keyboard))

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query: return

    results = []
    # yt-dlp দিয়ে সার্চ রেজাল্ট আনা (নমুনা হিসেবে একটি রেজাল্ট দেখাচ্ছি)
    results.append(
        InlineQueryResultArticle(
            id=str(uuid4()),
            title=f"Search YouTube: {query}",
            input_message_content=InputTextMessageContent(f"Searching for: {query}\nPlease wait...")
        )
    )
    await update.inline_query.answer(results)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_lang
    query = update.callback_query
    await query.answer()

    if query.data == "hide":
        await query.message.delete()
    elif query.data == "show_languages":
        # ২০টি ভাষার লিস্ট (এখানে নমুনা হিসেবে ২টি দেওয়া হলো)
        keyboard = [
            [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"), InlineKeyboardButton("🇧🇩 Bengali", callback_data="lang_bn")],
            [InlineKeyboardButton("🇮🇳 Hindi", callback_data="lang_hi"), InlineKeyboardButton("🇸🇦 Arabic", callback_data="lang_ar")]
        ]
        await query.edit_message_text("Select your language:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data.startswith("lang_"):
        current_lang = query.data.split("_")[1]
        await query.edit_message_text(f"Language changed to: {current_lang.upper()}\nRun /start to refresh.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith('http'): return
    status = await update.message.reply_text("⚡ Processing...")
    
    ydl_opts = {'format': 'best', 'outtmpl': f'{DOWNLOAD_DIR}/%(title).30s.%(ext)s', 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        with open(filename, 'rb') as v:
            await update.message.reply_video(video=v, caption="✅ Success! | @IH_Maruf")
        await status.delete()
        if os.path.exists(filename): os.remove(filename)
    except:
        await status.edit_text("❌ Error: Unsupported link.")

def main():
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex('^(Menu|মেনু)$'), handle_menu))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(InlineQueryHandler(inline_query))
    application.run_polling()

if __name__ == '__main__':
    main()
