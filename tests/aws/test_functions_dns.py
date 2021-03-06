import json
import unittest

from unittest.mock import MagicMock, Mock, patch, mock_open

import dynamicdns

from dynamicdns.aws.functions.dns import handle 

from dynamicdns.models import Error

from dynamicdns.aws.route53 import Route53Provider
from dynamicdns.aws.s3config import S3ConfigProvider
from dynamicdns.aws.boto3wrapper import Boto3Wrapper

from dynamicdns.processor import Processor


class TestDNS(unittest.TestCase):


    @patch('dynamicdns.processor.factory')
    @patch('dynamicdns.aws.s3config.factory')
    def testDNSSuccess(self, mock_config, mock_processor):
        self.__setUpMocks(configFailed=False, hashFailed=False, updateFailed=False, mock_config=mock_config, mock_processor=mock_processor)

        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}
        
        result = handle(event, context)
        self.__checkJson(result, "SUCCESS", "OK")

        event = {
            'queryStringParameters': { 'raw': '', 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}
        
        result = handle(event, context)
        self.__checkRaw(result, "SUCCESS", "OK")


    @patch('dynamicdns.processor.factory')
    @patch('dynamicdns.aws.s3config.factory')
    def testDNSFailConfig(self, mock_config, mock_processor):
        self.__setUpMocks(configFailed=True, hashFailed=False, updateFailed=False, mock_config=mock_config, mock_processor=mock_processor)
        
        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}

        result = handle(event, context)
        self.__checkJson(result, "FAIL", "Config Load failed")

        event = {
            'queryStringParameters': { 'raw': '', 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}
        
        result = handle(event, context)
        self.__checkRaw(result, "FAIL", "Config Load failed")


    @patch('dynamicdns.processor.factory')
    @patch('dynamicdns.aws.s3config.factory')
    def testDNSFailHashcheck(self, mock_config, mock_processor):
        self.__setUpMocks(configFailed=False, hashFailed=True, updateFailed=False, mock_config=mock_config, mock_processor=mock_processor)

        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}

        result = handle(event, context)
        self.__checkJson(result, "FAIL", "Hashcheck failed")

        event = {
            'queryStringParameters': { 'raw': '', 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}

        result = handle(event, context)
        self.__checkRaw(result, "FAIL", "Hashcheck failed")


    @patch('dynamicdns.processor.factory')
    @patch('dynamicdns.aws.s3config.factory')
    def testDNSFailUpdate(self, mock_config, mock_processor):
        self.__setUpMocks(configFailed=False, hashFailed=False, updateFailed=True, mock_config=mock_config, mock_processor=mock_processor)

        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}

        result = handle(event, context)
        self.__checkJson(result, "FAIL", "Update failed")

        event = {
            'queryStringParameters': { 'raw': '', 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}

        result = handle(event, context)
        self.__checkRaw(result, "FAIL", "Update failed")


    @patch('dynamicdns.processor.factory')
    @patch('dynamicdns.aws.s3config.factory')
    def testDNSMissingParamInternalIp(self, mock_config, mock_processor):
        self.__setUpMocks(configFailed=False, hashFailed=False, updateFailed=False, mock_config=mock_config, mock_processor=mock_processor)

        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}
        
        result = handle(event, context)
        self.__checkJson(result, "SUCCESS", "OK")

        event = {
            'queryStringParameters': { 'raw': '', 'hostname': 'abc', 'hash': 'xyz'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}
        
        result = handle(event, context)
        self.__checkRaw(result, "SUCCESS", "OK")


    @patch('dynamicdns.processor.factory')
    @patch('dynamicdns.aws.s3config.factory')
    def testDNSMissingParamHostname(self, mock_config, mock_processor):
        self.__setUpMocks(configFailed=False, hashFailed=False, updateFailed=False, mock_config=mock_config, mock_processor=mock_processor)

        event = {
            'queryStringParameters': { 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}
        
        result = handle(event, context)
        self.__checkJson(result, "FAIL", "You have to pass 'hostname' querystring parameters.")

        event = {
            'queryStringParameters': { 'raw': '', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}
        
        result = handle(event, context)
        self.__checkRaw(result, "FAIL", "You have to pass 'hostname' querystring parameters.")


    @patch('dynamicdns.processor.factory')
    @patch('dynamicdns.aws.s3config.factory')
    def testDNSMissingParamHash(self, mock_config, mock_processor):
        self.__setUpMocks(configFailed=False, hashFailed=False, updateFailed=False, mock_config=mock_config, mock_processor=mock_processor)
 
        event = {
            'queryStringParameters': { 'hostname': 'abc', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}

        result = handle(event, context)
        self.__checkJson(result, "FAIL", "You have to pass 'hash' querystring parameters.")

        event = {
            'queryStringParameters': { 'raw': '', 'hostname': 'abc', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}

        result = handle(event, context)
        self.__checkRaw(result, "FAIL", "You have to pass 'hash' querystring parameters.")


    @patch('dynamicdns.processor.factory')
    @patch('dynamicdns.aws.s3config.factory')
    def testDNSMissingParamSourceIp(self, mock_config, mock_processor):
        self.__setUpMocks(configFailed=False, hashFailed=False, updateFailed=False, mock_config=mock_config, mock_processor=mock_processor)


        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'}
        }
        context = {}

        result = handle(event, context)
        self.__checkJson(result, "FAIL", "Source IP address cannot be extracted from request context.")

        event = {
            'queryStringParameters': { 'raw': '', 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'}
        }
        context = {}

        result = handle(event, context)
        self.__checkRaw(result, "FAIL", "Source IP address cannot be extracted from request context.")


        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': {}
        }
        context = {}
        result = handle(event, context)
        self.__checkJson(result, "FAIL", "Source IP address cannot be extracted from request context.")

        event = {
            'queryStringParameters': { 'raw': '', 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': {}
        }
        context = {}
        result = handle(event, context)
        self.__checkRaw(result, "FAIL", "Source IP address cannot be extracted from request context.")


        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': None
        }
        context = {}
        result = handle(event, context)
        self.__checkJson(result, "FAIL", "Source IP address cannot be extracted from request context.")

        event = {
            'queryStringParameters': { 'raw': '', 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': None
        }
        context = {}
        result = handle(event, context)
        self.__checkRaw(result, "FAIL", "Source IP address cannot be extracted from request context.")


        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': {} } 
        }
        context = {}
        result = handle(event, context)
        self.__checkJson(result, "FAIL", "Source IP address cannot be extracted from request context.")

        event = {
            'queryStringParameters': { 'raw': '', 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': {} } 
        }
        context = {}
        result = handle(event, context)
        self.__checkRaw(result, "FAIL", "Source IP address cannot be extracted from request context.")


# -----------------------------------------------------------------------------
# TESTING HELPER METHODS
# -----------------------------------------------------------------------------

    def __setUpMocks(self, configFailed: bool, hashFailed: bool, updateFailed: bool, mock_config, mock_processor):

        config = S3ConfigProvider(None)

        config.aws_region = MagicMock(return_value = 'aws_region')
        config.route_53_record_ttl = MagicMock(return_value = 'route_53_record_ttl')
        config.route_53_record_type = MagicMock(return_value = 'route_53_record_type')
        config.route_53_zone_id = MagicMock(return_value = 'route_53_zone_id')
        config.shared_secret = MagicMock(return_value = 'shared_secret')

        if configFailed:
            config.load = MagicMock(return_value = Error("Config Load failed"))
        else:
            config.load = MagicMock(return_value = config)

        mock_config.return_value = config

        processor = Processor(None)
        if hashFailed:
            processor.checkhash = MagicMock(return_value = Error("Hashcheck failed"))
        else:
            processor.checkhash = MagicMock(return_value = None)
        
        if updateFailed:
            processor.update = MagicMock(return_value = Error("Update failed"))
        else:
            processor.update = MagicMock(return_value = "OK")

        mock_processor.return_value = processor

    def __checkJson(self, result, status, message):
        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{"status": "' + status + '", "message": "' + message + '"}')
        self.assertEqual(a, b)

    def __checkRaw(self, result, status, message):
        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'text/plain')        
        self.assertEqual(result['body'], status + '\n' + message)


if __name__ == '__main__':
    unittest.main()
