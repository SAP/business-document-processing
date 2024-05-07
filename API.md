
# sap_business_document_processing


# sap_business_document_processing.document_classification_client.dc_api_client


## DCApiClient
```python
DCApiClient(self,
            base_url,
            client_id,
            client_secret,
            uaa_url,
            url_path_prefix='document-classification/v1/',
            polling_threads=5,
            polling_sleep=5,
            polling_long_sleep=30,
            polling_max_attempts=120,
            logging_level=30)
```

This class provides an interface to access SAP Document Classification REST API from a Python application.
The structure of values returned by all the methods is documented in the API reference:
https://help.sap.com/viewer/ca60cd2ed44f4261a3ae500234c46f37/SHIP/en-US/c1045a561faf4ba0ae2b0e7713f5e6c4.html

- Argument base_url: The service URL taken from the service key (key 'url' in service key JSON)
- Argument client_id: The XSUAA client ID taken from the service key (key 'uaa.clientid' in service key JSON)
- Argument client_secret: The XSUAA client secret taken from the service key (key 'uaa.clientsecret' in service key JSON)
- Argument uaa_url: The XSUAA URL taken from the service key (key 'uaa.url' in service key JSON)
- Argument polling_threads: Number of threads used to poll for asynchronous DC APIs
- Argument polling_sleep: Number of seconds to wait between the polling attempts for most of the APIs,
the minimal value is 0.2
- Argument polling_long_sleep: Number of seconds to wait between the polling attempts for model training and
deployment operations, the minimal value is 0.2
- Argument polling_max_attempts: Maximum number of attempts used to poll for asynchronous DC APIs
- Argument logging_level: INFO level will log the operations progress, the default level WARNING should not
produce any logs


### classify_document
```python
DCApiClient.classify_document(document_path: str,
                              model_name,
                              model_version,
                              reference_id=None,
                              mime_type=None)
```

Submits request for document classification, checks the response and returns the reference ID for the
uploaded document

- Argument document_path: Path to the PDF file on the disk
- Argument model_name: The name of the model that was successfully deployed to be used for the classification
- Argument model_version: The version of the model that was successfully deployed to be used for the classification
- Argument reference_id: In case the document reference ID has to be managed by the user, it can be specified.
In this case the user is responsible for providing unique reference IDs for different documents
- Argument mime_type: The file type of the document uploaded

**Returns**: Object containing the reference ID of the classified document and the classification results


### classify_documents
```python
DCApiClient.classify_documents(documents_paths: typing.List[str],
                               model_name, model_version)
```

Submits requests for classification of multiple documents, checks the response and returns the reference ID
for the classified documents

- Argument documents_paths: Paths to the PDF files on the disk
- Argument model_name: The name of the model that was successfully deployed to be used for the classification
- Argument model_version: The version of the model that was successfully deployed to be used for the classification

**Returns**: An iterator of objects containing the reference ID of the classified document and the classification
results


### create_dataset
```python
DCApiClient.create_dataset()
```

Creates an empty dataset

**Returns**: Object containing the dataset id


### delete_dataset
```python
DCApiClient.delete_dataset(dataset_id)
```

Deletes a dataset with a given ID
- Argument dataset_id: The ID of the dataset to delete

**Returns**: Object containing the ID of the deleted dataset and the number of documents deleted


### delete_training_document
```python
DCApiClient.delete_training_document(dataset_id, document_id)
```

Deletes a training document from a dataset
- Argument dataset_id: The ID of the dataset where the document is located
- Argument document_id: The reference ID of the document

**Returns**: An empty object


### get_dataset_info
```python
DCApiClient.get_dataset_info(dataset_id)
```

Gets statistical information about a dataset with a given ID
- Argument dataset_id: The ID of the dataset

**Returns**: Summary information about the dataset that includes the number of documents in different processing
stages


### get_datasets_info
```python
DCApiClient.get_datasets_info()
```

Gets summary information about the existing datasets

**Returns**: An array of datasets corresponding to the 'datasets' part of the json response


### get_dataset_documents_info
```python
DCApiClient.get_dataset_documents_info(dataset_id,
                                       top: int = None,
                                       skip: int = None,
                                       count: bool = None)
```

