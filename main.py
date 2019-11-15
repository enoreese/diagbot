# !/usr/bin/env python3
# Copyright 2019 Google Inc. All Rights Reserved.
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

"""
"""

import json, os
from botlog import BotLog

from flask import Flask, request, jsonify, make_response

from DiagBot import Diagbot, validate_params
from Contexts import *

app = Flask(__name__)


log = BotLog()


@app.route('/', methods=['POST'])
def webhook():
    """This method handles the http requests for the Dialogflow webhook

    This is meant to be used in conjunction with the DiagBot Dialogflow agent
    """
    req = request.get_json(silent=True, force=True)
    try:
        action = req.get('queryResult').get('action')
    except AttributeError as error:
        log.error(error)
        return 'json error'

    print(req)

    if action == 'appointment.check':
        res = check_appointment(req)
    # elif action == 'appointment.change':
    #     res = change_appointment(req)
    elif action == 'create.appointment':
        res = new_appointment(req)
    elif action == 'diagnose':
        res = diagnose(req)
    elif action == 'prescribe':
        res = prescribe(req)
    elif action == 'confirmAppointment.yes':
        res = confirm_appointment(req)
    else:
        log.error('Unexpected action.')

    actionStr = 'Action: ' + action
    respStr = 'Response Object: '

    print(actionStr)

    log.log(actionStr)
    log.log(respStr)
    log.log(res)

    return make_response(jsonify(res))


def check_appointment(req):
    """Returns a string containing text with a response to the user
    with the diagbot or a prompt for more information

    Takes user's query and returns checks database for doctors appointment
    """
    parameters = req['queryResult']['parameters']

    print('Dialogflow Parameters:')
    print(json.dumps(parameters, indent=4))

    # validate request parameters, return an error if there are issues
    error, diagbot_params = validate_params(req)
    if error:
        log.error(error)
        return error

    # create a diagbot object which retrieves the diagbot from a external API
    try:
        diagbot = Diagbot(diagbot_params)
    # return an error if there is an error getting the diagbot
    except (ValueError, IOError) as error:
        log.error(error)
        return error

    response = diagbot.check_appointment()

    return {'fulfillmentText': response}

def prescribe(req):
    """Returns a string containing text with a response to the user
    with a indication if the activity provided is appropriate for the
    current weather or a prompt for more information

    Takes a city, activity and (optional) dates
    uses the template responses found in Diagbot_reply.py as templates
    and the activities listed in weather_entities.py
    """

    # validate request parameters, return an error if there are issues
    error, diagbot_params = validate_params(req['queryResult']['parameters'])
    if error:
        log.error(error)
        return error


    # create a diagbot object which retrieves the diagbot from a external API
    try:
        diagbot = Diagbot(diagbot_params)
    # return an error if there is an error getting the diagbot
    except (ValueError, IOError) as error:
        log.error(error)
        return error

    # get the response
    return {'fulfillmentText': diagbot.prescribe()}


def new_appointment(req):
    """Returns a string containing a human-readable response to the user
    with the available slots or a prompt for more information

    Takes time, date parameters and check for available slots
    """

    # validate request parameters, return an error if there are issues
    error, diagbot_params = validate_params(req)
    if error:
        log.error(error)
        return error


    # create a diagbot object which retrieves the diagbot from a external API
    try:
        diagbot = Diagbot(diagbot_params)
    # return an error if there is an error getting the diagbot
    except (ValueError, IOError) as error:
        log.error(error)
        return error

    # get the response
    obj = diagbot.new_appointment()
    print('appointment response object')
    print(obj)

    quick_reply = {}

    if obj['context'] == CONFIRM_APPOINTMENT_FOLLOWUP:
        outputContext = req['queryResult']['outputContexts']
    elif obj['context'] == CREATE_APPOINTMENT_FOLLOWUP:
        outputContext = [{
            'name': '{}/contexts/createappointment-followup'.format(req['session']),
            'lifespanCount': 1
        }]
        quick_reply = {
            "telegram": {
                "replies": [
                    [{
                        "text": 'Yeah, Sure!',
                        "callback_data": 'yes',
                    }],
                    [{
                        "text": 'No!',
                        "callback_data": 'no',
                    }]
                ],
                "choices": [],
                "symptoms": [],
            }
        }
    else:
        outputContext = req['queryResult']['outputContexts']

    return {
        "outputContexts": outputContext,
        "fulfillmentText": obj['fulfillmentText'],
        "payload": quick_reply
    }


def confirm_appointment(req):
    """Returns a string containing text with a response to the user
    with a confirmation of user's appointment
    """

    # validate request parameters, return an error if there are issues
    error, diagbot_params = validate_params(req['queryResult']['outputContexts'][0], True, req)
    if error:
        log.error(error)
        return error

    # create a diagbot object which retrieves the diagbot from a external API
    try:
        diagbot = Diagbot(diagbot_params)
    # return an error if there is an error getting the diagbot
    except (ValueError, IOError) as error:
        log.error(error)
        return error

    return {
        'fulfillmentText': diagbot.confirm_appointment(),
        # "payload": quick_reply
    }


