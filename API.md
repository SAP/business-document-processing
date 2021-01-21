
# sap_document_classification_client


# sap_document_classification_client.dc_api_client


## DCApiClient
```python
DCApiClient(self,
            base_url,
            client_id,
            client_secret,
            uaa_url,
            polling_threads=5,
            polling_sleep=5,
            polling_long_sleep=30,
            polling_max_attempts=120,
            logging_level=30)
```

This class provides an interface to access SAP Document Classification REST API from a Python application.
Structure of values returned by all the methods is documented in Swagger. See Swagger UI by adding:
/document-classification/v1 to your Document Classification service key URL value (from outside the uaa section).

- Argument base_url: The service URL taken from the service key (key 'url' in service key JSON)
- Argument client_id: The client ID taken from the service key (key 'uaa.clientid' in service key JSON)
- Argument client_secret: The client secret taken from the service key (key 'uaa.clientsecret' in service key JSON)
- Argument uaa_url: The XSUAA URL taken from the service key (key 'uaa.url' in service key JSON)
- Argument polling_threads: Number of threads used to poll for asynchronous DC APIs, the maximal value is 15
- Argument polling_sleep: Number of seconds to wait between the polling attempts for most of the APIs,
the minimal value is 0.2
- Argument polling_long_sleep: Number of seconds to wait between the polling attempts for model training and
deployment operations, the minimal value is 0.2
- Argument polling_max_attempts: Maximum number of attempts used to poll for asynchronous DC APIs
- Argument logging_level: INFO level will log the operations progress, the default level WARNING should not
produce any logs


### classify_document
```python
DCApiClient.classify_document(document_path,
                              model_name,
                              model_version,
                              reference_id=None,
                              mimetype=None)
```

Submits request for document classification, checks the response and returns the reference ID for the
uploaded document

- Argument document_path: Path to the PDF file on the disk
- Argument model_name: The name of the model that was successfully deployed to be used for the classification
- Argument model_version: The version of the model that was successfully deployed to be used for the classification
- Argument reference_id: In case the document reference ID has to be managed by the user, it can be specified.
In this case the user is responsible for providing unique reference IDs for different documents
- Argument mimetype: The file type of the document uploaded

**Returns**: Object containing the reference ID of the classified document and the classification results


### classify_documents
```python
DCApiClient.classify_documents(documents_paths,
                               model_name,
                               model_version,
                               silent=False)
```

Submits requests for classification of multiple documents, checks the response and returns the reference ID
for the classified documents

- Argument documents_paths: Paths to the PDF files on the disk
- Argument model_name: The name of the model that was successfully deployed to be used for the classification
- Argument model_version: The version of the model that was successfully deployed to be used for the classification
- Argument silent: If set to True will not throw an exception if classification for one or more documents failed

**Returns**: Array of objects containing the reference ID of the classified document and the classification results


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

**Returns**: Empty object


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

**Returns**: Object containing an array of datasets


### get_dataset_documents_info
```python
DCApiClient.get_dataset_documents_info(dataset_id,
                                       top=None,
                                       skip=None,
                                       count=None)
```

Gets the information about all the documents in a specific dataset
- Argument dataset_id: The ID of an existing dataset
- Argument top: Pagination: number of documents to be fetched in the current request
- Argument skip: Pagination: number of documents to skip for the current request
- Argument count: Flag to show count of number of documents in the dataset

**Returns**: Object that contains array of the documents


### get_classification_documents_info
```python
DCApiClient.get_classification_documents_info(model_name, model_version)
```

Gets the information about recently classified documents
- Argument model_name: The name of the model against which the documents were classified
- Argument model_version: The version of the model against which the documents were classified

**Returns**: Object containing an array of documents, information about each document includes its reference ID
and the classification status


### upload_document_to_dataset
```python
DCApiClient.upload_document_to_dataset(dataset_id,
                                       document_path,
                                       ground_truth,
                                       document_id=None,
                                       mime_type=None)
```

Uploads a single document and its ground truth to a specific dataset
- Argument dataset_id: The ID of the dataset
- Argument document_path: The path to the PDF document
- Argument ground_truth: Path to the ground truth JSON file or an object representing the ground truth
- Argument document_id: The reference ID of the document
- Argument mime_type: The file type of the document

**Returns**: Object containing information about the uploaded document


### upload_documents_directory_to_dataset
```python
DCApiClient.upload_documents_directory_to_dataset(
  dataset_id, path, silent=False)
```

- Argument dataset_id: The dataset_id of dataset to upload the documents to
- Argument path: The path has to contain document data files and JSON file with GT with corresponding names
- Argument silent: If set to True will not throw exception when upload of one of the documents fails,
in this case the upload statuses in the results array have to be validated manually

**Returns**: Array with the upload results


### upload_documents_to_dataset
```python
DCApiClient.upload_documents_to_dataset(dataset_id,
                                        documents_paths,
                                        ground_truths_paths,
                                        silent=False)
```


- Argument dataset_id: The dataset_id of dataset to upload the documents to
- Argument documents_paths: The paths of the PDF files
- Argument ground_truths_paths: The paths of the JSON files contining the ground truths
- Argument silent: If set to True will not throw exception when upload of one of the documents fails,
in this case the upload statuses in the results array have to be validated manually

**Returns**: Array with the upload results


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

**Returns**:


### get_trained_models_info
```python
DCApiClient.get_trained_models_info()
```

Gets information about all trained models

**Returns**: Object containing the array of trained models, each model information contains training status and
training accuracy data


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

**Returns**: Object containing the array of all deployed model servings


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