Gets the information about all the documents in a specific dataset
- Argument dataset_id: The ID of an existing dataset
- Argument top: Pagination: number of documents to be fetched in the current request
- Argument skip: Pagination: number of documents to skip for the current request
- Argument count: Flag to show count of number of documents in the dataset

**Returns**: Object that contains an array of the documents


### get_classification_documents_info
```python
DCApiClient.get_classification_documents_info(model_name, model_version)
```

Gets the information about recently classified documents
- Argument model_name: The name of the model against which the documents were classified
- Argument model_version: The version of the model against which the documents were classified

**Returns**: An array of document information correspond to the 'results' part of the json response. Each document
information includes its reference ID and the classification status.


### upload_document_to_dataset
```python
DCApiClient.upload_document_to_dataset(
  dataset_id,
  document_path: str,
  ground_truth: typing.Union[str, dict],
  document_id=None,
  mime_type=None,
  stratification_set=None)
```

Uploads a single document and its ground truth to a specific dataset
- Argument dataset_id: The ID of the dataset
- Argument document_path: The path to the PDF document
- Argument ground_truth: Path to the ground truth JSON file or an object representing the ground truth
- Argument document_id: The reference ID of the document
- Argument mime_type: The file type of the document
- Argument stratification_set: Defines a custom stratification set (training/validation/test)

**Returns**: Object containing information about the uploaded document


### upload_documents_directory_to_dataset
```python
DCApiClient.upload_documents_directory_to_dataset(
  dataset_id, path, file_extension='.pdf')
```

- Argument dataset_id: The ID of the dataset to upload the documents to
- Argument path: The path has to contain document data files and JSON file with GT with corresponding names
- Argument file_extension: The file format of the documents to be uploaded. Default is '.pdf'

**Returns**: An iterator with the upload results


### upload_documents_to_dataset
```python
DCApiClient.upload_documents_to_dataset(
  dataset_id, documents_paths: typing.List[str],
  ground_truths_paths: typing.List[typing.Union[str, dict]])
```


- Argument dataset_id: The ID of the dataset to upload the documents to
- Argument documents_paths: The paths of the PDF files
- Argument ground_truths_paths: The paths of the JSON files containing the ground truths

**Returns**: An iterator with the upload results


### train_model
```python
DCApiClient.train_model(model_name, dataset_id)
```

Trigger the process to train a new model version for documents classification, based on the documents in the
specific dataset and wait until this process is finished. The process may take significant time to complete
depending on the size of the dataset.
- Argument model_name: The name of the new model to train
- Argument dataset_id: The name of existing dataset containing enough documents for training

**Returns**: Object containing the statistical data about the trained model, including accuracy, recall and
precision


### delete_trained_model
```python
DCApiClient.delete_trained_model(model_name, model_version)
```

Deletes an existing trained model
- Argument model_name: Name of the existing model to delete
- Argument model_version: Version of the existing model to delete

**Returns**: An empty object


### get_trained_models_info
```python
DCApiClient.get_trained_models_info()
```

Gets information about all trained models

**Returns**: An array of trained models corresponding to the 'models' part of the json response . Each model
information contains training status and training accuracy data.


### get_trained_model_info
```python
DCApiClient.get_trained_model_info(model_name, model_version)
```

Gets information about a specific trained model
- Argument model_name: The name of the model
- Argument model_version: The version  of the model

**Returns**: Object containing the training status and training accuracy data


### deploy_model
```python
DCApiClient.deploy_model(model_name, model_version)
```

Deploys a trained model to be available for inference
- Argument model_name: The name of the trained model
- Argument model_version: The version of the trained model

**Returns**: Object containing information about the deployed model serving


### get_deployed_models_info
```python
DCApiClient.get_deployed_models_info()
```

Gets information about all deployed model servings

**Returns**: An array of all deployed model servings corresponding to the 'deployments' part if the json response


### get_deployed_model_info
```python
DCApiClient.get_deployed_model_info(model_name_or_deployment_id,
                                    model_version=None)
```

Gets information about a specific deployed model serving. This method can be called either with the ID of the
deployed model or with the model name and version
- Argument model_name_or_deployment_id: ID of the deployed model or the model name, if the model name is provided,
version has to be provided as well
- Argument model_version: The version of the deployed model

