import os
import json
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================== CONFIG ====================
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN not found!")
    exit(1)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== USERS FILE ====================
USERS_FILE = "users.json"

def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def add_user(user_id, username, first_name):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {
            "id": user_id,
            "username": username,
            "first_name": first_name,
            "joined_at": str(datetime.now())
        }
        save_users(users)
        return True
    return False

# ==================== WELCOME MESSAGE ====================
WELCOME_MESSAGE = """
🚀 **WELCOME TO [YOUR COMPANY NAME]** 🚀

💰 **Earn Money Online With Us!** 💰

Namaste! 🙏 Aapka swagat hai!

✅ 100% Secure & Trusted
📈 Minimum Investment: ₹500/-
💵 Daily Returns: 10% - 30%
🏆 Referral Bonus: 5%

🔽 **Options mein se choose karein:** 🔽
"""

# ==================== START COMMAND ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username, user.first_name)
    
    welcome = f"""
👋 **Namaste {user.first_name}!** 👋

{WELCOME_MESSAGE}
"""
    
    # 🔥 CHAT BUTTONS (Keyboard)
    keyboard = [
        [
            InlineKeyboardButton("📢 Proof Channel", callback_data="proof"),
            InlineKeyboardButton("📞 Support", callback_data="support")
        ],
        [
            InlineKeyboardButton("📊 Investment Plans", callback_data="plans"),
            InlineKeyboardButton("❓ Help", callback_data="help")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # 📸 IMAGE SEND KAREIN PEHLE
    image_url = "https://example.com/your-image.jpg"  # ⚠️ YAHAN APNI IMAGE URL DALEIN!
    
    try:
        await update.message.reply_photo(
            photo=image_url,
            caption=welcome,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    except:
        # Agar image nahi mili toh sirf text bhejein
        await update.message.reply_text(
            welcome,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

# ==================== BUTTON CALLBACK ====================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    data = query.data
    
    # ===== PROOF CHANNEL =====
    if data == "proof":
        text = """
📢 **PROOF CHANNEL** 📢

✅ Hamare real payment proofs:

🔹 Channel: [@your_proof_channel](https://t.me/your_proof_channel)
🔹 500+ Satisfied Investors
🔹 Daily Payouts

👇 **Join karein:**
👉 [@your_proof_channel](https://t.me/your_proof_channel)
"""
        keyboard = [
            [InlineKeyboardButton("🔙 Back", callback_data="back")],
            [InlineKeyboardButton("📢 Join Channel", url="https://t.me/your_proof_channel")]
        ]
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # ===== CONTACT SUPPORT =====
    elif data == "support":
        text = """
📞 **CONTACT SUPPORT** 📞

👤 Admin: [@your_admin](https://t.me/your_admin)
📧 Email: support@yourcompany.com
💬 WhatsApp: +91-XXXXXXXXXX

📌 **24/7 Available**
"""
        keyboard = [
            [InlineKeyboardButton("🔙 Back", callback_data="back")],
            [InlineKeyboardButton("📩 Contact Admin", url="https://t.me/your_admin")]
        ]
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # ===== INVESTMENT PLANS =====
    elif data == "plans":
        text = """
📊 **INVESTMENT PLANS** 📊

┌─────────────────────────────┐
│ 🥇 BASIC PLAN               │
│ 💵 ₹500 - ₹5,000            │
│ 📈 10% Daily Returns        │
│ ⏳ 30 Days                  │
└─────────────────────────────┘

┌─────────────────────────────┐
│ 🥈 SILVER PLAN              │
│ 💵 ₹5,001 - ₹25,000         │
│ 📈 15% Daily Returns        │
│ ⏳ 30 Days                  │
└─────────────────────────────┘

┌─────────────────────────────┐
│ 🥇 GOLD PLAN                │
│ 💵 ₹25,001 - ₹1L            │
│ 📈 20% Daily Returns        │
│ ⏳ 30 Days                  │
└─────────────────────────────┘

┌─────────────────────────────┐
│ 👑 PLATINUM PLAN            │
│ 💵 ₹1L+                     │
│ 📈 30% Daily Returns        │
│ ⏳ 30 Days                  │
└─────────────────────────────┘

📌 Minimum: ₹500 only!
✅ Instant Withdrawal
"""
        keyboard = [
            [InlineKeyboardButton("🔙 Back", callback_data="back")],
            [InlineKeyboardButton("💰 Invest Now", callback_data="invest")]
        ]
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # ===== INVEST NOW =====
    elif data == "invest":
        text = """
💰 **INVEST NOW** 💰

Apna investment plan select karein:

1️⃣ Basic Plan - ₹500
2️⃣ Silver Plan - ₹5,000
3️⃣ Gold Plan - ₹25,000
4️⃣ Platinum Plan - ₹1,00,000

📌 **Steps:**
1. Support se contact karein
2. Payment karein (UPI/Bank)
3. Investment confirm ho jayega

👇 **Support se baat karein:**
"""
        keyboard = [
            [InlineKeyboardButton("🔙 Back", callback_data="back")],
            [InlineKeyboardButton("📞 Contact Support", url="https://t.me/your_admin")]
        ]
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # ===== HELP / FAQ =====
    elif data == "help":
        text = """
❓ **HELP / FAQ** ❓

**Q: Minimum investment?**
A: ₹500/-

**Q: Returns kaise milte hain?**
A: Daily aapke wallet mein

**Q: Withdrawal kaise karein?**
A: Support se contact karein

**Q: Kya ye safe hai?**
A: 100% Secure platform

📌 **Still have questions?**
Contact support 👇
"""
        keyboard = [
            [InlineKeyboardButton("🔙 Back", callback_data="back")],
            [InlineKeyboardButton("📞 Contact Support", url="https://t.me/your_admin")]
        ]
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # ===== BACK TO MAIN MENU =====
    elif data == "back":
        welcome = f"""
👋 **Namaste {user.first_name}!** 👋

{WELCOME_MESSAGE}
"""
        keyboard = [
            [
                InlineKeyboardButton("📢 Proof Channel", callback_data="proof"),
                InlineKeyboardButton("📞 Support", callback_data="support")
            ],
            [
                InlineKeyboardButton("📊 Investment Plans", callback_data="plans"),
                InlineKeyboardButton("❓ Help", callback_data="help")
            ]
        ]
        
        # Image ke saath wapas bhejein
        image_url = "https://example.com/your-image.jpg"
        try:
            await query.edit_message_media(
                media=InputMediaPhoto(
                    media=image_url,
                    caption=welcome,
                    parse_mode='Markdown'
                ),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            await query.edit_message_text(
                welcome,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

# ==================== HELP COMMAND ====================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
📚 **Commands:**

/start - Main menu
/help - Help
/status - Bot status
"""
    keyboard = [
        [InlineKeyboardButton("📢 Proof", callback_data="proof")],
        [InlineKeyboardButton("📞 Support", callback_data="support")],
        [InlineKeyboardButton("📊 Plans", callback_data="plans")]
    ]
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== STATUS ====================
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    text = f"""
🤖 **Bot Status**

👥 Total Users: {len(users)}
✅ Status: Online

⚡️ Bot is working perfectly!
"""
    await update.message.reply_text(text, parse_mode='Markdown')

# ==================== ERROR ====================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

# ==================== MAIN ====================
def main():
    print("🤖 Starting Investment Bot with Image...")
    print(f"✅ Bot Token: {'Found ✅' if BOT_TOKEN else 'Not Found ❌'}")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_error_handler(error_handler)
    
    print("✅ Bot is running!")
    app.run_polling(allowed_updates=[])

if __name__ == "__main__":
    main()
