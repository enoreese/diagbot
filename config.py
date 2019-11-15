# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module that holds the configuration for app.py including
API keys, MongoDB configuration parameters

This is meant to be used with the Diagbot agent for Dialogflow, located at

"""
import os

GMAIL_PASSWORD = ''

INFERMEDICA_APP_KEY = ''
INFERMEDICA_APP_ID = ''
INFERMEDICA_DEV_MODE = True
_DEFAULT_TEMP_UNIT = 'F'

# TWITTER CONFIGURATION PARAMETERS
TWITTER_CONSUMER_KEY = os.environ.get('CONSUMER_KEY', None)
TWITTER_CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET', None)
TWITTER_CURRENT_USER_ID = os.environ.get('CURRENT_USER_ID', None)
TWITTER_ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', None)
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET', None)
TWITTER_FALLBACK_ID = os.environ.get('TWITTER_FALLBACK_ID', None)

# MONGODB CONFIGURATION PARAMETERS
MONGO_CLIENT_HOST = os.environ.get('MONGO_CLIENT_HOST', 'localhost')
MONGO_CLIENT_PORTNUMBER = os.environ.get('MONGO_CLIENT_PORTNUMBER', '27017')
MONGODB_NAME = os.environ.get('MONGODB_NAME', 'DIAG_DB')
MONGO_CONVERSATION_COLLECTION = os.environ.get('MONGO_CONVERSATION_COLLECTION', 'DIAG_DB_CONV')
MONGO_SUBSCRIPTION_COLLECTION = os.environ.get('MONGO_SUBSCRIPTION_COLLECTION', None)
MONGO_USER_COLLECTION = os.environ.get('MONGO_USER_COLLECTION', 'DIAG_DB_USER')
MONGO_APPOINTMENT_COLLECTION = os.environ.get('MONGO_APPOINTMENT_COLLECTION', 'DIAG_DB_APPO')

# DIALOGFLOW CONFIGURATION PARAMETERS
DIALOGFLOW_PROJECT_ID = os.environ.get('DIALOGFLOW_PROJECT_ID', '')

# TELEGRAM CONFIGURATION SETTINGS
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')

# GOOGLE CONFIGURATION SETTINGS
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', '') 