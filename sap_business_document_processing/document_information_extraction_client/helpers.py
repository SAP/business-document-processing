# SPDX-FileCopyrightText: 2020 2019-2020 SAP SE
#
# SPDX-License-Identifier: Apache-2.0
import mimetypes

from .constants import API_FIELD_CLIENT_ID, API_FIELD_DOCUMENT_TYPE, API_FIELD_ENRICHMENT, API_FIELD_TEMPLATE_ID, \
    API_FIELD_EXTRACTED_HEADER_FIELDS, API_FIELD_EXTRACTED_LINE_ITEM_FIELDS, API_FIELD_SCHEMA_ID, \
    API_REQUEST_FIELD_EXTRACTED_FIELDS, API_FIELD_FILE_TYPE, API_REQUEST_FIELD_RECEIVED_DATE, API_FIELD_NAME, \
    API_FIELD_DESCRIPTION, API_FIELD_LABEL, API_FIELD_DEFAULT_EXTRACTOR, API_FIELD_FIELD_NAME, API_FIELD_SETUP_TYPE, \
    API_FIELD_STATIC, API_FIELD_SETUP_TYPE_VERSION, API_FIELD_SETUP, API_FIELD_FORMATTING_TYPE, API_FIELD_FORMATTING, \
    API_FIELD_FORMATTING_TYPE_VERSION, MODEL_TYPE_DEFAULT, SETUP_TYPE_VERSION_1, \
    SETUP_TYPE_VERSION_2, API_FIELD_TYPE, API_FIELD_PRIORITY, SETUP_TYPE_AUTO, MODEL_TYPE_LLM, \
    API_FIELD_DATATYPE, MODEL_TYPE_TEMPLATE, SETUP_TYPE_MANUAL, SETUP_TYPE_PRIORITY


def create_document_options(client_id, document_type, header_fields=None, line_item_fields=None, template_id=None,
                            schema_id=None, received_date=None, enrichment=None):
    options = {
        API_FIELD_CLIENT_ID: client_id,
        API_FIELD_DOCUMENT_TYPE: document_type,
    }

    if schema_id is not None:
        options[API_FIELD_SCHEMA_ID] = schema_id
    else:
        options[API_REQUEST_FIELD_EXTRACTED_FIELDS] = {}
        try:
            header_fields = _convert_string_to_list(header_fields)
        except TypeError:
            raise TypeError(f'Input variable \'header_fields\' has wrong type: {type(header_fields)}. Should be a '
                            f'string of comma separated values or a list of strings')
        options[API_REQUEST_FIELD_EXTRACTED_FIELDS][API_FIELD_EXTRACTED_HEADER_FIELDS] = header_fields

        try:
            line_item_fields = _convert_string_to_list(line_item_fields)
        except TypeError:
            raise TypeError(f'Input variable \'line_item_fields\' has wrong type: {type(line_item_fields)}. Should be '
                            f'a string of comma separated values or a list of strings')

        options[API_REQUEST_FIELD_EXTRACTED_FIELDS][API_FIELD_EXTRACTED_LINE_ITEM_FIELDS] = line_item_fields

    if template_id is not None:
        options[API_FIELD_TEMPLATE_ID] = template_id

    if received_date is not None:
        options[API_REQUEST_FIELD_RECEIVED_DATE] = received_date

    if enrichment is not None:
        options[API_FIELD_ENRICHMENT] = enrichment

    return options


def _convert_string_to_list(parameter) -> list:
    if parameter is None:
        parameter = []
    elif isinstance(parameter, str):
        parameter = [s.strip() for s in parameter.split(',')]
    elif not isinstance(parameter, list):
        raise TypeError
    return parameter


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


