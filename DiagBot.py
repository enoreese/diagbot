# -*- coding:utf8 -*-
# !/usr/bin/env python
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

"""Module that defines the Diagbot class and defines helper functions to
process and validate date related to the diagnosis class

This is meant to be used with the TEEBOT agent for Dialogflow
"""

import random, json
from datetime import datetime as dt
from datetime import timedelta
from config import *
from Contexts import *
from pymongo import MongoClient, ASCENDING, DESCENDING
from botlog import BotLog
import smtplib, ssl

import requests
import infermedica_api

from config import ( INFERMEDICA_APP_ID, INFERMEDICA_APP_KEY, INFERMEDICA_DEV_MODE, GMAIL_PASSWORD )
from Replies import *

log = BotLog()

APPOINTMENT_FLAG = False


class Diagbot(object):
    """The Forecast object implements tracking of and forecast retrieval for
    a request for a weather forecast.  Several methods return various human
    readable strings that contain the weather forecast, condition, temperature
    and the appropriateness of outfits and activities to for forecasted weather

    This requires setting the WWO_API_KEY constant in config.py to a string
    with a valid WWO API key for retrieving weather forecasts

    Attributes:
        city (str): the city for the weather forecast
        datetime_start (datetime.datetime): forecast start date or datetime
        datetime_end (datetime.datetime): forecast end date or datetime
        unit (str): the unit of temperature: Celsius ('C') or Fahrenheit ('F')
        action (dict): any actions in the request (activity, condition, outfit)
        forecast (dict): structure containing the weather forecast from WWO
    """

    def __init__(self, params):
        """Initializes the DiagBot object

        gets the forecast for the provided dates
        """

        global APPOINTMENT_FLAG


        # Initialize the parameters
        self.userId = params['userId']
        # self.userName = params['userName']
        # self.location = params['Location']
        self.time = params['Time']
        self.date = params['Date']
        self.gender = params['Gender']
        self.bodyType = params['BodyType']
        self.fullname = params['Fullname']
        self.email = params['Email']
        self.pri_symptom = params['Primary_Symptom']
        self.age = params['Age']
        self.queryText = params['QueryText']
        self.symptoms = params['Symptoms']
        self.condition = params['Condition']

        self.choices = params['Choices']

        # if not self.symptoms:
        #     self.symptoms = []
        # else:
        #     self.symptoms = params['symptoms']

        if (self.queryText == 'createAppointment'):
            APPOINTMENT_FLAG = True


        # Initialize the database (MongoDB)
        try:
            self.mongoCon()
        except Exception as error:
            log.error(error)

        # Initialize infermedica API
        try:
            self.infermedica, self.infermedica_req = self.infermedicaCon()
        except Exception as error:
            log.error(error)

    def mongoCon(self):
        """
        Instantiate MongoDB Database
        """
        self.mongoClient = MongoClient()
        self.mongoClient = MongoClient(MONGO_CLIENT_HOST)

        # Access database
        self.mydatabase = self.mongoClient[MONGODB_NAME]

        # Access collection of the database
        self.conv_collection = self.mydatabase[MONGO_CONVERSATION_COLLECTION]
        self.sub_collection = self.mydatabase[MONGO_SUBSCRIPTION_COLLECTION]

    def infermedicaCon(self):
        """
        Instantiate Infermedica API
        """
        infermedica_api.configure({
            'app_id': '143fb87b',
            'app_key': '7c3c9dd9c4adcdc0d9c314007c28441f',
            'dev_mode': True  # Use only during development on production remove this parameter
        })

        return infermedica_api.get_api(), infermedica_api

    def __send_email(self, receiver_email, message):
        smtp_server = "smtp.gmail.com"
        port = 587  # For starttls
        sender_email = "my@gmail.com"
        password = GMAIL_PASSWORD

        # Create a secure SSL context
        context = ssl.create_default_context()

        # Try to log in to server and send email
        try:
            server = smtplib.SMTP(smtp_server, port)
            server.ehlo()  # Can be omitted
            server.starttls(context=context)  # Secure the connection
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)

            # TODO: Send email here
            server.sendmail(sender_email, receiver_email, message)
        except Exception as e:
            # Print any error messages to stdout
            log.error(e)
        finally:
            server.quit()

    # def __search_infermedica(self, query):
    #     """Calls the Infermedical API for a symptom
    #
    #     raises an exception for network errors
    #     Returns a symptom ID in the response
    #     """
    #
    #     result = self.infermedica.lookup(phrase=query, sex=self.gender)
    #     # log.log(result)
    #
    #     if result:
    #         return dict(id=result['id'], label=result['label'], state='present')
    #     else:
    #         result = self.infermedica.search(phrase=query, sex=self.gender, max_results=3,
    #                                          filters=[infermedica_api.SEARCH_FILTERS.SYMPTOMS])
    #         # log.log(result)
    #         return dict(id=result[0]['id'], label=result[0]['label'], state='present')

    # def __diagnose_infermedica(self, age, gender, symptoms, request=None):
    #     """Calls the Infermedical API for a diagnosis
    #
    #     raises an exception for network errors
    #     Returns a diagnosis object in the response
    #     """
    #
    #     if not request:
    #         request = self.infermedica_req.Diagnosis(age=int(age), sex=gender.lower())
    #
    #         for symptom in symptoms:
    #             request.add_symptom(_id=symptom['id'], state=symptom['state'], initial=True)
    #
    #     #     Call diagnosis
    #     #     log.log(request)
    #         request = self.infermedica.diagnosis(request)
    #         log.log(request)
    #     else:
    #         for symptom in symptoms:
    #             request.add_symptom(symptom['id'], symptom['state'])
    #
    #         #     Call Diagnosis
    #         request = self.infermedica.diagnosis(request)
    #         # log.log(request)
    #
    #     return request

    def diagnose(self):
        """
            Diagnose User's symptoms and Outputs Condition
        """

        userId = int(self.userId)
        age = (self.age)
        gender = self.gender
        symptoms = self.symptoms
        log.log(symptoms)

        log.log(userId)

        # Check database if user already exists
        user = self.mydatabase[MONGO_USER_COLLECTION].find_one({'userId': userId})

        # Save to log file and print to console
        log.log(user)

        # if user exists
        if user:
            # Has user provided age?
            if 'age' in user:
                log.log('Fetch Users Age')
                age = int(user['age'])
                gender = user['gender']
            else:
                if self.age and self.gender:
                    log.log('Save Users Details')
                    # adds new age and gender to user database
                    self.mydatabase[MONGO_USER_COLLECTION].find_one_and_update({'userId': userId},
                                                                               {"$set": {'age': int(age),
                                                                                         'gender': gender}})

        # checks for age parameter
        if not age:
            text = 'How old are you? '
            return {
                'context': QUESTION,
                'fulfillmentText': text
            }
        # checks for gender
        if not gender:
            text = 'Gender? '
            return {
                'context': QUESTION,
                'fulfillmentText': text
            }

        # checks for primary symptom
        if not self.pri_symptom:
            text = 'What is your primary symptom? '
            return {
                'context': QUESTION,
                'fulfillmentText': text
            }


        print('continue here')

        # If user has not been created, create him now
        if not user:
            user_record = {
                'age': int(age),
                'gender': gender,
                'created': dt.utcnow(),
                'userId': userId
            }

            # add new user to database
            newUser = self.mydatabase[MONGO_USER_COLLECTION].insert_one(user_record).inserted_id


        # If symptom list is empty, search infermedica for users primary symptoms
        if len(symptoms) == 0:
            log.log('Search Symptom')
            # if user sends body part
            if self.bodyType:
                # create a new strings adding body part to primary symptom
                primary_symptom = str(self.bodyType) + ' ' + str(self.pri_symptom)
            else:
                primary_symptom = self.pri_symptom

            log.log(primary_symptom)

            # Call function to search Infermedica API for users primary symptoms
            pri_symptom = self.__search_infermedica(primary_symptom)
            # add the symptom to list of symptoms
            symptoms.append(pri_symptom)
            log.log(symptoms)

        req = None

        # Pick choice
        if self.choices:
            for choice in self.choices:
                if choice['name'].lower() == self.queryText.lower():
                    req = choice

        if req:
            log.log('Diagnose Symptom')

            symptoms.append({
                "id": req['id'],
                "label": req['name'].lower(),
                "state": "present"
            })
            log.log(symptoms)

            req = self.__diagnose_infermedica(age, gender, symptoms)

            # Stop asking and return Condition if symptoms are more than 6
            # if list of symtoms is less than 6, keep asking questions
            if len(symptoms) < 6:
                log.log('Return Question')
                if req.question:
                    questionText = req.question.text

                    choices = []
                    if req.question.type == 'single':
                        for choice in req.question.items[0]['choices']:
                            choices.append({
                                'id': req.question.items[0]['id'],
                                'name': choice['label']
                            })
                    else:
                        for choice in req.question.items:
                            choices.append({
                                'id': choice['id'],
                                'name': choice['name']
                            })

                    # return the question
                    return {
                        'context': QUESTION,
                        'fulfillmentText': questionText,
                        'choices': choices,
                        'symptoms': symptoms,
                        # 'req': req
                    }
            else:
                # symptoms are more than 6, return the predicted condition
                if req.conditions:
                    log.log('Return Condition')
                    conditionName = req.conditions[0]['name']
                    probability = req.conditions[0]['probability']

                    # return condition
                    return {
                        'context': QUESTION,
                        'choices': [],
                        'symptoms': [],
                        'fulfillmentText': random.choice(DIAGNOSIS).format(condition=conditionName, probability=probability),
                        'followupEventInput': {
                            "name": "prescribe",
                            "parameters": {
                                "condition": conditionName,
                            },
                            "languageCode": "en-US",
                        },
                    }

        else:
            req = self.__diagnose_infermedica(age, gender, symptoms)

            if req.question:
                questionText = req.question.text
                choices = []
                for choice in req.question.items:
                    choices.append({
                        'id': choice['id'],
                        'name': choice['name']
                    })

                return {
                    'context': QUESTION,
                    'fulfillmentText': questionText,
                    'choices': choices,
                    'symptoms': symptoms,
                    # 'req': req
                }

    def new_appointment(self):
        """
            Creates new Doctor appointment
        """

        userId = self.userId

        # Check if users already exists
        user = self.mydatabase[MONGO_USER_COLLECTION].find_one({'userId': userId})

        if user:
            self.email = user['email']

        #    TODO: Request OTP
        #     if not self.otp:
        #         text = 'OTP sent to your phonenumber? '
        #         return {
        #             'context': CONFIRM_APPOINTMENT_FOLLOWUP,
        #             'fulfillmentText': text
        #         }
            # TODO: Confirm OTP

        # else:
        webhook_payload = CONFIRM_APPOINTMENT_FOLLOWUP
        # check for time parameter
        if not self.time:
            text = 'What time? (8am - 6pm) '
            return {
                'context': webhook_payload,
                'fulfillmentText': text
            }
        # check for date parameter
        if not self.date:
            text = 'What date? '
            return {
                'context': webhook_payload,
                'fulfillmentText': text
            }
        # check for email parameter
        if not self.email:
            text = 'Your Email? So we can reach you. '
            return {
                'context': webhook_payload,
                'fulfillmentText': text
            }

        else:


            # TODO: Check if Date and time is booked
            # appointments = self.mydatabase[MONGO_APPOINTMENT_COLLECTION].find({'date': parse_datetime_input(self.date),
            #                                                                    'time': parse_datetime_input(self.time)})
            # # If date already exists, ask user to accept new date
            # if appointments:
            #     date = parse_datetime_input(self.date)
            #     date = date.date()
            #     time = parse_datetime_input(self.time)
            #     new_time = time + timedelta(hours=1)
            #     new_time = new_time.time()
            #
            #     text = 'That slot is already booked. Try on {date} by {time}. Continue? '.format \
            #         (date=date, time=new_time)
            #
            #     return dict(context=CREATE_APPOINTMENT_FOLLOWUP, fulfillmentText=text)

            date = parse_datetime_input(self.date)
            date = date.date()
            time = parse_datetime_input(self.time)
            time = time.time()

            text = 'You\'ve booked an appointment on {date} by {time}. Continue? '.format\
                (date=date, time=time)

            return dict(context=CREATE_APPOINTMENT_FOLLOWUP, fulfillmentText=text)

    def confirm_appointment(self):
        """
        Confirms user's appointment after booking

        returns appointment confirmation message
        """

        userId = self.userId

        # check for user in database
        user = self.mydatabase[MONGO_USER_COLLECTION].find_one({'userId': userId})
        print(user)

        # if user exists
        if user:
            # if user does not have email in database
            if not 'email' in user:
                email = self.email
                log.log('Save Users Details')
                # add email to user's database
                self.mydatabase[MONGO_USER_COLLECTION].find_one_and_update({'userId': userId},
                                                                           {"$set": {'email': email}})
            else:
                email = user['email']
        else:
            # if user does not exist
            email = self.email

            # create new user
            user_record = {
                'email': email,
                'created': dt.utcnow(),
                'userId': userId
            }

            # Add user to USER database
            newUser = self.mydatabase[MONGO_USER_COLLECTION].insert_one(user_record).inserted_id


        date = parse_datetime_input(self.date)
        date = date.date()
        time = parse_datetime_input(self.time)
        time = time.time()

        # create appointment
        appointment_record = {
            'userId': userId,
            'time': str(time),
            'date': str(date),
            'paired': False,
            'appointmentComplete': False,
            '_userId': user['_id'] if user else newUser
        }

        # add appointment to APPOINTMENT database
        self.mydatabase[MONGO_APPOINTMENT_COLLECTION].insert(appointment_record)

        res = random.choice(CONFIRM_APPOINTMENT)

        # Send appointment email
        self.__send_email(receiver_email=email, message=res)

        return res.format()

    def check_appointment(self):
        """
        Checks database for user's latest doctors appointment
        """

        # Find appointment in database
        appointments = self.mydatabase[MONGO_APPOINTMENT_COLLECTION].find({'userId': self.userId})

        # if no appointments
        if appointments.count() == 0:
            return 'You currently have no appointment scheduled. You can schedule one now!'

        # if appointment, sort in ascending order
        appointments = appointments.sort('date', ASCENDING)
        # take the first appointment
        appointment = appointments[0]

        # if appointment has not been completed
        if not appointment['appointmentComplete']:
            response = random.choice(CHECK_APPOINTMENT).format(day=appointment['date'], time=appointment['time'])
        else:
            response = 'No recent appointment.'

        return response

    def prescribe(self):
        """
        Provides prescription based on provided condition
        """

        # Find appointment in database

        conditions = []


        if self.condition.lower() == 'gastroenteritis':
            response = 'Next Steps: \n'
            response += 'Rehydration: if there\'s some dehydration, give 20 ml/kg/hour of ORS for 4 hours and then reasses. \n'
            response += 'Replace losses with oral rehydration solution or  sugar and salt solution. \n'
            response += 'Maintainance fluid: Give as brest milk or milk according to age requirement as soon as the child is rehydrated. \n'
            response += 'Give elemental zinc: Up to 10 kg weight, 10 mg a day for 2 weeks, 10 kg or more, give 20 mg a day for 2 weeks \n'
            response += 'Continur feeding. \n'
            response += 'Follow up. '

        if self.condition.lower() == 'malaria':
            response = 'Next Steps: \n'
            response += 'Rehydration: if there\'s some dehydration, give 20 ml/kg/hour of ORS for 4 hours and then reasses. \n'
            response += 'Replace losses with oral rehydration solution or  sugar and salt solution. \n'
            response += 'Maintainance fluid: Give as brest milk or milk according to age requirement as soon as the child is rehydrated. \n'
            response += 'Give elemental zinc: Up to 10 kg weight, 10 mg a day for 2 weeks, 10 kg or more, give 20 mg a day for 2 weeks \n'
            response += 'Continur feeding. \n'
            response += 'Follow up. '

        if self.condition.lower() == 'gastric ulcer':
            response = 'Next Steps: \n'
            response += 'Rehydration: if there\'s some dehydration, give 20 ml/kg/hour of ORS for 4 hours and then reasses. \n'
            response += 'Replace losses with oral rehydration solution or  sugar and salt solution. \n'
            response += 'Maintainance fluid: Give as brest milk or milk according to age requirement as soon as the child is rehydrated. \n'
            response += 'Give elemental zinc: Up to 10 kg weight, 10 mg a day for 2 weeks, 10 kg or more, give 20 mg a day for 2 weeks \n'
            response += 'Continur feeding. \n'
            response += 'Follow up. '

        return response


