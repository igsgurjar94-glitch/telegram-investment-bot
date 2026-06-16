import os
import json
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from admin_handlers import (
    show_admin_panel,
    admin_view_users,
    admin_broadcast,
    admin_stats,
    cancel_broadcast,
    handle_broadcast_message,
    load_users,
    count_active_users
)

# ==================== CONFIG ====================
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN not found!")
    exit(1)

# 🔑 APNA TELEGRAM USER ID YAHAN DALEIN!
ADMIN_IDS = [8473800312]  # <-- Apni ID daalein

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== WELCOME MESSAGE ====================
WELCOME_MESSAGE = """
🚀 **WELCOME TO [SHREE GANESH BAZAR]** 🚀

💰 **Earn Money Online With Us!** 💰

Namaste! 🙏 Aapka swagat hai!

✅ 100% Secure & Trusted
📈 Minimum Investment: ₹500/-
💵 Daily Returns: 10% - 30%
🏆 Referral Bonus: 5%

🔽 **Neeche options mein se choose karein:** 🔽
"""

# ==================== ADD USER ====================
def add_user(user_id, username, first_name):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {
            "id": user_id,
            "username": username,
            "first_name": first_name,
            "joined_at": str(datetime.now()),
            "last_active": str(datetime.now())
        }
        with open("users.json", 'w') as f:
            json.dump(users, f, indent=2)
        return True
    else:
        users[str(user_id)]["last_active"] = str(datetime.now())
        with open("users.json", 'w') as f:
            json.dump(users, f, indent=2)
        return False

# ==================== START ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username, user.first_name)
    
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
    
    if user.id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")])
    
    await update.message.reply_text(
        welcome,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== BUTTON CALLBACK ====================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    data = query.data
    
    # ===== ADMIN PANEL CALLBACKS =====
    if data == "admin_panel":
        if user.id in ADMIN_IDS:
            await show_admin_panel(update, context)
        else:
            await query.edit_message_text("❌ Aap admin nahi hain!")
        return
    
    if data == "admin_back":
        if user.id in ADMIN_IDS:
            await show_admin_panel(update, context)
        return
    
    if data == "admin_users":
        if user.id in ADMIN_IDS:
            await admin_view_users(update, context)
        return
    
    if data == "admin_broadcast":
        if user.id in ADMIN_IDS:
            await admin_broadcast(update, context)
        return
    
    if data == "admin_stats":
        if user.id in ADMIN_IDS:
            await admin_stats(update, context)
        return
    
    if data == "cancel_broadcast":
        if user.id in ADMIN_IDS:
            await cancel_broadcast(update, context)
        return
    
    # ===== NORMAL USER CALLBACKS =====
    if data == "proof":
        text = """
📢 **PROOF CHANNEL** 📢

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

🔄 /start - Dobara start karein
"""
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=back_button()
        )
    
    elif data == "back":
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
        if user.id in ADMIN_IDS:
            keyboard.append([InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")])
        
        await query.edit_message_text(
            welcome,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

def back_button():
    keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back")]]
    return InlineKeyboardMarkup(keyboard)

# ==================== HELP ====================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
📚 **Commands:**

/start - Main menu
/help - Help
/status - Bot status
/cancel - Cancel broadcast
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
📅 Active Today: {count_active_users()}
✅ Status: Online

⚡️ Bot is working perfectly!
"""
    await update.message.reply_text(text, parse_mode='Markdown')

# ==================== CANCEL ====================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['broadcast_mode'] = False
    await update.message.reply_text("✅ Cancelled!")

# ==================== ERROR ====================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ Kuch technical issue ho gaya! Support se contact karein."
        )

# ==================== MAIN ====================
def main():
    print("🤖 Starting Investment Bot with Admin Panel...")
    print(f"✅ Bot Token: {'Found ✅' if BOT_TOKEN else 'Not Found ❌'}")
    print(f"👑 Admins: {ADMIN_IDS}")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast_message))
    app.add_error_handler(error_handler)
    
    print("✅ Bot is running!")
    app.run_polling(allowed_updates=[])

if __name__ == "__main__":
    main()
