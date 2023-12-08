# SPDX-FileCopyrightText: 2020 2019-2020 SAP SE
#
# SPDX-License-Identifier: Apache-2.0
import json
import mimetypes
import os.path

from .constants import API_FIELD_CLIENT_ID, API_FIELD_DOCUMENT_TYPE, API_FIELD_ENRICHMENT, API_FIELD_TEMPLATE_ID, \
    API_FIELD_EXTRACTED_HEADER_FIELDS, API_FIELD_EXTRACTED_LINE_ITEM_FIELDS, API_REQUEST_FIELD_EXTRACTED_FIELDS, \
    API_FIELD_FILE_TYPE, API_REQUEST_FIELD_RECEIVED_DATE, \
    DEFAULT_EXTRACTOR_FIELDS_FILE_PATH, SETUP_TYPE_VERSION_1, API_FIELD_SCHEMA_NAME, API_FIELD_DESCRIPTION, \
    API_FIELD_LABEL, API_FIELD_DEFAULT_EXTRACTOR, API_FIELD_FIELD_NAME, API_FIELD_SETUP_TYPE, \
    API_FIELD_SETUP_TYPE_VERSION, API_FIELD_SETUP, API_FIELD_FORMATTING_TYPE, API_FIELD_FORMATTING, \
    API_FIELD_FORMATTING_TYPE_VERSION, API_FIELD_STATIC, API_FIELD_TYPE, API_FIELD_IS_LINE_ITEM, SETUP_TYPE_AUTO, \
    API_FIELD_PRIORITY, MODEL_TYPE_LLM, SETUP_TYPE_VERSION_2, MODEL_TYPE_TEMPLATE, SETUP_TYPE_MANUAL, \
    API_FIELD_DATATYPE, MODEL_TYPE_DEFAULT
from ..common.exceptions import DoxApiInvalidDataProvidedError, DOXInternalServerError


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


def generate_item_payload(item, setup_type_version, datatype, setup_fields=None):
    payload = {
        API_FIELD_SCHEMA_NAME: item[API_FIELD_SCHEMA_NAME],
        API_FIELD_DESCRIPTION: item[API_FIELD_DESCRIPTION],
        API_FIELD_LABEL: item[API_FIELD_LABEL],
        API_FIELD_DEFAULT_EXTRACTOR: {
            API_FIELD_FIELD_NAME: item[API_FIELD_SCHEMA_NAME]
        },
        API_FIELD_SETUP_TYPE: API_FIELD_STATIC,
        API_FIELD_SETUP_TYPE_VERSION: setup_type_version,
        API_FIELD_SETUP: setup_fields,
        API_FIELD_FORMATTING_TYPE: datatype[item[API_FIELD_SCHEMA_NAME]],
        API_FIELD_FORMATTING: {},
        API_FIELD_FORMATTING_TYPE_VERSION: "1.0.0"
    }
    return payload


