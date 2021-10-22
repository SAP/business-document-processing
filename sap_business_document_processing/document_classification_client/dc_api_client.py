# SPDX-FileCopyrightText: 2020 2019-2020 SAP SE
#
# SPDX-License-Identifier: Apache-2.0

from concurrent.futures import ThreadPoolExecutor
import json
import logging
import os
import time
from typing import Iterator, List, Union

from sap_business_document_processing.common.http_client_base import CommonClient
from sap_business_document_processing.common.helpers import get_ground_truth_json, function_wrap_errors
from .constants import API_DATASET_ID_FIELD, API_DATASETS_FIELD, API_DEPLOYMENT_ID_FIELD, API_DEPLOYMENTS_FIELD, \
    API_DOCUMENT_FIELD, API_DOCUMENT_ID_FIELD, API_GROUND_TRUTH_FIELD, API_MIME_TYPE_FIELD, API_MODELS_FIELD, \
    API_MODEL_NAME_FIELD, API_MODEL_VERSION_FIELD, API_PAGINATION_COUNT_PARAM, API_PAGINATION_SKIP_PARAM, \
    API_PAGINATION_TOP_PARAM, API_PARAMETERS_FIELD, API_RESULTS_FIELD, API_STRATIFICATION_SET_FIELD, DATASETS_ENDPOINT,\
    DATASET_DOCUMENTS_ENDPOINT, DATASET_DOCUMENT_ENDPOINT, DATASET_ENDPOINT, DEPLOYMENTS_ENDPOINT, DOCUMENTS_ENDPOINT, \
    DOCUMENT_RESULT_ENDPOINT, MODEL_DEPLOYMENT_ENDPOINT, MODEL_TRAINING_JOBS_ENDPOINT, TRAINED_MODELS_ENDPOINT, \
    TRAINED_MODEL_ENDPOINT


