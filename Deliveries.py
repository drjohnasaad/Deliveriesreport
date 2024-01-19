from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import datetime
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Replace 'YOUR_BOT_TOKEN' and 'YOUR_GOOGLE_SHEET_ID' with actual values
TOKEN = '6325604865:AAEylxxR5vrT6Ihbp2TOlK7K92L02ywduSM'
GOOGLE_SHEET_ID = '1-R4Gd86jyNUhGQqnfRmK8qEihXIA-G9eUtqSQyPpsX4'

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Bot is running. Use /report to get today\'s messages report.')

def extract_info(message_text):
    # Extract relevant information using regex
    match = re.search(r'Rx: (\d+)\n(.+)\n(.+)\n(.+)\nCopay&Notes  : \son (.+)\nby (.+)', message_text)
    if match:
        return match.groups()
    return None

def report(update: Update, context: CallbackContext) -> None:
    today = datetime.date.today()
    messages_data = []

    for message in context.bot.get_chat_messages(update.message.chat_id, date=today):
        info = extract_info(message.text)
        if info:
            messages_data.append(info)

    if messages_data:
        # Connect to Google Sheets
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('your-credentials.json', scope)
        gc = gspread.authorize(credentials)
        sheet = gc.open_by_key(GOOGLE_SHEET_ID).sheet1

        # Update Google Sheet with the extracted data
        for data in messages_data:
            sheet.append_row(data)

        update.message.reply_text(f"Today's Messages Report has been updated in Google Sheets.")
    else:
        update.message.reply_text("No valid messages found today.")

def main() -> None:
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("report", report))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
