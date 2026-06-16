import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from config import BOT_TOKEN
from handlers import (
    start, button_callback, help_command,
    plans_command, support_command, proof_command,
    error_handler
)

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the bot"""
    
    application = Application.builder().token(BOT_TOKEN).build()

    # ---------- COMMAND HANDLERS ----------
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("plans", plans_command))
    application.add_handler(CommandHandler("support", support_command))
    application.add_handler(CommandHandler("proof", proof_command))

    # ---------- CALLBACK HANDLER (for all buttons) ----------
    application.add_handler(CallbackQueryHandler(button_callback))

    # ---------- ERROR HANDLER ----------
    application.add_error_handler(error_handler)

    # ---------- START BOT ----------
    logger.info("🤖 Investment Bot is starting...")
    print("""
    ╔═══════════════════════════════════╗
    ║   🤖 Investment Bot Started!      ║
    ║   Press Ctrl+C to stop            ║
    ╚═══════════════════════════════════╝
    """)
    
    application.run_polling(allowed_updates=[])

if __name__ == "__main__":
    main()
