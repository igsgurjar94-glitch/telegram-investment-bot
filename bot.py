import os
import json
import logging
import random
import string
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================== CONFIG ====================
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN not found!")
    exit(1)

ADMIN_IDS = [8473800312]  # 🔑 APNI ID YAHAN DALEIN!

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== DATA FILES ====================
for file in ["users.json", "transactions.json", "withdrawals.json"]:
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

# ==================== USER FUNCTIONS ====================
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

def create_user(user_id, username, first_name):
    users = load_json("users.json")
    if str(user_id) not in users:
        users[str(user_id)] = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "main_balance": 0,
            "bonus_balance": 0,
            "locked_balance": 0,
            "total_earned": 0,
            "total_invested": 0,
            "plan": "none",
            "investment_date": None,
            "maturity_date": None,
            "daily_reward": 0,
            "last_claim_date": None,
            "days_claimed": 0,
            "games_played": 0,
            "games_won": 0,
            "referrals": 0,
            "total_withdrawn": 0,
            "pending_withdrawal": 0,
            "joined_at": str(datetime.now())
        }
        save_json("users.json", users)
        return True
    return False

# ==================== PLANS ====================
PLANS = {
    "basic": {"name": "🟢 Basic", "min": 500, "max": 1000, "daily_return": 2, "duration": 30},
    "silver": {"name": "🔵 Silver", "min": 2000, "max": 5000, "daily_return": 2.5, "duration": 30},
    "gold": {"name": "🟡 Gold", "min": 10000, "max": 25000, "daily_return": 3, "duration": 30},
    "platinum": {"name": "🔴 Platinum", "min": 50000, "max": 100000, "daily_return": 4, "duration": 30}
}

# ==================== START ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    create_user(user.id, user.username, user.first_name)
    await main_menu(update, context)

# ==================== MAIN MENU ====================
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = get_user(user.id)
    
    balance = user_data.get('main_balance', 0)
    bonus = user_data.get('bonus_balance', 0)
    plan = user_data.get('plan', 'none')
    plan_name = PLANS.get(plan, {}).get('name', 'No Active Plan') if plan != 'none' else 'No Active Plan'
    
    text = f"""
╔═══════════════════════════════╗
║      🏦 **WELCOME BACK**       ║
║         {user.first_name}       ║
╚═══════════════════════════════╝

📊 **YOUR PORTFOLIO**

┌─────────────────────────────┐
│ 💰 Main Balance  : ₹{balance}   │
│ 🎁 Bonus Balance : ₹{bonus}    │
│ 📈 Active Plan   : {plan_name} │
└─────────────────────────────┘

💡 **What would you like to do?**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    keyboard = [
        [InlineKeyboardButton("💰 INVEST", callback_data="invest"), InlineKeyboardButton("🎁 DAILY", callback_data="daily")],
        [InlineKeyboardButton("🎮 GAME", callback_data="game"), InlineKeyboardButton("📊 WALLET", callback_data="wallet")],
        [InlineKeyboardButton("👥 REFER", callback_data="referral"), InlineKeyboardButton("🏦 WITHDRAW", callback_data="withdraw")],
        [InlineKeyboardButton("📢 PROOF", callback_data="proof"), InlineKeyboardButton("📞 SUPPORT", callback_data="support")]
    ]
    
    if user.id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("⚙️ ADMIN PANEL", callback_data="admin")])
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ==================== BACK ====================
async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await main_menu(update, context)

# ==================== INVEST ====================
async def invest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
╔═══════════════════════════════╗
║      💰 **INVESTMENT PLANS**   ║
╚═══════════════════════════════╝

┌─────────────────────────────┐
│ 🟢 **BASIC PLAN**           │
│ 💵 ₹500 - ₹1,000            │
│ 📈 2% Daily Return          │
│ ⏳ 30 Days                  │
└─────────────────────────────┘

┌─────────────────────────────┐
│ 🔵 **SILVER PLAN**          │
│ 💵 ₹2,000 - ₹5,000          │
│ 📈 2.5% Daily Return        │
│ ⏳ 30 Days                  │
└─────────────────────────────┘

┌─────────────────────────────┐
│ 🟡 **GOLD PLAN**            │
│ 💵 ₹10,000 - ₹25,000        │
│ 📈 3% Daily Return          │
│ ⏳ 30 Days                  │
└─────────────────────────────┘

┌─────────────────────────────┐
│ 🔴 **PLATINUM PLAN**        │
│ 💵 ₹50,000 - ₹1,00,000      │
│ 📈 4% Daily Return          │
│ ⏳ 30 Days                  │
└─────────────────────────────┘

📌 Type: `/invest [plan] [amount]`
Example: `/invest basic 500`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    keyboard = [
        [InlineKeyboardButton("🟢 Basic", callback_data="plan_basic")],
        [InlineKeyboardButton("🔵 Silver", callback_data="plan_silver")],
        [InlineKeyboardButton("🟡 Gold", callback_data="plan_gold")],
        [InlineKeyboardButton("🔴 Platinum", callback_data="plan_platinum")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back")]
    ]
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

# ==================== INVEST PLAN ====================
async def invest_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    plan_name = query.data.replace("plan_", "")
    plan = PLANS.get(plan_name)
    
    if not plan:
        await query.edit_message_text("❌ Invalid plan!")
        return
    
    text = f"""
