import os
import json
import logging
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================== CONFIG ====================
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN not found!")
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

def create_user(user_id, username, first_name):
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
        return True
    return False

# ==================== PLANS ====================
PLANS = {
    "basic": {"name": "Basic", "min": 500, "max": 1000, "daily": 2},
    "silver": {"name": "Silver", "min": 2000, "max": 5000, "daily": 2.5},
    "gold": {"name": "Gold", "min": 10000, "max": 25000, "daily": 3},
    "platinum": {"name": "Platinum", "min": 50000, "max": 100000, "daily": 4}
}

# ==================== START ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    create_user(user.id, user.username, user.first_name)
    
    user_data = get_user(user.id)
    balance = user_data.get('balance', 0)
    
    text = f"""
🏦 WELCOME {user.first_name}!

💰 Balance: ₹{balance}

📌 Choose an option:
"""
    
    keyboard = [
        [InlineKeyboardButton("💰 Invest", callback_data="invest")],
        [InlineKeyboardButton("🎁 Daily Reward", callback_data="daily")],
        [InlineKeyboardButton("🎮 Play Game", callback_data="game")],
        [InlineKeyboardButton("📊 Wallet", callback_data="wallet")],
        [InlineKeyboardButton("👥 Refer", callback_data="refer")],
        [InlineKeyboardButton("🏦 Withdraw", callback_data="withdraw")]
    ]
    
    if user.id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("⚙️ Admin", callback_data="admin")])
    
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

# ==================== BACK ====================
async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_data = get_user(user.id)
    balance = user_data.get('balance', 0)
    
    text = f"""
🏦 MAIN MENU

💰 Balance: ₹{balance}

📌 Choose an option:
"""
    
    keyboard = [
        [InlineKeyboardButton("💰 Invest", callback_data="invest")],
        [InlineKeyboardButton("🎁 Daily Reward", callback_data="daily")],
        [InlineKeyboardButton("🎮 Play Game", callback_data="game")],
        [InlineKeyboardButton("📊 Wallet", callback_data="wallet")],
        [InlineKeyboardButton("👥 Refer", callback_data="refer")],
        [InlineKeyboardButton("🏦 Withdraw", callback_data="withdraw")]
    ]
    
    if user.id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("⚙️ Admin", callback_data="admin")])
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

# ==================== INVEST ====================
async def invest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
💰 INVESTMENT PLANS

| Plan | Min | Daily % |
|------|-----|---------|
| Basic | ₹500 | 2% |
| Silver | ₹2,000 | 2.5% |
| Gold | ₹10,000 | 3% |
| Platinum | ₹50,000 | 4% |

📌 /invest [plan] [amount]
Example: /invest basic 500
"""
    
    keyboard = [
        [InlineKeyboardButton("Basic ₹500", callback_data="plan_basic")],
        [InlineKeyboardButton("Silver ₹2,000", callback_data="plan_silver")],
        [InlineKeyboardButton("Gold ₹10,000", callback_data="plan_gold")],
        [InlineKeyboardButton("Platinum ₹50,000", callback_data="plan_platinum")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ]
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def invest_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    plan_name = query.data.replace("plan_", "")
    plan = PLANS.get(plan_name)
    
    if not plan:
        await query.edit_message_text("Invalid plan!")
        return
    
    text = f"""
📊 {plan['name']} PLAN

💰 Min: ₹{plan['min']}
💰 Max: ₹{plan['max']}
📈 Daily: {plan['daily']}%