class DCApiClient(CommonClient):
    """
    This class provides an interface to access SAP Document Classification REST API from a Python application.
    The structure of values returned by all the methods is documented in the API reference:
    https://help.sap.com/viewer/ca60cd2ed44f4261a3ae500234c46f37/SHIP/en-US/c1045a561faf4ba0ae2b0e7713f5e6c4.html

    :param base_url: The service URL taken from the service key (key 'url' in service key JSON)
    :param client_id: The XSUAA client ID taken from the service key (key 'uaa.clientid' in service key JSON)
    :param client_secret: The XSUAA client secret taken from the service key (key 'uaa.clientsecret' in service key JSON)
    :param uaa_url: The XSUAA URL taken from the service key (key 'uaa.url' in service key JSON)
    :param polling_threads: Number of threads used to poll for asynchronous DC APIs
    :param polling_sleep: Number of seconds to wait between the polling attempts for most of the APIs,
    the minimal value is 0.2
    :param polling_long_sleep: Number of seconds to wait between the polling attempts for model training and
    deployment operations, the minimal value is 0.2
    :param polling_max_attempts: Maximum number of attempts used to poll for asynchronous DC APIs
    :param logging_level: INFO level will log the operations progress, the default level WARNING should not
    produce any logs
    """

    def __init__(self,
                 base_url,
                 client_id,
                 client_secret,
                 uaa_url,
                 url_path_prefix='document-classification/v1/',
                 polling_threads=5,
                 polling_sleep=5,
                 polling_long_sleep=30,
                 polling_max_attempts=120,
                 logging_level=logging.WARNING):
        """
        Creates a new instance of a client object to access the SAP Document Classification service
        """
        super(DCApiClient, self).__init__(base_url=base_url,
                                          client_id=client_id,
                                          client_secret=client_secret,
                                          uaa_url=uaa_url,
                                          polling_threads=polling_threads,
                                          polling_sleep=polling_sleep,
                                          polling_long_sleep=polling_long_sleep,
                                          polling_max_attempts=polling_max_attempts,
                                          url_path_prefix=url_path_prefix,
                                          logger_name='DCApiClient',
                                          logging_level=logging_level)

    # Inference
    def classify_document(self, document_path: str, model_name, model_version, reference_id=None, mime_type=None) -> dict:
        """
        Submits request for document classification, checks the response and returns the reference ID for the
        uploaded document

        :param document_path: Path to the PDF file on the disk
        :param model_name: The name of the model that was successfully deployed to be used for the classification
        :param model_version: The version of the model that was successfully deployed to be used for the classification
        :param reference_id: In case the document reference ID has to be managed by the user, it can be specified.
        In this case the user is responsible for providing unique reference IDs for different documents
        :param mime_type: The file type of the document uploaded
        :return: Object containing the reference ID of the classified document and the classification results
        """

        options = {}
        if reference_id is not None:
            options[API_DOCUMENT_ID_FIELD] = reference_id
        if mime_type is not None:
            options[API_MIME_TYPE_FIELD] = mime_type
        data = {API_PARAMETERS_FIELD: json.dumps(options)}
        with open(document_path, 'rb') as file:
            response = self.post(DOCUMENTS_ENDPOINT(modelName=model_name, modelVersion=model_version),
                                 files={API_DOCUMENT_FIELD: file},
                                 data=data,
                                 log_msg_before=f'Submitting document {document_path} for classification',
                                 log_msg_after=f'Document {document_path} submitted for classification '
                                 f'successfully, waiting for result')
        classification_job = response.json()
        result = self._poll_for_url(DOCUMENT_RESULT_ENDPOINT(modelName=model_name,
                                                             modelVersion=model_version,
                                                             id=classification_job[API_DOCUMENT_ID_FIELD]),
                                    wait_status=409).json()
        return result

    def _classify_document_wrap_errors(self,
                                       document_path,
                                       model_name,
                                       model_version,
                                       reference_id=None,
                                       mime_type=None):
        result = function_wrap_errors(self.classify_document, document_path, model_name, model_version,
                                      reference_id, mime_type)
        if isinstance(result, Exception):
            result.document_path = document_path
        else:
            result['document_path'] = document_path
        return result

    def classify_documents(self, documents_paths: List[str], model_name, model_version) -> Iterator[dict]:
        """
        Submits requests for classification of multiple documents, checks the response and returns the reference ID
        for the classified documents

        :param documents_paths: Paths to the PDF files on the disk
        :param model_name: The name of the model that was successfully deployed to be used for the classification
        :param model_version: The version of the model that was successfully deployed to be used for the classification
        :return: An iterator of objects containing the reference ID of the classified document and the classification
        results
        """
        number_of_documents = len(documents_paths)
        assert number_of_documents > 0, 'Please supply at least one document'
        self.logger.debug(f'Started classification of {number_of_documents} documents against the model {model_name}'
                          f' with version {model_version} in parallel using {self.polling_threads} threads')
        with ThreadPoolExecutor(min(self.polling_threads, number_of_documents)) as pool:
            results = pool.map(self._classify_document_wrap_errors, documents_paths, [model_name] * number_of_documents,
                               [model_version] * number_of_documents)
        self.logger.info(f'Finished classification of {number_of_documents} documents against the model {model_name} '
                         f'with version {model_version}')
        return self._create_result_iterator(results)

    # Training
    def create_dataset(self) -> dict:
        """
        Creates an empty dataset
        :return: Object containing the dataset id
        """
        response = self.post(DATASETS_ENDPOINT,
                             log_msg_before='Creating a new dataset',
                             log_msg_after='Successfully created a new dataset')
        return response.json()

    def delete_dataset(self, dataset_id) -> dict:
        """
        Deletes a dataset with a given ID
        :param dataset_id: The ID of the dataset to delete
        :return: Object containing the ID of the deleted dataset and the number of documents deleted
        """
        response = self.delete(DATASET_ENDPOINT(dataset_id=dataset_id),
                               log_msg_before=f'Deleting the dataset {dataset_id}',
                               log_msg_after=f'Successfully deleted the dataset {dataset_id}')
        return response.json()

    def delete_training_document(self, dataset_id, document_id) -> {}:
        """
        Deletes a training document from a dataset
        :param dataset_id: The ID of the dataset where the document is located
        :param document_id: The reference ID of the document
        :return: An empty object
        """
        response = self.delete(DATASET_DOCUMENT_ENDPOINT(dataset_id=dataset_id, document_id=document_id),
                               log_msg_before=f'Deleting the document {document_id} from the dataset {dataset_id}',
                               log_msg_after=f'Successfully deleted the document {document_id} from the '
                               f'dataset {dataset_id}')
        return response.json()

    def get_dataset_info(self, dataset_id) -> dict:
        """
        Gets statistical information about a dataset with a given ID
        :param dataset_id: The ID of the dataset
        :return: Summary information about the dataset that includes the number of documents in different processing
        stages
        """
        response = self.get(DATASET_ENDPOINT(dataset_id=dataset_id),
                            log_msg_before=f'Getting information about the dataset {dataset_id}',
                            log_msg_after=f'Successfully got the information about the dataset {dataset_id}')
        return response.json()

    def get_datasets_info(self) -> List[dict]:
        """
        Gets summary information about the existing datasets
        :return: An array of datasets corresponding to the 'datasets' part of the json response
        """
        response = self.get(DATASETS_ENDPOINT,
                            log_msg_before='Getting information about datasets',
                            log_msg_after='Successfully got the information about the datasets')
        return response.json()[API_DATASETS_FIELD]

    def get_dataset_documents_info(self, dataset_id, top: int = None, skip: int = None, count: bool = None) -> dict:
        """
        Gets the information about all the documents in a specific dataset
        :param dataset_id: The ID of an existing dataset
        :param top: Pagination: number of documents to be fetched in the current request
        :param skip: Pagination: number of documents to skip for the current request
        :param count: Flag to show count of number of documents in the dataset
        :return: Object that contains an array of the documents
        """
        params = {}
        if top is not None:
            params[API_PAGINATION_TOP_PARAM] = top
        if skip is not None:
            params[API_PAGINATION_SKIP_PARAM] = skip
        if count is not None:
            params[API_PAGINATION_COUNT_PARAM] = count
        response = self.get(DATASET_DOCUMENTS_ENDPOINT(dataset_id=dataset_id), params=params,
                            log_msg_before=f'Getting information about the documents in the dataset {dataset_id}',
                            log_msg_after=f'Successfully got the information about the documents in the '
                            f'dataset {dataset_id}')
        return response.json()

    def get_classification_documents_info(self, model_name, model_version) -> List[dict]:
        """
        Gets the information about recently classified documents
        :param model_name: The name of the model against which the documents were classified
        :param model_version: The version of the model against which the documents were classified
        :return: An array of document information correspond to the 'results' part of the json response. Each document
        information includes its reference ID and the classification status.
        """
        response = self.get(DOCUMENTS_ENDPOINT(modelName=model_name, modelVersion=model_version),
                            log_msg_before=f'Getting information about documents that were recently classified against '
                            f'the model {model_name} with version {model_version}',
                            log_msg_after=f'Successfully got the information about the documents that were recently '
                            f'classified against the model {model_name} with version {model_version}')
        return response.json()[API_RESULTS_FIELD]

    def upload_document_to_dataset(self, dataset_id, document_path: str, ground_truth: Union[str, dict],
                                   document_id=None, mime_type=None, stratification_set=None) -> dict:
        """
        Uploads a single document and its ground truth to a specific dataset
        :param dataset_id: The ID of the dataset
        :param document_path: The path to the PDF document
        :param ground_truth: Path to the ground truth JSON file or an object representing the ground truth
        :param document_id: The reference ID of the document
        :param mime_type: The file type of the document
        :param stratification_set: Defines a custom stratification set (training/validation/test)
        :return: Object containing information about the uploaded document
        """
        ground_truth_json = get_ground_truth_json(ground_truth)

        data = {API_GROUND_TRUTH_FIELD: ground_truth_json}
        if document_id is not None:
            data[API_DOCUMENT_ID_FIELD] = document_id
        if mime_type is not None:
            data[API_MIME_TYPE_FIELD] = mime_type
        if stratification_set is not None:
            data[API_STRATIFICATION_SET_FIELD] = stratification_set
        with open(document_path, 'rb') as file:
            response = self.post(DATASET_DOCUMENTS_ENDPOINT(dataset_id=dataset_id),
                                 files={API_DOCUMENT_FIELD: file},
                                 data={API_PARAMETERS_FIELD: json.dumps(data)},
                                 log_msg_before=f'Uploading the document {document_path} with ground truth '
                                 f'{str(ground_truth_json)} to the dataset {dataset_id}',
                                 log_msg_after=f'Successfully uploaded the document {document_path} with ground truth '
                                 f'{str(ground_truth_json)} to the dataset {dataset_id}, waiting for the document '
                                 f'processing')
        return self._poll_for_url(DATASET_DOCUMENT_ENDPOINT(dataset_id=dataset_id,
                                                            document_id=response.json()[API_DOCUMENT_ID_FIELD]),
                                  wait_status=409).json()

    def _upload_document_to_dataset_wrap_errors(self, dataset_id, document_path, ground_truth, document_id=None):
        result = function_wrap_errors(self.upload_document_to_dataset, dataset_id, document_path, ground_truth,
                                      document_id)
        if isinstance(result, Exception):
            result.document_path = document_path
        else:
            result['document_path'] = document_path
        return result

    def upload_documents_directory_to_dataset(self, dataset_id, path, file_extension='.pdf'):
        """
        :param dataset_id: The ID of the dataset to upload the documents to
        :param path: The path has to contain document data files and JSON file with GT with corresponding names
        :param file_extension: The file format of the documents to be uploaded. Default is '.pdf'
        :return: An iterator with the upload results
        """
        files = self._find_files(path, file_extension)
        files_id = [os.path.splitext(os.path.basename(f))[0] for f in files]
        assert len(files_id) > 0, 'No training data found'
        ground_truth_files = [os.path.join(path, f + '.json') for f in files_id]
        assert len(files_id) == len(ground_truth_files), 'The folder has a different number of documents and ' \
                                                         'ground truths'
        return self.upload_documents_to_dataset(dataset_id=dataset_id,
                                                documents_paths=files,
                                                ground_truths_paths=ground_truth_files)

    def upload_documents_to_dataset(self, dataset_id, documents_paths: List[str],
                                    ground_truths_paths: List[Union[str, dict]]) -> Iterator[dict]:
        """

        :param dataset_id: The ID of the dataset to upload the documents to
        :param documents_paths: The paths of the PDF files
        :param ground_truths_paths: The paths of the JSON files containing the ground truths
        :return: An iterator with the upload results
        """
        number_of_documents = len(documents_paths)
        assert number_of_documents > 0, 'Please supply at least one document'
        self.logger.debug(f'Started uploading of {number_of_documents} documents to the dataset {dataset_id} in '
                          f'parallel using {self.polling_threads} threads')
        with ThreadPoolExecutor(min(self.polling_threads, number_of_documents)) as pool:
            results = pool.map(self._upload_document_to_dataset_wrap_errors, [dataset_id] * number_of_documents,
                               documents_paths, ground_truths_paths)
        self.logger.info(f'Finished uploading of {number_of_documents} documents to the dataset {dataset_id}')
        return self._create_result_iterator(results)

    # Model training and management
    def train_model(self, model_name, dataset_id) -> dict:
        """
        Trigger the process to train a new model version for documents classification, based on the documents in the
        specific dataset and wait until this process is finished. The process may take significant time to complete
        depending on the size of the dataset.
        :param model_name: The name of the new model to train
        :param dataset_id: The name of existing dataset containing enough documents for training
        :return: Object containing the statistical data about the trained model, including accuracy, recall and
        precision
        """
        response = self.post(MODEL_TRAINING_JOBS_ENDPOINT(modelName=model_name), json={API_DATASET_ID_FIELD: dataset_id},
                             validate=False,
                             log_msg_before=f'Triggering training of the model {model_name} from the dataset {dataset_id}')
        if response.status_code == 409:
            time.sleep(self.polling_long_sleep)
            return self.train_model(model_name, dataset_id)
        self.raise_for_status_with_logging(response)
        response_json = response.json()
        return self._poll_for_url(TRAINED_MODEL_ENDPOINT(model_name=response_json[API_MODEL_NAME_FIELD],
                                                         model_version=response_json[API_MODEL_VERSION_FIELD]),
                                  log_msg_before=f'Triggered training of the model {model_name} from the dataset '
                                  f'{dataset_id}, waiting for the training to complete',
                                  wait_status=409,
                                  sleep_interval=self.polling_long_sleep).json()

    def delete_trained_model(self, model_name, model_version) -> {}:
        """
        Deletes an existing trained model
        :param model_name: Name of the existing model to delete
        :param model_version: Version of the existing model to delete
        :return: An empty object
        """
        response = self.delete(TRAINED_MODEL_ENDPOINT(model_name=model_name, model_version=model_version),
                               log_msg_before=f'Triggering deletion of the model {model_name} with version {model_version}',
                               log_msg_after=f'Successfully deleted the model {model_name} with version {model_version}')
        return response.json()

    def get_trained_models_info(self) -> List[dict]:
        """
        Gets information about all trained models
        :return: An array of trained models corresponding to the 'models' part of the json response . Each model
        information contains training status and training accuracy data.
        """
        response = self.get(TRAINED_MODELS_ENDPOINT,
                            log_msg_before='Getting information about all trained models',
                            log_msg_after='Getting information about all trained models')
        return response.json()[API_MODELS_FIELD]

    def get_trained_model_info(self, model_name, model_version) -> dict:
        """
        Gets information about a specific trained model
        :param model_name: The name of the model
        :param model_version: The version  of the model
        :return: Object containing the training status and training accuracy data
        """
        response = self.get(TRAINED_MODEL_ENDPOINT(model_name=model_name, model_version=model_version),
                            log_msg_before=f'Getting information about the model {model_name} with version {model_version}',
                            log_msg_after=f'Successfully got the information about the model {model_name} with version {model_version}')
        return response.json()

    # Model deployment
    def deploy_model(self, model_name, model_version) -> dict:
        """
        Deploys a trained model to be available for inference
        :param model_name: The name of the trained model
        :param model_version: The version of the trained model
        :return: Object containing information about the deployed model serving
        """
        response = self.post(DEPLOYMENTS_ENDPOINT, validate=False,
                             json={
                                 API_MODEL_VERSION_FIELD: model_version,
                                 API_MODEL_NAME_FIELD: model_name
                             },
                             log_msg_before=f'Triggering the deployment of the model {model_name} with version {model_version}')
        if response.status_code == 409:
            # TODO: Change the API to differ between the 409 codes, see: DIGITALCONTENTPROCESSING-709
            if 'model is already deployed' in response.text:
                self.raise_for_status_with_logging(response)
            time.sleep(self.polling_long_sleep)
            return self.deploy_model(model_name, model_version)
        self.raise_for_status_with_logging(response)
        return self._poll_for_url(MODEL_DEPLOYMENT_ENDPOINT(deployment_id=response.json()[API_DEPLOYMENT_ID_FIELD]),
                                  log_msg_before=f'Successfully triggered the deployment of the model {model_name} '
                                  f'with version {model_version}, waiting for the deployment completion',
                                  wait_status=409,
                                  sleep_interval=self.polling_long_sleep).json()

    def get_deployed_models_info(self) -> List[dict]:
        """
        Gets information about all deployed model servings
        :return: An array of all deployed model servings corresponding to the 'deployments' part if the json response
        """
        response = self.get(DEPLOYMENTS_ENDPOINT,
                            log_msg_before='Getting information about all deployed models',
                            log_msg_after='Successfully got information about all deployed models')
        return response.json()[API_DEPLOYMENTS_FIELD]

    def get_deployed_model_info(self, model_name_or_deployment_id, model_version=None) -> dict:
        """
        Gets information about a specific deployed model serving. This method can be called either with the ID of the
        deployed model or with the model name and version
        :param model_name_or_deployment_id: ID of the deployed model or the model name, if the model name is provided,
        version has to be provided as well
        :param model_version: The version of the deployed model
        :return: Object containing the information about the deployed model serving
        """
        if model_version:
            deployed_models = self.get_deployed_models_info()
            models = [
                model for model in deployed_models
                if model[API_MODEL_NAME_FIELD] == model_name_or_deployment_id and model[API_MODEL_VERSION_FIELD] == model_version
            ]
            assert len(models) == 1, f"Model with name {model_name_or_deployment_id} and version {model_version} " \
                f"does not exist, or more than one deployment exists for given name and version"
            self.logger.info(f'Successfully got information about the deployment of the model '
                             f'{model_name_or_deployment_id} with version {model_version}')
            return models[0]
        else:
            response = self.get(MODEL_DEPLOYMENT_ENDPOINT(deployment_id=model_name_or_deployment_id),
                                log_msg_before=f'Getting the deployment of the model with ID {model_name_or_deployment_id}',
                                log_msg_after=f'Successfully got information about the deployment of the model with '
                                f'ID {model_name_or_deployment_id}')
            return response.json()

    def undeploy_model(self, model_name_or_deployment_id, model_version=None) -> {}:
        """
        Removes a deployment of the specific model serving. This method can be called either with the ID of the
        deployed model or with the model name and version
        :param model_name_or_deployment_id: ID of the deployed model or the model name, if the model name is provided,
        version has to be provided as well
        :param model_version: The version of the deployed model
        :return: An empty object
        """
        if model_version:
            model_name_or_deployment_id = self.get_deployed_model_info(model_name_or_deployment_id,
                                                                       model_version)[API_DEPLOYMENT_ID_FIELD]
        self.delete(MODEL_DEPLOYMENT_ENDPOINT(deployment_id=model_name_or_deployment_id),
                    log_msg_before=f'Triggering the removal of the model deployment with ID {model_name_or_deployment_id}',
                    log_msg_after=f'Successfully triggered the removal of the model deployment with ID '
                    f'{model_name_or_deployment_id}, waiting for the deployment completion')
        return self._poll_for_url(MODEL_DEPLOYMENT_ENDPOINT(deployment_id=model_name_or_deployment_id), False, 404,
                                  200).json()

    @staticmethod
    def _find_files(directory, file_extension):
        return [os.path.join(directory, name) for name in os.listdir(directory)
                if name.lower().endswith(file_extension)]
