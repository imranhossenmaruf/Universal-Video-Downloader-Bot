import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import yt_dlp

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

DOWNLOAD_DIR = 'downloads'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# --- Functions ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # আপনার দেওয়া হুবহু টেক্সট
    welcome_text = (
        "🔗 Send me a link to a post on Instagram, YouTube, TikTok, etc. "
        "— in a few seconds, the photo, text, or video will be yours!"
    )

    # ইনলাইন বাটন: Add a bot to the chat এবং Invite a friend
    inline_keyboard = [
        [InlineKeyboardButton("➕ Add a bot to the chat", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton("✉️ Invite a friend", url=f"https://t.me/share/url?url=https://t.me/{context.bot.username}")]
    ]
    inline_markup = InlineKeyboardMarkup(inline_keyboard)

    # নিচে Reply Keyboard: Menu
    reply_keyboard = [['Menu']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    await update.message.reply_text(welcome_text, reply_markup=inline_markup)
    # রিপ্লাই কিবোর্ড একটিভ করার জন্য ছোট মেসেজ
    await update.message.reply_text("Click 'Menu' for options 👇", reply_markup=reply_markup)

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # আপনি যেভাবে লিস্টটি দিয়েছেন হুবহু সেভাবে
    menu_details = (
        "📥 **My options:**\n\n"
        "▫️ Instagram: reels, posts & stories\n"
        "▫️ Pinterest: videos & stories\n"
        "▫️ Tiktok: videos, photos & audio\n"
        "▫️ Twitter (X): videos & voice\n"
        "▫️ Vk: videos & clips\n"
        "▫️ Reddit: videos & gifs\n"
        "▫️ Twitch: clips\n"
        "▫️ Vimeo\n"
        "▫️ Ok: video\n"
        "▫️ Tumblr: videos & audio\n"
        "▫️ Dailymotion: videos\n"
        "▫️ Likee: videos\n"
        "▫️ Soundcloud\n"
        "▫️ Apple Music\n"
        "▫️ Spotify\n\n"
        "⭐️ **Subscription:** not active"
    )

    # মেনুর নিচের ইনলাইন বাটনগুলো
    options_keyboard = [
        [InlineKeyboardButton("➕ Add a bot to the chat", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton("🛠 Support", url="https://t.me/IH_Maruf"), InlineKeyboardButton("🔄 Change", callback_data="change")],
        [InlineKeyboardButton("✉️ Invite a friend", url=f"https://t.me/share/url?url=https://t.me/{context.bot.username}")],
        [InlineKeyboardButton("💎 Buy Subscription", callback_data="buy"), InlineKeyboardButton("❌ Hide", callback_data="hide")]
    ]
    options_markup = InlineKeyboardMarkup(options_keyboard)

    await update.message.reply_text(menu_details, reply_markup=options_markup, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "hide":
        await query.message.delete()
    elif query.data == "buy":
        await query.message.reply_text("Subscription system is under development by @IH_Maruf")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith('http'):
        return

    status_msg = await update.message.reply_text("⚡ Processing...")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(title).30s.%(ext)s', # ফাইল নেম সর্ট করা
        'restrictfilenames': True,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as video:
            await update.message.reply_video(video=video, caption="✅ Success! | Admin: @IH_Maruf")
        
        await status_msg.delete()
        if os.path.exists(filename): os.remove(filename)
    except Exception as e:
        await status_msg.edit_text("❌ Failed. Link not supported or file too long.")

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Set BOT_TOKEN in secrets!")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex('^Menu$'), handle_menu))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    application.add_handler(CallbackQueryHandler(button_callback))

    print("🤖 Bot is active and following @IH_Maruf's instructions...")
    application.run_polling()

if __name__ == '__main__':
    main()
