import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Railway se token le rahe hain
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN not found!")
    print("Please add BOT_TOKEN in Railway Environment Variables")
    exit(1)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== WELCOME MESSAGE ====================
WELCOME_MESSAGE = """
🚀 **WELCOME TO [YOUR COMPANY NAME]** 🚀

💰 **Earn Money Online With Us!** 💰

Namaste! 🙏 Aapka swagat hai!

✅ 100% Secure & Trusted
📈 Minimum Investment: ₹500/-
💵 Daily Returns: 10% - 30%
🏆 Referral Bonus: 5%

🔽 **Neeche options mein se choose karein:** 🔽
"""

# ==================== START COMMAND ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    welcome = f"""
👋 **Namaste {user.first_name}!** 👋

{WELCOME_MESSAGE}
"""
    
    keyboard = [
        [InlineKeyboardButton("📢 Proof Channel", callback_data="proof")],
        [InlineKeyboardButton("📞 Contact Support", callback_data="support")],
        [InlineKeyboardButton("📊 Investment Plans", callback_data="plans")],
        [InlineKeyboardButton("❓ Help / FAQ", callback_data="help")]
    ]
    
    await update.message.reply_text(
        welcome,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== BUTTON HANDLERS ====================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
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
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            disable_web_page_preview=True,
            reply_markup=back_button()
        )
    
    elif data == "support":
        text = """
📞 **CONTACT SUPPORT** 📞

👤 Admin: [@your_admin](https://t.me/your_admin)
📧 Email: support@yourcompany.com
💬 WhatsApp: +91-XXXXXXXXXX

📌 **24/7 Available**
"""
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=back_button()
        )
    
    elif data == "plans":
        text = """
📊 **INVESTMENT PLANS** 📊

┌─────────────────────────────┐
│ 🥇 BASIC PLAN               │
│ 💵 ₹500 - ₹5,000            │
│ 📈 10% Daily Returns        │
└─────────────────────────────┘

┌─────────────────────────────┐
│ 🥈 SILVER PLAN              │
│ 💵 ₹5,001 - ₹25,000         │
│ 📈 15% Daily Returns        │
└─────────────────────────────┘

┌─────────────────────────────┐
│ 🥇 GOLD PLAN                │
│ 💵 ₹25,001 - ₹1L            │
│ 📈 20% Daily Returns        │
└─────────────────────────────┘

┌─────────────────────────────┐
│ 👑 PLATINUM PLAN            │
│ 💵 ₹1L+                     │
│ 📈 30% Daily Returns        │
└─────────────────────────────┘

📌 Minimum: ₹500 only!
✅ Instant Withdrawal
"""
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=back_button()
        )
    
    elif data == "help":
        text = """
❓ **HELP / FAQ** ❓

Q: Minimum investment?
A: ₹500/-

Q: Returns kaise milte hain?
A: Daily aapke wallet mein

Q: Withdrawal kaise karein?
A: Support se contact karein

Q: Kya ye safe hai?
A: 100% Secure

🔄 /start - Dobara start karein
"""
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=back_button()
        )
    
    elif data == "back":
        # Wapas main menu
        user = update.effective_user
        welcome = f"""
👋 **Namaste {user.first_name}!** 👋

{WELCOME_MESSAGE}
"""
        keyboard = [
            [InlineKeyboardButton("📢 Proof Channel", callback_data="proof")],
            [InlineKeyboardButton("📞 Contact Support", callback_data="support")],
            [InlineKeyboardButton("📊 Investment Plans", callback_data="plans")],
            [InlineKeyboardButton("❓ Help / FAQ", callback_data="help")]
        ]
        await query.edit_message_text(
            welcome,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

def back_button():
    keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back")]]
    return InlineKeyboardMarkup(keyboard)

# ==================== HELP COMMAND ====================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
📚 **Commands:**

/start - Main menu
/help - Help

👇 Buttons use karein:
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

# ==================== ERROR HANDLER ====================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ Kuch technical issue ho gaya! Support se contact karein."
        )

# ==================== MAIN ====================
def main():
    print("🤖 Starting Investment Bot...")
    print(f"✅ Bot Token: {'Found ✅' if BOT_TOKEN else 'Not Found ❌'}")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_error_handler(error_handler)
    
    print("✅ Bot is running! Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=[])

if __name__ == "__main__":
    main()
