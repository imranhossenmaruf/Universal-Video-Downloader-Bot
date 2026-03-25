import os
import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import yt_dlp

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

DOWNLOAD_DIR = 'downloads'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# --- Functions ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ১. মেইন মেসেজ টেক্সট
    welcome_text = (
        "🔗 Send me a link to a post on Instagram, YouTube, TikTok, etc. "
        "— in a few seconds, the photo, text, or video will be yours!"
    )

    # ২. ইনলাইন বাটন (Inline Keyboard)
    inline_keyboard = [
        [InlineKeyboardButton("➕ Add a bot to the chat", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton("✉️ Invite a friend", url=f"https://t.me/share/url?url=https://t.me/{context.bot.username}&text=Check out this awesome downloader bot!") ]
    ]
    inline_markup = InlineKeyboardMarkup(inline_keyboard)

    # ৩. রিপ্লাই কিবোর্ড (Bottom Menu)
    reply_keyboard = [['Menu']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    await update.message.reply_text(welcome_text, reply_markup=inline_markup)
    # মেনু বাটনটি আলাদা মেসেজে পাঠানো যাতে কিবোর্ডটি পপ-আপ করে
    await update.message.reply_text("Tap 'Menu' to see supported platforms 👇", reply_markup=reply_markup)

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == 'Menu':
        menu_text = (
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

        options_keyboard = [
            [InlineKeyboardButton("➕ Add a bot to the chat", url=f"https://t.me/{context.bot.username}?startgroup=true")],
            [InlineKeyboardButton("🛠 Support", url="https://t.me/IH_Maruf"), InlineKeyboardButton("🔄 Change", callback_data="change")],
            [InlineKeyboardButton("✉️ Invite a friend", url=f"https://t.me/share/url?url=https://t.me/{context.bot.username}")],
            [InlineKeyboardButton("💎 Buy Subscription", callback_data="buy")],
            [InlineKeyboardButton("❌ Hide", callback_data="hide")]
        ]
        options_markup = InlineKeyboardMarkup(options_keyboard)

        await update.message.reply_text(menu_text, reply_markup=options_markup, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "hide":
        await query.message.delete()
    elif query.data == "buy":
        await query.message.reply_text("💳 Subscription service is coming soon! Contact @IH_Maruf for details.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if url.startswith('http'):
        status_msg = await update.message.reply_text("⚡ Processing your request...")
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{DOWNLOAD_DIR}/%(title).30s.%(ext)s',
            'restrictfilenames': True,
            'quiet': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            with open(filename, 'rb') as video:
                await update.message.reply_video(video=video, caption="✅ Done! | @IH_Maruf")
            
            await status_msg.delete()
            if os.path.exists(filename): os.remove(filename)
        except Exception as e:
            await status_msg.edit_text("❌ Error: Unsupported link or file too large.")

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex('^Menu$'), handle_menu))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    application.add_handler(CallbackQueryHandler(button_callback))

    print("🤖 Bot is running like a Long Distance Runner...")
    application.run_polling()

if __name__ == '__main__':
    main()