def generate_item_payload(item, setup_type_version, setup_field_type=None, datatype=None, setup_type=API_FIELD_STATIC):
    if datatype is None:
        datatype = item[API_FIELD_DATATYPE]
    payload = {
        API_FIELD_NAME: item[API_FIELD_NAME],
        API_FIELD_DESCRIPTION: item[API_FIELD_DESCRIPTION],
        API_FIELD_LABEL: item[API_FIELD_LABEL],
        API_FIELD_DEFAULT_EXTRACTOR: {
            API_FIELD_FIELD_NAME: item[API_FIELD_NAME]
        },
        API_FIELD_SETUP_TYPE: setup_type,
        API_FIELD_SETUP_TYPE_VERSION: setup_type_version,
        API_FIELD_SETUP: {
            API_FIELD_TYPE: setup_field_type,
            API_FIELD_PRIORITY: SETUP_TYPE_PRIORITY
        },
        API_FIELD_FORMATTING_TYPE: datatype,
        API_FIELD_FORMATTING: {},
        API_FIELD_FORMATTING_TYPE_VERSION: "1.0.0"
    }
    return payload


def create_list_for_header_and_line_items(items, extracted_items):
    name_to_type_list = {}
    for item in items:
        field_name = item[API_FIELD_NAME]
        name_to_type_list[field_name] = next(
            (field.get(API_FIELD_TYPE) for field in extracted_items if field.get(API_FIELD_NAME) == field_name),
            None)
        if name_to_type_list[field_name] is None:
            raise ValueError(f'fieldName not found in defaultExtractor values. Please provide valid fieldName from '
                             '/capabilities API.')
    return name_to_type_list


def create_payload_for_schema_fields(model_type, setup_type_version, header_fields, line_fields, capabilities=None):
    header_items, line_items = [], []

    if model_type == MODEL_TYPE_DEFAULT:
        header_name_to_type, line_name_to_type = {}, {}

        extracted_header_fields = capabilities.get(API_REQUEST_FIELD_EXTRACTED_FIELDS, {}) \
            .get(API_FIELD_EXTRACTED_HEADER_FIELDS, [])
        extracted_line_item_fields = capabilities.get(API_REQUEST_FIELD_EXTRACTED_FIELDS, {}) \
            .get(API_FIELD_EXTRACTED_LINE_ITEM_FIELDS, [])

        header_name_to_type = create_list_for_header_and_line_items(header_fields, extracted_header_fields)
        line_name_to_type = create_list_for_header_and_line_items(line_fields, extracted_line_item_fields)

        if setup_type_version == SETUP_TYPE_VERSION_1:
            """  FOR DEFAULT MODEL 1.0.0 """
            for item in header_fields:
                item_payload = generate_item_payload(item, SETUP_TYPE_VERSION_1,
                                                     datatype=header_name_to_type.get(item[API_FIELD_NAME]))
                header_items.append(item_payload)
            for item in line_fields:
                item_payload = generate_item_payload(item, SETUP_TYPE_VERSION_1,
                                                     datatype=line_name_to_type.get(item[API_FIELD_NAME]))
                line_items.append(item_payload)

        elif setup_type_version == SETUP_TYPE_VERSION_2:
            """  FOR DEFAULT MODEL 2.0.0 """
            for item in header_fields:
                item_payload = generate_item_payload(item, SETUP_TYPE_VERSION_2, SETUP_TYPE_AUTO,
                                                     datatype=header_name_to_type.get(item[API_FIELD_NAME]))
                header_items.append(item_payload)
            for item in line_fields:
                item_payload = generate_item_payload(item, SETUP_TYPE_VERSION_2, SETUP_TYPE_AUTO,
                                                     datatype=line_name_to_type.get(item[API_FIELD_NAME]))
                line_items.append(item_payload)

    elif model_type in [MODEL_TYPE_LLM, MODEL_TYPE_TEMPLATE]:
        if model_type == MODEL_TYPE_LLM:
            """  FOR LLM MODEL """
            setup_type = SETUP_TYPE_AUTO
        else:
            """  FOR TEMPLATE MODEL """
            setup_type = SETUP_TYPE_MANUAL
        for item in header_fields:
            item_payload = generate_item_payload(item, SETUP_TYPE_VERSION_2, setup_type)
            item_payload[API_FIELD_DEFAULT_EXTRACTOR] = {}
            header_items.append(item_payload)
        for item in line_fields:
            item_payload = generate_item_payload(item, SETUP_TYPE_VERSION_2, setup_type)
            item_payload[API_FIELD_DEFAULT_EXTRACTOR] = {}
            line_items.append(item_payload)

    return header_items, line_items
