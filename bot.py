import os
import json
import logging
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================== CONFIG ====================
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN not found! Set BOT_TOKEN in environment variables.")
    exit(1)

ADMIN_IDS = [8473800312]  # 🔑 APNI ID YAHAN DALEIN!

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== DATA FILES ====================
for file in ["users.json", "withdrawals.json"]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump({}, f)

def load_json(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

def get_user(user_id):
    users = load_json("users.json")
    return users.get(str(user_id))

def update_user(user_id, data):
    users = load_json("users.json")
    if str(user_id) in users:
        users[str(user_id)].update(data)
        save_json("users.json", users)
        return True
    return False

def create_user(user_id, username, first_name, referrer_id=None):
    users = load_json("users.json")
    if str(user_id) not in users:
        users[str(user_id)] = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "balance": 0,
            "invested": 0,
            "plan": "none",
            "daily_reward": 0,
            "last_claim": None,
            "days_claimed": 0,
            "games_played": 0,
            "games_won": 0,
            "referrals": 0,
            "withdrawn": 0,
            "joined_at": str(datetime.now())
        }
        save_json("users.json", users)
        
        if referrer_id:
            ref_user = get_user(referrer_id)
            if ref_user:
                update_user(referrer_id, {
                    "balance": ref_user.get('balance', 0) + 50,
                    "referrals": ref_user.get('referrals', 0) + 1
                })
        return True
    return False

# ==================== PLANS ====================
PLANS = {
    "basic": {"name": "Basic", "min": 500, "max": 1000, "daily": 2, "emoji": "🟢"},
    "silver": {"name": "Silver", "min": 2000, "max": 5000, "daily": 2.5, "emoji": "🔵"},
    "gold": {"name": "Gold", "min": 10000, "max": 25000, "daily": 3, "emoji": "🟡"},
    "platinum": {"name": "Platinum", "min": 50000, "max": 100000, "daily": 4, "emoji": "🔴"}
}

