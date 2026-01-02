import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from PIL import Image
import imageio
import asyncio
from dotenv import load_dotenv

load_dotenv()  # .env faylni yuklaydi
TOKEN = os.getenv("TOKEN")

from telegram.ext import ApplicationBuilder

app = ApplicationBuilder().token(TOKEN).build()


def make_zoom_gif(image_path, output_path):
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    frames = []

    # Zoom in
    for i in range(10):
        scale = 1 + i * 0.05
        nw, nh = int(w * scale), int(h * scale)
        r = img.resize((nw, nh))
        l = (nw - w) // 2
        t = (nh - h) // 2
        frames.append(r.crop((l, t, l + w, t + h)))

    # Zoom out
    for i in range(10):
        scale = 1.5 - i * 0.05
        nw, nh = int(w * scale), int(h * scale)
        r = img.resize((nw, nh))
        l = (nw - w) // 2
        t = (nh - h) // 2
        frames.append(r.crop((l, t, l + w, t + h)))

    imageio.mimsave(output_path, frames, duration=0.08)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom!\nRasm yubor — men uni zoom effekt bilan GIF qilib beraman 🎥"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]
        file = await photo.get_file()

        os.makedirs("temp", exist_ok=True)
        img_path = "temp/input.jpg"
        gif_path = "temp/result.gif"

        await file.download_to_drive(img_path)
        make_zoom_gif(img_path, gif_path)

        await update.message.reply_animation(animation=open(gif_path, "rb"))

    except Exception as e:
        await update.message.reply_text(f"Xatolik yuz berdi: {e}")
    finally:
        # Temp fayllarni tozalash
        if os.path.exists(img_path):
            os.remove(img_path)
        if os.path.exists(gif_path):
            os.remove(gif_path)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("GIF bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