def validate_params(parameters, context=False, other_params={}):
    """Takes a list of parameters from a HTTP request and validates them

    Returns a string of errors (or empty string) and a list of params
    """

    # Initialize error and params
    error_response = ''
    params = {}

    if context:
        parameters = parameters['parameters']
        queryText = other_params['queryResult']['queryText']
        other_param = other_params['originalDetectIntentRequest']['payload']
        print(parameters)
    else:
        # other_param = parameters['originalDetectIntentRequest']['payload']['data']['message']['from']
        other_param = parameters['originalDetectIntentRequest']['payload']
        queryText = parameters['queryResult']['queryText']
        parameters = parameters['queryResult']['parameters']
        print(parameters)

    # Query Text parameter
    if (queryText):
        params['QueryText'] = queryText
    else:
        params['QueryText'] = None

    # Email parameter
    if (parameters.get('gender')):
        params['Gender'] = parameters.get('gender')
    else:
        params['Gender'] = None

    # Age parameter
    if (parameters.get('age')):
        params['Age'] = parameters.get('age')
    else:
        params['Age'] = None

    # Rooms parameter
    if (parameters.get('pri_symptom')):
        params['Primary_Symptom'] = parameters.get('pri_symptom')
    else:
        params['Primary_Symptom'] = None

    # CleanType parameter
    if (parameters.get('BodyPart')):
        params['BodyType'] = parameters.get('BodyPart')
    else:
        params['BodyType'] = None

    # Address parameter
    if (parameters.get('address')):
        params['Address'] = parameters.get('address')
    else:
        params['Address'] = None

    # Date parameter
    if (parameters.get('date')):
        params['Date'] = parameters.get('date')
    else:
        params['Date'] = None

    # Time parameter
    if (parameters.get('time')):
        params['Time'] = parameters.get('time')
    else:
        params['Time'] = None

    # Fullname parameter
    if (other_params.get('first_name')):
        fullname = str(other_params.get('first_name')) + ' ' + str(other_params.get('last_name'))
        params['Fullname'] = fullname
    else:
        params['Fullname'] = None

    # Email parameter
    if (parameters.get('email')):
        params['Email'] = parameters.get('email')
    else:
        params['Email'] = None

    # Condition parameter
    if (parameters.get('condition')):
        params['Condition'] = parameters.get('condition')
    else:
        params['Condition'] = None

    # Twitter Platform User Id
    if other_param.get('user_id'):
        params['userId'] = other_param.get('user_id')
    else:
        params['userId'] = None

    # Symptoms List Parameter
    if other_param.get('symptoms'):
        params['Symptoms'] = other_param.get('symptoms')
    else:
        params['Symptoms'] = []

    # Req Object Parameter
    if other_param.get('choices'):
        params['Choices'] = other_param.get('choices')
    else:
        params['Choices'] = []

    return error_response.strip(), params


