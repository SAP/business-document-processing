# SPDX-FileCopyrightText: 2020 2019-2020 SAP SE
#
# SPDX-License-Identifier: Apache-2.0

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def retry_session(pool_maxsize=None, retries=3, backoff_factor=1, status_forcelist=(500, 502, 503, 504)):
    session = requests.Session()
    # see: https://urllib3.readthedocs.io/en/latest/reference/urllib3.uil.html for Retry class
    retry = Retry(total=retries,
                  read=retries,
                  status=retries,
                  connect=retries,
                  backoff_factor=backoff_factor,
                  status_forcelist=status_forcelist,
                  method_whitelist=['GET'],
                  raise_on_status=False)
    adapter = HTTPAdapter(max_retries=retry, pool_maxsize=pool_maxsize)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session
