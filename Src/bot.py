import os
import logging
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# লোগিং সেটআপ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ডিরেক্টরি তৈরি
DOWNLOAD_DIR = 'downloads'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# ফাইল নেম ক্লিন করার ফাংশন
def clean_filename(title):
    # শুধু অক্ষর এবং সংখ্যা রাখবে, বাকি সব বাদ দিয়ে নাম ছোট করবে
    clean_title = re.sub(r'[^\w\s-]', '', title).strip()
    return clean_title[:30] # সর্বোচ্চ ৩০ ক্যারেক্টার

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 হাই! আমি ইউনিভার্সাল ভিডিও ডাউনলোডার।\nযেকোনো ভিডিও লিঙ্ক পাঠান, আমি ডাউনলোড করে দিচ্ছি।")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    status_msg = await update.message.reply_text("⏳ প্রসেসিং হচ্ছে, দয়া করে অপেক্ষা করুন...")

    # yt-dlp সেটিংস
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(title).30s.%(ext)s', # নাম ছোট রাখা
        'restrictfilenames': True, # স্পেশাল ক্যারেক্টার বাদ দেওয়া
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # ভিডিও পাঠানো
        await status_msg.edit_text("📤 আপলোড হচ্ছে...")
        with open(filename, 'rb') as video:
            await update.message.reply_video(video=video, caption=f"✅ সফলভাবে ডাউনলোড হয়েছে।\n👤 Admin: @IH_Maruf")
        
        await status_msg.delete()

        # ডাউনলোড শেষে ফাইল মুছে ফেলা (স্টোরেজ বাঁচানোর জন্য)
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        await status_msg.edit_text(f"❌ দুঃখিত, ভিডিওটি ডাউনলোড করা সম্ভব হয়নি।\n\nকারণ: ফাইল নেম খুব বড় অথবা লিঙ্কটি সাপোর্ট করছে না।")

def main():
    # গিটহাব সিক্রেট থেকে টোকেন নেওয়া
    TOKEN = os.getenv("BOT_TOKEN")
    
    if not TOKEN:
        print("Error: BOT_TOKEN variable not found!")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("🤖 বটটি সফলভাবে চালু হয়েছে...")
    application.run_polling(poll_interval=1.0, timeout=30)

if __name__ == '__main__':
    main()