📌 /invest {plan_name} [amount]
"""
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="invest")]]))

async def invest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /invest [plan] [amount]")
        return
    
    plan_name = context.args[0].lower()
    try:
        amount = int(context.args[1])
    except:
        await update.message.reply_text("Enter valid amount!")
        return
    
    plan = PLANS.get(plan_name)
    if not plan:
        await update.message.reply_text("Invalid plan!")
        return
    
    if amount < plan['min'] or amount > plan['max']:
        await update.message.reply_text(f"Amount must be ₹{plan['min']}-₹{plan['max']}")
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
        f"✅ Investment Successful!\n\n"
        f"Plan: {plan['name']}\n"
        f"Amount: ₹{amount}\n"
        f"Daily: ₹{daily_return:.0f}",
        parse_mode='Markdown'
    )

# ==================== DAILY REWARD ====================
async def daily_reward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    if user_data.get('plan') == 'none':
        await query.edit_message_text("No active investment!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))
        return
    
    today = str(datetime.now().date())
    if user_data.get('last_claim') == today:
        await query.edit_message_text("Already claimed today!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))
        return
    
    reward = int(user_data.get('daily_reward', 0))
    if reward == 0:
        await query.edit_message_text("No reward available!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))
        return
    
    balance = user_data.get('balance', 0)
    days = user_data.get('days_claimed', 0) + 1
    
    update_user(user_id, {
        "balance": balance + reward,
        "last_claim": today,
        "days_claimed": days
    })
    
    await query.edit_message_text(
        f"🎁 Daily Reward!\n\n"
        f"💰 Amount: ₹{reward}\n"
        f"💎 New Balance: ₹{balance + reward}\n"
        f"📅 Day: {days}",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]])
    )

# ==================== GAME ====================
async def game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    if user_data.get('balance', 0) < 50:
        await query.edit_message_text("Need ₹50 to play!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))
        return
    
    context.user_data['game_active'] = True
    context.user_data['secret_number'] = random.randint(1, 10)
    
    await query.edit_message_text(
        "🎮 Lucky Number Game\n\n"
        "💰 Entry: ₹50\n"
        "🎯 Win: ₹100\n\n"
        "Type a number (1-10):",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel_game")]])
    )

async def cancel_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['game_active'] = False
    await query.edit_message_text("Game cancelled!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))

async def handle_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not context.user_data.get('game_active'):
        return
    
    try:
        guess = int(update.message.text)
    except:
        await update.message.reply_text("Send a number!")
        return
    
    if guess < 1 or guess > 10:
        await update.message.reply_text("Number must be 1-10!")
        return
    
    secret = context.user_data.get('secret_number')
    user_data = get_user(user_id)
    balance = user_data.get('balance', 0)
    
    if guess == secret:
        win = 90
        new_balance = balance - 50 + win
        update_user(user_id, {
            "balance": new_balance,
            "games_played": user_data.get('games_played', 0) + 1,
            "games_won": user_data.get('games_won', 0) + 1
        })
        await update.message.reply_text(
            f"🎉 YOU WON!\n\n"
            f"Guess: {guess}\n"
            f"Secret: {secret}\n"
            f"💰 Won: ₹{win}\n"
            f"💎 Balance: ₹{new_balance}",
            parse_mode='Markdown'
        )
    else:
        new_balance = balance - 50
        update_user(user_id, {
            "balance": new_balance,
            "games_played": user_data.get('games_played', 0) + 1
        })
        await update.message.reply_text(
            f"❌ YOU LOST!\n\n"
            f"Guess: {guess}\n"
            f"Secret: {secret}\n"
            f"💎 Balance: ₹{new_balance}",
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
📊 MY WALLET

💰 Balance: ₹{user_data.get('balance', 0)}
💎 Invested: ₹{user_data.get('invested', 0)}
🏦 Withdrawn: ₹{user_data.get('withdrawn', 0)}
🎮 Games: {user_data.get('games_played', 0)}
🏆 Wins: {user_data.get('games_won', 0)}
👥 Referrals: {user_data.get('referrals', 0)}
📅 Plan: {user_data.get('plan', 'None')}
"""
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))

# ==================== REFER ====================
async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    text = f"""
👥 REFER & EARN

💰 ₹50 per referral!

📤 Your Link:
https://t.me/{context.bot.username}?start=ref_{user_id}
"""
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))

