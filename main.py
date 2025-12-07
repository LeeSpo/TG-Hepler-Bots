import logging
import os
import requests
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Error: Please provide an argument, e.g\\., `/run IBKR`",
            parse_mode=constants.ParseMode.MARKDOWN_V2
        )
        return

    arg = context.args[0].upper()
    env_var_name = f"WEBHOOK_{arg}"
    webhook_url = os.environ.get(env_var_name)

    if not webhook_url:
        await update.message.reply_text(
            f"Error: No webhook configured for argument: `{arg}` \\(Expected env var: `{env_var_name}`\\)",
            parse_mode=constants.ParseMode.MARKDOWN_V2
        )
        return

    try:
        response = requests.get(webhook_url)
        response.raise_for_status()
        # You might want to customize the success message or use the response from the webhook
        await update.message.reply_text(
            'Run Succeed\n```json\n{\n  "message": "Workflow was started"\n}\n```',
            parse_mode=constants.ParseMode.MARKDOWN_V2
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to trigger webhook: {e}")
        # Escape special characters for MarkdownV2 if needed, or just wrap in code block
        error_msg = str(e).replace('!', '\\!').replace('.', '\\.').replace('-', '\\-').replace('=', '\\=')
        await update.message.reply_text(
            f"Error: Failed to trigger webhook\n```\n{error_msg}\n```",
            parse_mode=constants.ParseMode.MARKDOWN_V2
        )

async def post_init(application):
    await application.bot.set_my_commands([
        ("run", "Run a workflow. Usage: /run <ARG>"),
    ])

if __name__ == '__main__':
    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token:
        logging.error("BOT_TOKEN environment variable not set.")
        exit(1)

    application = ApplicationBuilder().token(bot_token).post_init(post_init).build()
    
    run_handler = CommandHandler('run', run_command)
    application.add_handler(run_handler)
    
    application.run_polling()
