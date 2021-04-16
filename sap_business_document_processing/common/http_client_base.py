# SPDX-FileCopyrightText: 2020 2019-2020 SAP SE
#
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import time
from oauthlib.oauth2 import BackendApplicationClient, MissingTokenError
from requests_oauthlib import OAuth2Session

from .constants import API_DOCUMENT_EXTRACTED_TEXT_FIELD,  MAX_POLLING_THREADS, MIN_POLLING_INTERVAL, FAILED_STATUSES, \
    SUCCEEDED_STATUSES
from .exceptions import BDPApiException, BDPClientException, BDPFailedAsynchronousOperationException, \
    BDPPollingTimeoutException, BDPServerException, BDPUnauthorizedException
from .helpers import add_retry_to_session, make_url, make_oauth_url


class CommonClient:
    def __init__(self,
                 base_url,
                 client_id,
                 client_secret,
                 uaa_url,
                 polling_threads=15,
                 polling_sleep=5,
                 polling_long_sleep=30,
                 polling_max_attempts=120,
                 url_path_prefix='',
                 logger_name='CommonClient',
                 logging_level=logging.WARNING):
        self.common_logger = logging.getLogger('CommonClient')
        self.common_logger.setLevel(logging_level)
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging_level)
        if polling_threads > MAX_POLLING_THREADS:
            self.logger.warning('The number of parallel polling threads of {} is too high, the number was set to '
                                'maximal allowed amount of {}'.format(polling_threads, MAX_POLLING_THREADS))
            polling_threads = MAX_POLLING_THREADS
        if polling_sleep < MIN_POLLING_INTERVAL:
            self.logger.warning('The polling interval of {} is too small, the number was set to minimal '
                                'allowed amount of {}'.format(polling_sleep, MIN_POLLING_INTERVAL))
            polling_sleep = MIN_POLLING_INTERVAL
        if polling_long_sleep < MIN_POLLING_INTERVAL:
            self.logger.warning('The polling interval for long operations of {} is too small, the number was set to '
                                'minimal allowed amount of {}'.format(polling_long_sleep, MIN_POLLING_INTERVAL))
            polling_long_sleep = MIN_POLLING_INTERVAL
        self.base_url = make_url(base_url, url_path_prefix)
        self.polling_max_attempts = polling_max_attempts
        self.polling_sleep = polling_sleep
        self.polling_long_sleep = polling_long_sleep
        self.polling_threads = polling_threads
        self.client_id = client_id
        self.client_secret = client_secret
        self.uaa_url = uaa_url
        self._session = None

    @property
    def session(self):
        if self._session is None:
            self._session = self._get_oauth_session(self.client_id, self.client_secret, self.uaa_url)
        return self._session

    def _get_oauth_session(self, client_id, client_secret, uaa_url):
        if not uaa_url or not client_id or not client_secret:
            raise BDPClientException('Authentication is missing')
        client = BackendApplicationClient(client_id)
        session = OAuth2Session(client=client)
        add_retry_to_session(session, pool_maxsize=self.polling_threads)
        tries, i = 2, 0
        for i in range(tries):
            try:
                session.fetch_token(token_url=make_oauth_url(uaa_url), client_id=client_id, client_secret=client_secret)
                return session
            except MissingTokenError as e:
                if i < tries - 1:
                    time.sleep(5)
                    continue
                else:
                    raise BDPApiException(f'Unable to fetch the Bearer Token after {tries} tries') from e

    def _poll_for_url(self,
                      path,
                      check_json_status=True,
                      success_status=200,
                      wait_status=None,
                      sleep_interval=None,
                      get_status=lambda r: r['status'],
                      log_msg_before=None,
                      log_msg_after=None,
                      **kwargs):
        if not sleep_interval:
            sleep_interval = self.polling_sleep

        if log_msg_before is not None:
            self.logger.debug(log_msg_before)
        for _ in range(self.polling_max_attempts):
            response = self.get(path, validate=False, **kwargs)
            if (wait_status is not None) and response.status_code == wait_status:
                time.sleep(sleep_interval)
            elif response.status_code == success_status:
                if check_json_status:
                    response_status = get_status(response.json())
                    if response_status in SUCCEEDED_STATUSES:
                        if log_msg_after is not None:
                            self.logger.info(log_msg_after)
                        return response
                    elif response_status in FAILED_STATUSES:
                        raise BDPFailedAsynchronousOperationException("Asynchronous job with URL '{}' failed".format(
                            self.path_to_url(path)), response=response)
                    else:
                        time.sleep(sleep_interval)
                else:
                    if log_msg_after is not None:
                        self.logger.info(log_msg_after)
                    return response
            else:
                self.raise_for_status_with_logging(response)
        raise BDPPollingTimeoutException("Polling for URL '{}' timed out after {} seconds".format(
            self.path_to_url(path), sleep_interval * self.polling_max_attempts))

    def path_to_url(self, path):
        return make_url(self.base_url, path)

    def _request(self, request_func, path: str, validate: bool, log_msg_before=None, log_msg_after=None, **kwargs):
        # add central logging here
        if log_msg_before is not None:
            self.logger.debug(log_msg_before)
        response = request_func(self.path_to_url(path), **kwargs)
        if validate:
            self.raise_for_status_with_logging(response)
        if log_msg_after is not None:
            self.logger.info(log_msg_after)
        return response

    def get(self, path: str, validate=True, **kwargs):
        return self._request(self.session.get, path, validate, **kwargs)

    def post(self, path: str, validate=True, **kwargs):
        return self._request(self.session.post, path, validate, **kwargs)

    def delete(self, path: str, validate=True, **kwargs):
        return self._request(self.session.delete, path, validate, **kwargs)

    @staticmethod
    def _validate_results(results, error_message):
        failed_results = []
        valid_results = []
        for result in results:
            failed_result = None
            if isinstance(result, BDPClientException):
                try:
                    failed_result = result.response.json()
                    failed_result['status_code'] = result.status_code
                    if failed_result.get(API_DOCUMENT_EXTRACTED_TEXT_FIELD):
                        failed_result[API_DOCUMENT_EXTRACTED_TEXT_FIELD] = failed_result[
                                                                               API_DOCUMENT_EXTRACTED_TEXT_FIELD][
                                                                           :50] + '... truncated'
                except json.JSONDecodeError:
                    failed_result = {'error': result.args[0],
                                     'status_code': result.status_code}
            elif isinstance(result, BDPApiException):
                failed_result = {'error': result.args[0]}
                if result.status_code:
                    failed_result['status_code'] = result.status_code
            elif isinstance(result, Exception):
                failed_result = {'error': result.args[0]}

            if failed_result:
                if hasattr(result, 'document_path'):
                    failed_result['document_path'] = result.document_path
                failed_results.append(failed_result)
            else:
                valid_results.append(result)

        if len(failed_results) > 0:
            raise BDPApiException(error_message + ': ' + str(failed_results))
        return valid_results

    def raise_for_status_with_logging(self, response):
        e = None
        if response.status_code == 401:
            e = BDPUnauthorizedException('Missing authorization for this service', response, status_code=401)
        elif 400 <= response.status_code < 500:
            try:
                msg = str(response.json())
            except json.JSONDecodeError:
                msg = response.text
            e = BDPClientException(msg, response=response, status_code=response.status_code)
        elif 500 <= response.status_code < 600:
            e = BDPServerException(response.text, response=response, status_code=response.status_code)

        if e is not None:
            self.common_logger.warning(f'{response.request.method} request to URL {response.url} failed '
                                       f'with body: {response.text}')
            raise e

    @staticmethod
    def _create_result_iterator(base_iterator):
        return ResultIterator(base_iterator)


class ResultIterator:
    def __init__(self, base):
        self.base = iter(base)

    def __iter__(self):
        return self

    def __next__(self):
        result = next(self.base)
        if isinstance(result, Exception):
            raise result
        return result