**Returns**: Object containing the information about the deployed model serving


### undeploy_model
```python
DCApiClient.undeploy_model(model_name_or_deployment_id,
                           model_version=None)
```

Removes a deployment of the specific model serving. This method can be called either with the ID of the
deployed model or with the model name and version
- Argument model_name_or_deployment_id: ID of the deployed model or the model name, if the model name is provided,
version has to be provided as well
- Argument model_version: The version of the deployed model

**Returns**: An empty object


# sap_business_document_processing.document_information_extraction_client.dox_api_client


## DoxApiClient
```python
DoxApiClient(self,
             base_url,
             client_id,
             client_secret,
             uaa_url,
             url_path_prefix='document-information-extraction/v1/',
             polling_threads=5,
             polling_sleep=5,
             polling_max_attempts=60,
             logging_level=30)
```

This class provides an interface to access SAP Document Information Extraction REST API from a Python application.
The structure of the values returned by all the methods is documented in the API reference:
https://help.sap.com/viewer/5fa7265b9ff64d73bac7cec61ee55ae6/SHIP/en-US/ded7d34e60f1422ba2e04e892a7f0e25.html

- Argument base_url: The service URL taken from the service key (key 'url' in service key JSON)
- Argument client_id: The XSUAA client ID taken from the service key (key 'uaa.clientid' in service key JSON)
- Argument client_secret: The XSUAA client secret taken from the service key (key 'uaa.clientsecret' in service key JSON)
- Argument uaa_url: The XSUAA URL taken from the service key (key 'uaa.url' in the service key JSON)
- Argument polling_threads: Number of threads used to poll for asynchronous APIs
- Argument polling_sleep: Number of seconds to wait between the polling attempts for APIs, the minimal value is 0.2
- Argument polling_max_attempts: Maximum number of attempts used to poll for asynchronous APIs
- Argument logging_level: INFO level will log the operations progress, the default level WARNING should not
produce any logs


### get_capabilities
```python
DoxApiClient.get_capabilities()
```

Gets the capabilities available for the service instance.

**Returns**: Dictionary with available extraction fields, enrichment and document types.


### create_client
```python
DoxApiClient.create_client(client_id, client_name)
```

Creates a new client for whom a document can be uploaded
- Argument client_id: The ID of the new client
- Argument client_name: The name of the new client

**Returns**: The API endpoint response as dictionary


### create_clients
```python
DoxApiClient.create_clients(clients: list)
```

Creates one or more clients for whom documents can be uploaded
- Argument clients: A list of clients to be created. For the format of a client see documentation

**Returns**: The API endpoint response as dictionary


### get_clients
```python
DoxApiClient.get_clients(top: int = 100,
                         skip: int = None,
                         client_id_starts_with: str = None)
```

Gets all existing clients filtered by the parameters
- Argument top: The maximum number of clients to get. Default is 100
- Argument skip: (optional) Index of the first client to get
- Argument client_id_starts_with: (optional) Filters the clients by the characters the ID starts with

**Returns**: List of existing clients as dictionaries corresponding to the 'payload' part of the json response


### delete_client
```python
DoxApiClient.delete_client(client_id)
```

Deletes a client with the given client ID
- Argument client_id: The ID of the client to be deleted

**Returns**: The API endpoint response as dictionary


### delete_clients
```python
DoxApiClient.delete_clients(client_ids: list = None)
```

Deletes multiple clients with the given client IDs
- Argument client_ids: (optional) List of IDs of clients to be deleted. If no IDs are provided, all clients will be
deleted

**Returns**: The API endpoint response as dictionary


### post_client_capability_mapping
```python
DoxApiClient.post_client_capability_mapping(
  client_id,
  document_type: str = 'paymentAdvice',
  file_type: str = 'Excel',
  header_fields: typing.Union[str, typing.List[str]] = None,
  line_item_fields: typing.Union[str, typing.List[str]] = None)
```

Post the client capability mapping for the Identifier API provided by the customer to the entity client DB
- Argument client_id: The ID of the client for which to upload the capability mapping
- Argument document_type: The document type of for which the mapping applies. Default is 'paymentAdvice'
- Argument file_type: The file type for which the mapping applies. Default is 'Excel'
- Argument header_fields: A list of mappings for the header fields. For the format see documentation
- Argument line_item_fields: A list of mappings for the line item fields. For the format see documentation

