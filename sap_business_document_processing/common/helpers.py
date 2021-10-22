# SPDX-FileCopyrightText: 2020 2019-2020 SAP SE
#
# SPDX-License-Identifier: Apache-2.0
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def make_url(base, extension):
    if base.endswith('/'):
        base = base[:-1]
    if not extension.startswith('/'):
        extension = '/' + extension
    return base + extension


def make_oauth_url(auth_url):
    if auth_url.endswith('/'):
        auth_url = auth_url[:-1]
    if auth_url.endswith('/oauth/token'):
        return auth_url
    return make_url(auth_url, '/oauth/token')


def function_wrap_errors(function, *args):
    try:
        return function(*args)
    except Exception as e:
        return e


def get_ground_truth_json(ground_truth):
    if isinstance(ground_truth, str):
        with open(ground_truth, 'r') as file:
            return json.load(file)
    elif isinstance(ground_truth, dict):
        return ground_truth
    else:
        raise ValueError('Wrong argument type, string (path to ground truth file) or a dictionary (ground truth as '
                         'JSON format) are expected for \'ground_truth\'')


def add_retry_to_session(session: requests.Session, pool_maxsize=None, retries=3, backoff_factor=1,
                         status_forcelist=(500, 502, 503, 504)):

    # see: https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html for Retry class
    retry = Retry(total=retries,
                  read=retries,
                  status=retries,
                  connect=retries,
                  backoff_factor=backoff_factor,
                  status_forcelist=status_forcelist,
                  allowed_methods=['GET'],
                  raise_on_status=False)
    adapter = HTTPAdapter(max_retries=retry, pool_maxsize=pool_maxsize)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