def diagnose(req):
    """Returns a string containing text with a response to the user
    with a indication of user's predicted condition or a prompt to answer questions for more information

    Takes an age, gender, primary symptom and (optional) body part.
    """

    parameters = req

    # validate request parameters, return an error if there are issues
    error, diagbot_params = validate_params(parameters)
    if error:
        log.error(error)
        return error


    # create a diagbot object which retrieves the diagbot from a external API
    try:
        diagbot = Diagbot(diagbot_params)
    # return an error if there is an error getting the diagbot
    except (ValueError, IOError) as error:
        log.error(error)
        return error

    obj = diagbot.diagnose()

    log.log(obj)

    outputContext = req['queryResult']['outputContexts']
    #     [{
    #     'name': '{}/contexts/{}'.format(req['session'], obj['context']),
    #     'lifespanCount': 5
    # }]

    replies = []
    if 'choices' in obj:
        for choice in obj['choices']:
            replies.append([{
                "text": choice['name'],
                "callback_data": choice['name'].lower(),
            }])

        return {
            "outputContexts": outputContext,
            "fulfillmentText": obj['fulfillmentText'],
            "payload": {
                "telegram": {
                    "replies": replies,
                    "choices": obj['choices'],
                    "symptoms": obj['symptoms'],
                    # "req": obj['req']
                }
            },
        }
    else:
        return {
            "outputContexts": outputContext,
            "fulfillmentText": obj['fulfillmentText'],
        }

# def welcome(req):
#     """Returns a string containing text with a response to the user
#     with a indication if temperature provided is consisting with the
#     current weather or a prompt for more information
#
#     Takes a city, temperature and (optional) dates.  Temperature ranges for
#     hot, cold, chilly and warm can be configured in config.py
#     uses the template responses found in Diagbot_reply.py as templates
#     """
#
#     parameters = req
#
#     # validate request parameters, return an error if there are issues
#     error, diagbot_params = validate_params(parameters)
#     if error:
#         log.error(error)
#         return error
#
#
#     # create a diagbot object which retrieves the diagbot from a external API
#     try:
#         diagbot = Diagbot(diagbot_params)
#     # return an error if there is an error getting the diagbot
#     except (ValueError, IOError) as error:
#         log.error(error)
#         return error
#
#     obj = diagbot.welcome()
#
#     if not obj['context']:
#         outputContext = []
#         for context in req['queryResult']['outputContexts']:
#             context['lifespanCount'] = 0
#             outputContext.append(context)
#         res = {
#             "outputContexts": outputContext,
#             "fulfillmentText": obj['text'],
#             "payload": {
#                 "twitter": {
#                     "replies": [
#                         {
#                             "label": 'Book a Kleen!',
#                             "description": 'Book a Basic, After Party, Moving in/out Kleen',
#                             "metadata": 'book a clean',
#                         },
#                         {
#                             "label": 'Check my appointment',
#                             "description": 'Check pending kleens',
#                             "metadata": 'check my appointment',
#                         },
#                         {
#                             "label": 'Edit my appointment',
#                             "description": 'Edit pending kleens',
#                             "metadata": 'edit my appointment',
#                         },
#                     ]
#                 }
#             }
#         }
#     else:
#         res = {
#                 "outputContexts": req['queryResult']['outputContexts'],
#                 "fulfillmentText": obj['text'],
#                 "payload": {
#                     "twitter": {
#                         "replies": [
#                             {
#                                 "label": 'Yeah, Sure!',
#                                 "description": 'Sign me up to your newsletter',
#                                 "metadata": 'yes',
#                             },
#                             {
#                                 "label": 'Nah. Not now!',
#                                 "description": 'Not now',
#                                 "metadata": 'no',
#                             }
#                         ]
#                     }
#                 }
#             }
#
#     return res

def noSamePreference(req):
    """Returns a string containing text with a response to the user
    with a indication if temperature provided is consisting with the
    current weather or a prompt for more information

    Takes a city, temperature and (optional) dates.  Temperature ranges for
    hot, cold, chilly and warm can be configured in config.py
    uses the template responses found in Diagbot_reply.py as templates
    """

    parameters = req

    # validate request parameters, return an error if there are issues
    error, diagbot_params = validate_params(parameters)
    if error:
        log.error(error)
        return error


    # create a diagbot object which retrieves the diagbot from a external API
    try:
        diagbot = Diagbot(diagbot_params)
    # return an error if there is an error getting the diagbot
    except (ValueError, IOError) as error:
        log.error(error)
        return error

    obj = diagbot.no_same_preference()

    if obj['parameters']:
        res = {
                "followupEventInput": {
                    "name": "createAppointment",
                    "parameters": {
                        "phoneNumber": obj['parameters']['phone'],
                        "fullname": obj['parameters']['name']
                    },
                    "languageCode": "en-US",
                },
            }

    return res

def yesSamePreference(req):
    """Returns a string containing text with a response to the user
    with a indication if the outfit provided is appropriate for the
    current weather or a prompt for more information

    Takes a city, outfit and (optional) dates
    uses the template responses found in Diagbot_reply.py as templates
    and the outfits listed in weather_entities.py
    """

    # validate request parameters, return an error if there are issues
    error, diagbot_params = validate_params(req)
    if error:
        log.error(error)
        return error

    # create a diagbot object which retrieves the diagbot from a external API
    try:
        diagbot = Diagbot(diagbot_params)
    # return an error if there is an error getting the diagbot
    except (ValueError, IOError) as error:
        log.error(error)
        return error

    return {'fulfillmentText': diagbot.yes_same_preference()}

def main():
    log.log('Starting Dialogflow Fulfillment')
    port = int(os.environ.get('PORT', 5050))
    app.run(debug=True, host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