**Returns**: The API endpoint response as dictionary


### post_client_capability_mapping_with_options
```python
DoxApiClient.post_client_capability_mapping_with_options(
  client_id, options: dict)
```

Post the client capability mapping for the Identifier API provided by the customer to the entity client DB
- Argument client_id: The ID of the client for which to upload the capability mapping
- Argument options: The mapping that should be uploaded. For the format see documentation

**Returns**: The API endpoint response as dictionary


### extract_information_from_document
```python
DoxApiClient.extract_information_from_document(
  document_path: str,
  client_id,
  document_type: str,
  mime_type: str = 'application/pdf',
  header_fields: typing.Union[str, typing.List[str]] = None,
  line_item_fields: typing.Union[str, typing.List[str]] = None,
  template_id=None,
  schema_id=None,
  received_date=None,
  enrichment=None,
  return_null_values: bool = False)
```

Extracts the information from a document. The function will run until a processing result can be returned or
a timeout is reached
- Argument document_path: The path to the document
- Argument client_id: The client ID for which the document should be uploaded
- Argument document_type: The type of the document being uploaded. For available document types see documentation
- Argument mime_type: Content type of the uploaded file. If 'unknown' is given, the content type is fetched
automatically. Default is 'application/pdf'. The 'constants.py' file contains
CONTENT_TYPE_[JPEG, PDF, PNG, TIFF, UNKNOWN] that can be used here.
- Argument header_fields: A list of header fields to be extracted. Can be given as list of strings or as comma
separated string. If none are given, no header fields will be extracted. Will be ignored, if schema_id is
provided
- Argument line_item_fields: A list of line item fields to be extracted. Can be given as list of strings
or as comma separated string. If none are given, no line item fields will be extracted. Will be ignored, if
schema_id is provided.
- Argument template_id: (optional) The ID of the template to be used for this document
- Argument schema_id: (optional) The ID of the schema to be used for the document. Only schema_id OR header_fields
and line_item_fields can be used. If given, header_fields and line_item_fields are ignored
- Argument received_date: (optional) The date the document was received
- Argument enrichment: (optional) A dictionary of entities that should be used for entity matching
- Argument return_null_values: Flag if fields with null as value should be included in the response or not.
Default is False

**Returns**: The extracted information of the document as dictionary


### extract_information_from_document_with_options
```python
DoxApiClient.extract_information_from_document_with_options(
  document_path: str,
  options: dict,
  mime_type: str = 'application/pdf',
  return_null_values: bool = False)
```

Extracts the information from a document. The function will run until a processing result can be returned or
a timeout is reached.
- Argument document_path: The path to the document
- Argument options: The options for processing the document as dictionary. It has to include at least a valid client
ID and document type
- Argument mime_type: Content type of the uploaded file. If 'unknown' is given, the content type is fetched
automatically. Default is 'application/pdf'. The 'constants.py' file contains
CONTENT_TYPE_[JPEG, PDF, PNG, TIFF, UNKNOWN] that can be used here.
- Argument return_null_values: Flag if fields with null as value should be included in the response or not.
Default is False

**Returns**: The extracted information of the document as dictionary


### extract_information_from_documents
```python
DoxApiClient.extract_information_from_documents(
  document_paths: typing.List[str],
  client_id,
  document_type: str,
  mime_type: str = 'application/pdf',
  mime_type_list: typing.List[str] = None,
  header_fields: typing.Union[str, typing.List[str]] = None,
  line_item_fields: typing.Union[str, typing.List[str]] = None,
  template_id=None,
  schema_id=None,
  received_date=None,
  enrichment=None,
  return_null_values: bool = False)
```

