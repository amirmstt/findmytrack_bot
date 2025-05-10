import os
from difflib import get_close_matches
from telegram import (
    Update, ReplyKeyboardMarkup, InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, CallbackContext, CallbackQueryHandler
)

# ===== تنظیمات ربات =====
TOKEN = "7609797156:AAFiRNxZjAwRuc_Tx0E7KCivFUPXdvFnp6o"
MUSIC_FOLDER = "C:\\Users\\Shay\\Desktop\\mymusicbot\\music"
user_playlists = {}

# ===== دستورات =====

async def start(update: Update, context: CallbackContext):
    keyboard = [
        ["/search 🎵", "/playlist 📂"],
        ["/help ❓", "/about ℹ️"]
    ]
    await update.message.reply_text(
        "به ربات موزیک‌یاب Findmytrack خوش اومدی! 🎧\n\n"
        "یکی از گزینه‌ها رو انتخاب کن:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "📌 دستورها:\n"
        "/search - جستجوی آهنگ\n"
        "/playlist - پلی‌لیست شخصی شما\n"
        "فقط کافیه اسم آهنگ یا خواننده رو بفرستی!"
    )

async def about(update: Update, context: CallbackContext):
    await update.message.reply_text("این ربات توسط خودت ساخته شده! ✌️\nنام: Findmytrack")

async def search_command(update: Update, context: CallbackContext):
    await update.message.reply_text("لطفاً اسم آهنگ یا خواننده رو بنویس تا برات بگردم! 🎶")

# ===== هندل پیام‌ها =====

async def handle_message(update: Update, context: CallbackContext):
    query = update.message.text.strip().lower()
    files = os.listdir(MUSIC_FOLDER)
    matches = get_close_matches(query, [f.lower() for f in files], n=5, cutoff=0.3)

    if not matches:
        yt_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        await update.message.reply_text(f"❌ آهنگ پیدا نشد.\nولی یه لینک از یوتیوب برات دارم:\n{yt_url}")
        return

    # فقط یکی خیلی نزدیک بود؟ همون یکی رو بفرست
    if len(matches) == 1:
        filename = matches[0]
        file_path = os.path.join(MUSIC_FOLDER, filename)
        await update.message.reply_audio(audio=open(file_path, 'rb'))

        # دکمه امتیازدهی
        keyboard = [[
            InlineKeyboardButton("❤️ خیلی دوست داشتم", callback_data=f"like|{filename}"),
            InlineKeyboardButton("👎 نه جالب نبود", callback_data=f"dislike|{filename}")
        ]]
        await update.message.reply_text("نظرتو درباره این آهنگ بگو:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text("🎵 چند تا آهنگ مشابه پیدا کردم:")
        for filename in matches:
            file_path = os.path.join(MUSIC_FOLDER, filename)
            await update.message.reply_audio(audio=open(file_path, 'rb'))

            keyboard = [[
                InlineKeyboardButton("❤️ خیلی دوست داشتم", callback_data=f"like|{filename}"),
                InlineKeyboardButton("👎 نه جالب نبود", callback_data=f"dislike|{filename}")
            ]]
            await update.message.reply_text("نظرتو درباره این آهنگ بگو:", reply_markup=InlineKeyboardMarkup(keyboard))

# ===== امتیازدهی =====

async def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    action, track = query.data.split('|')

    if action == "like":
        await query.edit_message_text(text=f"❤️ نظر ثبت شد برای: {track}")
    elif action == "dislike":
        await query.edit_message_text(text=f"👎 نظر منفی ثبت شد برای: {track}")

# ===== پلی‌لیست =====

async def playlist(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    playlist = user_playlists.get(user_id, [])
    if playlist:
        text = "🎵 پلی‌لیست شما:\n" + "\n".join(f"- {track}" for track in playlist)
    else:
        text = "پلی‌لیست شما خالیه. برای اضافه کردن، اسم آهنگ رو بفرست!"
    await update.message.reply_text(text)

# ===== اجرای ربات =====

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("about", about))
app.add_handler(CommandHandler("search", search_command))
app.add_handler(CommandHandler("playlist", playlist))
app.add_handler(CallbackQueryHandler(handle_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("ربات فعال شد...")
app.run_polling()