def create_payload_for_schema_fields(model_type, items):
    header_items, line_items = [], []
    current_directory = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_directory, DEFAULT_EXTRACTOR_FIELDS_FILE_PATH)
    header_name_to_type, line_name_to_type = [], []

    if model_type in [MODEL_TYPE_DEFAULT + SETUP_TYPE_VERSION_1, MODEL_TYPE_DEFAULT + SETUP_TYPE_VERSION_2]:
        if os.path.exists(json_file_path):
            with open(str(json_file_path), 'r') as file:
                data = json.load(file)

            extracted_header_fields = data.get(API_REQUEST_FIELD_EXTRACTED_FIELDS, {}) \
                .get(API_FIELD_EXTRACTED_HEADER_FIELDS, [])
            extracted_line_item_fields = data.get(API_REQUEST_FIELD_EXTRACTED_FIELDS, {}) \
                .get(API_FIELD_EXTRACTED_LINE_ITEM_FIELDS, [])

            for item in items:
                schema_name = item[API_FIELD_SCHEMA_NAME]
                is_line_item = item[API_FIELD_IS_LINE_ITEM]

                matching_fields = [field for field in extracted_header_fields if
                                   field.get(API_FIELD_SCHEMA_NAME) == schema_name] if not is_line_item \
                    else [field for field in extracted_line_item_fields
                          if field.get(API_FIELD_SCHEMA_NAME) == schema_name]

                if matching_fields:
                    if not is_line_item:
                        header_name_to_type.append({schema_name: field[API_FIELD_TYPE] for field in matching_fields})
                    else:
                        line_name_to_type.append({schema_name: field[API_FIELD_TYPE] for field in matching_fields})
                else:
                    error_msg = 'fieldName not found in defaultExtractor values. Please provide valid fieldName from ' \
                                '/capabilities API.'
                    raise DoxApiInvalidDataProvidedError(error_msg)
        else:
            error_msg = 'Internal Server Error'
            raise DOXInternalServerError(error_msg)

    setup_fields = {
        API_FIELD_TYPE: None,
        API_FIELD_PRIORITY: '1'
    }

    if model_type == MODEL_TYPE_DEFAULT + SETUP_TYPE_VERSION_1:
        """  FOR DEFAULT MODEL 1.0.0 """
        for item in items:
            if not item[API_FIELD_IS_LINE_ITEM]:
                value = {item[API_FIELD_SCHEMA_NAME]: next((field[item[API_FIELD_SCHEMA_NAME]] for field
                                                            in header_name_to_type if item[API_FIELD_SCHEMA_NAME]
                                                            in field), None)}
                item_payload = generate_item_payload(item, SETUP_TYPE_VERSION_1, value)
                header_items.append(item_payload)
            else:
                value = {item[API_FIELD_SCHEMA_NAME]: next((field[item[API_FIELD_SCHEMA_NAME]] for field
                                                            in line_name_to_type if item[API_FIELD_SCHEMA_NAME]
                                                            in field), None)}
                item_payload = generate_item_payload(item, SETUP_TYPE_VERSION_1, value)
                line_items.append(item_payload)
    elif model_type == MODEL_TYPE_DEFAULT + SETUP_TYPE_VERSION_2:
        """  FOR DEFAULT MODEL 2.0.0 """
        setup_fields[API_FIELD_TYPE] = SETUP_TYPE_AUTO
        for item in items:
            if not item[API_FIELD_IS_LINE_ITEM]:
                value = {item[API_FIELD_SCHEMA_NAME]: next((field[item[API_FIELD_SCHEMA_NAME]] for field
                                                            in header_name_to_type if item[API_FIELD_SCHEMA_NAME]
                                                            in field), None)}
                item_payload = generate_item_payload(item, SETUP_TYPE_VERSION_2, value, setup_fields=setup_fields)
                header_items.append(item_payload)
            else:
                value = {item[API_FIELD_SCHEMA_NAME]: next((field[item[API_FIELD_SCHEMA_NAME]] for field
                                                            in line_name_to_type if item[API_FIELD_SCHEMA_NAME]
                                                            in field), None)}
                item_payload = generate_item_payload(item, SETUP_TYPE_VERSION_2, value, setup_fields=setup_fields)
                line_items.append(item_payload)
    elif model_type == MODEL_TYPE_LLM:
        """  FOR LLM MODEL """
        setup_fields[API_FIELD_TYPE] = SETUP_TYPE_AUTO
        for item in items:
            item_payload = generate_item_payload(item, SETUP_TYPE_VERSION_2,
                                                 {item[API_FIELD_SCHEMA_NAME]: item[API_FIELD_DATATYPE]},
                                                 setup_fields=setup_fields)
            item_payload[API_FIELD_DEFAULT_EXTRACTOR] = {}
            if not item[API_FIELD_IS_LINE_ITEM]:
                header_items.append(item_payload)
            else:
                line_items.append(item_payload)
    elif model_type == MODEL_TYPE_TEMPLATE:
        """  FOR TEMPLATE MODEL """
        setup_fields[API_FIELD_TYPE] = SETUP_TYPE_MANUAL
        for item in items:
            item_payload = generate_item_payload(item, SETUP_TYPE_VERSION_2,
                                                 {item[API_FIELD_SCHEMA_NAME]: item[API_FIELD_DATATYPE]},
                                                 setup_fields=setup_fields)
            item_payload[API_FIELD_DEFAULT_EXTRACTOR] = {}
            if not item[API_FIELD_IS_LINE_ITEM]:
                header_items.append(item_payload)
            else:
                line_items.append(item_payload)

    payload = {
        API_FIELD_EXTRACTED_HEADER_FIELDS: header_items,
        API_FIELD_EXTRACTED_LINE_ITEM_FIELDS: line_items
    }
    return payload