Extracts the information from multiple documents. The function will run until all documents have been processed
or a timeout is reached. The given parameters will be used for all documents
- Argument document_paths: A list of paths to the documents
- Argument client_id: The client ID for which the documents should be uploaded
- Argument document_type: The type of the document being uploaded. For available document types see documentation
- Argument mime_type: Content type that is used for all uploaded files. If 'unknown' is given, the content type is
fetched automatically. Default is 'application/pdf'. The 'constants.py' file contains
CONTENT_TYPE_[JPEG, PDF, PNG, TIFF, UNKNOWN] that can be used here.
- Argument mime_type_list: A list of content types for each file to be uploaded. Has to have the same length as
'document_paths'. If this parameter is given, 'mime_type' will be ignored.
- Argument header_fields: A list of header fields to be extracted. Can be given as list of strings or as comma
separated string. If none are given, no header fields will be extracted. Will be ignored, if schema_id is
provided
- Argument line_item_fields: A list of line item fields to be extracted. Can be given as list of strings
or as comma separated string. If none are given, no line item fields will be extracted. Will be ignored, if
schema_id is provided.
- Argument template_id: (optional) The ID of the template to be used for the documents
- Argument schema_id: (optional) The ID of the schema to be used for the documents. Only schema_id OR header_fields
and line_item_fields can be used. If given, header_fields and line_item_fields are ignored
- Argument received_date: (optional) The date the documents were received
- Argument enrichment: (optional) A dictionary of entities that should be used for entity matching. For the format
see documentation
- Argument return_null_values: Flag if fields with null as value should be included in the responses or not.
Default is False

**Returns**: An iterator with extracted information for successful documents and exceptions for failed documents.
Use next(iterator) within a try-catch block to filter the failed documents.


### extract_information_from_documents_with_options
```python
DoxApiClient.extract_information_from_documents_with_options(
  document_paths: typing.List[str],
  options: dict,
  mime_type: str = 'application/pdf',
  mime_type_list: typing.List[str] = None,
  return_null_values: bool = False)
```

Extracts the information from multiple documents. The function will run until all documents have been processed
or a timeout is reached. The given options will be used for all documents
- Argument document_paths: A list of paths to the documents
- Argument options: The options for processing the documents as dictionary. It has to include at least a valid
client ID and document type
- Argument mime_type: Content type that is used for all uploaded files. If 'unknown' is given, the content type is
fetched automatically. Default is 'application/pdf'. The 'constants.py' file contains
CONTENT_TYPE_[JPEG, PDF, PNG, TIFF, UNKNOWN] that can be used here.
- Argument mime_type_list: A list of content types for each file to be uploaded. Has to have the same length as
'document_paths'. If this parameter is given, 'mime_type' will be ignored.
- Argument return_null_values: Flag if fields with null as value should be included in the responses or not.
Default is False

**Returns**: An iterator with extracted information for successful documents and exceptions for failed documents.
Use next(iterator) within a try-catch block to filter the failed documents.


### get_extraction_for_document
```python
DoxApiClient.get_extraction_for_document(
  document_id,
  extracted_values: bool = None,
  return_null_values: bool = False)
```

Gets the extracted information of an uploaded document by document ID. Raises an exception, when the document
failed or didn't finish processing after the maximum number of requests
- Argument document_id: The ID of the document
- Argument extracted_values: (optional) Flag if the extracted values or the ground truth should be returned. If set
to `True` the extracted values are returned. If set to `False` the ground truth is returned. If no ground truth
is available, the extracted values will be returned either way. If `None` is given, the ground truth is returned
if available
- Argument return_null_values: Flag if fields with null as value should be included in the response or not.
Default is False

**Returns**: The extracted information of the processed document or the ground truth as dictionary


### get_extraction_for_documents
```python
DoxApiClient.get_extraction_for_documents(
  document_ids: list,
  extracted_values: bool = None,
  return_null_values: bool = False)
```

Gets the extracted information for multiple documents given their document IDs
- Argument document_ids: A list of IDs of documents
- Argument extracted_values: (optional) Flag if the extracted values or the ground truth should be returned. If set
to `True` the extracted values are returned. If set to `False` the ground truth is returned. If no ground truth
is available, the extracted values will be returned either way. If `None` is given, the ground truth is returned
if available
- Argument return_null_values: Flag if fields with null as value should be included in the response or not.
Default is False

**Returns**: An iterator with extracted information or ground truths for successful documents and exceptions
for failed documents. Use next(iterator) within a try-catch block to filter the failed documents.