📊 **{plan['name']} PLAN**

💰 Min: ₹{plan['min']}
💰 Max: ₹{plan['max']}
📈 Daily: {plan['daily_return']}%
⏳ Duration: {plan['duration']} Days

📌 `/invest {plan_name} [amount]`
Example: `/invest {plan_name} 500`
"""
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 BACK", callback_data="invest")]
        ])
    )

# ==================== INVEST COMMAND ====================
async def invest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: `/invest [plan] [amount]`")
        return
    
    plan_name = context.args[0].lower()
    try:
        amount = int(context.args[1])
    except:
        await update.message.reply_text("❌ Enter valid amount!")
        return
    
    plan = PLANS.get(plan_name)
    if not plan:
        await update.message.reply_text("❌ Invalid plan!")
        return
    
    if amount < plan['min'] or amount > plan['max']:
        await update.message.reply_text(f"❌ Amount must be ₹{plan['min']}-₹{plan['max']}")
        return
    
    user_data = get_user(user_id)
    if user_data.get('plan') != 'none':
        await update.message.reply_text("❌ You already have an active investment!")
        return
    
    daily_return = (amount * plan['daily_return']) / 100
    
    update_user(user_id, {
        "main_balance": amount,
        "locked_balance": amount,
        "total_invested": amount,
        "plan": plan_name,
        "daily_reward": daily_return,
        "maturity_date": str(datetime.now() + timedelta(days=plan['duration']))
    })
    
    await update.message.reply_text(
        f"✅ **Investment Successful!**\n\n"
        f"Plan: {plan['name']}\n"
        f"Amount: ₹{amount}\n"
        f"Daily Reward: ₹{daily_return:.0f}",
        parse_mode='Markdown'
    )

# ==================== DAILY REWARD ====================
async def daily_reward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    if user_data.get('plan') == 'none':
        await query.edit_message_text("❌ No active investment!")
        return
    
    last_claim = user_data.get('last_claim_date')
    today = str(datetime.now().date())
    
    if last_claim == today:
        await query.edit_message_text("❌ Already claimed today!")
        return
    
    reward = int(user_data.get('daily_reward', 0))
    main_balance = user_data.get('main_balance', 0)
    days_claimed = user_data.get('days_claimed', 0)
    
    update_user(user_id, {
        "main_balance": main_balance + reward,
        "last_claim_date": today,
        "days_claimed": days_claimed + 1,
        "total_earned": user_data.get('total_earned', 0) + reward
    })
    
    await query.edit_message_text(
        f"🎁 **Daily Reward!**\n\n"
        f"💰 Amount: ₹{reward}\n"
        f"💎 New Balance: ₹{main_balance + reward}",
        parse_mode='Markdown'
    )

# ==================== GAME ====================
async def game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    if user_data.get('main_balance', 0) < 50:
        await query.edit_message_text("❌ Need ₹50 to play!")
        return
    
    context.user_data['game_active'] = True
    context.user_data['secret_number'] = random.randint(1, 10)
    
    await query.edit_message_text(
        "🎮 **Lucky Number Game**\n\n"
        "💰 Entry: ₹50\n"
        "🎯 Win: ₹100\n\n"
        "**Type a number (1-10):**",
        parse_mode='Markdown'
    )

# ==================== CANCEL GAME ====================
async def cancel_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['game_active'] = False
    await query.edit_message_text("✅ Game cancelled!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back")]]))

# ==================== HANDLE GAME ====================
async def handle_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not context.user_data.get('game_active'):
        return
    
    try:
        guess = int(update.message.text)
    except:
        await update.message.reply_text("❌ Send a number!")
        return
    
    if guess < 1 or guess > 10:
        await update.message.reply_text("❌ Number must be 1-10!")
        return
    
    secret = context.user_data.get('secret_number')
    user_data = get_user(user_id)
    main_balance = user_data.get('main_balance', 0)
    
    if guess == secret:
        win_amount = 90
        new_balance = main_balance - 50 + win_amount
        update_user(user_id, {
            "main_balance": new_balance,
            "games_played": user_data.get('games_played', 0) + 1,
            "games_won": user_data.get('games_won', 0) + 1,
            "total_earned": user_data.get('total_earned', 0) + win_amount
        })
        await update.message.reply_text(f"🎉 **YOU WON!**\n\nGuess: {guess}\nSecret: {secret}\n💰 Won: ₹{win_amount}\n💎 Balance: ₹{new_balance}")
    else:
        new_balance = main_balance - 50
        update_user(user_id, {
            "main_balance": new_balance,
            "games_played": user_data.get('games_played', 0) + 1
        })
        await update.message.reply_text(f"❌ **YOU LOST!**\n\nGuess: {guess}\nSecret: {secret}\n💎 Balance: ₹{new_balance}")
    
    context.user_data['game_active'] = False

# ==================== WALLET ====================
async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    text = f"""
📊 **MY WALLET**

