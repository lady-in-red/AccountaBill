#!/bin/bash

from datetime import datetime
import pytz
from model import User, Objective, connect_to_db, db, Message
from server import app
import os

from twilio.rest import Client

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

# Set number = to variable name
twilio_number = os.environ['TWILIO_NUMBER']

connect_to_db(app)

with open('numberstotext.txt', 'w') as outFile:
    # define what day's date is in YYYY-MM-DD format
    pacific = pytz.timezone('US/Pacific')
    today = datetime.now(tz=pacific).strftime('%Y-%m-%d')

    # query db to get all objectives due today
    days_objectives = Objective.query.filter_by(due_date=today).all()

    # for each obj due, find user phone number
    for each in days_objectives:
        obj = each.obj_id
        ob_text = each.obj_text

        # query db for user phone + set last_message_date
        user = User.query.filter_by(user_id=each.goal.user_id).first()
        user.last_message_date = today
        uphone = user.phone

        # write it to file and commit db
        outFile.write('\n' + str(uphone) + " " + str(obj) + " " + today)
        db.session.commit()

        # Twilio interaction
        # send reminder that objective is due today
        body = 'Your objective for the day is: ' + ob_text + 'Text back "' + str(obj) + '" when you have completed this objective today.'
        new_message = client.api.account.messages.create(to=uphone,
                                                         from_=twilio_number,
                                                         body=body)
