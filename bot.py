import os
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# ==================== 配置 ====================
# 优先读取环境变量，没有的话用你提供的 Token（部署后请换成新 Token）
BOT_TOKEN = os.getenv("BOT_TOKEN", "9105103442:AAEP3gfCBn6_WE0QdD10a-F6P0er9QwRcHo")

# 时代少年团成员
TNT_MEMBERS = [
    "马嘉祺", "丁程鑫", "宋亚轩", "刘耀文",
    "张真源", "严浩翔", "贺峻霖",
    "嘉祺", "程鑫", "亚轩", "耀文",
    "真源", "浩翔", "峻霖"
]

FAKE_AMOUNT = "500000000"

# ==================== 工具函数 ====================
def generate_fake_address() -> str:
    chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    return "T" + "".join(random.choice(chars) for _ in range(33))

def is_tnt_related(text: str) -> bool:
    text_lower = text.lower()
    for name in TNT_MEMBERS:
        if name.lower() in text_lower:
            return True
    return False

def generate_fancy_id(name: str) -> str:
    decorations = [
        "ღ", "♡", "❀", "✿", "❁", "✾", "⋆", "✦", "✧", "✩", "✪",
        "꧁", "꧂", "༺", "༻", "『", "』", "【", "】",
        "♥", "❤", "💕", "💖", "💗", "💘", "💝", "💞",
        "✨", "🌟", "⭐", "🌠", "💫", "🔥"
    ]
    
    styles = [
        f"꧁༺ ღLove唯爱 {name} ღ ༻꧂",
        f"『 ♡ 专属 · {name} ♡ 』",
        f"❀ 永远的 {name} ❀",
        f"✦ 只属于你的 {name} ✦",
        f"ღ 心之所向 · {name} ღ",
        f"꧁ 唯爱 {name} ꧂",
        f"【 专属ID · {name} 】",
        f"♡ {name} 是唯一 ♡",
        f"⋆˙⟡ {name} 永远 ⋆˙⟡",
        f"༺ 只此一人 · {name} ༻",
        f"ღLove唯爱 {name}ღ",
        f"꧁༺ {name} ༻꧂",
    ]
    
    base = random.choice(styles)
    extra = "".join(random.choice(decorations) for _ in range(random.randint(4, 7)))
    return f"{extra}\n{base}\n{extra}"

# ==================== 处理函数 ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "欢迎使用时代少年团专属定制机器人~\n\n"
        "直接发送你想定制的内容，例如：\n"
        "「定制马嘉祺专属ID」\n"
        "「给我一个丁程鑫的」\n\n"
        "⚠️ 仅支持时代少年团成员，其他人物不给生成。"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    
    if not is_tnt_related(user_text):
        await update.message.reply_text(
            "❌ 检测到非时代少年团人物\n\n"
            "本机器人仅支持时代少年团成员定制：\n"
            "马嘉祺 / 丁程鑫 / 宋亚轩 / 刘耀文\n"
            "张真源 / 严浩翔 / 贺峻霖\n\n"
            "请重新发送正确的请求~"
        )
        return
    
    # 提取名字
    name = "未知"
    for member in TNT_MEMBERS:
        if member in user_text:
            name = member
            break
    
    context.user_data["pending_name"] = name
    
    fake_addr = generate_fake_address()
    
    keyboard = [[InlineKeyboardButton("完成✅", callback_data="pay_done")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"老师老师~ 收到定制请求啦\n\n"
        f"请先完成测试付款：\n\n"
        f"💰 金额：{FAKE_AMOUNT} USDT\n"
        f"📍 地址：\n`{fake_addr}`\n\n"
        f"（这是测试用假地址，随便点完成就行）\n\n"
        f"付完后点下面按钮↓",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def pay_done_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    name = context.user_data.get("pending_name")
    if not name:
        await query.edit_message_text("没有待处理的订单哦，请重新发送定制请求。")
        return
    
    fancy = generate_fancy_id(name)
    
    await query.edit_message_text(
        f"✅ 付款已确认（测试）\n\n"
        f"为你生成的专属内容：\n\n"
        f"{fancy}\n\n"
        f"————————————\n"
        f"喜欢可以再来定制其他成员~"
    )
    
    context.user_data.pop("pending_name", None)

# ==================== 主程序 ====================
def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(pay_done_callback, pattern="^pay_done$"))
    
    print("机器人已启动...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()