💰 Balance: ₹{user_data.get('main_balance', 0)}
🎁 Bonus: ₹{user_data.get('bonus_balance', 0)}
🔒 Locked: ₹{user_data.get('locked_balance', 0)}
📈 Earned: ₹{user_data.get('total_earned', 0)}
💎 Invested: ₹{user_data.get('total_invested', 0)}
🏦 Withdrawn: ₹{user_data.get('total_withdrawn', 0)}
🎮 Games: {user_data.get('games_played', 0)}
🏆 Wins: {user_data.get('games_won', 0)}
👥 Referrals: {user_data.get('referrals', 0)}
"""
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back")]])
    )

# ==================== REFERRAL ====================
async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    text = f"""
👥 **REFER & EARN**

💰 ₹50 per referral!

📤 Your Link:
`https://t.me/{context.bot.username}?start=ref_{user_id}`

💡 Share and earn!
"""
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back")]])
    )

# ==================== WITHDRAW ====================
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    balance = user_data.get('main_balance', 0)
    
    if balance < 100:
        await query.edit_message_text(f"❌ Min ₹100! Balance: ₹{balance}")
        return
    
    await query.edit_message_text(
        f"🏦 **WITHDRAWAL**\n\nBalance: ₹{balance}\nMin: ₹100\nMax: ₹500\nFee: ₹10\n\n📌 `/withdraw [amount]`",
        parse_mode='Markdown'
    )

# ==================== WITHDRAW COMMAND ====================
async def withdraw_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if len(context.args) < 1:
        await update.message.reply_text("❌ Usage: `/withdraw [amount]`")
        return
    
    try:
        amount = int(context.args[0])
    except:
        await update.message.reply_text("❌ Enter valid amount!")
        return
    
    user_data = get_user(user_id)
    balance = user_data.get('main_balance', 0)
    
    if amount < 100:
        await update.message.reply_text("❌ Min ₹100!")
        return
    if amount > 500:
        await update.message.reply_text("❌ Max ₹500!")
        return
    if amount > balance:
        await update.message.reply_text(f"❌ Insufficient! You have ₹{balance}")
        return
    
    net_amount = amount - 10
    
    update_user(user_id, {
        "main_balance": balance - amount,
        "total_withdrawn": user_data.get('total_withdrawn', 0) + net_amount,
        "pending_withdrawal": amount
    })
    
    await update.message.reply_text(
        f"✅ **Withdrawal Request Sent!**\n\n"
        f"Amount: ₹{amount}\nFee: ₹10\nNet: ₹{net_amount}\n⏳ 24-48 hrs",
        parse_mode='Markdown'
    )

# ==================== PROOF ====================
async def proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📢 **PROOF CHANNEL**\n\n✅ Real Payment Proofs\n✅ Daily Payouts\n\n📌 [@your_channel](https://t.me/your_channel)",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back")]])
    )

# ==================== SUPPORT ====================
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📞 **SUPPORT**\n\n👤 Admin: @your_admin\n📧 Email: support@company.com\n⏰ 24/7 Available",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back")]])
    )

# ==================== ADMIN PANEL ====================
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await query.edit_message_text("❌ Access Denied!")
        return
    
    users = load_json("users.json")
    withdrawals = load_json("withdrawals.json")
    
    total_users = len(users)
    total_invested = sum(u.get('total_invested', 0) for u in users.values())
    total_earned = sum(u.get('total_earned', 0) for u in users.values())
    total_withdrawn = sum(u.get('total_withdrawn', 0) for u in users.values())
    pending = len([w for w in withdrawals.values() if w.get('status') == 'pending'])
    
    text = f"""
