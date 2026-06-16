import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Bot token - Railway se environment variable le rahe hain
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN not found! Add it in Railway variables.")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------- WELCOME MESSAGE ----------
WELCOME_MESSAGE = """
🚀 **WELCOME TO [YOUR COMPANY NAME]** 🚀

💰 **Earn Money Online With Us!** 💰

✅ 100% Secure & Trusted
📈 Minimum Investment: ₹500/-
💵 Daily Returns: 10% - 30%

🔽 **Neeche options mein se choose karein:** 🔽
"""

# ---------- START COMMAND ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    welcome = f"""
👋 **Namaste {user.first_name}!** 👋

{WELCOME_MESSAGE}
"""
    
    keyboard = [
        [InlineKeyboardButton("📢 Proof Channel", callback_data="proof_channel")],
        [InlineKeyboardButton("📞 Contact Support", callback_data="contact_support")],
        [InlineKeyboardButton("📊 Investment Plans", callback_data="investment_plans")],
        [InlineKeyboardButton("❓ Help / FAQ", callback_data="help_faq")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

# ---------- BUTTON CLICK HANDLER ----------
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "proof_channel":
        text = """
📢 **PROOF CHANNEL** 📢

🔹 Channel: [@your_proof_channel](https://t.me/your_proof_channel)
🔹 500+ Satisfied Investors
🔹 Daily Payment Proofs

👇 **Join Now:**
👉 [@your_proof_channel](https://t.me/your_proof_channel)
"""
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            disable_web_page_preview=True,
            reply_markup=back_button()
        )
    
    elif data == "contact_support":
        text = """
📞 **CONTACT SUPPORT** 📞

👤 Admin: [@your_admin](https://t.me/your_admin)
📧 Email: support@yourcompany.com
📌 24/7 Available

⚠️ *Kisi bhi issue ke liye contact karein!*
"""
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=back_button()
        )
    
    elif data == "investment_plans":
        text = """
📊 **INVESTMENT PLANS** 📊

┌─────────────────────────────┐
│ 🥇 **BASIC PLAN**           │
│ 💵 ₹500 - ₹5,000            │
│ 📈 10% Daily Returns        │
└─────────────────────────────┘

┌─────────────────────────────┐
│ 🥈 **SILVER PLAN**          │
│ 💵 ₹5,001 - ₹25,000         │
│ 📈 15% Daily Returns        │
└─────────────────────────────┘

┌─────────────────────────────┐
│ 🥇 **GOLD PLAN**            │
│ 💵 ₹25,001 - ₹1L            │
│ 📈 20% Daily Returns        │
└─────────────────────────────┘

┌─────────────────────────────┐
│ 👑 **PLATINUM PLAN**        │
│ 💵 ₹1L+                     │
│ 📈 30% Daily Returns        │
└─────────────────────────────┘

📌 **Minimum Investment:** ₹500 only!
✅ Instant Withdrawal
✅ No Hidden Charges

👉 Support se contact karein aur invest karein!
"""
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=back_button()
        )
    
    elif data == "help_faq":
        text = """
❓ **FAQ** ❓

**Q: Minimum investment kitna hai?**
A: ₹500/-

**Q: Returns kaise milte hain?**
A: Daily aapke wallet mein

**Q: Withdrawal kaise karein?**
A: Support se contact karein

**Q: Kya ye safe hai?**
A: 100% Secure platform hai

🔄 /start - Dobara start karein
"""
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=back_button()
        )
    
    elif data == "back_to_main":
        user = update.effective_user
        welcome = f"""
👋 **Namaste {user.first_name}!** 👋

{WELCOME_MESSAGE}
"""
        keyboard = [
            [InlineKeyboardButton("📢 Proof Channel", callback_data="proof_channel")],
            [InlineKeyboardButton("📞 Contact Support", callback_data="contact_support")],
            [InlineKeyboardButton("📊 Investment Plans", callback_data="investment_plans")],
            [InlineKeyboardButton("❓ Help / FAQ", callback_data="help_faq")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            welcome,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

def back_button():
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ---------- HELP COMMAND ----------
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
📚 **Available Commands:**

/start - Main menu open karein
/help - Help menu
/plans - Investment plans
/support - Contact support
/proof - Proof channel

👇 Neeche buttons use karein:
"""
    keyboard = [
        [InlineKeyboardButton("📢 Proof Channel", callback_data="proof_channel")],
        [InlineKeyboardButton("📞 Contact Support", callback_data="contact_support")],
        [InlineKeyboardButton("📊 Investment Plans", callback_data="investment_plans")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

# ---------- ERROR HANDLER ----------
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error: {context.error}")

# ---------- MAIN ----------
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_error_handler(error_handler)
    
    logger.info("🤖 Investment Bot is starting...")
    print("""
    ╔═══════════════════════════════════╗
    ║   🤖 Investment Bot Started!      ║
    ║   Press Ctrl+C to stop            ║
    ╚═══════════════════════════════════╝
    """)
    
    application.run_polling(allowed_updates=[])

if __name__ == "__main__":
    main()