### get_document_list
```python
DoxApiClient.get_document_list(client_id=None)
```

Gets a list of  document jobs filtered by the client ID
- Argument client_id: (optional) The client ID for which the document jobs should be get. Gets all document jobs if
no client ID is given

**Returns**: A list of document jobs as dictionaries corresponding to the 'results' part of the json response


### delete_documents
```python
DoxApiClient.delete_documents(document_ids: list = None)
```

Deletes a list of documents or all documents
- Argument document_ids: (optional) A list of document IDs that shall be deleted. If this argument is not provided,
all documents are deleted.

**Returns**: The API endpoint response as dictionary


### upload_enrichment_data
```python
DoxApiClient.upload_enrichment_data(client_id,
                                    data,
                                    data_type: str,
                                    subtype: str = None)
```

Creates one or more enrichment data records. The function returns after all data was created successfully or
raises an exception if something went wrong.
- Argument client_id: The client ID for which the data records shall be created.
- Argument data: A list of data to be uploaded. For the format of the data see documentation
- Argument data_type: The type of data which is uploaded. For the available data types see documentation
- Argument subtype: (optional) Only used for type 'businessEntity'. For the available subtypes see documentation

**Returns**: The API endpoint response as dictionary


### get_enrichment_data
```python
DoxApiClient.get_enrichment_data(client_id,
                                 data_type: str,
                                 subtype: str = None,
                                 top: int = None,
                                 skip: int = None,
                                 data_id=None,
                                 system=None,
                                 company_code=None)
```

Gets the enrichment data records filtered by the provided parameters
- Argument client_id: The ID of the client for which the enrichment data was created
- Argument data_type: The type of the data records. For the available data types see documentation
- Argument subtype: (optional) The subtype of the records. Only used for type 'businessEntity'. For the available
subtypes see documentation
- Argument top: (optional) The maximum number records to be returned
- Argument skip: (optional) The index of the first record to be returned
- Argument data_id: (optional) The ID of a single data record. Only one will be returned
- Argument system: (optional) The system of a single record
- Argument company_code: (optional) The company code of a single record

**Returns**: A list of enrichment data records corresponding to the 'value' part of the json response. Returns a
list with one item when data_id is given


### delete_all_enrichment_data
```python
DoxApiClient.delete_all_enrichment_data(data_type: str = None)
```

This endpoint is deleting all enrichment data records for the account
- Argument data_type: (Optional) The type of enrichment data that should be deleted. For the available data types
see documentation

**Returns**: The API endpoint response as dictionary


### delete_enrichment_data
```python
DoxApiClient.delete_enrichment_data(client_id,
                                    enrichment_records: list,
                                    data_type: str,
                                    subtype: str = None,
                                    delete_async: bool = False)
```

Deletes the enrichment data records with the given IDs in the payload
- Argument client_id: The client ID for which the enrichment data was created
- Argument enrichment_records: A list of dictionaries with the form: ``{'id':'', 'system':'', 'companyCode':''}``
- Argument data_type: The type of enrichment data that should be deleted. For the available document data types see
documentation
- Argument subtype: (optional) The subtype of the records that should be deleted. Only used for type
'businessEntity'. For the available subtypes see documentation
- Argument delete_async: Set to ``True`` to delete data records asynchronously. Asynchronous deletion should be
used when deleting large amounts of data to improve performance. Default is ``False``

**Returns**: The API endpoint response as dictionary


### activate_enrichment_data
```python
DoxApiClient.activate_enrichment_data(params=None)
```

Activates all enrichment data records for the current tenant
- Argument params: Optional. A dictionary, list of tuples or bytes to send as a query string.

**Returns**: The API endpoint response as dictionary


### get_image_for_document
```python
DoxApiClient.get_image_for_document(document_id, page_no: int)
```

Gets the image of a document page for the given document ID and page number
- Argument document_id: The ID of the document
- Argument page_no: The page number for which to get the image

**Returns**: The image of the document page in the PNG format as bytes


### get_document_page_text
```python
DoxApiClient.get_document_page_text(document_id, page_no: int)
```

Gets the text for a document page for the given document ID and page number
- Argument document_id: The ID of the document
- Argument page_no: The page number for which to get the text