╔═══════════════════════════════╗
║     ⚙️ **ADMIN PANEL**          ║
╚═══════════════════════════════╝

┌─────────────────────────────┐
│ 👥 Total Users  : {total_users}     │
│ 💰 Total Invested: ₹{total_invested} │
│ 💎 Total Earned : ₹{total_earned}  │
│ 🏦 Total Withdrawn: ₹{total_withdrawn} │
│ ⏳ Pending       : {pending}        │
└─────────────────────────────┘

📌 **Admin Commands:**
• /stats - Bot Statistics
• /broadcast [msg] - Send to all
• /approve [id] - Approve WD

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 VIEW USERS", callback_data="admin_users")],
            [InlineKeyboardButton("📢 SEND BROADCAST", callback_data="admin_broadcast")],
            [InlineKeyboardButton("⏳ PENDING WITHDRAWALS", callback_data="admin_pending")],
            [InlineKeyboardButton("🔙 BACK", callback_data="back")]
        ])
    )

# ==================== ADMIN USERS ====================
async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await query.edit_message_text("❌ Access Denied!")
        return
    
    users = load_json("users.json")
    
    if not users:
        text = "📊 No users found!"
    else:
        text = f"📊 ALL USERS ({len(users)})\n\n"
        count = 0
        for uid, data in list(users.items()):
            count += 1
            text += f"{count}. {data.get('first_name', 'Unknown')} (@{data.get('username', 'N/A')})\n"
            text += f"   💰 ₹{data.get('main_balance', 0)} | 📈 {data.get('plan', 'None')}\n\n"
            if count >= 20:
                text += f"... and {len(users) - 20} more users"
        
