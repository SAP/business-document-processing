# SPDX-FileCopyrightText: 2020 2019-2020 SAP SE
#
# SPDX-License-Identifier: Apache-2.0

from concurrent.futures import ThreadPoolExecutor
import json
import logging
from typing import List

from sap_business_document_processing.common.http_client_base import CommonClient
from sap_business_document_processing.common.helpers import function_wrap_errors
from .capabilities import DoxDataType, DoxDataSubType
from .constants import API_FIELD_CLIENT_ID, API_FIELD_CLIENT_LIMIT, API_FIELD_CLIENT_NAME, API_FIELD_ID, \
    API_FIELD_EXTRACTED_VALUES, API_FIELD_RESULTS, API_FIELD_RETURN_NULL, API_FIELD_STATUS, API_FIELD_VALUE, \
    API_FIELD_DATA_FOR_RETRAINING, API_HEADER_ACCEPT, API_REQUEST_FIELD_CLIENT_START_WITH, API_REQUEST_FIELD_FILE, \
    API_REQUEST_FIELD_LIMIT, API_REQUEST_FIELD_OFFSET, API_REQUEST_FIELD_OPTIONS, API_REQUEST_FIELD_PAYLOAD, \
    API_REQUEST_FIELD_ENRICHMENT_COMPANYCODE, API_REQUEST_FIELD_ENRICHMENT_ID, API_REQUEST_FIELD_ENRICHMENT_SUBTYPE, \
    API_REQUEST_FIELD_ENRICHMENT_SYSTEM, API_REQUEST_FIELD_ENRICHMENT_TYPE, CONTENT_TYPE_PNG
from .endpoints import CAPABILITIES_ENDPOINT, CLIENT_ENDPOINT, CLIENT_MAPPING_ENDPOINT, DATA_ACTIVATION_ASYNC_ENDPOINT,\
    DATA_ACTIVATION_ID_ENDPOINT, DATA_ENDPOINT, DATA_ASYNC_ENDPOINT, DATA_ID_ENDPOINT, DOCUMENT_ENDPOINT, \
    DOCUMENT_CONFIRM_ENDPOINT, DOCUMENT_ID_ENDPOINT, DOCUMENT_ID_REQUEST_ENDPOINT, DOCUMENT_PAGE_ENDPOINT, \
    DOCUMENT_PAGE_DIMENSIONS_ENDPOINT, DOCUMENT_PAGES_DIMENSIONS_ENDPOINT, DOCUMENT_PAGE_TEXT_ENDPOINT, \
    DOCUMENT_PAGES_TEXT_ENDPOINT
from .helpers import merge_document_options