**Returns**: The text for the page as a list of dictionaries corresponding to the 'value' part of the json response


### get_document_text
```python
DoxApiClient.get_document_text(document_id)
```

Gets the text for all pages of a document
- Argument document_id: The ID of the document

**Returns**: A dictionary mapping the page numbers to the text corresponding to the 'results' part of the json reponse


### get_request_for_document
```python
DoxApiClient.get_request_for_document(document_id)
```

Gets the request of a processed document
- Argument document_id: The ID of the document

**Returns**: The request of the document as dictionary


### get_page_dimensions_for_document
```python
DoxApiClient.get_page_dimensions_for_document(document_id, page_no: int)
```

Gets the dimensions of a document page
- Argument document_id: The ID of the document
- Argument page_no: The page number for which to get the dimensions

**Returns**: The height and width of the document page as dictionary


### get_all_dimensions_for_document
```python
DoxApiClient.get_all_dimensions_for_document(document_id)
```

Gets the dimensions of all document pages
- Argument document_id: The ID of the document

**Returns**: The height and width of all document pages as dictionary with page number as key corresponding to the
'results' part of the json response


### post_ground_truth_for_document
```python
DoxApiClient.post_ground_truth_for_document(
  document_id, ground_truth: typing.Union[str, dict])
```

Saves the ground truth for a document
- Argument document_id: The ID of the document
- Argument ground_truth: Path to the ground truth JSON file or an object representing the ground truth

**Returns**: The API endpoint response as dictionary


### post_confirm_document
```python
DoxApiClient.post_confirm_document(document_id,
                                   data_for_retraining=False)
```

Sets the document status to confirmed
- Argument document_id: The ID of the document
- Argument data_for_retraining: Indicates whether the document should be allowed for retraining. Default is False

**Returns**: The API endpoint response as dictionary


### create_schema
```python
DoxApiClient.create_schema(client_id, schema_name, schema_desc,
                           document_type, document_type_desc)
```

Creates a new schema
- Argument client_id: The client ID for which the schema shall be created
- Argument schema_name: Name for the schema to be created
- Argument schema_desc: Description for the schema to be created
- Argument document_type: Document Type which will be supported by the schema
- Argument document_type_desc: Document Type description for the schema to be created

**Returns**: The API endpoint response as dictionary


### get_schema_configurations
```python
DoxApiClient.get_schema_configurations(client_id,
                                       predefined: bool = None,
                                       document_type: str = None,
                                       skip: int = None,
                                       top: int = None,
                                       order_by: str = None)
```

Retrieves all schemas for the provided client
- Argument client_id: The client ID for which the schema details need to be fetched
- Argument predefined: (optional) The arguement which specifies if the schema is predefined schema or not
- Argument document_type: (optional) The argument to filter out schemas based on the provided document_type
- Argument skip: (optional) The index of the first record to be returned
- Argument top: (optional) The maximum number records to be returned
- Argument order_by: (optional) The value to order the elements returned based on it

**Returns**: The schema values as dictionary with 'schemas' as key of the json response


### delete_schema
```python
DoxApiClient.delete_schema(client_id, schema_id)
```

Deletes specified schema for a client
- Argument client_id: The client ID for which the schema shall be deleted
- Argument schema_id: ID of the schema that shall be deleted [string]

**Returns**: The API endpoint response as dictionary


### delete_schemas
```python
DoxApiClient.delete_schemas(client_id, schema_ids)
```

Deletes multiple schemas for a client
- Argument client_id: The client ID for which the schemas shall be deleted
- Argument schema_ids: IDs of the schemas that shall be deleted [list of strings]

**Returns**: The API endpoint response as dictionary


### create_schema_version
```python
DoxApiClient.create_schema_version(client_id, schema_id)
```

Creates a new version for the schema
- Argument client_id: The client ID for which the new version shall be created
- Argument schema_id: ID for the schema from which new version shall be created

**Returns**: The API endpoint response as dictionary


### get_schema_configuration_details
```python
DoxApiClient.get_schema_configuration_details(client_id, schema_id)
```

Retrieves details for a specific schema
- Argument client_id: The client ID for which the schema details shall be fetched
- Argument schema_id: The ID of the schema whose details shall be fetched

