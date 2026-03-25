import os
import logging
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# লগিং সেটআপ (যাতে কোনো এরর হলে বুঝতে পারেন)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# গিটহাব সিক্রেট বা এনভায়রনমেন্ট থেকে টোকেন নেওয়া
BOT_TOKEN = os.getenv('BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 স্বাগতম! আমি একটি অল-ইন-ওয়ান ভিডিও ডাউনলোডার বট।\n\n"
        "যেকোনো ভিডিওর লিঙ্ক (YouTube, FB, Insta, TikTok) এখানে পাঠান, "
        "আমি সরাসরি ফাইলটি আপনাকে পাঠিয়ে দেব।"
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    # ইউজারকে প্রসেসিং মেসেজ দেওয়া
    status_msg = await update.message.reply_text("⏳ ভিডিওটি প্রসেস করছি, দয়া করে একটু অপেক্ষা করুন...")

    # yt-dlp এর কনফিগারেশন
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s', # ডাউনলোড ফোল্ডারে সেভ হবে
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ভিডিওর তথ্য সংগ্রহ এবং ডাউনলোড
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'No Title')
            thumbnail = info.get('thumbnail')
            file_path = ydl.prepare_filename(info)

            # থাম্বনেইল থাকলে সেটি আগে পাঠানো
            if thumbnail:
                await context.bot.send_photo(
                    chat_id=chat_id, 
                    photo=thumbnail, 
                    caption=f"🎬 **Title:** {title}"
                )
            
            # সরাসরি ভিডিও ফাইল পাঠানো
            with open(file_path, 'rb') as video_file:
                await context.bot.send_video(
                    chat_id=chat_id, 
                    video=video_file, 
                    caption="✅ ডাউনলোড সম্পন্ন হয়েছে!",
                    supports_streaming=True
                )
            
            # পাঠানো শেষ হলে ফাইলটি ডিলিট করে দেওয়া (স্টোরেজ বাঁচানোর জন্য)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # প্রসেসিং মেসেজটি ডিলিট করা
            await status_msg.delete()

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await update.message.reply_text("❌ দুঃখিত! ভিডিওটি ডাউনলোড করা সম্ভব হয়নি। লিঙ্কটি সঠিক কিনা চেক করুন।")

if __name__ == '__main__':
    # ডাউনলোড করার জন্য ফোল্ডার না থাকলে তৈরি করা
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    # টোকেন চেক করা
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN এনভায়রনমেন্ট ভেরিয়েবলে পাওয়া যায়নি!")
    else:
        # বট চালু করা
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_video))
        
        print("🤖 বটটি সফলভাবে চালু হয়েছে...")
        app.run_polling()
