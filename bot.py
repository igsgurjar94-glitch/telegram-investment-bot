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

ADMIN_IDS = [8473800312]  # Apni ID daalein

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

# ==================== MAIN MENU ====================
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main Menu - Professional Design"""
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
        [
            InlineKeyboardButton("💰 INVEST", callback_data="invest"),
            InlineKeyboardButton("🎁 DAILY", callback_data="daily")
        ],
        [
            InlineKeyboardButton("🎮 GAME", callback_data="game"),
            InlineKeyboardButton("📊 WALLET", callback_data="wallet")
        ],
        [
            InlineKeyboardButton("👥 REFER", callback_data="referral"),
            InlineKeyboardButton("🏦 WITHDRAW", callback_data="withdraw")
        ],
        [
            InlineKeyboardButton("📢 PROOF", callback_data="proof"),
            InlineKeyboardButton("📞 SUPPORT", callback_data="support")
        ]
    ]
    
    if user.id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("⚙️ ADMIN PANEL", callback_data="admin")])
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== START ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    create_user(user.id, user.username, user.first_name)
    await main_menu(update, context)

# ==================== BACK BUTTON ====================
async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
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
        [
            InlineKeyboardButton("💰 INVEST", callback_data="invest"),
            InlineKeyboardButton("🎁 DAILY", callback_data="daily")
        ],
        [
            InlineKeyboardButton("🎮 GAME", callback_data="game"),
            InlineKeyboardButton("📊 WALLET", callback_data="wallet")
        ],
        [
            InlineKeyboardButton("👥 REFER", callback_data="referral"),
            InlineKeyboardButton("🏦 WITHDRAW", callback_data="withdraw")
        ],
        [
            InlineKeyboardButton("📢 PROOF", callback_data="proof"),
            InlineKeyboardButton("📞 SUPPORT", callback_data="support")
        ]
    ]
    
    if user.id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("⚙️ ADMIN PANEL", callback_data="admin")])
    
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

📌 **How to Invest:**
Type: `/invest [plan] [amount]`
Example: `/invest basic 500`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    keyboard = [
        [InlineKeyboardButton("🟢 Basic (₹500)", callback_data="plan_basic")],
        [InlineKeyboardButton("🔵 Silver (₹2,000)", callback_data="plan_silver")],
        [InlineKeyboardButton("🟡 Gold (₹10,000)", callback_data="plan_gold")],
        [InlineKeyboardButton("🔴 Platinum (₹50,000)", callback_data="plan_platinum")],
        [InlineKeyboardButton("🔙 BACK TO MENU", callback_data="back")]
    ]
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

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
╔═══════════════════════════════╗
║   📊 **{plan['name']} PLAN**     ║
╚═══════════════════════════════╝

┌─────────────────────────────┐
│ 💰 Min Amount   : ₹{plan['min']}  │
│ 💰 Max Amount   : ₹{plan['max']} │
│ 📈 Daily Return : {plan['daily_return']}%  │
│ ⏳ Duration     : {plan['duration']} Days │
│ 💎 Total Return : {plan['daily_return'] * plan['duration']}% │
└─────────────────────────────┘

📌 **Send amount using:**
`/invest {plan_name} [amount]`

Example: `/invest {plan_name} 500`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 BACK TO PLANS", callback_data="invest")],
        [InlineKeyboardButton("🏠 MAIN MENU", callback_data="back")]
    ]
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== INVEST COMMAND ====================
async def invest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ **Usage:** `/invest [plan] [amount]`\n\n"
            "Plans: basic, silver, gold, platinum\n"
            "Example: `/invest basic 500`",
            parse_mode='Markdown'
        )
        return
    
    plan_name = context.args[0].lower()
    try:
        amount = int(context.args[1])
    except:
        await update.message.reply_text("❌ Please enter a valid amount!")
        return
    
    plan = PLANS.get(plan_name)
    if not plan:
        await update.message.reply_text("❌ Invalid plan! Choose: basic, silver, gold, platinum")
        return
    
    if amount < plan['min'] or amount > plan['max']:
        await update.message.reply_text(
            f"❌ Amount must be between ₹{plan['min']} and ₹{plan['max']} for {plan['name']} plan!"
        )
        return
    
    user_data = get_user(user_id)
    if user_data.get('plan') != 'none':
        await update.message.reply_text(
            "❌ You already have an active investment!\n"
            "Please wait until maturity or contact support."
        )
        return
    
    daily_return = (amount * plan['daily_return']) / 100
    total_return = amount + (daily_return * plan['duration'])
    
    update_user(user_id, {
        "main_balance": amount,
        "locked_balance": amount,
        "total_invested": amount,
        "plan": plan_name,
        "investment_date": str(datetime.now()),
        "maturity_date": str(datetime.now() + timedelta(days=plan['duration'])),
        "daily_reward": daily_return
    })
    
    text = f"""
╔═══════════════════════════════╗
║   ✅ **INVESTMENT SUCCESSFUL** ║
╚═══════════════════════════════╝

┌─────────────────────────────┐
│ 📊 Plan       : {plan['name']}   │
│ 💰 Amount     : ₹{amount}      │
│ 📈 Daily      : ₹{daily_return:.0f}   │
│ ⏳ Duration   : {plan['duration']} Days │
│ 💎 Total      : ₹{total_return:.0f}   │
└─────────────────────────────┘

🎁 **Claim your daily reward now!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎁 CLAIM DAILY REWARD", callback_data="daily")],
            [InlineKeyboardButton("🏠 MAIN MENU", callback_data="back")]
        ])
    )