class DoxApiClient(CommonClient):
    """
    This class is the main entry point to consume the SAP Document Information Extraction REST API from a Python
    application.

    :param base_url: The service URL taken from the service key (key 'url' in service key JSON)
    :param client_id: The XSUAA client ID taken from the service key (key 'uaa.clientid' in service key JSON)
    :param client_secret: The XSUAA client secret taken from the service key (key 'uaa.clientsecret' in service key JSON)
    :param uaa_url: The XSUAA URL taken from the service key (key 'uaa.url' in the service key JSON)
    :param polling_threads: Number of threads used to poll for asynchronous APIs, the maximal value is 15
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
                                           url_path_prefix='document-information-extraction/v1/',
                                           logger_name='DoxApiClient',
                                           logging_level=logging_level)

    def get_capabilities(self):
        """
        Gets the capabilities available for the service instance.
        :return: Dictionary with available extraction fields, enrichment and document types.
        """
        response = self.get(CAPABILITIES_ENDPOINT,
                            log_msg_before='Getting all available capabilities',
                            log_msg_after='Successfully got all available capabilities')
        return response.json()

    def create_client(self, client_id, client_name):
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

    def create_clients(self, clients: list):
        """
        Creates one or more clients for whom documents can be uploaded
        :param clients: A list of clients to be created. List items can be dictionaries or :class:`DoxClient`.
        :return: The API endpoint response as dictionary
        """
        response = self.post(CLIENT_ENDPOINT, json={API_FIELD_VALUE: clients},
                             log_msg_before=f'Creating {len(clients)} clients',
                             log_msg_after=f'Successfully created {len(clients)} clients')
        return response.json()

    def get_clients(self, limit=100, client_id_starts_with=None, offset=None):
        """
        Gets all existing clients filtered by the parameters
        :param limit: The maximum number of clients to get. Default is 100
        :param client_id_starts_with: (optional) Filters the clients by the characters the ID starts with
        :param offset: (optional) Index of the first client to get
        :return: List of existing clients as dictionaries
        """
        params = {API_FIELD_CLIENT_LIMIT: limit}
        if client_id_starts_with is not None:
            params[API_REQUEST_FIELD_CLIENT_START_WITH] = str(client_id_starts_with)
        if offset is not None:
            params[API_REQUEST_FIELD_OFFSET] = int(offset)

        response = self.get(CLIENT_ENDPOINT, params=params,
                            log_msg_before='Getting up to {} clients{}'.format(
                                limit, f' that start with \'{client_id_starts_with}\'' if client_id_starts_with else ''))
        self.logger.info(f'Successfully got {len(response.json()[API_REQUEST_FIELD_PAYLOAD])} clients')
        return response.json()[API_REQUEST_FIELD_PAYLOAD]

    def delete_client(self, client_id):
        """
        Deletes a client with the given client ID
        :param client_id: The ID of the client to be deleted
        :return: The API endpoint response as dictionary
        """
        return self.delete_clients([client_id])

    def delete_clients(self, client_ids: list = None):
        """
        Deletes multiple clients with the given client IDs
        :param client_ids: (optional) List of IDs of clients to be deleted. If no IDs ar provided, all clients will be
        deleted
        :return: The API endpoint response as dictionary
        """
        payload = {API_FIELD_VALUE: client_ids} if (client_ids is not None) else {}

        response = self.delete(CLIENT_ENDPOINT, json=payload,
                               log_msg_before=f"Deleting {len(client_ids) if client_ids else 'all'} clients",
                               log_msg_after='Successfully deleted clients')
        return response.json()

    def post_client_capability_mapping(self, client_id, options):
        """
        Post the client capability mapping for the Identifier API provided by the customer to the entity client DB
        :param client_id: The ID of the client for which to upload the capability mapping
        :param options: The mapping that should be uploaded
        :return: The API endpoint response as dictionary
        """
        response = self.post(CLIENT_MAPPING_ENDPOINT, params={API_FIELD_CLIENT_ID: client_id},
                             data={API_REQUEST_FIELD_OPTIONS: json.dumps(options)},
                             log_msg_before=f'Create custom capability mapping for client {client_id}',
                             log_msg_after=f'Successfully created custom capability mapping for client {client_id}')
        return response.json()

    def upload_document(self, document_path: str, client_id=None, document_type: str = None, options: dict = None,
                        header_fields=None, line_item_fields=None, template_id=None, received_date=None,
                        enrichment=None, return_null_values=False):
        """
        Uploads one document for processing. The function will run until a processing result can be returned or a
        timeout is reached
        :param document_path: The path to the document to be uploaded
        :param client_id: The client ID for which the document should be uploaded. Can be omitted, if an ID is given in
        the 'options' parameter
        :param document_type: The type of the document being uploaded. Options are 'invoice' or 'paymentAdvice'. Can be
        omitted, if the type is specified in the options parameter
        :param options: (optional) The options for processing the document as dictionary. If no client ID or document
        type are given as parameters, they have to be given in this dictionary. If other parameters are given, they
        overwrite the respective values in this dictionary
        :param header_fields: (optional) A list of header fields to be extracted. Can be given as list of strings or as
        comma separated string. If none are given, all available header fields are used
        :param line_item_fields: (optional) A list of line item fields to be extracted. Can be given as list of string
        or as comma separated string. If none are given, all available line item fields are used
        :param template_id: (optional) The ID of the template to be used for this document
        :param received_date: (optional) The date the document was received
        :param enrichment: (optional) A dictionary of entities that should be used for entity matching
        :param return_null_values: Flag if fields with null as value should be included in the response or not.
        Default is False
        :return: The result of the processed document as dictionary
        """
        return next(self.upload_documents([document_path], client_id, document_type, options=options,
                                          header_fields=header_fields, line_item_fields=line_item_fields,
                                          template_id=template_id, received_date=received_date, enrichment=enrichment,
                                          return_null_values=return_null_values, silent=True))

    def upload_documents(self, document_paths: List[str], client_id=None, document_type=None, options=None,
                         header_fields=None, line_item_fields=None, template_id=None, received_date=None,
                         enrichment=None, return_null_values=False, wait_for_results=True, silent=False):
        """
        Uploads multiple documents for processing. If wait_for_results is True, the function will run until all
        documents have been processed or a timeout is reached. The given parameters will be applied to all documents.
        :param document_paths: A list of paths to the documents to be uploaded
        :param client_id: The client ID for which the document should be uploaded. Can be omitted, if an ID is given in
        the 'options' parameter
        :param document_type: The type of the document being uploaded. Options are 'invoice' or 'paymentAdvice'
        :param options: (optional) The options for processing the document as dictionary. If no client ID or document
        type are given as parameters, they have to be given in this dictionary. If other parameters are given, they
        overwrite the respective values in this dictionary
        :param header_fields: (optional) A list of header fields to be extracted. Can be passed as list of strings or as
        comma separated string. If none are given, all available header fields are used
        :param line_item_fields: (optional) A list of line item fields to be extracted. Can be passed as list of string
        or as comma separated string. If none are given, all available line item are used
        :param template_id: (optional) The ID of the template to be used for this document
        :param received_date: (optional) The date the document was received
        :param enrichment: (optional) A dictionary of entities that should be used for entity matching
        :param return_null_values: Flag if fields with null as value should be included in the response or not.
        Default is False
        :param wait_for_results: Flag if the method will wait for the processed results. Default is True.
        :param silent: If True, the functions returns even if some documents failed uploading or processing. If False,
        will raise an exception if at least one document failed. Default is False
        :return: An iterator with results for successful documents and exceptions for failed documents. Use
        next(iterator) within a try-catch block to filter the failed documents. If input argument `wait_for_results` is
        true, the iterator will contain processed document results. If false, the iterator will contain information
        about the uploaded document including its ID; the user can use `get_document_results` method to further fetch
        the processed results given the iterator.
        """
        if not isinstance(document_paths, list) or len(document_paths) == 0:
            raise ValueError(f'Expected argument \'document_paths\' to be a non-empty list of paths to documents to be uploaded, '
                             f'but got {document_paths}')
        number_of_documents = len(document_paths)

        options = merge_document_options(options, client_id, document_type, header_fields, line_item_fields,
                                         template_id, received_date, enrichment)

        self.logger.debug(f'Starting upload of {number_of_documents} documents for client {client_id} in parallel using '
                          f'{self.polling_threads} threads')
        with ThreadPoolExecutor(min(self.polling_threads, number_of_documents)) as pool:
            upload_results = pool.map(self._single_upload_wrap_errors, document_paths, [options] * number_of_documents)
        if not silent:
            upload_results = self._validate_results(upload_results, 'Some documents could not be uploaded successfully')

        self.logger.info(f'Finished uploading {number_of_documents} documents for client {client_id}')
        if not wait_for_results:
            return self._create_result_iterator(upload_results)

        return self.get_documents_results(upload_results, return_null_values, silent)

    def get_documents_results(self, upload_results, return_null_values=False, silent=False):
        """
        Get results of multiple documents, given their upload results.
        :param upload_results: A list of uploaded documents. This input parameter typically can be the output of method
        upload_documents(..., wait_for_results=False).
        :param return_null_values: Flag if fields with null as value should be included in the response or not.
        Default is False
        :param silent: If True, the functions returns even if some documents failed uploading or processing. If False,
        will raise an exception if at least one document failed. Default is False
        :return: An iterator with processed document results for successful documents and exceptions for failed
        documents. Use next(iterator) within a try-catch block to filter the failed documents.
        """
        if not isinstance(upload_results, list):
            upload_results = list(upload_results)
        self.logger.debug(f'Waiting for {len(upload_results)} documents to be processed')
        with ThreadPoolExecutor(min(self.polling_threads, len(upload_results))) as pool:
            results = pool.map(self._get_document_wrap_errors, upload_results,
                               [return_null_values] * len(upload_results))
        if not silent:
            results = self._validate_results(results, 'Some documents could not be processed successfully')
        self.logger.info(f'{len(upload_results)} documents have been processed')
        return self._create_result_iterator(results)

    def _single_upload(self, document_path: str, options):
        with open(document_path, 'rb') as file:
            response = self.post(DOCUMENT_ENDPOINT,
                                 files={API_REQUEST_FIELD_FILE: file},
                                 data={API_REQUEST_FIELD_OPTIONS: json.dumps(options)})
        return response.json()

    def _single_upload_wrap_errors(self, document_path, options):
        return function_wrap_errors(self._single_upload, document_path, options)

    def _get_document_wrap_errors(self, upload_result, *args):
        if isinstance(upload_result, Exception):
            return upload_result
        return function_wrap_errors(self.get_document_result, upload_result[API_FIELD_ID], True, *args)

    def get_documents(self, client_id: str = None):
        """
        Gets all document jobs filtered by the client ID
        :param client_id: (optional) The client ID for which the document jobs should be get. Gets all document jobs if
        no client ID is given
        :return: A list of document jobs as dictionaries
        """
        params = {API_FIELD_CLIENT_ID: client_id} if client_id else None

        response = self.get(DOCUMENT_ENDPOINT, params=params,
                            log_msg_before=f"Getting all documents for {f'client {client_id}' if client_id else 'all clients'}")
        self.logger.info(f'Successfully got {len(response.json()[API_FIELD_RESULTS])} documents')
        return response.json()[API_FIELD_RESULTS]

    def delete_documents(self, document_ids: list = None):
        """
        Deletes a list of documents or all documents
        :param document_ids: (optional) A list of document IDs that shall be deleted. If this argument is not provided, all documents
        are deleted.
        :return: The API endpoint response as dictionary
        """
        payload = {API_FIELD_VALUE: document_ids} if (document_ids is not None) else {}

        response = self.delete(DOCUMENT_ENDPOINT, json=payload,
                               log_msg_before=f"Deleting {len(document_ids if payload else 'all')} documents",
                               log_msg_after='Successfully deleted documents')
        return response.json()

    def get_document_result(self, document_id, extracted_values: bool = None, return_null_values: bool = False):
        """
        Gets the processing result of an uploaded document by document ID. Raises en exception, when the documents
        failed or didn't finish processing after the maximum number of requests
        :param document_id: The ID of the document uploaded for processing
        :param extracted_values: (optional) Flag if the extracted values or the ground truth should be returned. If set
        to `True` the extracted values are returned. If set to `False` the ground truth is returned. If no ground truth
        is available, the extracted values will be returned either way. If `None` is given, the ground truth is returned
        if available
        :param return_null_values: Flag if fields with null as value should be included in the response or not.
        Default is False
        :return: The result of the processed document or the ground truth as dictionary
        """
        params = {
            API_FIELD_RETURN_NULL: return_null_values
        }
        if extracted_values is not None:
            params[API_FIELD_EXTRACTED_VALUES] = extracted_values

        response = self._poll_for_url(DOCUMENT_ID_ENDPOINT.format(document_id=document_id), params=params,
                                      log_msg_before=f'Getting document result with ID {document_id}',
                                      log_msg_after=f'Successfully got document result with ID {document_id}')
        return response.json()

    def upload_enrichment_data(self, client_id, data, data_type, subtype=None):
        """
        Creates one or more enrichment data records. The function returns after all data was created successfully or
        raises an exception if something went wrong.
        :param client_id: The client ID for which the data records shall be created.
        :param data: A list of data to be uploaded. A 'businessEntity' record has the following format:
        {"id":"BE0001", "name":"","accountNumber":"", "address1":"", "address2": "", "city":"", "countryCode":"",
        "postalCode":"","state":"", "email":"", "phone":"", "bankAccount":"", "taxId":""}. An 'employee' record has the
        following format: {"id":"E0001", "email":"", "firstName":"", "middleName": "", "lastName":""}
        :param data_type: The type of data which is uploaded. Can be given as instance of the enum :enum:`DoxDataType`
        or as string. Options are 'businessEntity' and 'employee'
        :param subtype: (optional) Only used for type 'businessEntity'. Can be given as instance of the enum
        :enum:`DoxDataSubType` or as string. Options are 'supplier', 'customer' or 'companyCode'
        :return: The API endpoint response as dictionary
        """
        params = {
            API_FIELD_CLIENT_ID: client_id,
            API_REQUEST_FIELD_ENRICHMENT_TYPE: str(data_type)
        }
        if data_type == DoxDataType.BUSINESS_ENTITY and subtype is not None:
            params[API_REQUEST_FIELD_ENRICHMENT_SUBTYPE] = str(subtype)
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

    def upload_enrichment_data_employee(self, client_id, data):
        """
        Creates one or more 'employee' enrichment data records
        :param client_id: The client ID for which the data records shall be created
        :param data: The data records to be uploaded. A record should have the following format: {"id":"E0001",
        "email":"", "firstName":"", "middleName": "", "lastName":""}
        :return: The API endpoint response as dictionary
        """
        return self.upload_enrichment_data(client_id, DoxDataType.EMPLOYEE, data)

    def upload_enrichment_data_supplier(self, client_id, data):
        """
        Creates one or more 'supplier' enrichment data records
        :param client_id: The client ID for which the data records shall be created
        :param data: The data records to be uploaded. A record should have the following format: {"id":"BE0001",
        "name":"", "accountNumber":"", "address1":"", "address2": "", "city":"", "countryCode":"", "postalCode":"",
        "state":"", "email":"", "phone":"", "bankAccount":"", "taxId":""}
        :return: The API endpoint response as dictionary
        """
        return self.upload_enrichment_data(client_id, DoxDataType.BUSINESS_ENTITY, data, DoxDataSubType.SUPPLIER)

    def upload_enrichment_data_customer(self, client_id, data):
        """
        Creates one or more 'customer' enrichment data records
        :param client_id: The client ID for which the data records shall be created
        :param data: The data records to be uploaded. A record should have he following format: {"id":"BE0001",
        "name":"", "accountNumber":"", "address1":"", "address2": "", "city":"", "countryCode":"", "postalCode":"",
        "state":"", "email":"", "phone":"", "bankAccount":"", "taxId":""}
        :return: The API endpoint response as dictionary
        """
        return self.upload_enrichment_data(client_id, DoxDataType.BUSINESS_ENTITY, data, DoxDataSubType.CUSTOMER)

    def get_enrichment_data(self, client_id, data_type, data_id=None, offset=None, limit=None, subtype=None,
                            system=None, company_code=None):
        """
        Gets the enrichment data records filtered by the provided parameters
        :param client_id: The ID of the client for which the enrichment data was created
        :param data_type: The type of the data records. Can be given as an instance of :enum:`DoxDataType` or string.
        Options are 'businessEntity' or 'employee'
        :param data_id: (optional) The ID of a single data record. Only one will be returned
        :param offset: (optional) The index of the first record to be returned
        :param limit: (optional) The maximum number records to be returned
        :param subtype: (optional) The subtype of the records. Only used for type 'businessEntity'. Can be given as
        instance of :enum:`DoxDataSubType` or as string. Options are 'supplier', 'customer' or 'companyCode'
        :param system: (optional) The system of a single record
        :param company_code: (optional) The company code of a single record
        :return: A list of enrichment data records. Returns a list with one item when data_id is given
        """
        params = {
            API_FIELD_CLIENT_ID: client_id,
            API_REQUEST_FIELD_ENRICHMENT_TYPE: str(data_type)
        }
        if data_id is not None:
            params[API_REQUEST_FIELD_ENRICHMENT_ID] = data_id
        if offset is not None:
            params[API_REQUEST_FIELD_OFFSET] = offset
        if limit is not None:
            params[API_REQUEST_FIELD_LIMIT] = limit
        if subtype is not None:
            params[API_REQUEST_FIELD_ENRICHMENT_SUBTYPE] = str(subtype)
        if system is not None:
            params[API_REQUEST_FIELD_ENRICHMENT_SYSTEM] = system
        if company_code is not None:
            params[API_REQUEST_FIELD_ENRICHMENT_COMPANYCODE] = company_code

        response = self.get(DATA_ENDPOINT, params=params,
                            log_msg_before=f'Getting enrichment data records for client {client_id}')
        self.logger.info(f'Successfully got {len(response.json()[API_FIELD_VALUE])} enrichment data records')
        return response.json()[API_FIELD_VALUE]

    def delete_all_enrichment_data(self, data_type=None):
        """
        This endpoint is deleting all master data records for the account
        :param data_type: (Optional) The type of enrichment data that should be deleted. Can be given as
        :enum:`DoxDataType` or string. Options are 'businessEntity' or 'employee'
        :return: The API endpoint response as dictionary
        """
        delete_url = DATA_ASYNC_ENDPOINT

        params = {API_REQUEST_FIELD_ENRICHMENT_TYPE: str(data_type)} if data_type else None
        response = self.delete(delete_url, json={API_FIELD_VALUE: []}, params=params,
                               log_msg_before=f"Start deleting all{f' {data_type}' if data_type else ''} enrichment data records")

        job_id = response.json()[API_FIELD_ID]
        response = self._poll_for_url(DATA_ID_ENDPOINT.format(id=job_id),
                                      get_status=lambda r: r[API_FIELD_VALUE][API_FIELD_STATUS],
                                      log_msg_after=f"Successfully deleted all{f' {data_type}' if data_type else ''} enrichment data records")
        return response.json()

    def delete_enrichment_data(self, client_id, data_type, payload: list, subtype=None, delete_async=False):
        """
        Deletes the enrichment data records with the given IDs in the payload
        :param client_id: The client ID for which the enrichment data was created
        :param data_type: The type of enrichment data that should be deleted. Can be given as :enum:`DoxDataType` or
        string. Options are 'businessEntity' or 'employee'
        :param payload: A list of dictionaries with the form: ``{'id':'', 'system':'', 'companyCode':''}``
        :param subtype: (optional) The subtype of the records that should be deleted. Only used for type
        'businessEntity'. Can be given as instance of :enum:`DoxDataSubType` or as string. Options are 'supplier',
        'customer' or 'companyCode'
        :param delete_async: Set to ``True`` to delete data records asynchronously. Asynchronous deletion should be
        used when deleting large amounts of data to improve performance. Default is ``False``
        :return: The API endpoint response as dictionary
        """
        params = {
            API_FIELD_CLIENT_ID: client_id,
            API_REQUEST_FIELD_ENRICHMENT_TYPE: str(data_type)
        }
        if subtype is not None:
            params[API_REQUEST_FIELD_ENRICHMENT_SUBTYPE] = str(subtype)
        delete_url = DATA_ASYNC_ENDPOINT if delete_async else DATA_ENDPOINT
        response = self.delete(delete_url, json={API_FIELD_VALUE: payload}, params=params,
                               log_msg_before=f"Start deleting {len(payload) if len(payload) > 0 else 'all'} "
                               f"enrichment data records for client {client_id}")

        if delete_async:
            job_id = response.json()[API_FIELD_ID]
            response = self._poll_for_url(DATA_ID_ENDPOINT.format(id=job_id),
                                          get_status=lambda r: r[API_FIELD_VALUE][API_FIELD_STATUS],
                                          log_msg_after=f"Successfully deleted {len(payload) if len(payload) > 0 else 'all'} "
                                          f"enrichment data records for client {client_id}")
        return response.json()

    def activate_enrichment_data(self):
        """
        Activates all enrichment data records for the current tenant
        :return: The API endpoint response as dictionary
        """
        response = self.post(DATA_ACTIVATION_ASYNC_ENDPOINT,
                             log_msg_before='Start activating enrichment data records')

        response = self._poll_for_url(DATA_ACTIVATION_ID_ENDPOINT.format(id=response.json()[API_FIELD_ID]),
                                      get_status=lambda r: r[API_FIELD_VALUE][API_FIELD_STATUS],
                                      log_msg_after='Successfully activated enrichment data records')
        return response.json()

    def get_image_for_document(self, document_id, page_no: int):
        """
        Gets the image of a document page for the given document ID and page number
        :param document_id: The ID of the document
        :param page_no: The page number for which to get the image
        :return: The image of the document page in the PNG format as bytearray
        """
        headers = {API_HEADER_ACCEPT: CONTENT_TYPE_PNG}
        response = self.get(DOCUMENT_PAGE_ENDPOINT.format(document_id=document_id, page_number=page_no),
                            headers=headers,
                            log_msg_before=f'Getting image for page {page_no} of document with ID {document_id}',
                            log_msg_after=f'Successfully got image for page {page_no} of document with ID {document_id}')
        return response.content

    def get_document_page_text(self, document_id, page_no: int):
        """
        Gets the text for a document page for the given document ID and page number
        :param document_id: The ID of the document
        :param page_no: The page number for which to get the text
        :return: The text for the page as dictionary
        """
        response = self.get(DOCUMENT_PAGE_TEXT_ENDPOINT.format(document_id=document_id, page_number=page_no),
                            log_msg_before=f'Getting text for page {page_no} of document with ID {document_id}',
                            log_msg_after=f'Successfully got text for page {page_no} of document with ID {document_id}')
        return response.json()[API_FIELD_VALUE]

    def get_document_text(self, document_id):
        """
        Gets the text for all pages of a document
        :param document_id: The ID of the document
        :return: A dictionary mapping the page numbers to the text
        """
        response = self.get(DOCUMENT_PAGES_TEXT_ENDPOINT.format(document_id=document_id),
                            log_msg_before=f'Getting text for all pages of document with ID {document_id}',
                            log_msg_after=f'Successfully got text fot all pages of document with ID {document_id}')
        return response.json()[API_FIELD_RESULTS]

    def get_request_for_document(self, document_id):
        """
        Gets the request of a processed document
        :param document_id: The ID of the document
        :return: The request of the document as dictionary
        """
        response = self.get(DOCUMENT_ID_REQUEST_ENDPOINT.format(document_id=document_id),
                            log_msg_before=f'Getting request information for document with ID {document_id}',
                            log_msg_after=f'Successfully got request information for document with ID {document_id}')
        return response.json()

    def get_page_dimensions_for_document(self, document_id, page_no: int):
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

    def get_all_dimensions_for_document(self, document_id):
        """
        Gets the dimensions of all document pages
        :param document_id: The ID of the document
        :return: The height and width of all document pages as dictionary with page number as key
        """
        response = self.get(DOCUMENT_PAGES_DIMENSIONS_ENDPOINT.format(document_id=document_id),
                            log_msg_before=f'Getting dimensions for all pages of document with ID {document_id}',
                            log_msg_after=f'Successfully got dimensions for all pages of document with ID {document_id}')
        return response.json()[API_FIELD_RESULTS]

    def post_ground_truth_for_document(self, document_id, ground_truth):
        """
        Saves the ground truth for a document
        :param document_id: The ID of the document
        :param ground_truth: Path to the ground truth JSON file or an object representing the ground truth
        :return: The API endpoint response as dictionary
        """
        if isinstance(ground_truth, str):
            with open(ground_truth, 'r') as file:
                ground_truth_json = json.load(file)
        elif isinstance(ground_truth, dict):
            ground_truth_json = ground_truth
        else:
            raise ValueError('Wrong argument type, string (path to ground truth file) or a dictionary (ground truth as '
                             'JSON format) are expected for ground_truth argument')

        response = self.post(DOCUMENT_ID_ENDPOINT.format(document_id=document_id), json=ground_truth_json,
                             log_msg_before=f'Uploading ground truth for document with ID {document_id}',
                             log_msg_after=f'Successfully uploaded ground truth for document with ID {document_id}')
        return response.json()

    def post_confirm_document(self, document_id, data_for_retraining=False):
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
