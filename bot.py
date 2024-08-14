import os
import logging
from urllib.parse import urlparse, urlunparse
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from scrapers.scrapers import NfceScraper
from database import Database

load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("logs/bot.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Initialize database
db = Database()

# List of valid URL prefixes
VALID_URL_PREFIXES = [
    "http://www4.fazenda.rj.gov.br/consultaNFCe/QRCode",
    "https://consultadfe.fazenda.rj.gov.br/consultaNFCe/QRCode",
]

# URL to transform from and to
URL_TRANSFORM_FROM = "https://consultadfe.fazenda.rj.gov.br/consultaNFCe/QRCode"
URL_TRANSFORM_TO = "http://www4.fazenda.rj.gov.br/consultaNFCe/QRCode"

async def start(update: Update, context):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    db.add_user(user.id, user.first_name, user.last_name, user.username)
    await update.message.reply_text(
        f"Hi {user.first_name}! Send me a NFCe URL to scrape."
    )


async def help_command(update: Update, context):
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Send me a NFCe URL to scrape.")


def is_valid_url(url: str) -> bool:
    """Check if the URL starts with any of the valid prefixes."""
    return any(url.startswith(prefix) for prefix in VALID_URL_PREFIXES)


def transform_url(url: str) -> str:
    """Transform the URL if it matches the specific pattern."""
    if url.startswith(URL_TRANSFORM_FROM):
        parsed_url = urlparse(url)
        new_parsed_url = parsed_url._replace(
            scheme="http", netloc="www4.fazenda.rj.gov.br"
        )
        return urlunparse(new_parsed_url)
    return url

async def scrape_nfce(update: Update, context):
    """Scrape NFCe data from the provided URL."""
    url = update.message.text

    # Transform URL if necessary
    url = transform_url(url)

    if not is_valid_url(url):
        await update.message.reply_text("Please send a valid NFCe URL.")
        return

    await update.message.reply_text("Scraping data, please wait...")

    try:
        scraper = NfceScraper()
        data = scraper.get(url)

        # Save data to database
        db.save_invoice(update.effective_user.id, data)

        # Send a summary of the scraped data
        summary = (
            f"Invoice scraped successfully!\n\n"
            f"Company: {data['empresa']['razao_social']}\n"
            f"Date: {data['informacoes']['data_emissao']}\n"
            f"Total: R$ {data['totais']['valor_a_pagar']:.2f}\n"
            f"Items: {data['totais']['quantidade_itens']}"
        )

        await update.message.reply_text(summary)
    except Exception as e:
        logger.error(f"Error scraping NFCe: {e}")
        await update.message.reply_text(
            "An error occurred while scraping the NFCe. Please try again later."
        )


def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - scrape the NFCe
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, scrape_nfce)
    )

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