**Returns**: The schema details as dictionary


### update_schema_configuration
```python
DoxApiClient.update_schema_configuration(client_id, schema_id,
                                         schema_name, schema_desc,
                                         document_type_desc)
```

Updates the schema details for a specific schema
- Argument client_id: The client ID for which the details shall be updated
- Argument schema_id: ID for the schema for which details shall be updated
- Argument schema_name: Name of the schema (updated or old)
- Argument schema_desc: Description for the schema (updated or old)
- Argument document_type_desc: Description of the document-type for the schema (updated or old)

**Returns**: The API endpoint response as dictionary


### add_schema_version_fields
```python
DoxApiClient.add_schema_version_fields(client_id,
                                       schema_id,
                                       version,
                                       header_fields=[],
                                       line_item_fields=[])
```

Adds Header and Line Item fields to a schema version
- Argument client_id: The client ID for which the fields shall be added
- Argument schema_id: ID for the schema for which fields shall be added
- Argument version: Version of the schema for which fields shall be added
- Argument header_fields: (optional) List of header fields that shall be added
- Argument line_item_fields: (optional) List of line item fields that shall be added

**Returns**: The API endpoint response as dictionary


### activate_schema_version
```python
DoxApiClient.activate_schema_version(client_id, schema_id, version)
```

Activates a schema version
- Argument client_id: The client ID for which the schema version shall be activated
- Argument schema_id: ID for the schema for which the schema version shall be activated
- Argument version: Version of the schema that shall be activated

**Returns**: The API endpoint response as dictionary


### deactivate_schema_version
```python
DoxApiClient.deactivate_schema_version(client_id, schema_id, version)
```

Deactivates a schema version
- Argument client_id: The client ID for which the schema version shall be deactivated
- Argument schema_id: ID for the schema for which the schema version shall be deactivated
- Argument version: Version of the schema that shall be deactivated

**Returns**: The API endpoint response as dictionary


### get_schema_capabilities
```python
DoxApiClient.get_schema_capabilities()
```

Retrieves the capabilities for all schemas

**Returns**: The schema capabilities as dictionary


### delete_schema_versions
```python
DoxApiClient.delete_schema_versions(client_id, schema_id, versions)
```

Deletes specific versions of the schema
- Argument client_id: The client ID for which the schema version shall be deleted
- Argument schema_id: ID for the schema for which the schema version shall be deleted
- Argument versions: List of versions of the schema that shall be deleted

**Returns**: The API endpoint response as dictionary


### get_all_schema_versions
```python
DoxApiClient.get_all_schema_versions(client_id, schema_id)
```

Retrieves all the versions associated with a schema
- Argument client_id: The client ID for which the schema versions shall be fetched
- Argument schema_id: ID for the schema for which the schema versions shall be fetched

**Returns**: The schema version details as dictionary with 'schemas' as key of the json response


### get_schema_version_details
```python
DoxApiClient.get_schema_version_details(client_id, schema_id, version)
```

Retrieves specific version details associated with a schema
- Argument client_id: The client ID for which the schema version shall be fetched
- Argument schema_id: ID for the schema for which the schema version shall be fetched
- Argument version: Version of the schema that shall be fetched

**Returns**: Schema version details as dictionary


### create_schema_with_fields
```python
DoxApiClient.create_schema_with_fields(client_id,
                                       schema_name,
                                       schema_desc,
                                       document_type,
                                       document_type_desc,
                                       model_type,
                                       setup_type_version=None,
                                       header_fields=None,
                                       line_fields=None)
```

Creates schema along with header fields and line items
- Argument client_id: The client ID for which the schema shall be created
- Argument schema_name: Name for the schema to be created
- Argument schema_desc: Description for the schema to be created
- Argument document_type: Document Type which will be supported by the schema
- Argument document_type_desc: Document Type description for the schema to be created
- Argument model_type: Type of model for document extraction
- Argument setup_type_version: (optional) The version of setup_type for the fields to be added
- Argument header_fields: (optional) List of header fields that shall be added
- Argument line_fields: (optional) List of line item fields that shall be added

**Returns**: The response message and schema_id as a dictionary

Header and Line items should have name, description, label and datatype in dictionary format.

