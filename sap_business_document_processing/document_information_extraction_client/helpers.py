# SPDX-FileCopyrightText: 2020 2019-2020 SAP SE
#
# SPDX-License-Identifier: Apache-2.0

from .capabilities import HEADER_FIELD_NAMES_FOR_DOCUMENT_TYPES, LINE_ITEM_FIELDS_NAMES_FOR_DOCUMENT_TYPES
from .constants import API_FIELD_CLIENT_ID, API_FIELD_DOCUMENT_TYPE, API_FIELD_ENRICHMENT, API_FIELD_TEMPLATE_ID, \
    API_FIELD_EXTRACTED_HEADER_FIELDS, API_FIELD_EXTRACTED_LINE_ITEM_FIELDS, API_REQUEST_FIELD_EXTRACTED_FIELDS, \
    API_REQUEST_FIELD_RECEIVED_DATE


def create_document_options(client_id, document_type):
    return {
        API_FIELD_CLIENT_ID: client_id,
        API_FIELD_DOCUMENT_TYPE: document_type,
        API_REQUEST_FIELD_EXTRACTED_FIELDS: {}
    }


def merge_document_options(options=None, client_id=None, document_type=None, header_fields=None, line_item_fields=None,
                           template_id=None, received_date=None, enrichment=None):
    if not options:
        options = create_document_options(client_id, document_type)

    if options.get(API_REQUEST_FIELD_EXTRACTED_FIELDS) is None:
        options[API_REQUEST_FIELD_EXTRACTED_FIELDS] = {}

    if client_id is not None:
        options[API_FIELD_CLIENT_ID] = client_id

    if document_type is not None:
        options[API_FIELD_DOCUMENT_TYPE] = document_type

    if header_fields:
        if isinstance(header_fields, str):
            options[API_REQUEST_FIELD_EXTRACTED_FIELDS][API_FIELD_EXTRACTED_HEADER_FIELDS] = \
                [s.strip() for s in header_fields.split(',')]
        elif isinstance(header_fields, list):
            options[API_REQUEST_FIELD_EXTRACTED_FIELDS][API_FIELD_EXTRACTED_HEADER_FIELDS] = header_fields
        else:
            raise TypeError(f'Input variable header_fields has wrong datatype: {type(header_fields)}')
    elif not line_item_fields:
        if document_type in HEADER_FIELD_NAMES_FOR_DOCUMENT_TYPES:
            options[API_REQUEST_FIELD_EXTRACTED_FIELDS][API_FIELD_EXTRACTED_HEADER_FIELDS] = \
                HEADER_FIELD_NAMES_FOR_DOCUMENT_TYPES[document_type]
        else:
            raise NotImplementedError(f'Not implemented for document type {document_type}')

    if line_item_fields:
        if isinstance(line_item_fields, str):
            options[API_REQUEST_FIELD_EXTRACTED_FIELDS][API_FIELD_EXTRACTED_LINE_ITEM_FIELDS] = \
                [s.strip() for s in line_item_fields.split(',')]
        elif isinstance(line_item_fields, list):
            options[API_REQUEST_FIELD_EXTRACTED_FIELDS][API_FIELD_EXTRACTED_LINE_ITEM_FIELDS] = line_item_fields
        else:
            raise TypeError(f'Input variable line_item_fields has wrong datatype: {type(line_item_fields)}')
    elif not header_fields:
        if document_type in LINE_ITEM_FIELDS_NAMES_FOR_DOCUMENT_TYPES:
            options[API_REQUEST_FIELD_EXTRACTED_FIELDS][API_FIELD_EXTRACTED_LINE_ITEM_FIELDS] = \
                LINE_ITEM_FIELDS_NAMES_FOR_DOCUMENT_TYPES[document_type]
        else:
            raise NotImplementedError(f'Not implemented for document type {document_type}')

    if template_id is not None:
        options[API_FIELD_TEMPLATE_ID] = template_id

    if received_date is not None:
        options[API_REQUEST_FIELD_RECEIVED_DATE] = received_date

    if enrichment is not None:
        options[API_FIELD_ENRICHMENT] = enrichment

    return options
