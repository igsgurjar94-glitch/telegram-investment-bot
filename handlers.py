import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- WELCOME MESSAGE (Aap ise edit kar sakte hain) ----------
WELCOME_MESSAGE = """
🚀 **WELCOME TO [YOUR COMPANY NAME]** 🚀

💰 **Earn Money Online With Us!** 💰

Namaste! 🙏 
Aapka swagat hai hamari platform par. 
Hum dete hain best investment opportunities with guaranteed returns.

✅ **Why Choose Us?**
• 100% Secure & Trusted
• Instant Withdrawals
• 24/7 Customer Support
• High ROI (Returns)

📈 **Minimum Investment:** ₹500/- only
💵 **Daily Returns:** 10% - 30%
🏆 **Referral Bonus:** 5% lifetime

👀 Pehle hamare Proof Channel check karein,
phir support se baat karein,
aur fir investment plan dekhein!

**⚠️ Note:** Sirf apni risk capacity ke hisaab se invest karein.

🔽 **Neeche diye gaye options mein se choose karein:** 🔽
"""

# ---------- BUTTON HANDLERS ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /start command - Shows welcome message with buttons"""
    user = update.effective_user
    
    # Custom welcome with user's name
    welcome = f"""
👋 **Namaste {user.first_name}!** 👋

{WELCOME_MESSAGE}
"""
    
    # ---------- BUTTONS CREATE KARENGE ----------
    keyboard = [
        [
            InlineKeyboardButton("📢 Proof Channel", callback_data="proof_channel"),
        ],
        [
            InlineKeyboardButton("📞 Contact Support", callback_data="contact_support"),
        ],
        [
            InlineKeyboardButton("📊 Investment Plans", callback_data="investment_plans"),
        ],
        [
            InlineKeyboardButton("❓ Help / FAQ", callback_data="help_faq"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Message send karo with buttons
    await update.message.reply_text(
        welcome,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# ---------- BUTTON CLICK HANDLERS ----------

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button clicks"""
    query = update.callback_query
    await query.answer()  # Acknowledge button press
    
    data = query.data
    
    # ---------- PROOF CHANNEL BUTTON ----------
    if data == "proof_channel":
        proof_text = """
📢 **PROOF CHANNEL** 📢

✅ Hamare real payment proofs dekhein:

🔹 Channel Link: [Click Here](https://t.me/your_proof_channel)
🔹 Daily Payouts
🔹 Real Users Reviews
🔹 500+ Satisfied Investors

👇 **Join karein aur khud dekhein:**
👉 [@your_proof_channel](https://t.me/your_proof_channel)

💡 *Proof dekhne ke baad support se baat karein!*
"""
        await query.edit_message_text(
            proof_text,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=back_button()
        )
    
    # ---------- CONTACT SUPPORT BUTTON ----------
    elif data == "contact_support":
        support_text = """
📞 **CONTACT SUPPORT** 📞

Hum hain aapke liye 24/7 available!

🔹 **Direct Contact:**
   👤 Admin: [@your_admin_username](https://t.me/your_admin_username)
   👤 Support: [@your_support_bot](https://t.me/your_support_bot)

🔹 **Email:** support@yourcompany.com
🔹 **WhatsApp:** +91-XXXXXXXXXX

📌 **Support Hours:** 24/7 (Always Online)

⚠️ *Kisi bhi issue ke liye support se contact karein!*
"""
        await query.edit_message_text(
            support_text,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=back_button()
        )
    
    # ---------- INVESTMENT PLANS BUTTON ----------
    elif data == "investment_plans":
        plans_text = """
📊 **INVESTMENT PLANS** 📊

💰 **Choose Your Plan:**

┌─────────────────────────────┐
│ 🥇 **BASIC PLAN**           │
│ 💵 Amount: ₹500 - ₹5,000    │
│ 📈 Returns: 10% Daily       │
│ ⏳ Duration: 30 Days        │
│ 💰 Total ROI: 300%          │
└─────────────────────────────┘

┌─────────────────────────────┐
│ 🥈 **SILVER PLAN**          │
│ 💵 Amount: ₹5,001 - ₹25,000 │
│ 📈 Returns: 15% Daily       │
│ ⏳ Duration: 30 Days        │
│ 💰 Total ROI: 450%          │
└─────────────────────────────┘

┌─────────────────────────────┐
│ 🥇 **GOLD PLAN**            │
│ 💵 Amount: ₹25,001 - ₹1L    │
│ 📈 Returns: 20% Daily       │
│ ⏳ Duration: 30 Days        │
│ 💰 Total ROI: 600%          │
└─────────────────────────────┘

┌─────────────────────────────┐
│ 👑 **PLATINUM PLAN**        │
│ 💵 Amount: ₹1L+             │
│ 📈 Returns: 30% Daily       │
│ ⏳ Duration: 30 Days        │
│ 💰 Total ROI: 900%          │
└─────────────────────────────┘

✅ **Benefits:**
• Instant Withdrawal
• No Hidden Charges
• 100% Secure

📌 **Minimum Investment:** ₹500 only!

👉 Support se contact karein aur invest karein!
"""
        await query.edit_message_text(
            plans_text,
            parse_mode="Markdown",
            reply_markup=back_button()
        )
    
    # ---------- HELP / FAQ BUTTON ----------
    elif data == "help_faq":
        help_text = """
❓ **HELP / FAQ** ❓

**Q: Minimum investment kitna hai?**
A: Sirf ₹500/- se start kar sakte hain.

**Q: Returns kaise milte hain?**
A: Daily returns aapke wallet mein aate hain.

**Q: Withdrawal kaise karein?**
A: Support se contact karein, 24 hours mein payment aa jayegi.

**Q: Kya ye safe hai?**
A: 100% secure aur trusted platform hai.

**Q: Koi hidden charges?**
A: Bilkul nahi! Sab transparent hai.

**Q: Referral bonus kaise milega?**
A: Apne referral link share karein, 5% lifetime bonus.

📌 **Still have questions?**
Contact support: @your_admin_username

🔄 /start - Dobara start karein
"""
        await query.edit_message_text(
            help_text,
            parse_mode="Markdown",
            reply_markup=back_button()
        )
    
    # ---------- BACK BUTTON - Go to main menu ----------
    elif data == "back_to_main":
        # Wapas main menu par le jao
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
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

# ---------- BACK BUTTON FUNCTION ----------
def back_button():
    """Returns back button for all pages"""
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ---------- HELP COMMAND ----------
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /help command"""
    help_text = """
📚 **Available Commands:**

🔹 /start - Main menu open karein
🔹 /help - Help menu
🔹 /plans - Direct investment plans
🔹 /support - Contact support
🔹 /proof - Proof channel

Ya neeche diye gaye buttons use karein! 👇
"""
    keyboard = [
        [InlineKeyboardButton("📢 Proof Channel", callback_data="proof_channel")],
        [InlineKeyboardButton("📞 Contact Support", callback_data="contact_support")],
        [InlineKeyboardButton("📊 Investment Plans", callback_data="investment_plans")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(help_text, parse_mode="Markdown", reply_markup=reply_markup)

# ---------- ADDITIONAL DIRECT COMMANDS ----------
async def plans_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Direct /plans command"""
    # Investment plans wala message show karo using button_callback
    query = type('obj', (object,), {'data': 'investment_plans'})()
    query.edit_message_text = update.message.reply_text
    await button_callback(update, context)

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Direct /support command"""
    query = type('obj', (object,), {'data': 'contact_support'})()
    query.edit_message_text = update.message.reply_text
    await button_callback(update, context)

async def proof_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Direct /proof command"""
    query = type('obj', (object,), {'data': 'proof_channel'})()
    query.edit_message_text = update.message.reply_text
    await button_callback(update, context)

# ---------- ERROR HANDLER ----------
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ Kuch technical issue ho gaya! Support se contact karein."
        )
