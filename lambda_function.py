"""
This is an Alexa Skill for the Duke Smart Home, to turn on or off lights in the
home via simple voice commands.

Made as part of the 2017-2018 Smart Home X Project
"""

from __future__ import print_function
from botocore.vendored import requests

# Dictionary imported directly from 
# https://dukesmarthomeapi.herokuapp.com/
room_dict = { 'Dirty Lab': [26], 
	'Clean Lab Cabinets': [3], 
	'Clean Lab': [4],
	'South West Bedroom': [6],
	'Downstairs Bedroom': [7],
	'North West Bedroom': [9],
	'North East Bedroom': [21],
	'South East Bedroom': [28],
	'West Balcony': [35],
	'Front Porch': [35],
	'Back Porch': [36],
	'Kitchen': [11],
	'Front Indoor Lights': [12],
	'White Board Lights': [31],
	'Kitchen Cabinets': [38],
	'Main Room': [11,12,31],
	'Media Room': [20,24],
	'Upper Floor': [0,2],
	'East Upper Bathroom': [17],
	'West Upper Bathroom': [15],
	'West Lower Bathroom': [13] }

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(speechlet_response):
    return {
        'version': '1.0',
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    card_title = "Welcome"
    speech_output = "Welcome to the Duke Smart Home Lights app! " \
                    "Please tell me which lights to turn on or off by saying, " \
                    "turn off the lights in the, followed by the name of the room."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me which lights to turn on or off by saying, " \
                    "turn off the lights in the, followed by the name of the room."
    should_end_session = False
    return build_response(build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using the Duke Smart Home Lights skill. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response(build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def turn_on_light(intent, session):
    card_title = intent['name']
    should_end_session = False

    if 'LightName' in intent['slots']:
        light_name = intent['slots']['LightName']['value']
        speech_output = "I have sent in a request to turn on the lights."
        reprompt_text = "Have the lights not turned on? Please try again."
        
        response = requests.get("https://dukesmarthomeapi.herokuapp.com/lights/7?status=ON")
    else:
        speech_output = "I'm not sure what room's lights you wanted to turn on. " \
                        "Please try again."
        reprompt_text = "I'm still not quite sure what room you are talking about. " \
                        "Please try again."
    return build_response(build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        

def turn_off_light(intent, session):
    card_title = intent['name']
    should_end_session = False

    if 'LightName' in intent['slots']:
        light_name = intent['slots']['LightName']['value']
        speech_output = "I have sent in a request to turn off the lights."
        reprompt_text = "Have the lights not turned off? Please try again."
        
        response = requests.get("https://dukesmarthomeapi.herokuapp.com/lights/7?status=OFF")
    else:
        speech_output = "I'm not sure what room's lights you wanted to turn off. " \
                        "Please try again."
        reprompt_text = "I'm still not quite sure what room you are talking about. " \
                        "Please try again."
    return build_response(build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "TurnOnLight":
        return turn_on_light(intent, session)
    elif intent_name == "TurnOffLight":
        return turn_off_light(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
