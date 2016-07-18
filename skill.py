from __future__ import print_function
import json
import re
import urllib2

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
    if intent_name == "getHumidIntent":
        return getHumidity(intent, session)
    elif intent_name == "getPressureIntent":
        return getPressure(intent, session)
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

# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():
    session_attributes = {}
    card_title = "Yahoo Weather"
    speech_output = "I can lookup the humidity and Pressure on Yahoo Weather. Just ask me, How Humid is it outside? "
    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session, speech_output))


def handle_session_end_request():
    should_end_session = True
    return build_response({}, build_speechlet_response(
        None, None, None, should_end_session, None))

def getHumidity(intent, session):
    url = "https://query.yahooapis.com/v1/public/yql?q=select%20atmosphere%20from%20weather.forecast%20where%20woeid%3D[WOEID GOES HERE]&format=json&diagnostics=true&callback="
    response = urllib2.urlopen(url)
    data = dict(json.loads(response.read()))
    humidity = data['query']['results']['channel']['atmosphere']['humidity']

    session_attributes = {}
    card_title = "Yahoo Weather"
    speech_output = "The humidity is currently " + humidity + " percent"
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, "", should_end_session, speech_output))

def getPressure(intent, session):
    url = "https://query.yahooapis.com/v1/public/yql?q=select%20atmosphere%20from%20weather.forecast%20where%20woeid%3D[WOEID GOES HERE]&format=json&diagnostics=true&callback="
    response = urllib2.urlopen(url)
    data = dict(json.loads(response.read()))
    pressure = data['query']['results']['channel']['atmosphere']['pressure']
    rising = data['query']['results']['channel']['atmosphere']['rising']

    if rising == 1:
        rising = "Rising"
    elif rising == 2:
        rising = "Falling"
    else:
        rising = "Steady"

    session_attributes = {}
    card_title = "Yahoo Weather"
    speech_output = "The pressure is currently " + pressure + " pounds per square inch and is " + rising
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, "", should_end_session, speech_output))





# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session, card_text):
    if output == None:
        return {
            'shouldEndSession': should_end_session
        }
    elif title == None:
        return {
            'outputSpeech': {
                'type': 'PlainText',
                'text': output
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': reprompt_text
                }
            },
            'shouldEndSession': should_end_session
        }
    else:
        return {
            'outputSpeech': {
                'type': 'PlainText',
                'text': output
            },
            'card': {
                'type': 'Simple',
                'title':  title,
                'content': card_text
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': reprompt_text
                }
            },
            'shouldEndSession': should_end_session
        }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }