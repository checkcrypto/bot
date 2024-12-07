import random
import asyncio
from mnemonic import Mnemonic
from eth_account import Account
from web3 import Web3
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable unaudited HD wallet features
Account.enable_unaudited_hdwallet_features()

# Ethereum node URL
ETHEREUM_NODE_URL = "https://cloudflare-eth.com"

# Connect to Ethereum node
def connect_to_web3():
    web3 = Web3(Web3.HTTPProvider(ETHEREUM_NODE_URL))
    if not web3.is_connected():
        raise ConnectionError("Failed to connect to the Ethereum node.")
    return web3

# Initialize the mnemonic object
mnemo = Mnemonic("english")

# Provided seed list
SEED_WORDS = [
    "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract", "absurd",
    "abuse", "access", "accident", "account", "accuse", "achieve", "acid", "acoustic",
    "acquire", "across", "act", "action", "actor", "actress", "actual", "adapt", "add",
    "addict", "address", "adjust", "admit"
]

# Generate a valid 12-word mnemonic
def generate_valid_mnemonic():
    while True:
        phrase = ' '.join(random.sample(SEED_WORDS, 12))
        if mnemo.check(phrase):
            return phrase

# Derive address and check balance
def check_balance(web3, mnemonic):
    account = Account.from_mnemonic(mnemonic)
    address = account.address
    balance_wei = web3.eth.get_balance(address)
    balance_eth = web3.from_wei(balance_wei, 'ether')
    return address, balance_eth

# Telegram command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome! Use /generate to create a single mnemonic or /autogenerate to continuously generate mnemonics and check balances."
    )

# Telegram command: /generate
async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    web3 = connect_to_web3()
    mnemonic = generate_valid_mnemonic()
    await update.message.reply_text(f"Generated Mnemonic: {mnemonic}")
    try:
        address, balance = check_balance(web3, mnemonic)
        await update.message.reply_text(f"Ethereum Address: {address}\nBalance: {balance} ETH")
        if balance > 0:
            await update.message.reply_text("Non-zero balance found.")
    except Exception as e:
        await update.message.reply_text(f"Error while checking balance: {e}")

# Telegram command: /autogenerate
async def autogenerate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    web3 = connect_to_web3()
    await update.message.reply_text("Auto-generation started. Use /stop to halt the process.")
    context.chat_data["stop"] = False  # Initialize stop flag

    count = 0  # Track the number of attempts
    while True:
        # Check stop flag
        if context.chat_data.get("stop", False):
            await update.message.reply_text("Stopping auto-generation as requested.")
            break

        count += 1
        mnemonic = generate_valid_mnemonic()
        try:
            address, balance = check_balance(web3, mnemonic)
            await update.message.reply_text(
                f"Checked {count}:\nMnemonic: {mnemonic}\nAddress: {address}\nBalance: {balance} ETH"
            )
            if balance > 0:
                await update.message.reply_text("Non-zero balance found. Stopping auto-generation.")
                break
        except Exception as e:
            await update.message.reply_text(f"Error during checked {count}: {e}")

        await asyncio.sleep(1)  # Add a delay to avoid rate limits

# Telegram command: /stop
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "stop" in context.chat_data:
        context.chat_data["stop"] = True  # Set the stop flag
        await update.message.reply_text("Stopping the auto-generation process. This may take a few seconds.")
    else:
        await update.message.reply_text("No auto-generation process is running.")

# Main function to run the bot
def main():
    TELEGRAM_BOT_TOKEN = "7766913521:AAHmxJdBptH4uLxBxmMWjojstYxWZLX3pTI"

    # Create Application instance
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("generate", generate))
    application.add_handler(CommandHandler("autogenerate", autogenerate))
    application.add_handler(CommandHandler("stop", stop))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()