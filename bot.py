import os
import json
import logging
import random
import string
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================== CONFIG ====================
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN not found!")
    exit(1)

# 🔑 APNA TELEGRAM USER ID YAHAN DALEIN!
ADMIN_IDS = [8473800312]

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== DATA FILES ====================
USERS_FILE = "users.json"
TRANSACTIONS_FILE = "transactions.json"
WITHDRAWALS_FILE = "withdrawals.json"

# ==================== LOAD/SAVE FUNCTIONS ====================
def load_json(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

def load_users():
    return load_json(USERS_FILE)

def save_users(users):
    save_json(USERS_FILE, users)

def load_transactions():
    return load_json(TRANSACTIONS_FILE)

def save_transactions(txns):
    save_json(TRANSACTIONS_FILE, txns)

def load_withdrawals():
    return load_json(WITHDRAWALS_FILE)

def save_withdrawals(wds):
    save_json(WITHDRAWALS_FILE, wds)

# ==================== USER FUNCTIONS ====================
def generate_referral_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def create_user(user_id, username, first_name):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            
            # WALLET
            "main_balance": 0,
            "bonus_balance": 0,
            "locked_balance": 0,
            "total_earned": 0,
            
            # INVESTMENT
            "total_invested": 0,
            "plan": "none",
            "investment_date": None,
            "maturity_date": None,
            "daily_reward": 0,
            
            # DAILY REWARD
            "last_claim_date": None,
            "days_claimed": 0,
            "total_claimed": 0,
            
            # GAME
            "games_played": 0,
            "games_won": 0,
            "game_bonus": 0,
            
            # REFERRAL
            "referral_code": generate_referral_code(),
            "referred_by": None,
            "referrals": 0,
            "referral_bonus": 0,
            
            # WITHDRAWAL
            "total_withdrawn": 0,
            "pending_withdrawal": 0,
            
            # SYSTEM
            "joined_at": str(datetime.now()),
            "last_active": str(datetime.now()),
            "is_active": True
        }
        save_users(users)
        return True
    return False

def get_user(user_id):
    users = load_users()
    return users.get(str(user_id))

def update_user(user_id, data):
    users = load_users()
    if str(user_id) in users:
        users[str(user_id)].update(data)
        save_users(users)
        return True
    return False

def add_transaction(user_id, txn_type, amount, description, status="completed"):
    txns = load_transactions()
    txn_id = f"txn_{int(datetime.now().timestamp())}_{random.randint(1000, 9999)}"
    txns[txn_id] = {
        "user_id": user_id,
        "type": txn_type,
        "amount": amount,
        "description": description,
        "status": status,
        "date": str(datetime.now())
    }
    save_transactions(txns)
    return txn_id

# ==================== INVESTMENT PLANS ====================
PLANS = {
    "basic": {
        "name": "🟢 Basic",
        "min": 500,
        "max": 1000,
        "daily_return": 2,  # 2%
        "duration": 30,
        "total_return": 60  # 60%
    },
    "silver": {
        "name": "🔵 Silver",
        "min": 2000,
        "max": 5000,
        "daily_return": 2.5,
        "duration": 30,
        "total_return": 75
    },
    "gold": {
        "name": "🟡 Gold",
        "min": 10000,
        "max": 25000,
        "daily_return": 3,
        "duration": 30,
        "total_return": 90
    },
    "platinum": {
        "name": "🔴 Platinum",
        "min": 50000,
        "max": 100000,
        "daily_return": 4,
        "duration": 30,
        "total_return": 120
    }
}