def parse_datetime_input(datetime_input):
    """Takes a string containing date/time and intervals in ISO-8601 format

    Returns a start and end Python datetime.datetime object
    datetimes are None if the string is not a date/time
    datetime_end is None if the string is not a date/time interval
    """

    # Date time
    # If the string is length 8 datetime_input has the form 17:30:00
    if len(datetime_input) == 8:
        # if only the time is provided assume its for the current date
        current_date = dt.now().strftime('%Y-%m-%dT')

        datetime = dt.strptime(
            current_date + datetime_input,
            '%Y-%m-%dT%H:%M:%S')
        datetime_end = None
    # If the string is length 10 datetime_input has the form 2014-08-09
    elif len(datetime_input) == 10:
        datetime = dt.strptime(datetime_input, '%Y-%m-%d').date()
    # If the string is length 20 datetime_input has the form
    # 2014-08-09T16:30:00Z
    elif len(datetime_input) == 20:
        datetime = dt.strptime(datetime_input, '%Y-%m-%dT%H:%M:%SZ')

    elif len(datetime_input) == 25:
        # Split date into start and end times
        datetime = dt.strptime(datetime_input[:len(datetime_input)-3] + datetime_input[len(datetime_input)-2:], '%Y-%m-%dT%H:%M:%S%z')

    else:
        datetime = None

    return datetime
