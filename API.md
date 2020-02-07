# sap-document-classification-client

# sap-document-classification-client.dc_api_client

## DCApiClient
```python
DCApiClient(self, base_url, client_id, client_secret, uaa_url, polling_threads=10, polling_sleep=1, polling_long_sleep=30, polling_max_attempts=200, logging_level=30)
```

This class provides an interface to access SAP Document Classification REST API from a Python application.
Structure of values returned by all the methods is documented in Swagger.

### classify_document
```python
DCApiClient.classify_document(self, document_path, model_name, model_version, reference_id=None, mimetype='pdf')
```

Submits request for document classification, checks the response and returns the reference ID for the
uploaded document

:param document_path: Path to the PDF file on the disk
:param model_name: The name of the model that was successfully deployed to be used for the classification
:param model_version: The version of the model that was successfully deployed to be used for the classification
:param reference_id: In case the document reference ID has to be managed by the user, it can be specified.
In this case the user is responsible for providing unique reference IDs for different documents
:param mimetype: The file type of the document uploaded
:return: Object containing the reference ID of the classified document and the classification results

### classify_documents
```python
DCApiClient.classify_documents(self, documents_paths, model_name, model_version, silent=False)
```

Submits requests for classification of multiple documents, checks the response and returns the reference ID
for the classified documents

:param documents_paths: Paths to the PDF files on the disk
:param model_name: The name of the model that was successfully deployed to be used for the classification
:param model_version: The version of the model that was successfully deployed to be used for the classification
:param silent: If set to True will not throw an exception if classification for one or more documents failed
:return: Array of objects containing the reference ID of the classified document and the classification results

### create_dataset
```python
DCApiClient.create_dataset(self)
```

Creates an empty dataset
:return: Object containing the dataset id

### delete_dataset
```python
DCApiClient.delete_dataset(self, dataset_id)
```

Deletes a dataset with a given ID
:param dataset_id: The ID of the dataset to delete
:return: Object containing the ID of the deleted dataset and the number of documents deleted

### delete_training_document
```python
DCApiClient.delete_training_document(self, dataset_id, document_id)
```

Deletes a training document from a dataset
:param dataset_id: The ID of the dataset where the document is located
:param document_id: The reference ID of the document
:return: Empty object

### get_dataset_info
```python
DCApiClient.get_dataset_info(self, dataset_id)
```

Gets statistical information about a dataset with a given ID
:param dataset_id: The ID of the dataset
:return: Summary information about the dataset that includes the number of documents in different processing
stages

### get_datasets_info
```python
DCApiClient.get_datasets_info(self)
```

Gets summary information about the existing datasets
:return: Object containing an array of datasets

### get_dataset_documents_info
```python
DCApiClient.get_dataset_documents_info(self, dataset_id, top=None, skip=None, count=None)
```

Gets the information about all the documents in a specific dataset
:param dataset_id: The ID of an existing dataset
:param top: Pagination: number of documents to be fetched in the current request
:param skip: Pagination: number of documents to skip for the current request
:param count: Flag to show count of number of documents in the dataset
:return: Object that contains array of the documents

### get_classification_documents_info
```python
DCApiClient.get_classification_documents_info(self, model_name, model_version)
```

Gets the information about recently classified documents
:param model_name: The name of the model against which the documents were classified
:param model_version: The version of the model against which the documents were classified
:return: Object containing an array of documents, information about each document includes its reference ID
and the classification status

### upload_document_to_dataset
```python
DCApiClient.upload_document_to_dataset(self, dataset_id, document_path, ground_truth, document_id=None, mime_type='pdf')
```

Uploads a single document and its ground truth to a specific dataset
:param dataset_id: The ID of the dataset
:param document_path: The path to the PDF document
:param ground_truth: Path to the ground truth JSON file or an object representing the ground truth
:param document_id: The reference ID of the document
:param mime_type: The file type of the document
:return: Object containing information about the uploaded document

### upload_documents_directory_to_dataset
```python
DCApiClient.upload_documents_directory_to_dataset(self, dataset_id, path, silent=False)
```

:param dataset_id: The dataset_id of dataset to upload the documents to
:param path: The path has to contain PDF and JSON files with corresponding names
:param silent: If set to True will not throw exception when upload of one of the documents fails,
in this case the upload statuses in the results array have to be validated manually
:return: Array with the upload results

### upload_documents_to_dataset
```python
DCApiClient.upload_documents_to_dataset(self, dataset_id, documents_paths, ground_truths_paths, silent=False)
```


:param dataset_id: The dataset_id of dataset to upload the documents to
:param documents_paths: The paths of the PDF files
:param ground_truths_paths: The paths of the JSON files contining the ground truths
:param silent: If set to True will not throw exception when upload of one of the documents fails,
in this case the upload statuses in the results array have to be validated manually
:return: Array with the upload results

### train_model
```python
DCApiClient.train_model(self, model_name, dataset_id)
```

Trigger the process to train a new model version for documents classification, based on the documents in the
specific dataset and wait until this process is finished. The process may take significant time to complete
depending on the size of the dataset.
:param model_name: The name of the new model to train
:param dataset_id: The name of existing dataset containing enough documents for training
:return: Object containing the statistical data about the trained model, including accuracy, recall and
precision

### delete_trained_model
```python
DCApiClient.delete_trained_model(self, model_name, model_version)
```

Deletes an existing trained model
:param model_name: Name of the existing model to delete
:param model_version: Version of the existing model to delete
:return:

### get_trained_models_info
```python
DCApiClient.get_trained_models_info(self)
```

Gets information about all trained models
:return: Object containing the array of trained models, each model information contains training status and
training accuracy data

### get_trained_model_info
```python
DCApiClient.get_trained_model_info(self, model_name, model_version)
```

Gets information about a specific trained model
:param model_name: The name of the model
:param model_version: The version  of the model
:return: Object containing the training status and training accuracy data

### deploy_model
```python
DCApiClient.deploy_model(self, model_name, model_version)
```

Deploys a trained model to be available for inference
:param model_name: The name of the trained model
:param model_version: The version of the trained model
:return: Object containing information about the deployed model serving

### get_deployed_models_info
```python
DCApiClient.get_deployed_models_info(self)
```

Gets information about all deployed model servings
:return: Object containing the array of all deployed model servings

### get_deployed_model_info
```python
DCApiClient.get_deployed_model_info(self, model_name_or_deployment_id, model_version=None)
```

Gets information about a specific deployed model serving. This method can be called either with the ID of the
deployed model or with the model name and version
:param model_name_or_deployment_id: ID of the deployed model or the model name, if the model name is provided,
version has to be provided as well
:param model_version: The version of the deployed model
:return: Object containing the information about the deployed model serving

### undeploy_model
```python
DCApiClient.undeploy_model(self, model_name_or_deployment_id, model_version=None)
```

Removes a deployment of the specific model serving. This method can be called either with the ID of the
deployed model or with the model name and version
:param model_name_or_deployment_id: ID of the deployed model or the model name, if the model name is provided,
version has to be provided as well
:param model_version: The version of the deployed model
:return: An empty object

