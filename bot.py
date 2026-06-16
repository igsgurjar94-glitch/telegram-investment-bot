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

# Admin IDs (Yahan apna Telegram User ID daalein)
ADMIN_IDS = [8473800312]  # 🔑 APNA TELEGRAM USER ID YAHAN DALEIN!

# Users data store karne ke liye
USERS_FILE = "users.json"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== USER MANAGEMENT ====================
def load_users():
    """Users ko file se load karein"""
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    """Users ko file mein save karein"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def add_user(user_id, username, first_name):
    """Naya user add karein"""
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {
            "id": user_id,
            "username": username,
            "first_name": first_name,
            "joined_at": str(datetime.now()),
            "last_active": str(datetime.now())
        }
        save_users(users)
        return True
    else:
        # Update last active
        users[str(user_id)]["last_active"] = str(datetime.now())
        save_users(users)
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

🔽 **Neeche options mein se choose karein:** 🔽
"""

# ==================== START COMMAND ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # User ko database mein save karein
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
    
    # Agar admin hai toh admin panel button add karein
    if user.id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")])
    
    await update.message.reply_text(
        welcome,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== ADMIN PANEL ====================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin Panel Show Karein"""
    user = update.effective_user
    
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Aap admin nahi hain!")
        return
    
    users = load_users()
    total_users = len(users)
    
    text = f"""
⚙️ **ADMIN PANEL** ⚙️

📊 **Statistics:**
• Total Users: {total_users}
• Active Today: {count_active_users()}
• Bot Status: ✅ Online

📌 **Select an option below:**
"""
    
    keyboard = [
        [InlineKeyboardButton("📊 View All Users", callback_data="admin_users")],
        [InlineKeyboardButton("📢 Send Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📈 Bot Stats", callback_data="admin_stats")],
        [InlineKeyboardButton("🔙 Back to Main", callback_data="back")]
    ]
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def count_active_users():
    """Aaj active users count karein"""
    users = load_users()
    today = str(datetime.now().date())
    count = 0
    for uid, data in users.items():
        if data.get("last_active", "").startswith(today):
            count += 1
    return count

# ==================== ADMIN BUTTON HANDLERS ====================
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel ke buttons handle karein"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    if user.id not in ADMIN_IDS:
        await query.edit_message_text("❌ Aap admin nahi hain!")
        return
    
    data = query.data
    
    if data == "admin_users":
        # Users list dikhayein
        users = load_users()
        if not users:
            text = "📊 **No users found!**"
        else:
            text = f"📊 **Total Users:** {len(users)}\n\n"
            for uid, data in list(users.items())[:10]:  # Sirf 10 users dikhayein
                text += f"• {data.get('first_name', 'Unknown')} (@{data.get('username', 'N/A')})\n"
            if len(users) > 10:
                text += f"\n... aur {len(users) - 10} users aur hain"
        
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=admin_back_button()
        )
    
    elif data == "admin_broadcast":
        # Broadcast mode - user se message maangein
        context.user_data['broadcast_mode'] = True
        await query.edit_message_text(
            "📢 **Broadcast Mode Activated!**\n\n"
            "Message likhein jo aap sabhi users ko bhejna chahte hain.\n\n"
            "⚠️ Ye message **ALL USERS** ko jayega! (Kuch der lag sakti hai)\n\n"
            "❌ Cancel karne ke liye /cancel type karein.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_broadcast")]
            ])
        )
    
    elif data == "cancel_broadcast":
        context.user_data['broadcast_mode'] = False
        await query.edit_message_text(
            "✅ Broadcast cancelled!",
            reply_markup=admin_back_button()
        )
    
    elif data == "admin_stats":
        # Stats dikhayein
        users = load_users()
        total = len(users)
        active = count_active_users()
        
        text = f"""
📈 **BOT STATISTICS**

📊 **Users:**
• Total: {total}
• Active Today: {active}

📅 **Bot Info:**
• Status: ✅ Online
• Uptime: 24/7
• Started: {datetime.now().strftime('%Y-%m-%d')}

🔧 **System:**
• Python: 3.10
• Library: python-telegram-bot
"""
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=admin_back_button()
        )

def admin_back_button():
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ==================== BROADCAST FUNCTION ====================
async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message bhejne ke liye"""
    user = update.effective_user
    
    if user.id not in ADMIN_IDS:
        return
    
    if context.user_data.get('broadcast_mode'):
        message_text = update.message.text
        
        users = load_users()
        total = len(users)
        sent = 0
        failed = 0
        
        status_msg = await update.message.reply_text(
            f"📢 **Sending broadcast to {total} users...**\nPlease wait ⏳"
        )
        
        for uid, data in users.items():
            try:
                await context.bot.send_message(
                    chat_id=int(uid),
                    text=f"📢 **Announcement** 📢\n\n{message_text}",
                    parse_mode='Markdown'
                )
                sent += 1
            except Exception as e:
                failed += 1
                logger.error(f"Failed to send to {uid}: {e}")
        
        await status_msg.edit_text(
            f"✅ **Broadcast Complete!**\n\n"
            f"📤 Sent: {sent}\n"
            f"❌ Failed: {failed}\n"
            f"👥 Total: {total}"
        )
        
        context.user_data['broadcast_mode'] = False

# ==================== CANCEL COMMAND ====================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel broadcast mode"""
    context.user_data['broadcast_mode'] = False
    await update.message.reply_text("✅ Cancelled!")

# ==================== BUTTON HANDLERS ====================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    data = query.data
    
    # Admin panel callbacks
    if data == "admin_panel":
        await admin_panel(update, context)
        return
    
    if data == "admin_back":
        await admin_panel(update, context)
        return
    
    if data.startswith("admin_"):
        await admin_callback(update, context)
        return
    
    # Normal user callbacks
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

# ==================== HELP COMMAND ====================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
📚 **Commands:**

/start - Main menu
/help - Help
/status - Bot status

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

# ==================== STATUS COMMAND ====================
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

# ==================== ERROR HANDLER ====================
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
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("cancel", cancel))
    
    # Callback handler for buttons
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Message handler for broadcast
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    print("✅ Bot is running! Press Ctrl+C to stop.")
    print(f"👑 Admin Panel ready! Admin IDs: {ADMIN_IDS}")
    app.run_polling(allowed_updates=[])

if __name__ == "__main__":
    main()
