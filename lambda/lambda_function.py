"""
    Copyright (C) 2020 heyjas Systems - All Rights Reserved
 You may use, distribute and modify this code under the
 terms and conditions defined in file 'LICENSE.txt', which
 is part of this source code package.
 """

from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.dispatch_components import (AbstractRequestHandler, AbstractExceptionHandler, AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.skill_builder import SkillBuilder
from airtable import Airtable

import logging
import json
import random
import requests

# Establish connection with the airtable table_name

bse = 'YOUR_BASE_ID'
tbl = 'YOUR_TABLE_NAME'
key = 'YOUR_API_KEY'

table = Airtable(bse, tbl, key)

# Initializing the logger and setting the level to "INFO"
# Read more about it here https://www.loggly.com/ultimate-guide/python-logging-basics/
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Intent Handlers

#This Handler is called when the skill is invoked by using only the invocation name(Ex. Alexa, open product locator)
class LaunchRequestHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        skill_name = language_prompts["SKILL_NAME"]
        
        speech_output = random.choice(language_prompts['WELCOME']).format(skill_name)
        reprompt = random.choice(language_prompts['WELCOME_REPROMPT'])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class TellProductLocationIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return is_intent_name("TellProductLocationIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        session_attributes = handler_input.attributes_manager.session_attributes
        
        try:
            color_name = handler_input.request_envelope.request.intent.slots["color_name"].value
            prod_name = session_attributes['prod_name']
            
            user_details = {'Name': prod_name, 'Color': color_name}
            table.insert(user_details)
            
            speech_output = random.choice(language_prompts['COLOR_CONFIRMED']).format(prod_name)
            reprompt = random.choice(language_prompts['COLOR_CONFIRMED_REPROMPT'])
        except:
            speech_output = random.choice(language_prompts['COLOR_UNCONFIRMED'])
            reprompt = random.choice(language_prompts['COLOR_UNCONFIRMED_REPROMPT'])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class GetProductLocationIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return is_intent_name("GetProductLocationIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        
        prod_name = handler_input.request_envelope.request.intent.slots["prod_name"].value
        
        search_record = table.match('Name', prod_name)
        favourite_color = search_record['fields']['Color']
        
        speech_output = random.choice(language_prompts['GET_FAV_COLOR']).format(prod_name, favourite_color)
        reprompt = random.choice(language_prompts['GET_FAV_COLOR_REPROMPT'])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = random.choice(language_prompts["CANCEL_STOP_RESPONSE"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .set_should_end_session(True)
                .response
            )

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = random.choice(language_prompts["HELP"])
        reprompt = random.choice(language_prompts["HELP_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

# This handler handles utterances that can't be matched to any other intent handler.
class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = random.choice(language_prompts["FALLBACK"])
        reprompt = random.choice(language_prompts["FALLBACK_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class SessionEndedRequesthandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)
    
    def handle(self, handler_input):
        logger.info("Session ended with the reason: {}".format(handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response

# Exception Handlers

# This exception handler handles syntax or routing errors. If you receive an error stating 
# the request handler is not found, you have not implemented a handler for the intent or 
# included it in the skill builder below
class CatchAllExceptionHandler(AbstractExceptionHandler):
    
    def can_handle(self, handler_input, exception):
        return True
    
    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        
        speech_output = language_prompts["ERROR"]
        reprompt = language_prompts["ERROR_REPROMPT"]
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

# Interceptors

# This interceptor logs each request sent from Alexa to our endpoint.
class RequestLogger(AbstractRequestInterceptor):

    def process(self, handler_input):
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))

# This interceptor logs each response our endpoint sends back to Alexa.
class ResponseLogger(AbstractResponseInterceptor):

    def process(self, handler_input, response):
        logger.debug("Alexa Response: {}".format(response))

# This interceptor is used for supporting different languages and locales. It detects the users locale,
# loads the corresponding language prompts and sends them as a request attribute object to the handler functions.
class LocalizationInterceptor(AbstractRequestInterceptor):

    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        logger.info("Locale is {}".format(locale))
        
        try:
            with open("languages/"+str(locale)+".json") as language_data:
                language_prompts = json.load(language_data)
        except:
            with open("languages/"+ str(locale[:2]) +".json") as language_data:
                language_prompts = json.load(language_data)
        
        handler_input.attributes_manager.request_attributes["_"] = language_prompts

# Skill Builder
# Define a skill builder instance and add all the request handlers,
# exception handlers and interceptors to it.

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(TellProductLocationIntentHandler())
sb.add_request_handler(GetProductLocationIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequesthandler())

sb.add_exception_handler(CatchAllExceptionHandler())

sb.add_global_request_interceptor(LocalizationInterceptor())
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

lambda_handler = sb.lambda_handler()