# ==================== WITHDRAW ====================
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    balance = user_data.get('balance', 0)
    
    if balance < 100:
        await query.edit_message_text(f"Min ₹100! Balance: ₹{balance}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))
        return
    
    await query.edit_message_text(
        f"🏦 WITHDRAWAL\n\n"
        f"Balance: ₹{balance}\n"
        f"Min: ₹100\n"
        f"Max: ₹500\n\n"
        f"📌 /withdraw [amount]",
        parse_mode='Markdown'
    )

async def withdraw_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /withdraw [amount]")
        return
    
    try:
        amount = int(context.args[0])
    except:
        await update.message.reply_text("Enter valid amount!")
        return
    
    user_data = get_user(user_id)
    balance = user_data.get('balance', 0)
    
    if amount < 100:
        await update.message.reply_text("Min ₹100!")
        return
    if amount > 500:
        await update.message.reply_text("Max ₹500!")
        return
    if amount > balance:
        await update.message.reply_text(f"Insufficient! You have ₹{balance}")
        return
    
    net = amount - 10
    update_user(user_id, {
        "balance": balance - amount,
        "withdrawn": user_data.get('withdrawn', 0) + net
    })
    
    await update.message.reply_text(
        f"✅ Withdrawal Request Sent!\n\n"
        f"Amount: ₹{amount}\n"
        f"Fee: ₹10\n"
        f"Net: ₹{net}\n"
        f"⏳ 24-48 hrs",
        parse_mode='Markdown'
    )

# ==================== ADMIN ====================
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await query.edit_message_text("Access Denied!")
        return
    
    users = load_json("users.json")
    total = len(users)
    
    text = f"""
⚙️ ADMIN PANEL

👥 Users: {total}
💰 Invested: ₹{sum(u.get('invested', 0) for u in users.values())}

📌 Commands:
/stats - Stats
/broadcast [msg] - Broadcast
/approve [id] - Approve WD
"""
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Users", callback_data="admin_users")],
            [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
            [InlineKeyboardButton("⏳ Pending", callback_data="admin_pending")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ])
    )

async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await query.edit_message_text("Access Denied!")
        return
    
    users = load_json("users.json")
    text = f"📊 USERS ({len(users)})\n\n"
    for uid, data in list(users.items())[:10]:
        text += f"• {data.get('first_name')} | ₹{data.get('balance')}\n"
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin")]]))

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await query.edit_message_text("Access Denied!")
        return
    
    await query.edit_message_text("Send: /broadcast [message]", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin")]]))

async def admin_pending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await query.edit_message_text("Access Denied!")
        return
    
    wds = load_json("withdrawals.json")
    pending = {}
    for k, v in wds.items():
        if v.get('status') == 'pending':
            pending[k] = v
    
    if not pending:
        text = "No pending withdrawals!"
    else:
        text = f"⏳ PENDING ({len(pending)})\n\n"
        for wid, data in list(pending.items()):
            text += f"• {data.get('first_name')} | ₹{data.get('amount')}\n"
            text += f"  ✅ /approve {wid}\n\n"
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin")]]))

async def admin_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await admin(update, context)

# ==================== COMMANDS ====================
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Not admin!")
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /broadcast [message]")
        return
    
    msg = ' '.join(context.args)
    users = load_json("users.json")
    sent = 0
    
    for uid in users:
        try:
            await context.bot.send_message(chat_id=int(uid), text=f"📢 Announcement\n\n{msg}")
            sent += 1
        except:
            pass
    
    await update.message.reply_text(f"Broadcast sent to {sent} users!")

async def approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Not admin!")
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /approve [wd_id]")
        return
    
    wid = context.args[0]
    wds = load_json("withdrawals.json")
    
    if wid not in wds:
        await update.message.reply_text("Not found!")
        return
    
    wds[wid]['status'] = 'approved'
    save_json("withdrawals.json", wds)
    
    await update.message.reply_text("Withdrawal approved!")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Not admin!")
        return
    
    users = load_json("users.json")
    await update.message.reply_text(f"📊 Users: {len(users)}\n💰 Invested: ₹{sum(u.get('invested', 0) for u in users.values())}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start - Main Menu\n/invest - Invest\n/withdraw - Withdraw")

# ==================== ERROR HANDLER ====================