# ==================== START ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # Check if referral
    if context.args:
        ref_code = context.args[0]
        if ref_code.startswith("ref_"):
            ref_by = ref_code.replace("ref_", "")
            users = load_users()
            if ref_by in users and str(user_id) not in users:
                # Referral bonus
                ref_user = users[ref_by]
                ref_user["referrals"] = ref_user.get("referrals", 0) + 1
                ref_user["referral_bonus"] = ref_user.get("referral_bonus", 0) + 50
                ref_user["bonus_balance"] = ref_user.get("bonus_balance", 0) + 50
                save_users(users)
                await update.message.reply_text(
                    "🎉 **Referral Bonus!**\n\n"
                    "Aapko ₹50 bonus mila hai kyunki aapne kisi ko refer kiya!",
                    parse_mode='Markdown'
                )
    
    create_user(user.id, user.username, user.first_name)
    user_data = get_user(user_id)
    
    text = f"""
**🎮 WELCOME {user.first_name}!** 🎮

💰 **Investment & Rewards Bot**

🔥 **FEATURES:**

✅ **Invest** - ₹500 se start karein
✅ **Daily Reward** - Rozana 2-4% return
✅ **Game Bonus** - Game khelke extra kamao
✅ **Refer & Earn** - Dost laao, paisa pao
✅ **Safe Investment** - 30 days maturity

📊 **Your Stats:**
💰 Main Balance: ₹{user_data.get('main_balance', 0)}
🎁 Bonus Balance: ₹{user_data.get('bonus_balance', 0)}
🔒 Locked Balance: ₹{user_data.get('locked_balance', 0)}
💎 Total Earned: ₹{user_data.get('total_earned', 0)}
👥 Referrals: {user_data.get('referrals', 0)}

⬇️ **Choose Option Below:** ⬇️
"""
    
    keyboard = [
        [InlineKeyboardButton("💰 Invest Now", callback_data="invest")],
        [InlineKeyboardButton("🎁 Daily Reward", callback_data="daily_reward")],
        [InlineKeyboardButton("🎮 Play Game", callback_data="game")],
        [InlineKeyboardButton("📊 My Wallet", callback_data="wallet")],
        [InlineKeyboardButton("👥 Refer & Earn", callback_data="referral")],
        [InlineKeyboardButton("🏦 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("📢 Proof Channel", callback_data="proof")],
        [InlineKeyboardButton("📞 Support", callback_data="support")]
    ]
    
    if user_id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin")])
    
    image_url = os.getenv("IMAGE_URL", "https://example.com/banner.jpg")
    
    try:
        await update.message.reply_photo(
            photo=image_url,
            caption=text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except:
        await update.message.reply_text(
            text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ==================== INVEST ====================
async def invest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    text = """
**💰 INVESTMENT PLANS** 💰

**Choose Your Plan:**

| Plan | Min | Daily Return | Duration | Total |
|------|-----|--------------|----------|-------|
| 🟢 Basic | ₹500 | 2% | 30 Days | 60% |
| 🔵 Silver | ₹2,000 | 2.5% | 30 Days | 75% |
| 🟡 Gold | ₹10,000 | 3% | 30 Days | 90% |
| 🔴 Platinum | ₹50,000 | 4% | 30 Days | 120% |

📌 **How to Invest:**
Type: `/invest [plan] [amount]`

Example: `/invest basic 500`

⬇️ **Click a plan below:** ⬇️
"""
    
    keyboard = [
        [InlineKeyboardButton("🟢 Basic (₹500-1,000)", callback_data="plan_basic")],
        [InlineKeyboardButton("🔵 Silver (₹2,000-5,000)", callback_data="plan_silver")],
        [InlineKeyboardButton("🟡 Gold (₹10,000-25,000)", callback_data="plan_gold")],
        [InlineKeyboardButton("🔴 Platinum (₹50,000-1L)", callback_data="plan_platinum")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ]
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== INVEST PLAN BUTTON ====================
async def invest_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    plan_name = query.data.replace("plan_", "")
    plan = PLANS.get(plan_name)
    
    if not plan:
        await query.edit_message_text("❌ Invalid plan!")
        return
    
    context.user_data['invest_plan'] = plan_name
    
    text = f"""
**{plan['name']} PLAN** {plan['name']}

💰 **Amount Range:** ₹{plan['min']} - ₹{plan['max']}
📈 **Daily Return:** {plan['daily_return']}%
⏳ **Duration:** {plan['duration']} Days
💎 **Total Return:** {plan['total_return']}%

📌 **Send amount using command:**
`/invest {plan_name} [amount]`

Example: `/invest {plan_name} 500`

⚠️ **Minimum:** ₹{plan['min']}
⚠️ **Maximum:** ₹{plan['max']}

[🔙 Back](callback:invest)
"""
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown'
    )

# ==================== INVEST COMMAND ====================
async def invest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
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
        await update.message.reply_text("❌ Please enter valid amount!")
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
    
    if user_data.get('plan') != 'none' and user_data.get('plan') is not None:
        await update.message.reply_text(
            "❌ You already have an active investment!\n"
            "Wait for maturity or contact support."
        )
        return
    
    # Process investment
    daily_return = (amount * plan['daily_return']) / 100
    total_return = (amount * plan['total_return']) / 100
    
    update_user(user_id, {
        "main_balance": amount,
        "locked_balance": amount,
        "total_invested": amount,
        "plan": plan_name,
        "investment_date": str(datetime.now()),
        "maturity_date": str(datetime.now() + timedelta(days=plan['duration'])),
        "daily_reward": daily_return
    })
    
    add_transaction(user_id, "investment", amount, f"Invested in {plan['name']} plan")
    
    # Referral bonus (if referred)
    users = load_users()
    referred_by = user_data.get('referred_by')
    if referred_by and referred_by in users:
        users[referred_by]["bonus_balance"] = users[referred_by].get("bonus_balance", 0) + 50
        users[referred_by]["referral_bonus"] = users[referred_by].get("referral_bonus", 0) + 50
        users[referred_by]["referrals"] = users[referred_by].get("referrals", 0) + 1
        save_users(users)
    
    text = f"""
**✅ INVESTMENT SUCCESSFUL!** ✅

📊 **Plan:** {plan['name']}
💰 **Amount:** ₹{amount}
📈 **Daily Return:** ₹{daily_return:.0f} ({plan['daily_return']}%)
📅 **Duration:** {plan['duration']} Days
💎 **Total Return:** ₹{total_return:.0f} ({plan['total_return']}%)

🔒 **Locked Balance:** ₹{amount} (maturity: {plan['duration']} days)

🎁 **Claim daily reward every day!**

[🎁 Claim Daily Reward](callback:daily_reward)
"""
    
    await update.message.reply_text(text, parse_mode='Markdown')

# ==================== DAILY REWARD ====================
async def daily_reward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    if user_data.get('plan') == 'none':
        await query.edit_message_text(
            "❌ You don't have any active investment!\n"
            "Invest first to get daily rewards.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 Invest Now", callback_data="invest")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )
        return
    
    last_claim = user_data.get('last_claim_date')
    today = str(datetime.now().date())
    
    if last_claim == today:
        await query.edit_message_text(
            "❌ You already claimed today's reward!\n"
            "Come back tomorrow.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )
        return
    
    # Calculate reward
    daily_return = user_data.get('daily_reward', 0)
    days_claimed = user_data.get('days_claimed', 0)
    plan = PLANS.get(user_data.get('plan'))
    
    if plan and days_claimed >= plan['duration']:
        await query.edit_message_text(
            "✅ **Investment Matured!**\n\n"
            f"Your {plan['name']} plan has completed {plan['duration']} days.\n"
            "You can withdraw your money now!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏦 Withdraw", callback_data="withdraw")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )
        return
    
    # Claim reward
    reward = int(daily_return)
    main_balance = user_data.get('main_balance', 0)
    new_balance = main_balance + reward
    
    update_user(user_id, {
        "main_balance": new_balance,
        "last_claim_date": today,
        "days_claimed": days_claimed + 1,
        "total_claimed": user_data.get('total_claimed', 0) + reward,
        "total_earned": user_data.get('total_earned', 0) + reward
    })
    
    add_transaction(user_id, "daily_reward", reward, f"Daily reward - Day {days_claimed + 1}")
    
    text = f"""
**🎁 DAILY REWARD CLAIMED!** 🎁

📅 **Day:** {days_claimed + 1}/{plan['duration']}
💰 **Reward:** ₹{reward}
💎 **New Balance:** ₹{new_balance}

⏳ **Next Reward:** Tomorrow

[🎮 Play Game](callback:game) | [📊 Wallet](callback:wallet)
"""
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎮 Play Game", callback_data="game")],
            [InlineKeyboardButton("📊 My Wallet", callback_data="wallet")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
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
            "Game entry fee: ₹50\n"
            "Your Balance: ₹{balance}\n\n"
            "Invest more or claim daily reward!".format(balance=user_data.get('main_balance', 0)),
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 Invest", callback_data="invest")],
                [InlineKeyboardButton("🎁 Daily Reward", callback_data="daily_reward")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )
        return
    
    text = """
**🎮 LUCKY NUMBER GAME** 🎮

💰 **Entry Fee:** ₹50
🎯 **Win Prize:** ₹100 (2x)
❌ **Loss:** ₹50 goes to pool

**Rules:**
1. Guess a number between 1-10
2. If correct → You win ₹100!
3. If wrong → ₹50 lost

📊 **Your Stats:**
• Games Played: {games}
• Games Won: {won}
• Win Rate: {win_rate}%

⬇️ **Type a number (1-10) to play!** ⬇️
""".format(
    games=user_data.get('games_played', 0),
    won=user_data.get('games_won', 0),
    win_rate=int((user_data.get('games_won', 0) / max(user_data.get('games_played', 1), 1)) * 100)
)
    
    context.user_data['game_active'] = True
    context.user_data['game_bet'] = 50
    context.user_data['secret_number'] = random.randint(1, 10)
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_game")]
        ])
    )

# ==================== HANDLE GAME GUESS ====================
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
    
    user_data = get_user(user_id)
    secret = context.user_data.get('secret_number')
    bet = context.user_data.get('game_bet', 50)
    
    if guess == secret:
        # WIN
        win_amount = 100
        platform_fee = int(win_amount * 0.1)
        winner_amount = win_amount - platform_fee
        
        main_balance = user_data.get('main_balance', 0)
        new_balance = main_balance - bet + winner_amount
        
        update_user(user_id, {
            "main_balance": new_balance,
            "games_played": user_data.get('games_played', 0) + 1,
            "games_won": user_data.get('games_won', 0) + 1,
            "game_bonus": user_data.get('game_bonus', 0) + winner_amount,
            "total_earned": user_data.get('total_earned', 0) + winner_amount
        })
        
        add_transaction(user_id, "game_win", winner_amount, f"Won game! Guess: {guess}, Secret: {secret}")
        
        text = f"""
**🎉 CONGRATULATIONS! YOU WON!** 🎉

🎯 **Your Guess:** {guess}
🔢 **Secret Number:** {secret}

💰 **Bet Amount:** ₹{bet}
💎 **Win Amount:** ₹{winner_amount}
🏦 **Platform Fee:** ₹{platform_fee} (10%)

📊 **New Balance:** ₹{new_balance}

[🎮 Play Again](callback:game) | [🏠 Main Menu](callback:back)
"""
        keyboard = [
            [InlineKeyboardButton("🎮 Play Again", callback_data="game")],
            [InlineKeyboardButton("🎁 Daily Reward", callback_data="daily_reward")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back")]
        ]
        
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        
    else:
        # LOSS
        main_balance = user_data.get('main_balance', 0)
        new_balance = main_balance - bet
        
        update_user(user_id, {
            "main_balance": new_balance,
            "games_played": user_data.get('games_played', 0) + 1
        })
        
        add_transaction(user_id, "game_loss
