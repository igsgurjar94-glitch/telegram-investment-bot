import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

USERS_FILE = "users.json"

def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def count_active_users():
    users = load_users()
    today = str(datetime.now().date())
    count = 0
    for uid, data in users.items():
        if data.get("last_active", "").startswith(today):
            count += 1
    return count

# ==================== SHOW ADMIN PANEL ====================
async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin Panel Show Karein"""
    query = update.callback_query
    user = update.effective_user
    
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
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== VIEW USERS ====================
async def admin_view_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View all users"""
    query = update.callback_query
    users = load_users()
    
    if not users:
        text = "📊 **No users found!**"
    else:
        text = f"📊 **Total Users:** {len(users)}\n\n"
        count = 0
        for uid, data in list(users.items()):
            count += 1
            text += f"{count}. {data.get('first_name', 'Unknown')} (@{data.get('username', 'N/A')})\n"
            if count >= 20:
                text += f"\n... aur {len(users) - 20} users aur hain"
                break
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_back")]
    ]
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== BROADCAST ====================
async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start broadcast mode"""
    query = update.callback_query
    context.user_data['broadcast_mode'] = True
    
    keyboard = [
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_broadcast")]
    ]
    
    await query.edit_message_text(
        "📢 **Broadcast Mode Activated!**\n\n"
        "Message likhein jo aap sabhi users ko bhejna chahte hain.\n\n"
        "⚠️ Ye message **ALL USERS** ko jayega!\n\n"
        "❌ Cancel karne ke liye /cancel type karein.",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== STATS ====================
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics"""
    query = update.callback_query
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
• Started: {datetime.now().strftime('%Y-%m-%d')}

🔧 **System:**
• Python: 3.10
• Library: python-telegram-bot
"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_back")]
    ]
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== CANCEL BROADCAST ====================
async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel broadcast"""
    query = update.callback_query
    context.user_data['broadcast_mode'] = False
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_back")]
    ]
    
    await query.edit_message_text(
        "✅ Broadcast cancelled!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== HANDLE BROADCAST MESSAGE ====================
async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send broadcast message to all users"""
    user = update.effective_user
    
    if not context.user_data.get('broadcast_mode'):
        return
    
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
        except:
            failed += 1
    
    await status_msg.edit_text(
        f"✅ **Broadcast Complete!**\n\n"
        f"📤 Sent: {sent}\n"
        f"❌ Failed: {failed}\n"
        f"👥 Total: {total}"
    )
    context.user_data['broadcast_mode'] = False
