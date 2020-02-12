from base64 import b64encode
import json
import logging
import requests
import time
from urllib.parse import urljoin

from .http_request_retry import retry_session

STATUS_SUCCEEDED = 'SUCCEEDED'
STATUS_FAILED = 'FAILED'


class CommonClient:
    def __init__(self,
                 base_url,
                 client_id,
                 client_secret,
                 uaa_url,
                 polling_threads=20,
                 polling_sleep=1,
                 polling_long_sleep=30,
                 polling_max_attempts=200,
                 url_path_prefix='',
                 logging_level=logging.WARNING):
        self.logger = logging.getLogger('CommonClient')
        self.logger.setLevel(logging_level)
        self.same_line_logger = logging.getLogger('CommonClientSameLine')
        single_line_stream = logging.StreamHandler()
        single_line_stream.terminator = ''
        self.same_line_logger.addHandler(single_line_stream)
        headers = {'Authorization': 'Bearer {}'.format(self.get_access_token(client_id, client_secret, uaa_url))}
        if base_url[-1] != '/':
            base_url += '/'
        base_url += url_path_prefix
        self.base_url = base_url
        self.session = retry_session(pool_maxsize=polling_threads)
        self.session.headers = headers
        self.polling_max_attempts = polling_max_attempts
        self.polling_sleep = polling_sleep
        self.polling_long_sleep = polling_long_sleep
        self.polling_threads = polling_threads

    # Authentication
    def get_access_token(self, client_id, client_secret, uaa_url):
        self.logger.debug('Getting an access token from URL {}'.format(uaa_url))
        uaa_get_token_url = urljoin(uaa_url, 'oauth/token')
        token_auth_header = 'Basic {}'.format(
            b64encode('{}:{}'.format(client_id, client_secret).encode('utf-8')).decode())
        payload = 'grant_type=client_credentials'
        headers = {
            'authorization': token_auth_header,
            'cache-control': "no-cache",
            'content-type': "application/x-www-form-urlencoded"
        }
        response = requests.post(uaa_get_token_url, data=payload, headers=headers)
        response.raise_for_status()
        self.logger.info('Authentication finished successfully')
        return response.json().get('access_token')

    def _poll_for_url(self,
                      url,
                      payload=None,
                      check_json_status=True,
                      success_status=200,
                      wait_status=409,
                      sleep_interval=None):
        if not sleep_interval:
            sleep_interval = self.polling_sleep
        for _ in range(0, self.polling_max_attempts):
            response = self.session.get(url, json=payload)
            if response.status_code == wait_status:
                self.same_line_logger.info('.')
                time.sleep(sleep_interval)
            elif response.status_code == success_status:
                if check_json_status:
                    response_json = response.json()
                    if response_json['status'] == STATUS_SUCCEEDED:
                        return response
                    elif response_json['status'] == STATUS_FAILED:
                        raise FailedCallException(response)
                    else:
                        self.same_line_logger.info('.')
                        time.sleep(sleep_interval)
                else:
                    return response
            else:
                response.raise_for_status()
        raise PollingTimeoutException("Polling for URL {} timed out after {} seconds".format(
            url, sleep_interval * self.polling_max_attempts))

    def path_to_url(self, path):
        return self.base_url + path

    @staticmethod
    def _function_wrap_errors(function, *args):
        try:
            return function(*args)
        except PollingTimeoutException as e:
            return {'status': STATUS_FAILED, 'message': str(e)}
        except (requests.HTTPError, FailedCallException) as e:
            try:
                result = e.response.json()
            except Exception:
                result = {'response_text': e.response.text}
            result['status'] = STATUS_FAILED
            result['response_code'] = e.response.status_code
            return result
        except Exception as e:
            return {'status': STATUS_FAILED, 'message': str(e)}


class PollingTimeoutException(Exception):
    pass


class FailedCallException(Exception):
    def __init__(self, response):
        self.response = response

    def __str__(self):
        return json.dumps(self.response.json())
