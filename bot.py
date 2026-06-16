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
    print("Please add BOT_TOKEN in Railway Environment Variables")
    exit(1)

# Admin IDs
ADMIN_IDS = [8473800312]  # Apni ID daalein

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== DATA FILES ====================
# Railway par files create karein
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
    "basic": {"name": "Basic", "min": 500, "max": 1000, "daily_return": 2, "duration": 30},
    "silver": {"name": "Silver", "min": 2000, "max": 5000, "daily_return": 2.5, "duration": 30},
    "gold": {"name": "Gold", "min": 10000, "max": 25000, "daily_return": 3, "duration": 30},
    "platinum": {"name": "Platinum", "min": 50000, "max": 100000, "daily_return": 4, "duration": 30}
}

# ==================== START ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    create_user(user.id, user.username, user.first_name)
    user_data = get_user(user.id)
    
    text = f"""
🎮 **WELCOME {user.first_name}!** 🎮

💰 **Investment & Rewards Bot**

📊 **Your Stats:**
💰 Balance: ₹{user_data.get('main_balance', 0)}
🎁 Bonus: ₹{user_data.get('bonus_balance', 0)}
👥 Referrals: {user_data.get('referrals', 0)}

⬇️ **Choose Option:** ⬇️
"""
    
    keyboard = [
        [InlineKeyboardButton("💰 Invest", callback_data="invest")],
        [InlineKeyboardButton("🎁 Daily Reward", callback_data="daily")],
        [InlineKeyboardButton("🎮 Game", callback_data="game")],
        [InlineKeyboardButton("📊 Wallet", callback_data="wallet")],
        [InlineKeyboardButton("👥 Refer & Earn", callback_data="referral")],
        [InlineKeyboardButton("🏦 Withdraw", callback_data="withdraw")]
    ]
    
    if user.id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("⚙️ Admin", callback_data="admin")])
    
    await update.message.reply_text(
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

| Plan | Min | Daily % |
|------|-----|---------|
| Basic | ₹500 | 2% |
| Silver | ₹2,000 | 2.5% |
| Gold | ₹10,000 | 3% |
| Platinum | ₹50,000 | 4% |

📌 `/invest [plan] [amount]`
Example: `/invest basic 500`
"""
    
    keyboard = [
        [InlineKeyboardButton("Basic ₹500", callback_data="plan_basic")],
        [InlineKeyboardButton("Silver ₹2000", callback_data="plan_silver")],
        [InlineKeyboardButton("Gold ₹10000", callback_data="plan_gold")],
        [InlineKeyboardButton("Platinum ₹50000", callback_data="plan_platinum")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ]
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def invest_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    plan_name = query.data.replace("plan_", "")
    plan = PLANS.get(plan_name)
    
    if plan:
        await query.edit_message_text(
            f"📌 **{plan['name']} Plan**\n\n"
            f"Min: ₹{plan['min']}\n"
            f"Max: ₹{plan['max']}\n"
            f"Daily: {plan['daily_return']}%\n"
            f"Duration: {plan['duration']} Days\n\n"
            f"Send: `/invest {plan_name} [amount]`",
            parse_mode='Markdown'
        )

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
        win_amount = 90  # ₹100 - 10% fee
        new_balance = main_balance - 50 + win_amount
        
        update_user(user_id, {
            "main_balance": new_balance,
            "games_played": user_data.get('games_played', 0) + 1,
            "games_won": user_data.get('games_won', 0) + 1,
            "total_earned": user_data.get('total_earned', 0) + win_amount
        })
        
        await update.message.reply_text(
            f"🎉 **YOU WON!**\n\n"
            f"Your Guess: {guess}\n"
            f"Secret: {secret}\n"
            f"💰 You won ₹{win_amount}!\n"
            f"💎 New Balance: ₹{new_balance}",
            parse_mode='Markdown'
        )
    else:
        new_balance = main_balance - 50
        
        update_user(user_id, {
            "main_balance": new_balance,
            "games_played": user_data.get('games_played', 0) + 1
        })
        
        await update.message.reply_text(
            f"❌ **YOU LOST!**\n\n"
            f"Your Guess: {guess}\n"
            f"Secret: {secret}\n"
            f"💎 New Balance: ₹{new_balance}",
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
    
    await query.edit_message_text(text, parse_mode='Markdown')

# ==================== REFERRAL ====================
async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    text = f"""
👥 **REFER & EARN**

💰 ₹50 per referral!

📤 **Your Link:**
`https://t.me/{context.bot.username}?start=ref_{user_id}`

💡 Share and earn!
"""
    
    await query.edit_message_text(text, parse_mode='Markdown')

# ==================== WITHDRAW ====================
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    balance = user_data.get('main_balance', 0)
    
    if balance < 100:
        await query.edit_message_text(f"❌ Min withdrawal ₹100!\nYour Balance: ₹{balance}")
        return
    
    await query.edit_message_text(
        f"🏦 **WITHDRAWAL**\n\n"
        f"Balance: ₹{balance}\n"
        f"Min: ₹100 | Max: ₹500\n"
        f"Fee: ₹10\n\n"
        f"Send: `/withdraw [amount]`",
        parse_mode='Markdown'
    )

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
        await update.message.reply_text("❌ Max ₹500 per day!")
        return
    
    if amount > balance:
        await update.message.reply_text(f"❌ Insufficient! You have ₹{balance}")
        return
    
    net_amount = amount - 10
    
    update_user(user_id, {
        "main_balance": balance - amount,
        "total_withdrawn": user_data.get('total_withdrawn', 0) + net_amount
    })
    
    await update.message.reply_text(
        f"✅ **Withdrawal Request Sent!**\n\n"
        f"Amount: ₹{amount}\n"
        f"Fee: ₹10\n"
        f"Net: ₹{net_amount}\n"
        f"⏳ Processing: 24-48 hrs",
        parse_mode='Markdown'
    )

# ==================== BACK ====================
async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    text = f"🎮 **Main Menu**\n\n💰 Balance: ₹{user_data.get('main_balance', 0)}"
    
    keyboard = [
        [InlineKeyboardButton("💰 Invest", callback_data="invest")],
        [InlineKeyboardButton("🎁 Daily Reward", callback_data="daily")],
        [InlineKeyboardButton("🎮 Game", callback_data="game")],
        [InlineKeyboardButton("📊 Wallet", callback_data="wallet")],
        [InlineKeyboardButton("👥 Refer & Earn", callback_data="referral")],
        [InlineKeyboardButton("🏦 Withdraw", callback_data="withdraw")]
    ]
    
    if user_id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("⚙️ Admin", callback_data="admin")])
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

# ==================== ADMIN ====================
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await query.edit_message_text("❌ Not admin!")
        return
    
    users = load_json("users.json")
    
    text = f"""
⚙️ **ADMIN PANEL**

👥 Users: {len(users)}
💰 Total Invested: ₹{sum(u.get('total_invested', 0) for u in users.values())}
💎 Total Earned: ₹{sum(u.get('total_earned', 0) for u in users.values())}

📌 Commands:
/stats - Stats
/broadcast [msg] - Send to all
"""
    
    await query.edit_message_text(text, parse_mode='Markdown')

# ==================== STATS ====================
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Not admin!")
        return
    
    users = load_json("users.json")
    
    text = f"""
📊 **STATS**

👥 Users: {len(users)}
💰 Invested: ₹{sum(u.get('total_invested', 0) for u in users.values())}
💎 Earned: ₹{sum(u.get('total_earned', 0) for u in users.values())}
"""
    
    await update.message.reply_text(text, parse_mode='Markdown')

# ==================== BROADCAST ====================
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Not admin!")
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("❌ Usage: `/broadcast [message]`")
        return
    
    message = ' '.join(context.args)
    users = load_json("users.json")
    sent = 0
    
    for uid in users:
        try:
            await context.bot.send_message(
                chat_id=int(uid),
                text=f"📢 **Announcement**\n\n{message}",
                parse_mode='Markdown'
            )
            sent += 1
        except:
            pass
    
    await update.message.reply_text(f"✅ Broadcast sent to {sent} users!")

# ==================== HELP ====================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 **COMMANDS**\n\n"
        "/start - Main Menu\n"
        "/invest [plan] [amount] - Invest\n"
        "/withdraw [amount] - Withdraw\n"
        "/stats - Admin Stats\n"
        "/broadcast [msg] - Admin Broadcast",
        parse_mode='Markdown'
    )

# ==================== ERROR ====================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

# ==================== MAIN ====================
def main():
    print("🤖 Starting Investment Bot...")
    print(f"✅ Bot Token: {'Found ✅' if BOT_TOKEN else 'Not Found ❌'}")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("invest", invest_command))
    app.add_handler(CommandHandler("withdraw", withdraw_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    
    # Callbacks
    app.add_handler(CallbackQueryHandler(invest, pattern="^invest$"))
    app.add_handler(CallbackQueryHandler(invest_plan, pattern="^plan_"))
    app.add_handler(CallbackQueryHandler(daily_reward, pattern="^daily$"))
    app.add_handler(CallbackQueryHandler(game, pattern="^game$"))
    app.add_handler(CallbackQueryHandler(wallet, pattern="^wallet$"))
    app.add_handler(CallbackQueryHandler(referral, pattern="^referral$"))
    app.add_handler(CallbackQueryHandler(withdraw, pattern="^withdraw$"))
    app.add_handler(CallbackQueryHandler(back, pattern="^back$"))
    app.add_handler(CallbackQueryHandler(admin, pattern="^admin$"))
    
    # Game handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_game))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    print("✅ Bot is running!")
    app.run_polling(allowed_updates=[])

if __name__ == "__main__":
    main()