# ==================== DAILY REWARD ====================
async def daily_reward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    if user_data.get('plan') == 'none':
        await query.edit_message_text(
            "❌ **No Active Investment!**\n\n"
            "Invest first to get daily rewards.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 INVEST NOW", callback_data="invest")],
                [InlineKeyboardButton("🔙 BACK", callback_data="back")]
            ])
        )
        return
    
    last_claim = user_data.get('last_claim_date')
    today = str(datetime.now().date())
    
    if last_claim == today:
        await query.edit_message_text(
            "⏳ **Already Claimed Today!**\n\n"
            "Come back tomorrow for your next reward.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎮 PLAY GAME", callback_data="game")],
                [InlineKeyboardButton("🔙 BACK", callback_data="back")]
            ])
        )
        return
    
    plan = PLANS.get(user_data.get('plan'))
    days_claimed = user_data.get('days_claimed', 0)
    
    if plan and days_claimed >= plan['duration']:
        await query.edit_message_text(
            "✅ **Investment Matured!**\n\n"
            f"Your {plan['name']} plan has completed {plan['duration']} days.\n"
            "You can withdraw your money now!",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏦 WITHDRAW NOW", callback_data="withdraw")],
                [InlineKeyboardButton("🔙 BACK", callback_data="back")]
            ])
        )
        return
    
    reward = int(user_data.get('daily_reward', 0))
    main_balance = user_data.get('main_balance', 0)
    new_balance = main_balance + reward
    
    update_user(user_id, {
        "main_balance": new_balance,
        "last_claim_date": today,
        "days_claimed": days_claimed + 1,
        "total_claimed": user_data.get('total_claimed', 0) + reward,
        "total_earned": user_data.get('total_earned', 0) + reward
    })
    
    text = f"""
╔═══════════════════════════════╗
║     🎁 **DAILY REWARD**        ║
╚═══════════════════════════════╝

┌─────────────────────────────┐
│ 📅 Day        : {days_claimed + 1}/{plan['duration']} │
│ 💰 Reward     : ₹{reward}       │
│ 💎 New Balance: ₹{new_balance}  │
└─────────────────────────────┘

⏳ **Next Reward:** Tomorrow

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎮 PLAY GAME", callback_data="game")],
            [InlineKeyboardButton("📊 MY WALLET", callback_data="wallet")],
            [InlineKeyboardButton("🔙 BACK", callback_data="back")]
        ])
    )

# ==================== GAME ====================
async def game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    if user_data.get('main_balance', 0) < 50:
        await query.edit_message_text(
            "❌ **Insufficient Balance!**\n\n"
            "Game Entry: ₹50\n"
            f"Your Balance: ₹{user_data.get('main_balance', 0)}\n\n"
            "Invest or claim daily reward to play!",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 INVEST", callback_data="invest")],
                [InlineKeyboardButton("🎁 DAILY REWARD", callback_data="daily")],
                [InlineKeyboardButton("🔙 BACK", callback_data="back")]
            ])
        )
        return
    
    context.user_data['game_active'] = True
    context.user_data['secret_number'] = random.randint(1, 10)
    
    text = """
╔═══════════════════════════════╗
║       🎮 **LUCKY NUMBER**      ║
╚═══════════════════════════════╝

┌─────────────────────────────┐
│ 💰 Entry Fee   : ₹50        │
│ 🎯 Win Prize   : ₹100 (2x)  │
│ ❌ Loss        : ₹50        │
└─────────────────────────────┘

📌 **Rules:**
1️⃣ Guess a number (1-10)
2️⃣ Correct → Win ₹100
3️⃣ Wrong → ₹50 lost

💡 **Type a number (1-10) now!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ CANCEL GAME", callback_data="cancel_game")]
        ])
    )

# ==================== CANCEL GAME ====================
async def cancel_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data['game_active'] = False
    
    await query.edit_message_text(
        "✅ **Game Cancelled!**\n\nYour balance is safe.",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 MAIN MENU", callback_data="back")]
        ])
    )

# ==================== HANDLE GAME ====================
async def handle_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not context.user_data.get('game_active'):
        return
    
    try:
        guess = int(update.message.text)
    except:
        await update.message.reply_text("❌ Please send a **number** (1-10)!")
        return
    
    if guess < 1 or guess > 10:
        await update.message.reply_text("❌ Number must be **between 1-10**!")
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
        
        text = f"""
╔═══════════════════════════════╗
║     🎉 **YOU WON!** 🎉         ║
╚═══════════════════════════════╝

┌─────────────────────────────┐
│ 🎯 Your Guess : {guess}        │
│ 🔢 Secret     : {secret}       │
│ 💰 Win Amount : ₹{win_amount}  │
│ 💎 New Balance: ₹{new_balance} │
└─────────────────────────────┘

🎮 **Want to play again?**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        keyboard = [
            [InlineKeyboardButton("🎮 PLAY AGAIN", callback_data="game")],
            [InlineKeyboardButton("🎁 DAILY REWARD", callback_data="daily")],
            [InlineKeyboardButton("🏠 MAIN MENU", callback_data="back")]
        ]
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        new_balance = main_balance - 50
        
        update_user(user_id, {
            "main_balance": new_balance,
            "games_played": user_data.get('games_played', 0) + 1
        })
        
        text = f"""
╔═══════════════════════════════╗
║      ❌ **YOU LOST!** ❌        ║
╚═══════════════════════════════╝

┌─────────────────────────────┐
│ 🎯 Your Guess : {guess}        │
│ 🔢 Secret     : {secret}       │
│ 💰 Lost Amount: ₹50          │
│ 💎 New Balance: ₹{new_balance} │
└─────────────────────────────┘

💡 **Try again!