# ==================== START ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    referrer_id = None
    if context.args and context.args[0].startswith('ref_'):
        try:
            referrer_id = int(context.args[0].replace('ref_', ''))
        except:
            pass
    
    create_user(user.id, user.username, user.first_name, referrer_id)
    
    user_data = get_user(user.id)
    balance = user_data.get('balance', 0)
    
    text = f"""
🏦 **WELCOME {user.first_name}!**

💰 **Balance:** ₹{balance}

⚡ *Select an option below:*
"""
    
    keyboard = [
        [InlineKeyboardButton("💼 Invest Now", callback_data="invest")],
        [InlineKeyboardButton("🎁 Daily Bonus", callback_data="daily")],
        [InlineKeyboardButton("🎯 Play & Win", callback_data="game")],
        [InlineKeyboardButton("📊 My Wallet", callback_data="wallet")],
        [InlineKeyboardButton("👥 Invite Friends", callback_data="refer")],
        [InlineKeyboardButton("💳 Withdraw Funds", callback_data="withdraw")]
    ]
    
    if user.id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin")])
    
    await update.message.reply_text(
        text, 
        parse_mode='Markdown', 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== BACK ====================
async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_data = get_user(user.id)
    balance = user_data.get('balance', 0)
    
    text = f"""
🏦 **MAIN MENU**

💰 **Balance:** ₹{balance}

⚡ *Choose an option:*
"""
    
    keyboard = [
        [InlineKeyboardButton("💼 Invest Now", callback_data="invest")],
        [InlineKeyboardButton("🎁 Daily Bonus", callback_data="daily")],
        [InlineKeyboardButton("🎯 Play & Win", callback_data="game")],
        [InlineKeyboardButton("📊 My Wallet", callback_data="wallet")],
        [InlineKeyboardButton("👥 Invite Friends", callback_data="refer")],
        [InlineKeyboardButton("💳 Withdraw Funds", callback_data="withdraw")]
    ]
    
    if user.id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin")])
    
    await query.edit_message_text(
        text, 
        parse_mode='Markdown', 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== INVEST ====================
async def invest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
💰 **INVESTMENT PLANS**

📊 *Choose your plan:*

🟢 **Basic** — ₹500–1,000 • 2% daily
🔵 **Silver** — ₹2,000–5,000 • 2.5% daily  
🟡 **Gold** — ₹10,000–25,000 • 3% daily
🔴 **Platinum** — ₹50,000–1,00,000 • 4% daily

📌 `/invest [plan] [amount]`
*Example:* `/invest basic 500`
"""
    
    keyboard = [
        [InlineKeyboardButton("🟢 Basic • ₹500 • 2%", callback_data="plan_basic")],
        [InlineKeyboardButton("🔵 Silver • ₹2,000 • 2.5%", callback_data="plan_silver")],
        [InlineKeyboardButton("🟡 Gold • ₹10,000 • 3%", callback_data="plan_gold")],
        [InlineKeyboardButton("🔴 Platinum • ₹50,000 • 4%", callback_data="plan_platinum")],
        [InlineKeyboardButton("⬅️ Go Back", callback_data="back")]
    ]
    
    await query.edit_message_text(
        text, 
        parse_mode='Markdown', 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def invest_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    plan_name = query.data.replace("plan_", "")
    plan = PLANS.get(plan_name)
    
    if not plan:
        await query.edit_message_text("❌ Invalid plan!")
        return
    
    text = f"""
{plan['emoji']} **{plan['name']} PLAN**

💰 **Min:** ₹{plan['min']}
💰 **Max:** ₹{plan['max']}
📈 **Daily:** {plan['daily']}%

📌 `/invest {plan_name} [amount]`
"""
    
    await query.edit_message_text(
        text, 
        parse_mode='Markdown', 
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Plans", callback_data="invest")]])
    )

async def invest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if len(context.args) < 2:
        await update.message.reply_text("📌 Usage: /invest [plan] [amount]")
        return
    
    plan_name = context.args[0].lower()
    try:
        amount = int(context.args[1])
    except:
        await update.message.reply_text("❌ Enter valid amount!")
        return
    
    plan = PLANS.get(plan_name)
    if not plan:
        await update.message.reply_text("❌ Invalid plan! Use: basic, silver, gold, platinum")
        return
    
    if amount < plan['min'] or amount > plan['max']:
        await update.message.reply_text(f"❌ Amount must be ₹{plan['min']}-₹{plan['max']}")
        return
    
    daily_return = (amount * plan['daily']) / 100
    
    update_user(user_id, {
        "balance": amount,
        "invested": amount,
        "plan": plan_name,
        "daily_reward": daily_return,
        "last_claim": None,
        "days_claimed": 0
    })
    
    await update.message.reply_text(
        f"✅ **Investment Successful!**\n\n"
        f"📌 **Plan:** {plan['name']}\n"
        f"💰 **Amount:** ₹{amount}\n"
        f"📈 **Daily:** ₹{daily_return:.0f}",
        parse_mode='Markdown'
    )

# ==================== DAILY REWARD ====================
async def daily_reward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    if user_data.get('plan') == 'none':
        await query.edit_message_text(
            "❌ **No active investment!**\n\nInvest first to earn daily rewards.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back")]])
        )
        return
    
    today = str(datetime.now().date())
    if user_data.get('last_claim') == today:
        await query.edit_message_text(
            "⏳ **Already claimed today!**\n\nCome back tomorrow.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back")]])
        )
        return
    
    reward = int(user_data.get('daily_reward', 0))
    if reward == 0:
        await query.edit_message_text(
            "❌ No reward available!",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back")]])
        )
        return
    
    balance = user_data.get('balance', 0)
    days = user_data.get('days_claimed', 0) + 1
    
    update_user(user_id, {
        "balance": balance + reward,
        "last_claim": today,
        "days_claimed": days
    })
    
    await query.edit_message_text(
        f"🎁 **Daily Bonus Claimed!**\n\n"
        f"💰 **Amount:** ₹{reward}\n"
        f"💎 **New Balance:** ₹{balance + reward}\n"
        f"📅 **Day:** {days}",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back")]])
    )

# ==================== GAME ====================
async def game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    if user_data.get('balance', 0) < 50:
        await query.edit_message_text(
            "❌ **Need ₹50 to play!**",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back")]])
        )
        return
    
    context.user_data['game_active'] = True
    context.user_data['secret_number'] = random.randint(1, 10)
    
    await query.edit_message_text(
        "🎮 **Lucky Number Game**\n\n"
        "💰 **Entry:** ₹50\n"
        "🎯 **Win:** ₹100\n\n"
        "📌 Type a number (1-10):",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel_game")]])
    )

async def cancel_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['game_active'] = False
    await query.edit_message_text(
        "❌ Game cancelled!",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back")]])
    )

async def handle_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not context.user_data.get('game_active'):
        return
    
    try:
        guess = int(update.message.text)
    except:
        await update.message.reply_text("❌ Please send a valid number!")
        return
    
    if guess < 1 or guess > 10:
        await update.message.reply_text("❌ Number must be between 1-10!")
        return
    
    secret = context.user_data.get('secret_number')
    user_data = get_user(user_id)
    balance = user_data.get('balance', 0)
    
    if balance < 50:
        await update.message.reply_text("❌ Insufficient balance!")
        context.user_data['game_active'] = False
        return
    
    if guess == secret:
        win = 90
        new_balance = balance - 50 + win
        update_user(user_id, {
            "balance": new_balance,
            "games_played": user_data.get('games_played', 0) + 1,
            "games_won": user_data.get('games_won', 0) + 1
        })
        await update.message.reply_text(
            f"🎉 **YOU WON!**\n\n"
            f"🔢 Your Guess: {guess}\n"
            f"🤫 Secret Number: {secret}\n"
            f"💰 **Won:** ₹{win}\n"
            f"💎 **Balance:** ₹{new_balance}",
            parse_mode='Markdown'
        )
    else:
        new_balance = balance - 50
        update_user(user_id, {
            "balance": new_balance,
            "games_played": user_data.get('games_played', 0) + 1
        })
        await update.message.reply_text(
            f"❌ **YOU LOST!**\n\n"
            f"🔢 Your Guess: {guess}\n"
            f"🤫 Secret Number: {secret}\n"
            f"💎 **Balance:** ₹{new_balance}",
            parse_mode='Markdown'
        )
    
    context.user_data['game_active'] = False

# ==================== WALLET ====================
async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    text = f"""
📊 **MY WALLET**

━━━━━━━━━━━━━━━━━━
💰 **Balance:** ₹{user_data.get('balance', 0)}
💎 **Invested:** ₹{user_data.get('invested', 0)}
🏦 **Withdrawn:** ₹{user_data.get('withdrawn', 0)}
🎮 **Games Played:** {user_data.get('games_played', 0)}
🏆 **Games Won:** {user_data.get('games_won', 0)}
👥 **Referrals:** {user_data.get('referrals', 0)}
📅 **Plan:** {user_data.get('plan', 'None').title()}
━━━━━━━━━━━━━━━━━━
"""
    
    keyboard = [
        [InlineKeyboardButton("🔄 Refresh", callback_data="wallet")],
        [InlineKeyboardButton("⬅️ Main Menu", callback_data="back")]
    ]
    
    await query.edit_message_text(
        text, 
        parse_mode='Markdown', 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== REFER ====================
async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    bot_username = context.bot.username
    
    text = f"""
👥 **REFER & EARN**

💰 **₹50 per referral!**

📤 *Your Referral Link:*
`https://t.me/{bot_username}?start=ref_{user_id}`

⭐ Share this link with friends and earn ₹50 when they join!
"""
    
    keyboard = [
        [InlineKeyboardButton("📋 Copy Link", callback_data="copy_link")],
        [InlineKeyboardButton("⬅️ Main Menu", callback_data="back")]
    ]
    
    await query.edit_message_text(
        text, 
        parse_mode='Markdown', 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== WITHDRAW ====================
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    balance = user_data.get('balance', 0)
    
    if balance < 100:
        await query.edit_message_text(
            f"🚫 **Min ₹100 required!**\n\nYour Balance: ₹{balance}",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back")]])
        )
        return
    
    text = f"""
💳 **WITHDRAWAL**

━━━━━━━━━━━━━━━━━━
💰 **Balance:** ₹{balance}
💵 **Min:** ₹100
💵 **Max:** ₹500
💸 **Fee:** ₹10
━━━━━━━━━━━━━━━━━━

📌 `/withdraw [amount]`
*Example:* `/withdraw 200`
"""
    
    keyboard = [
        [InlineKeyboardButton("⬅️ Main Menu", callback_data="back")]
    ]
    
    await query.edit_message_text(
        text, 
        parse_mode='Markdown', 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def withdraw_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = update.effective_user
    
    if len(context.args) < 1:
        await update.message.reply_text("📌 Usage: /withdraw [amount]")
        return
    
    try:
        amount = int(context.args[0])
    except:
        await update.message.reply_text("❌ Enter valid amount!")
        return
    
    user_data = get_user(user_id)
    balance = user_data.get('balance', 0)
    
    if amount < 100:
        await update.message.reply_text("❌ Min ₹100!")
        return
    if amount > 500:
        await update.message.reply_text("❌ Max ₹500!")
        return
    if amount > balance:
        await update.message.reply_text(f"❌ Insufficient! You have ₹{balance}")
        return
    
    net = amount - 10
    
    wds = load_json("withdrawals.json")
    wid = str(int(datetime.now().timestamp()))
    wds[wid] = {
        "user_id": user_id,
        "first_name": user.first_name,
        "username": user.username,
        "amount": amount,
        "net": net,
        "status": "pending",
        "requested_at": str(datetime.now())
    }
    save_json("withdrawals.json", wds)
    
    update_user(user_id, {
        "balance": balance - amount,
        "withdrawn": user_data.get('withdrawn', 0) + net
    })
    
    await update.message.reply_text(
        f"✅ **Withdrawal Request Sent!**\n\n"
        f"💰 **Amount:** ₹{amount}\n"
        f"💸 **Fee:** ₹10\n"
        f"💎 **Net:** ₹{net}\n"
        f"⏳ **24-48 hrs**\n"
        f"🆔 **ID:** `{wid}`",
        parse_mode='Markdown'
    )

# ==================== ADMIN ====================
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await query.edit_message_text("🚫 **Access Denied!**", parse_mode='Markdown')
        return
    
    users = load_json("users.json")
    total = len(users)
    invested = sum(u.get('invested', 0) for u in users.values())
    
    text = f"""
⚙️ **ADMIN CONTROL PANEL**

👥 **Total Users:** {total}
💰 **Total Invested:** ₹{invested}

📌 *Admin Commands:*
• `/stats` — View statistics
• `/broadcast [msg]` — Send broadcast
• `/approve [id]` — Approve withdrawal
"""
    
    keyboard = [
        [InlineKeyboardButton("👥 User Management", callback_data="admin_users")],
        [InlineKeyboardButton("📢 Send Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("⏳ Pending Withdrawals", callback_data="admin_pending")],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back")]
    ]
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await query.edit_message_text("🚫 **Access Denied!**", parse_mode='Markdown')
        return
    
    users = load_json("users.json")
    text = f"👥 **USERS** ({len(users)})\n\n"
    count = 0
    for uid, data in users.items():
        count += 1
        text += f"{count}. {data.get('first_name')} | ₹{data.get('balance', 0)}\n"
        if count >= 20:
            break
    
    await query.edit_message_text(
        text, 
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin")]])
    )

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback
