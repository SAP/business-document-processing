# SPDX-FileCopyrightText: 2020 2019-2020 SAP SE
#
# SPDX-License-Identifier: Apache-2.0

from concurrent.futures import ThreadPoolExecutor
import json
import logging
from pathlib import Path
from typing import Iterator, List, Union

from sap_business_document_processing.common.http_client_base import CommonClient
from sap_business_document_processing.common.helpers import get_ground_truth_json, function_wrap_errors
from .constants import API_FIELD_CLIENT_ID, API_FIELD_CLIENT_LIMIT, API_FIELD_CLIENT_NAME, API_FIELD_ID, \
    API_FIELD_EXTRACTED_VALUES, API_FIELD_RESULTS, API_FIELD_RETURN_NULL, API_FIELD_STATUS, API_FIELD_VALUE, \
    API_FIELD_DATA_FOR_RETRAINING, API_HEADER_ACCEPT, API_REQUEST_FIELD_CLIENT_START_WITH, API_REQUEST_FIELD_FILE, \
    API_REQUEST_FIELD_LIMIT, API_REQUEST_FIELD_OFFSET, API_REQUEST_FIELD_OPTIONS, API_REQUEST_FIELD_PAYLOAD, \
    API_REQUEST_FIELD_ENRICHMENT_COMPANYCODE, API_REQUEST_FIELD_ENRICHMENT_ID, API_REQUEST_FIELD_ENRICHMENT_SUBTYPE, \
    API_REQUEST_FIELD_ENRICHMENT_SYSTEM, API_REQUEST_FIELD_ENRICHMENT_TYPE, CONTENT_TYPE_PDF, CONTENT_TYPE_PNG, \
    CONTENT_TYPE_UNKNOWN, DATA_TYPE_BUSINESS_ENTITY, DOCUMENT_TYPE_ADVICE, FILE_TYPE_EXCEL
from .endpoints import CAPABILITIES_ENDPOINT, CLIENT_ENDPOINT, CLIENT_MAPPING_ENDPOINT, DATA_ACTIVATION_ASYNC_ENDPOINT,\
    DATA_ACTIVATION_ID_ENDPOINT, DATA_ENDPOINT, DATA_ASYNC_ENDPOINT, DATA_ID_ENDPOINT, DOCUMENT_ENDPOINT, \
    DOCUMENT_CONFIRM_ENDPOINT, DOCUMENT_ID_ENDPOINT, DOCUMENT_ID_REQUEST_ENDPOINT, DOCUMENT_PAGE_ENDPOINT, \
    DOCUMENT_PAGE_DIMENSIONS_ENDPOINT, DOCUMENT_PAGES_DIMENSIONS_ENDPOINT, DOCUMENT_PAGE_TEXT_ENDPOINT, \
    DOCUMENT_PAGES_TEXT_ENDPOINT
from .helpers import create_document_options, create_capability_mapping_options, get_mimetype


class DoxApiClient(CommonClient):
    """
    This class provides an interface to access SAP Document Information Extraction REST API from a Python application.
    The structure of the values returned by all the methods is documented in the API reference:
    https://help.sap.com/viewer/5fa7265b9ff64d73bac7cec61ee55ae6/SHIP/en-US/ded7d34e60f1422ba2e04e892a7f0e25.html

    :param base_url: The service URL taken from the service key (key 'url' in service key JSON)
    :param client_id: The XSUAA client ID taken from the service key (key 'uaa.clientid' in service key JSON)
    :param client_secret: The XSUAA client secret taken from the service key (key 'uaa.clientsecret' in service key JSON)
    :param uaa_url: The XSUAA URL taken from the service key (key 'uaa.url' in the service key JSON)
    :param polling_threads: Number of threads used to poll for asynchronous APIs
    :param polling_sleep: Number of seconds to wait between the polling attempts for APIs, the minimal value is 0.2
    :param polling_max_attempts: Maximum number of attempts used to poll for asynchronous APIs
    :param logging_level: INFO level will log the operations progress, the default level WARNING should not
    produce any logs
    """

    def __init__(self,
                 base_url,
                 client_id,
                 client_secret,
                 uaa_url,
                 url_path_prefix='document-information-extraction/v1/',
                 polling_threads=5,
                 polling_sleep=5,
                 polling_max_attempts=60,
                 logging_level=logging.WARNING):
        """
        Creates a new instance of a client object to access the SAP Document Information Extraction service
        """
        super(DoxApiClient, self).__init__(base_url=base_url,
                                           client_id=client_id,
                                           client_secret=client_secret,
                                           uaa_url=uaa_url,
                                           polling_threads=polling_threads,
                                           polling_sleep=polling_sleep,
                                           polling_max_attempts=polling_max_attempts,
                                           url_path_prefix=url_path_prefix,
                                           logger_name='DoxApiClient',
                                           logging_level=logging_level)

    def get_capabilities(self) -> dict:
        """
        Gets the capabilities available for the service instance.
        :return: Dictionary with available extraction fields, enrichment and document types.
        """
        response = self.get(CAPABILITIES_ENDPOINT,
                            log_msg_before='Getting all available capabilities',
                            log_msg_after='Successfully got all available capabilities')
        return response.json()

    def create_client(self, client_id, client_name) -> dict:
        """
        Creates a new client for whom a document can be uploaded
        :param client_id: The ID of the new client
        :param client_name: The name of the new client
        :return: The API endpoint response as dictionary
        """
        return self.create_clients([{
            API_FIELD_CLIENT_ID: client_id,
            API_FIELD_CLIENT_NAME: client_name
        }])

    def create_clients(self, clients: list) -> dict:
        """
        Creates one or more clients for whom documents can be uploaded
        :param clients: A list of clients to be created. For the format of a client see documentation
        :return: The API endpoint response as dictionary
        """
        response = self.post(CLIENT_ENDPOINT, json={API_FIELD_VALUE: clients},
                             log_msg_before=f'Creating {len(clients)} clients',
                             log_msg_after=f'Successfully created {len(clients)} clients')
        return response.json()

    def get_clients(self, top: int = 100, skip: int = None, client_id_starts_with: str = None) -> List[dict]:
        """
        Gets all existing clients filtered by the parameters
        :param top: The maximum number of clients to get. Default is 100
        :param skip: (optional) Index of the first client to get
        :param client_id_starts_with: (optional) Filters the clients by the characters the ID starts with
        :return: List of existing clients as dictionaries corresponding to the 'payload' part of the json response
        """
        params = {API_FIELD_CLIENT_LIMIT: top}
        if client_id_starts_with is not None:
            params[API_REQUEST_FIELD_CLIENT_START_WITH] = client_id_starts_with
        if skip is not None:
            params[API_REQUEST_FIELD_OFFSET] = skip

        response = self.get(CLIENT_ENDPOINT, params=params,
                            log_msg_before='Getting up to {} clients{}'.format(
                                top, f' that start with \'{client_id_starts_with}\'' if client_id_starts_with else ''))
        self.logger.info(f'Successfully got {len(response.json()[API_REQUEST_FIELD_PAYLOAD])} clients')
        return response.json()[API_REQUEST_FIELD_PAYLOAD]

    def delete_client(self, client_id) -> dict:
        """
        Deletes a client with the given client ID
        :param client_id: The ID of the client to be deleted
        :return: The API endpoint response as dictionary
        """
        return self.delete_clients([client_id])

    def delete_clients(self, client_ids: list = None) -> dict:
        """
        Deletes multiple clients with the given client IDs
        :param client_ids: (optional) List of IDs of clients to be deleted. If no IDs are provided, all clients will be
        deleted
        :return: The API endpoint response as dictionary
        """
        payload = {API_FIELD_VALUE: client_ids} if (client_ids is not None) else {}

        response = self.delete(CLIENT_ENDPOINT, json=payload,
                               log_msg_before=f"Deleting {len(client_ids) if client_ids else 'all'} clients",
                               log_msg_after='Successfully deleted clients')
        return response.json()

    def post_client_capability_mapping(self, client_id, document_type: str = DOCUMENT_TYPE_ADVICE,
                                       file_type: str = FILE_TYPE_EXCEL, header_fields: Union[str, List[str]] = None,
                                       line_item_fields: Union[str, List[str]] = None) -> dict:
        """
        Post the client capability mapping for the Identifier API provided by the customer to the entity client DB
        :param client_id: The ID of the client for which to upload the capability mapping
        :param document_type: The document type of for which the mapping applies. Default is 'paymentAdvice'
        :param file_type: The file type for which the mapping applies. Default is 'Excel'
        :param header_fields: A list of mappings for the header fields. For the format see documentation
        :param line_item_fields: A list of mappings for the line item fields. For the format see documentation
        :return: The API endpoint response as dictionary
        """
        options = create_capability_mapping_options(document_type, file_type, header_fields, line_item_fields)
        return self.post_client_capability_mapping_with_options(client_id, options)

    def post_client_capability_mapping_with_options(self, client_id, options: dict) -> dict:
        """
        Post the client capability mapping for the Identifier API provided by the customer to the entity client DB
        :param client_id: The ID of the client for which to upload the capability mapping
        :param options: The mapping that should be uploaded. For the format see documentation
        :return: The API endpoint response as dictionary
        """
        response = self.post(CLIENT_MAPPING_ENDPOINT, params={API_FIELD_CLIENT_ID: client_id},
                             data={API_REQUEST_FIELD_OPTIONS: json.dumps(options)},
                             log_msg_before=f'Create custom capability mapping for client {client_id}',
                             log_msg_after=f'Successfully created custom capability mapping for client {client_id}')
        return response.json()

    def extract_information_from_document(self, document_path: str, client_id, document_type: str,
                                          mime_type: str = CONTENT_TYPE_PDF,
                                          header_fields: Union[str, List[str]] = None,
                                          line_item_fields: Union[str, List[str]] = None, template_id=None,
                                          received_date=None, enrichment=None, return_null_values: bool = False) -> dict:
        """
        Extracts the information from a document. The function will run until a processing result can be returned or
        a timeout is reached
        :param document_path: The path to the document
        :param client_id: The client ID for which the document should be uploaded
        :param document_type: The type of the document being uploaded. For available document types see documentation
        :param mime_type: Content type of the uploaded file. If 'unknown' is given, the content type is fetched
        automatically. Default is 'application/pdf'. The 'constants.py' file contains
        CONTENT_TYPE_[JPEG, PDF, PNG, TIFF, UNKNOWN] that can be used here.
        :param header_fields: A list of header fields to be extracted. Can be given as list of strings or as comma
        separated string. If none are given, no header fields will be extracted
        :param line_item_fields: A list of line item fields to be extracted. Can be given as list of strings or as comma
        separated string. If none are given, no line item fields will be extracted
        :param template_id: (optional) The ID of the template to be used for this document
        :param received_date: (optional) The date the document was received
        :param enrichment: (optional) A dictionary of entities that should be used for entity matching
        :param return_null_values: Flag if fields with null as value should be included in the response or not.
        Default is False
        :return: The extracted information of the document as dictionary
        """
        return next(self.extract_information_from_documents([document_path], client_id, document_type, mime_type,
                                                            header_fields=header_fields,
                                                            line_item_fields=line_item_fields, template_id=template_id,
                                                            received_date=received_date, enrichment=enrichment,
                                                            return_null_values=return_null_values))

    def extract_information_from_document_with_options(self, document_path: str, options: dict,
                                                       mime_type: str = CONTENT_TYPE_PDF,
                                                       return_null_values: bool = False) -> dict:
        """
        Extracts the information from a document. The function will run until a processing result can be returned or
        a timeout is reached.
        :param document_path: The path to the document
        :param options: The options for processing the document as dictionary. It has to include at least a valid client
        ID and document type
        :param mime_type: Content type of the uploaded file. If 'unknown' is given, the content type is fetched
        automatically. Default is 'application/pdf'. The 'constants.py' file contains
        CONTENT_TYPE_[JPEG, PDF, PNG, TIFF, UNKNOWN] that can be used here.
        :param return_null_values: Flag if fields with null as value should be included in the response or not.
        Default is False
        :return: The extracted information of the document as dictionary
        """
        return next(self.extract_information_from_documents_with_options([document_path], options, mime_type,
                                                                         return_null_values=return_null_values))

    def extract_information_from_documents(self, document_paths: List[str], client_id, document_type: str,
                                           mime_type: str = CONTENT_TYPE_PDF, mime_type_list: List[str] = None,
                                           header_fields: Union[str, List[str]] = None,
                                           line_item_fields: Union[str, List[str]] = None, template_id=None,
                                           received_date=None, enrichment=None,
                                           return_null_values: bool = False) -> Iterator[dict]:
        """
        Extracts the information from multiple documents. The function will run until all documents have been processed
        or a timeout is reached. The given parameters will be used for all documents
        :param document_paths: A list of paths to the documents
        :param client_id: The client ID for which the documents should be uploaded
        :param document_type: The type of the document being uploaded. For available document types see documentation
        :param mime_type: Content type that is used for all uploaded files. If 'unknown' is given, the content type is
        fetched automatically. Default is 'application/pdf'. The 'constants.py' file contains
        CONTENT_TYPE_[JPEG, PDF, PNG, TIFF, UNKNOWN] that can be used here.
        :param mime_type_list: A list of content types for each file to be uploaded. Has to have the same length as
        'document_paths'. If this parameter is given, 'mime_type' will be ignored.
        :param header_fields: A list of header fields to be extracted. Can be passed as list of strings or as comma
        separated string. If none are given, no header fields will be extracted
        :param line_item_fields: A list of line item fields to be extracted. Can be passed as list of strings
        or as comma separated string. If none are given, no line items fields are extracted
        :param template_id: (optional) The ID of the template to be used for the documents
        :param received_date: (optional) The date the documents were received
        :param enrichment: (optional) A dictionary of entities that should be used for entity matching. For the format
        see documentation
        :param return_null_values: Flag if fields with null as value should be included in the responses or not.
        Default is False
        :return: An iterator with extracted information for successful documents and exceptions for failed documents.
        Use next(iterator) within a try-catch block to filter the failed documents.
        """
        options = create_document_options(client_id, document_type, header_fields, line_item_fields, template_id,
                                          received_date, enrichment)
        return self.extract_information_from_documents_with_options(document_paths, options, mime_type, mime_type_list,
                                                                    return_null_values)

    def extract_information_from_documents_with_options(self, document_paths: List[str], options: dict,
                                                        mime_type: str = CONTENT_TYPE_PDF,
                                                        mime_type_list: List[str] = None,
                                                        return_null_values: bool = False) -> Iterator[dict]:
        """
        Extracts the information from multiple documents. The function will run until all documents have been processed
        or a timeout is reached. The given options will be used for all documents
        :param document_paths: A list of paths to the documents
        :param options: The options for processing the documents as dictionary. It has to include at least a valid
        client ID and document type
        :param mime_type: Content type that is used for all uploaded files. If 'unknown' is given, the content type is
        fetched automatically. Default is 'application/pdf'. The 'constants.py' file contains
        CONTENT_TYPE_[JPEG, PDF, PNG, TIFF, UNKNOWN] that can be used here.
        :param mime_type_list: A list of content types for each file to be uploaded. Has to have the same length as
        'document_paths'. If this parameter is given, 'mime_type' will be ignored.
        :param return_null_values: Flag if fields with null as value should be included in the responses or not.
        Default is False
        :return: An iterator with extracted information for successful documents and exceptions for failed documents.
        Use next(iterator) within a try-catch block to filter the failed documents.
        """
        if not isinstance(document_paths, list) or len(document_paths) == 0:
            raise ValueError(f'Expected argument \'document_paths\' to be a non-empty list of paths to documents to be '
                             f'uploaded, but got {document_paths}')
        number_of_documents = len(document_paths)
        if mime_type_list is None:
            mime_type_list = [mime_type] * number_of_documents
        elif not isinstance(mime_type_list, list) or len(mime_type_list) != number_of_documents:
            raise ValueError(f'The argument \'mime_type_list\' has to be a list of the same length as '
                             f'\'document_paths\', but got {mime_type_list}')

        client_id = options.get(API_FIELD_CLIENT_ID)
        self.logger.debug(
            f'Starting upload of {number_of_documents} documents for client {client_id} in parallel using '
            f'{self.polling_threads} threads')
        with ThreadPoolExecutor(min(self.polling_threads, number_of_documents)) as pool:
            upload_results = pool.map(self._single_upload_wrap_errors, document_paths, [options] * number_of_documents,
                                      mime_type_list)
        self.logger.info(f'Finished uploading {number_of_documents} documents for client {client_id}')

        upload_ids = [result if isinstance(result, Exception) else result[API_FIELD_ID] for result in upload_results]
        return self.get_extraction_for_documents(upload_ids, extracted_values=True,
                                                 return_null_values=return_null_values)

    def _single_upload(self, document_path: str, options, mime_type):
        if mime_type is CONTENT_TYPE_UNKNOWN:
            mime_type = get_mimetype(document_path)
        with open(document_path, 'rb') as file:
            response = self.post(DOCUMENT_ENDPOINT,
                                 files={API_REQUEST_FIELD_FILE: (Path(document_path).name, file, mime_type)},
                                 data={API_REQUEST_FIELD_OPTIONS: json.dumps(options)})
        return response.json()

    def _single_upload_wrap_errors(self, document_path, options, mime_type):
        return function_wrap_errors(self._single_upload, document_path, options, mime_type)

    def _get_extraction_for_document_wrap_errors(self, document_id, *args):
        if isinstance(document_id, Exception):
            return document_id
        return function_wrap_errors(self.get_extraction_for_document, document_id, *args)

    def get_extraction_for_document(self, document_id, extracted_values: bool = None,
                                    return_null_values: bool = False) -> dict:
        """
        Gets the extracted information of an uploaded document by document ID. Raises an exception, when the document
        failed or didn't finish processing after the maximum number of requests
        :param document_id: The ID of the document
        :param extracted_values: (optional) Flag if the extracted values or the ground truth should be returned. If set
        to `True` the extracted values are returned. If set to `False` the ground truth is returned. If no ground truth
        is available, the extracted values will be returned either way. If `None` is given, the ground truth is returned
        if available
        :param return_null_values: Flag if fields with null as value should be included in the response or not.
        Default is False
        :return: The extracted information of the processed document or the ground truth as dictionary
        """
        params = {
            API_FIELD_RETURN_NULL: return_null_values
        }
        if extracted_values is not None:
            params[API_FIELD_EXTRACTED_VALUES] = extracted_values

        response = self._poll_for_url(DOCUMENT_ID_ENDPOINT.format(document_id=document_id), params=params,
                                      log_msg_before=f'Getting extraction for document with ID {document_id}',
                                      log_msg_after=f'Successfully got extraction for document with ID {document_id}')
        return response.json()

    def get_extraction_for_documents(self, document_ids: list, extracted_values: bool = None,
                                     return_null_values: bool = False) -> Iterator[dict]:
        """
        Gets the extracted information for multiple documents given their document IDs
        :param document_ids: A list of IDs of documents
        :param extracted_values: (optional) Flag if the extracted values or the ground truth should be returned. If set
        to `True` the extracted values are returned. If set to `False` the ground truth is returned. If no ground truth
        is available, the extracted values will be returned either way. If `None` is given, the ground truth is returned
        if available
        :param return_null_values: Flag if fields with null as value should be included in the response or not.
        Default is False
        :return: An iterator with extracted information or ground truths for successful documents and exceptions
        for failed documents. Use next(iterator) within a try-catch block to filter the failed documents.
        """
        if not isinstance(document_ids, list) or len(document_ids) == 0:
            raise ValueError(f'Expected argument \'document_ids\' to be a non-empty list, but got {document_ids}')

        self.logger.debug(f'Start getting extracted information for {len(document_ids)} documents')
        with ThreadPoolExecutor(min(self.polling_threads, len(document_ids))) as pool:
            results = pool.map(self._get_extraction_for_document_wrap_errors, document_ids,
                               [extracted_values] * len(document_ids), [return_null_values] * len(document_ids))
        self.logger.info(f'Successfully got extracted information for {len(document_ids)} documents')

        return self._create_result_iterator(results)

    def get_document_list(self, client_id=None) -> List[dict]:
        """
        Gets a list of  document jobs filtered by the client ID
        :param client_id: (optional) The client ID for which the document jobs should be get. Gets all document jobs if
        no client ID is given
        :return: A list of document jobs as dictionaries corresponding to the 'results' part of the json response
        """
        params = {API_FIELD_CLIENT_ID: client_id} if client_id else None

        response = self.get(DOCUMENT_ENDPOINT, params=params,
                            log_msg_before=f"Getting all documents for {f'client {client_id}' if client_id else 'all clients'}")
        self.logger.info(f'Successfully got {len(response.json()[API_FIELD_RESULTS])} documents')
        return response.json()[API_FIELD_RESULTS]

    def delete_documents(self, document_ids: list = None) -> dict:
        """
        Deletes a list of documents or all documents
        :param document_ids: (optional) A list of document IDs that shall be deleted. If this argument is not provided,
        all documents are deleted.
        :return: The API endpoint response as dictionary
        """
        payload = {API_FIELD_VALUE: document_ids} if (document_ids is not None) else {}

        response = self.delete(DOCUMENT_ENDPOINT, json=payload,
                               log_msg_before=f"Deleting {len(document_ids if payload else 'all')} documents",
                               log_msg_after='Successfully deleted documents')
        return response.json()

    def upload_enrichment_data(self, client_id, data, data_type: str, subtype: str = None) -> dict:
        """
        Creates one or more enrichment data records. The function returns after all data was created successfully or
        raises an exception if something went wrong.
        :param client_id: The client ID for which the data records shall be created.
        :param data: A list of data to be uploaded. For the format of the data see documentation
        :param data_type: The type of data which is uploaded. For the available data types see documentation
        :param subtype: (optional) Only used for type 'businessEntity'. For the available subtypes see documentation
        :return: The API endpoint response as dictionary
        """
        params = {
            API_FIELD_CLIENT_ID: client_id,
            API_REQUEST_FIELD_ENRICHMENT_TYPE: data_type
        }
        if data_type == DATA_TYPE_BUSINESS_ENTITY and subtype is not None:
            params[API_REQUEST_FIELD_ENRICHMENT_SUBTYPE] = subtype
        if not isinstance(data, list):
            data = [data]
        resp = self.post(DATA_ASYNC_ENDPOINT, json={API_FIELD_VALUE: data}, params=params,
                         log_msg_before=f'Start uploading {len(data)} enrichment data '
                         f'records of type {data_type} for client {client_id}')
        job_id = resp.json()[API_FIELD_ID]
        response = self._poll_for_url(DATA_ID_ENDPOINT.format(id=job_id), sleep_interval=1,
                                      get_status=lambda r: r[API_FIELD_VALUE][API_FIELD_STATUS],
                                      log_msg_after=f'Successfully uploaded {len(data)} enrichment data records for client {client_id}')
        return response.json()

    def get_enrichment_data(self, client_id, data_type: str, subtype: str = None, top: int = None, skip: int = None,
                            data_id=None, system=None, company_code=None) -> List[dict]:
        """
        Gets the enrichment data records filtered by the provided parameters
        :param client_id: The ID of the client for which the enrichment data was created
        :param data_type: The type of the data records. For the available data types see documentation
        :param subtype: (optional) The subtype of the records. Only used for type 'businessEntity'. For the available
        subtypes see documentation
        :param top: (optional) The maximum number records to be returned
        :param skip: (optional) The index of the first record to be returned
        :param data_id: (optional) The ID of a single data record. Only one will be returned
        :param system: (optional) The system of a single record
        :param company_code: (optional) The company code of a single record
        :return: A list of enrichment data records corresponding to the 'value' part of the json response. Returns a
        list with one item when data_id is given
        """
        params = {
            API_FIELD_CLIENT_ID: client_id,
            API_REQUEST_FIELD_ENRICHMENT_TYPE: data_type
        }
        if data_id is not None:
            params[API_REQUEST_FIELD_ENRICHMENT_ID] = data_id
        if top is not None:
            params[API_REQUEST_FIELD_LIMIT] = top
        if skip is not None:
            params[API_REQUEST_FIELD_OFFSET] = skip
        if subtype is not None:
            params[API_REQUEST_FIELD_ENRICHMENT_SUBTYPE] = subtype
        if system is not None:
            params[API_REQUEST_FIELD_ENRICHMENT_SYSTEM] = system
        if company_code is not None:
            params[API_REQUEST_FIELD_ENRICHMENT_COMPANYCODE] = company_code

        response = self.get(DATA_ENDPOINT, params=params,
                            log_msg_before=f'Getting enrichment data records for client {client_id}')
        self.logger.info(f'Successfully got {len(response.json()[API_FIELD_VALUE])} enrichment data records')
        return response.json()[API_FIELD_VALUE]

    def delete_all_enrichment_data(self, data_type: str = None) -> dict:
        """
        This endpoint is deleting all enrichment data records for the account
        :param data_type: (Optional) The type of enrichment data that should be deleted. For the available data types
        see documentation
        :return: The API endpoint response as dictionary
        """
        delete_url = DATA_ASYNC_ENDPOINT

        params = {API_REQUEST_FIELD_ENRICHMENT_TYPE: data_type} if data_type else None
        response = self.delete(delete_url, json={API_FIELD_VALUE: []}, params=params,
                               log_msg_before=f"Start deleting all{f' {data_type}' if data_type else ''} enrichment data records")

        job_id = response.json()[API_FIELD_ID]
        response = self._poll_for_url(DATA_ID_ENDPOINT.format(id=job_id),
                                      get_status=lambda r: r[API_FIELD_VALUE][API_FIELD_STATUS],
                                      log_msg_after=f"Successfully deleted all{f' {data_type}' if data_type else ''} enrichment data records")
        return response.json()

    def delete_enrichment_data(self, client_id, enrichment_records: list, data_type: str, subtype: str = None,
                               delete_async: bool = False) -> dict:
        """
        Deletes the enrichment data records with the given IDs in the payload
        :param client_id: The client ID for which the enrichment data was created
        :param enrichment_records: A list of dictionaries with the form: ``{'id':'', 'system':'', 'companyCode':''}``
        :param data_type: The type of enrichment data that should be deleted. For the available document data types see
        documentation
        :param subtype: (optional) The subtype of the records that should be deleted. Only used for type
        'businessEntity'. For the available subtypes see documentation
        :param delete_async: Set to ``True`` to delete data records asynchronously. Asynchronous deletion should be
        used when deleting large amounts of data to improve performance. Default is ``False``
        :return: The API endpoint response as dictionary
        """
        params = {
            API_FIELD_CLIENT_ID: client_id,
            API_REQUEST_FIELD_ENRICHMENT_TYPE: data_type
        }
        if subtype is not None:
            params[API_REQUEST_FIELD_ENRICHMENT_SUBTYPE] = subtype
        delete_url = DATA_ASYNC_ENDPOINT if delete_async else DATA_ENDPOINT
        response = self.delete(delete_url, json={API_FIELD_VALUE: enrichment_records}, params=params,
                               log_msg_before=f"Start deleting {len(enrichment_records) if len(enrichment_records) > 0 else 'all'} "
                               f"enrichment data records for client {client_id}")

        if delete_async:
            job_id = response.json()[API_FIELD_ID]
            response = self._poll_for_url(DATA_ID_ENDPOINT.format(id=job_id),
                                          get_status=lambda r: r[API_FIELD_VALUE][API_FIELD_STATUS],
                                          log_msg_after=f"Successfully deleted {len(enrichment_records) if len(enrichment_records) > 0 else 'all'} "
                                          f"enrichment data records for client {client_id}")
        return response.json()

    def activate_enrichment_data(self, params=None) -> dict:
        """
        Activates all enrichment data records for the current tenant
        :param params: Optional. A dictionary, list of tuples or bytes to send as a query string.
        :return: The API endpoint response as dictionary
        """
        response = self.post(DATA_ACTIVATION_ASYNC_ENDPOINT, params=params,
                             log_msg_before='Start activating enrichment data records')

        response = self._poll_for_url(DATA_ACTIVATION_ID_ENDPOINT.format(id=response.json()[API_FIELD_ID]),
                                      get_status=lambda r: r[API_FIELD_VALUE][API_FIELD_STATUS],
                                      log_msg_after='Successfully activated enrichment data records')
        return response.json()

    def get_image_for_document(self, document_id, page_no: int) -> bytes:
        """
        Gets the image of a document page for the given document ID and page number
        :param document_id: The ID of the document
        :param page_no: The page number for which to get the image
        :return: The image of the document page in the PNG format as bytes
        """
        headers = {API_HEADER_ACCEPT: CONTENT_TYPE_PNG}
        response = self.get(DOCUMENT_PAGE_ENDPOINT.format(document_id=document_id, page_number=page_no),
                            headers=headers,
                            log_msg_before=f'Getting image for page {page_no} of document with ID {document_id}',
                            log_msg_after=f'Successfully got image for page {page_no} of document with ID {document_id}')
        return response.content

    def get_document_page_text(self, document_id, page_no: int) -> List[dict]:
        """
        Gets the text for a document page for the given document ID and page number
        :param document_id: The ID of the document
        :param page_no: The page number for which to get the text
        :return: The text for the page as a list of dictionaries corresponding to the 'value' part of the json response
        """
        response = self.get(DOCUMENT_PAGE_TEXT_ENDPOINT.format(document_id=document_id, page_number=page_no),
                            log_msg_before=f'Getting text for page {page_no} of document with ID {document_id}',
                            log_msg_after=f'Successfully got text for page {page_no} of document with ID {document_id}')
        return response.json()[API_FIELD_VALUE]

    def get_document_text(self, document_id) -> dict:
        """
        Gets the text for all pages of a document
        :param document_id: The ID of the document
        :return: A dictionary mapping the page numbers to the text corresponding to the 'results' part of the json reponse
        """
        response = self.get(DOCUMENT_PAGES_TEXT_ENDPOINT.format(document_id=document_id),
                            log_msg_before=f'Getting text for all pages of document with ID {document_id}',
                            log_msg_after=f'Successfully got text fot all pages of document with ID {document_id}')
        return response.json()[API_FIELD_RESULTS]

    def get_request_for_document(self, document_id) -> dict:
        """
        Gets the request of a processed document
        :param document_id: The ID of the document
        :return: The request of the document as dictionary
        """
        response = self.get(DOCUMENT_ID_REQUEST_ENDPOINT.format(document_id=document_id),
                            log_msg_before=f'Getting request information for document with ID {document_id}',
                            log_msg_after=f'Successfully got request information for document with ID {document_id}')
        return response.json()

    def get_page_dimensions_for_document(self, document_id, page_no: int) -> dict:
        """
        Gets the dimensions of a document page
        :param document_id: The ID of the document
        :param page_no: The page number for which to get the dimensions
        :return: The height and width of the document page as dictionary
        """
        response = self.get(DOCUMENT_PAGE_DIMENSIONS_ENDPOINT.format(document_id=document_id, page_number=page_no),
                            log_msg_before=f'Getting dimensions for page {page_no} of document with ID {document_id}',
                            log_msg_after=f'Successfully got dimensions for page {page_no} of document with ID {document_id}')
        return response.json()

    def get_all_dimensions_for_document(self, document_id) -> dict:
        """
        Gets the dimensions of all document pages
        :param document_id: The ID of the document
        :return: The height and width of all document pages as dictionary with page number as key corresponding to the
        'results' part of the json response
        """
        response = self.get(DOCUMENT_PAGES_DIMENSIONS_ENDPOINT.format(document_id=document_id),
                            log_msg_before=f'Getting dimensions for all pages of document with ID {document_id}',
                            log_msg_after=f'Successfully got dimensions for all pages of document with ID {document_id}')
        return response.json()[API_FIELD_RESULTS]

    def post_ground_truth_for_document(self, document_id, ground_truth: Union[str, dict]) -> dict:
        """
        Saves the ground truth for a document
        :param document_id: The ID of the document
        :param ground_truth: Path to the ground truth JSON file or an object representing the ground truth
        :return: The API endpoint response as dictionary
        """
        ground_truth_json = get_ground_truth_json(ground_truth)

        response = self.post(DOCUMENT_ID_ENDPOINT.format(document_id=document_id), json=ground_truth_json,
                             log_msg_before=f'Uploading ground truth for document with ID {document_id}',
                             log_msg_after=f'Successfully uploaded ground truth for document with ID {document_id}')
        return response.json()

    def post_confirm_document(self, document_id, data_for_retraining=False) -> dict:
        """
        Sets the document status to confirmed
        :param document_id: The ID of the document
        :param data_for_retraining: Indicates whether the document should be allowed for retraining. Default is False
        :return: The API endpoint response as dictionary
        """
        params = {
            API_FIELD_DATA_FOR_RETRAINING: data_for_retraining
        }
        response = self.post(DOCUMENT_CONFIRM_ENDPOINT.format(document_id=document_id), params=params,
                             log_msg_before=f'Confirming document with ID {document_id}',
                             log_msg_after=f'Successfully confirmed document with ID {document_id}')
        return response.json()
