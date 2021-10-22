# SPDX-FileCopyrightText: 2020 2019-2020 SAP SE
#
# SPDX-License-Identifier: Apache-2.0

import mimetypes

from .constants import API_FIELD_CLIENT_ID, API_FIELD_DOCUMENT_TYPE, API_FIELD_ENRICHMENT, API_FIELD_TEMPLATE_ID, \
    API_FIELD_EXTRACTED_HEADER_FIELDS, API_FIELD_EXTRACTED_LINE_ITEM_FIELDS, API_REQUEST_FIELD_EXTRACTED_FIELDS, \
    API_FIELD_FILE_TYPE, API_REQUEST_FIELD_RECEIVED_DATE


def create_document_options(client_id, document_type, header_fields=None, line_item_fields=None, template_id=None,
                            received_date=None, enrichment=None):
    options = {
        API_FIELD_CLIENT_ID: client_id,
        API_FIELD_DOCUMENT_TYPE: document_type,
        API_REQUEST_FIELD_EXTRACTED_FIELDS: {}
    }

    if header_fields is None:
        header_fields = []
    elif isinstance(header_fields, str):
        header_fields = [s.strip() for s in header_fields.split(',')]
    elif not isinstance(header_fields, list):
        raise TypeError(f'Input variable \'header_fields\' has wrong type: {type(header_fields)}. Should be a string '
                        f'of comma separated values or a list of strings')
    options[API_REQUEST_FIELD_EXTRACTED_FIELDS][API_FIELD_EXTRACTED_HEADER_FIELDS] = header_fields

    if line_item_fields is None:
        line_item_fields = []
    elif isinstance(line_item_fields, str):
        line_item_fields = [s.strip() for s in line_item_fields.split(',')]
    elif not isinstance(line_item_fields, list):
        raise TypeError(f'Input variable \'line_item_fields\' has wrong type: {type(line_item_fields)}. Should be a '
                        f'string of comma separated values or a list of strings')
    options[API_REQUEST_FIELD_EXTRACTED_FIELDS][API_FIELD_EXTRACTED_LINE_ITEM_FIELDS] = line_item_fields

    if template_id is not None:
        options[API_FIELD_TEMPLATE_ID] = template_id

    if received_date is not None:
        options[API_REQUEST_FIELD_RECEIVED_DATE] = received_date

    if enrichment is not None:
        options[API_FIELD_ENRICHMENT] = enrichment

    return options


def create_capability_mapping_options(document_type, file_type, header_fields=None, line_item_fields=None):
    options = {
        API_FIELD_DOCUMENT_TYPE: document_type,
        API_FIELD_FILE_TYPE: file_type
    }

    if header_fields is None:
        header_fields = []
    elif isinstance(header_fields, str):
        header_fields = [s.strip() for s in header_fields.split(',')]
    elif not isinstance(header_fields, list):
        raise TypeError(f'Input variable \'header_fields\' has wrong type: {type(header_fields)}. Should be a string '
                        f'of comma separated values or a list of strings')
    options[API_FIELD_EXTRACTED_HEADER_FIELDS] = header_fields

    if line_item_fields is None:
        line_item_fields = []
    elif isinstance(line_item_fields, str):
        line_item_fields = [s.strip() for s in line_item_fields.split(',')]
    elif not isinstance(line_item_fields, list):
        raise TypeError(f'Input variable \'line_item_fields\' has wrong type: {type(line_item_fields)}. Should be a '
                        f'string of comma separated values or a list of strings')
    options[API_FIELD_EXTRACTED_LINE_ITEM_FIELDS] = line_item_fields

    return options


def get_mimetype(filename: str) -> str:
    return mimetypes.guess_type(filename)[0]
