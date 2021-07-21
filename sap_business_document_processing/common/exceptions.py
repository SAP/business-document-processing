# SPDX-FileCopyrightText: 2020 2019-2020 SAP SE
#
# SPDX-License-Identifier: Apache-2.0


class BDPApiException(Exception):
    def __init__(self, message, response=None, status_code=None):
        super(BDPApiException, self).__init__(message)
        self.response = response
        self.status_code = status_code


class BDPPollingTimeoutException(BDPApiException):
    pass


class BDPFailedAsynchronousOperationException(BDPApiException):
    pass


class BDPClientException(BDPApiException):
    pass


class BDPServerException(BDPApiException):
    pass


class BDPUnauthorizedException(BDPClientException):
    pass
