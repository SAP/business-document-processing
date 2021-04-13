# SPDX-FileCopyrightText: 2020 2019-2020 SAP SE
#
# SPDX-License-Identifier: Apache-2.0

# Best practice to provide main classes on top level?
# Could decide on different approach, see: https://docs.python-guide.org/writing/structure/ or https://pythonpackaging.info/02-Package-Structure.html
from .document_classification_client.dc_api_client import DCApiClient
from .document_information_extraction_client.dox_api_client import DoxApiClient
