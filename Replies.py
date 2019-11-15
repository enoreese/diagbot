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

"""This module defines the text based template responses to be formatted
and sent to users with the proper data

This is meant to be used with the Diagbot agent for Dialogflow
"""

HELP_REPLY = ''

SUBSCRIBE_YES = [
    'Please input your Email Address.',
    'Input Email Address.',
    'Enter Email Address to continue.',
    'Thank you! Enter your Email Address.'
]

SUBSCRIBE_NO = [
    'Okay. What would you like to do? Type "help" for more information. ',
    'Alright! How can i be of assistance?.',
    'Fine! What can i do for you today?.',
]

DIAGNOSIS = [
    'The predicted condition is {condition} with probability: {probability} ',
]

WELCOME_BACK = [
    'Hey! Welcome back. What would you like to do? ',
    'Hi there! What can i do for you today? '
]

WELCOME_REPLY = [
    'Hi! Welcome to Kureen! Would you like to subscribe to Our Newsletter? ',
    'Hello! Welcome to Kureen! How can I help you? Would you like to subscribe to Our Newsletter? ',
    'Good day! Welcome to Kureen! Would you like to subscribe to Our Newsletter? ',
    'Greetings! Welcome to Kureen! Subscribe to Our Newsletter? '
]

CONFIRM_APPOINTMENT = [
    'Your appointment has been made. '
]

CHECK_APPOINTMENT = [
    'Your next appointment is on {day} by {time}.',
    'Your next Kleen is by {time} on {day}'
]

