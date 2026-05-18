import config, os
from telethon import TelegramClient, events, Button
import plugins.downloader as downloader
import plugins.search_engine as search_engine
import plugins.ai_engine as ai_engine

bot = TelegramClient('super_bot', config.API_ID, config.API_HASH).start(bot_token=config.BOT_TOKEN)
user_status = {}

def get_main_buttons():
    return [
        [Button.inline("🤖 AI Ask", b"ai_ask"), Button.inline("🎙️ AI Voice", b"ai_voice")],
        [Button.inline("🌍 AI Translator", b"ai_trans"), Button.inline("💻 Code Helper", b"ai_code")],
        [Button.inline("🎨 AI ပုံဆွဲမယ်", b"ai_img"), Button.inline("📰 သတင်း/Updates", b"ai_news")],
        [Button.inline("🎬 YT ရှာဖွေရေး", b"yt_search"), Button.inline("🎥 Downloader", b"dl")],
        [Button.inline("🔄 Restart Bot", b"start_again")]
    ]

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_status[event.sender_id] = None
    await event.reply("🔥 **Super AI Bot V4.0 (Ultimate Edition) အသင့်ဖြစ်ပါပြီ!**", buttons=get_main_buttons())

@bot.on(events.CallbackQuery)
async def callback(event):
    d, uid = event.data, event.sender_id
    back_btn = [Button.inline("⬅️ Back", b"start_again")]
    
    modes = {
        b"ai_ask": ("ai_general", "🤖 **သိချင်တာရှိရင် တောက်လျှောက်မေးပါ ဆရာကြီး-**"),
        b"ai_voice": ("ai_voice", "🎙️ **အသံပြောင်းချင်တဲ့ စာသားပေးပါ (MM/EN ရပါတယ်)-**"),
        b"ai_trans": ("ai_translate", "🌍 **ဘာသာပြန်ချင်တဲ့ စာသား ပေးပါ (EN ⇄ MM)-**"),
        b"ai_code": ("ai_coder", "💻 **ဘယ်လို Programming အကူအညီ လိုအပ်ပါသလဲ ဆရာကြီး-**"),
        b"ai_img": ("ai_image", "🎨 **ဘယ်လိုပုံမျိုး ဆွဲပေးရမလဲ (English လို ရိုက်ပေးပါ)-**"),
        b"ai_news": ("ai_news", "📰 **ဘယ်လိုသတင်းတွေ သိချင်ပါသလဲ (ဥပမာ- Tech news)-**"),
        b"dl": ("dl", "📥 **Video Link ပေးပါ (TikTok/YouTube/FB)-**"),
        b"yt_search": ("yt_search", "🔍 **ဗီဒီယိုအမည် ပေးပါ-**")
    }

    if d == b"start_again":
        user_status[uid] = None
        await event.edit("🚀 **ပင်မစာမျက်နှာ**", buttons=get_main_buttons())
    elif d in modes:
        user_status[uid] = modes[d][0]
        await event.edit(modes[d][1], buttons=back_btn)

@bot.on(events.NewMessage)
async def handle_all(event):
    if event.raw_text.startswith('/'): return
    uid, text = event.sender_id, event.raw_text
    st = user_status.get(uid)
    if not st: return

    m = await event.reply("⏳ **လုပ်ဆောင်နေပါပြီ ဆရာကြီး...**")
    
    if st == "ai_voice":
        v_path = ai_engine.text_to_speech(text)
        if v_path:
            await bot.send_file(event.chat_id, v_path, caption=f"🎙️ **'{text}' ကို ဖတ်ပြထားတာပါ**")
            os.remove(v_path)
        else: await event.reply("⚠️ အသံပြောင်းလို့ မရပါဘူး ဆရာကြီး။")
    
    elif st.startswith("ai_"):
        mode = st.split("_")[1]
        if mode == "image":
            img_url = ai_engine.generate_image_url(text)
            await bot.send_file(event.chat_id, img_url, caption=f"🎨 **AI ဆွဲပေးလိုက်တဲ့ပုံပါ:**\n`{text}`")
        else:
            res = ai_engine.ask_ai(text, mode=mode)
            await event.reply(f"🤖 **AI ရဲ့ အဖြေ:**\n\n{res}\n\n---")
    
    elif st == "dl":
        path, msg = downloader.download_video(text)
        if path and os.path.exists(path):
            await bot.send_file(event.chat_id, path, caption=msg); os.remove(path)
        else: await event.reply(msg)
        user_status[uid] = None
        
    elif st == "yt_search":
        res = search_engine.search_youtube(text); await event.reply(res)
        user_status[uid] = None

    await m.delete()

print("✅ Super Bot V4.0 စတင်ပါပြီ ဆရာကြီး...")
bot.run_until_disconnected()
