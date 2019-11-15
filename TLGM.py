#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple Bot to reply to Telegram messages.
This is the telegram server, This code
collects user queries from telegram application and post it to
Dialogflow on line 95
"""

from config import *
import dialogflow_v2 as dialogflow
from Replies import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError)
from pymongo import MongoClient
from google.protobuf import struct_pb2
from google.protobuf.json_format import MessageToJson, MessageToDict
# from google.appengine.api import urlfetch
# from google.appengine import runtime
# from google.appengine.runtime import apiproxy_errors
from botlog import BotLog
import logging
import uuid, datetime
import codecs, json, os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

PLATFORM = 'TLGRM'
OUTPUT_CONTEXT = {}
CHOICES = {}
SYMPTOMS = {}

# Enable logging
log = BotLog()

class DIAG_TLGM:

    def mongoCon(self):
        """
        Instantiate MongoDB Database
        """
        self.mongoClient = MongoClient()
        self.mongoClient = MongoClient(MONGO_CLIENT_HOST)

        # Access database
        self.mydatabase = self.mongoClient[MONGODB_NAME]

        # Access collection of the database
        self.collection = self.mydatabase[MONGO_CONVERSATION_COLLECTION]

    # Connect to dialogflow
    def apiaiCon(self):
        """
        Instantiate Dialogflow Client
        """
        self.session_client = dialogflow.SessionsClient()
        self.session = self.session_client.session_path(DIALOGFLOW_PROJECT_ID, str(uuid.uuid4()))

    # Define a few command handlers. These usually take the two arguments bot and
    # update. Error handlers also receive the raised TelegramError object in error.
    def start(self, bot, update):
        """Send a message when the command /start is issued."""
        update.message.reply_text('Hi! Tee Bot speaking, how may i help you?')

    def help(self, bot, update):
        """Send a message when the command /help is issued."""
        update.message.reply_text(HELP_REPLY)

    def onMessage(self, bot, update):
        """Handle the user message."""

        global OUTPUT_CONTEXT, CHOICES, SYMPTOMS

        user = update.message.from_user
        text = update.message.text

        # Instantiate mongo-db connection
        self.mongoCon()

        # Instantiate API.AI(Dialogflow)
        self.apiaiCon()

        params = struct_pb2.Struct()

        # Send custom parameters for backend processing
        params['user_id'] = str(user['id'])
        params['platform'] = PLATFORM
        params['choices'] = CHOICES
        params['symptoms'] = SYMPTOMS

        text_input = dialogflow.types.TextInput(
            text=text, language_code='en')


        query_input = dialogflow.types.QueryInput(text=text_input)

        if OUTPUT_CONTEXT:
            log.log(OUTPUT_CONTEXT)

            # Send query, context with parameters to Dialogflow
            original_request = dialogflow.types.QueryParameters(payload=params, contexts=OUTPUT_CONTEXT)
            # OUTPUT_CONTEXT = {}
        else:
            # Send query with parameters to Dialogflow
            original_request = dialogflow.types.QueryParameters(payload=params)

        try:
            # Get the response which is a json object
            response = self.session_client.detect_intent(
                session=self.session, query_input=query_input, query_params=original_request)
            log.log('Dialogflow Res')
            log.log(response)

            # If response text in not empty
            if response.query_result.fulfillment_text != None:
                record = {
                    'user_id': user['id'],
                    'query': str(text),
                    'reply': str(response.query_result.fulfillment_text),
                    'date': datetime.datetime.utcnow(),
                    'platform': PLATFORM
                }

                # Save Conversation into database
                req = self.collection.insert(record)

                # Set Dialogflow output context as a global variable, so we can reuse it later
                OUTPUT_CONTEXT = response.query_result.output_contexts

                if response.query_result.webhook_payload:
                    log.log('Webhook Payload')
                    payload = MessageToDict(response.query_result.webhook_payload)
                    log.log(payload)

                    # Save Choices and Symptoms as a global variable, so we can reuse it later
                    CHOICES = payload['telegram']['choices']
                    SYMPTOMS = payload['telegram']['symptoms']

                    responseObj = {
                        "message": response.query_result.fulfillment_text,
                        "symptoms": payload['telegram']['symptoms'],
                        "choices": payload['telegram']['choices']
                    }

                    # Send reply back to user (with quick reply)
                    self.send_message(update, responseObj, quick_reply=True)

                else:
                    log.log('No Webhook Payload')
                    responseObj = {
                        'message': response.query_result.fulfillment_text,
                    }

                    # Send reply back to user (without quick reply)
                    self.send_message(update, responseObj)

        except (TelegramError) as e:
            log.error(e)
            # Get the response which is a json object
            # response = self.session_client.detect_intent(
            #     session=self.session, query_input=query_input, query_params=original_request)

            # if response.query_result.fulfillment_text != None:
            #     update.message.reply_text(response.query_result.fulfillment_text)

    def send_message(self, update, obj, quick_reply=False):
        if not quick_reply:
            log.log('No Quick Reply')
            update.message.reply_text(obj['message'])
        else:
            log.log('Quick Reply')
            log.log(obj)

            # Create quick reply keyboard
            keyboard = []
            for choice in obj['choices']:
                keyboard.append([
                    KeyboardButton(choice['name'])
                ])

            reply_markup = ReplyKeyboardMarkup(keyboard)

            update.message.reply_text(obj['message'], reply_markup=reply_markup)

        return None

    def button(self, update, context):
        query = update.callback_query

        query.edit_message_text(text="Selected option: {}".format(query.data))

    def error_callback(self, bot, update, error):
        try:
            raise error
        except Unauthorized:
            log.error('Unauthorized')
        # remove update.message.chat_id from conversation list
        except BadRequest:
            log.error('BadRequest')
        # handle malformed requests - read more below!
        except TimedOut:
            log.error('TimedOut')
        # handle slow connection problems
        except NetworkError:
            log.error('NetworkError')
        # handle other connection problems
        except ChatMigrated as e:
            log.error(e)
        # the chat_id of a group has changed, use e.new_chat_id instead
        except TelegramError:
            log.error('TelegramError')
    # handle all other telegram related errors

    def main(self):
        """Start the bot."""
        # Create the EventHandler and pass in your bot's token.
        updater = Updater(TELEGRAM_TOKEN)

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CallbackQueryHandler(self.button))
        dp.add_handler(CommandHandler("help", self.help))

        # on noncommand i.e message - echo the message on Telegram
        dp.add_handler(MessageHandler(Filters.text, self.onMessage))

        # log all errors
        dp.add_error_handler(self.error_callback)

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()


if __name__ == '__main__':
    log.log('Starting Telegram Bot')
    diag_telegram = DIAG_TLGM()
    diag_telegram.main()
