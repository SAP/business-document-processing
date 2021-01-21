# SPDX-FileCopyrightText: 2020 2019-2020 SAP SE
#
# SPDX-License-Identifier: Apache-2.0

from concurrent.futures import ThreadPoolExecutor
import fnmatch
import json
import logging
import os
import re
import time

from .constants import API_DOCUMENT_EXTRACTED_TEXT_FIELD, API_DOCUMENT_ID_FIELD, API_MIME_TYPE_FIELD, \
    API_PAGINATION_COUNT_PARAM, API_PAGINATION_SKIP_PARAM, API_PAGINATION_TOP_PARAM, API_STATUS_FIELD, \
    DATASETS_ENDPOINT, DATASET_DOCUMENTS_ENDPOINT, DATASET_DOCUMENT_ENDPOINT, DATASET_ENDPOINT, DEPLOYMENTS_ENDPOINT, \
    DOCUMENTS_ENDPOINT, DOCUMENT_RESULT_ENDPOINT, MODEL_DEPLOYMENT_ENDPOINT, MODEL_TRAINING_JOBS_ENDPOINT, \
    TRAINED_MODELS_ENDPOINT, TRAINED_MODEL_ENDPOINT, MAX_POLLING_THREADS, MIN_POLLING_INTERVAL, \
    FILE_EXTENSIONS_FOR_FOLDER_UPLOAD
from .http_client_base import CommonClient, STATUS_SUCCEEDED, raise_for_status_with_logging


class DCApiClient(CommonClient):
    """
    This class provides an interface to access SAP Document Classification REST API from a Python application.
    Structure of values returned by all the methods is documented in Swagger. See Swagger UI by adding:
    /document-classification/v1 to your Document Classification service key URL value (from outside the uaa section).

    :param base_url: The service URL taken from the service key (key 'url' in service key JSON)
    :param client_id: The client ID taken from the service key (key 'uaa.clientid' in service key JSON)
    :param client_secret: The client secret taken from the service key (key 'uaa.clientsecret' in service key JSON)
    :param uaa_url: The XSUAA URL taken from the service key (key 'uaa.url' in service key JSON)
    :param polling_threads: Number of threads used to poll for asynchronous DC APIs, the maximal value is 15
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
                 polling_threads=5,
                 polling_sleep=5,
                 polling_long_sleep=30,
                 polling_max_attempts=120,
                 logging_level=logging.WARNING):
        """
        Creates a new instance of a client object to access the SAP Document Classification service
        """
        logger = logging.getLogger('DCApiClient')
        logger.setLevel(logging_level)
        if polling_threads > MAX_POLLING_THREADS:
            logger.warning('The number of parallel polling threads of {} is too high, the number was set to maximal '
                           'allowed amount of {}'.format(polling_threads, MAX_POLLING_THREADS))
            polling_threads = MAX_POLLING_THREADS
        if polling_sleep < MIN_POLLING_INTERVAL:
            logger.warning('The polling interval of {} is too small, the number was set to minimal '
                           'allowed amount of {}'.format(polling_sleep, MIN_POLLING_INTERVAL))
            polling_sleep = MIN_POLLING_INTERVAL
        if polling_long_sleep < MIN_POLLING_INTERVAL:
            logger.warning('The polling interval for long operations of {} is too small, the number was set to minimal '
                           'allowed amount of {}'.format(polling_long_sleep, MIN_POLLING_INTERVAL))
            polling_long_sleep = MIN_POLLING_INTERVAL
        CommonClient.__init__(self,
                              base_url=base_url,
                              client_id=client_id,
                              client_secret=client_secret,
                              uaa_url=uaa_url,
                              polling_threads=polling_threads,
                              polling_sleep=polling_sleep,
                              polling_long_sleep=polling_long_sleep,
                              polling_max_attempts=polling_max_attempts,
                              url_path_prefix='document-classification/v1/',
                              logging_level=logging_level)
        self.logger = logger

    # Inference
    def classify_document(self, document_path, model_name, model_version, reference_id=None, mimetype=None):
        """
        Submits request for document classification, checks the response and returns the reference ID for the
        uploaded document

        :param document_path: Path to the PDF file on the disk
        :param model_name: The name of the model that was successfully deployed to be used for the classification
        :param model_version: The version of the model that was successfully deployed to be used for the classification
        :param reference_id: In case the document reference ID has to be managed by the user, it can be specified.
        In this case the user is responsible for providing unique reference IDs for different documents
        :param mimetype: The file type of the document uploaded
        :return: Object containing the reference ID of the classified document and the classification results
        """

        options = {}
        if reference_id is not None:
            options[API_DOCUMENT_ID_FIELD] = reference_id
        if mimetype is not None:
            options[API_MIME_TYPE_FIELD] = mimetype
        data = {'parameters': json.dumps(options)}
        self.logger.debug('Submitting document {} for classification'.format(document_path))
        response = self.session.post(url=self.path_to_url(
            DOCUMENTS_ENDPOINT(modelName=model_name, modelVersion=model_version)),
            files={'document': open(document_path, 'rb')},
            data=data)
        self.logger.info(
            'Document {} submitted for classification successfully, waiting for result'.format(document_path))
        raise_for_status_with_logging(response)
        classification_job = response.json()
        return self._poll_for_url(
            self.path_to_url(
                DOCUMENT_RESULT_ENDPOINT(modelName=model_name,
                                         modelVersion=model_version,
                                         id=classification_job[API_DOCUMENT_ID_FIELD]))).json()

    def _classify_document_wrap_errors(self,
                                       document_path,
                                       model_name,
                                       model_version,
                                       reference_id=None,
                                       mimetype=None):
        result = self._function_wrap_errors(self.classify_document, document_path, model_name, model_version,
                                            reference_id, mimetype)
        result['document_path'] = document_path
        return result

    def classify_documents(self, documents_paths, model_name, model_version, silent=False):
        """
        Submits requests for classification of multiple documents, checks the response and returns the reference ID
        for the classified documents

        :param documents_paths: Paths to the PDF files on the disk
        :param model_name: The name of the model that was successfully deployed to be used for the classification
        :param model_version: The version of the model that was successfully deployed to be used for the classification
        :param silent: If set to True will not throw an exception if classification for one or more documents failed
        :return: Array of objects containing the reference ID of the classified document and the classification results
        """
        number_of_documents = len(documents_paths)
        self.logger.debug('Started classification of {} documents against the model {} with version {} in parallel '
                          'using {} threads'.format(number_of_documents, model_name, model_version,
                                                    self.polling_threads))
        assert number_of_documents > 0, 'Please supply at least one document'
        pool = ThreadPoolExecutor(self.polling_threads)
        results = pool.map(self._classify_document_wrap_errors, documents_paths, [model_name] * number_of_documents,
                           [model_version] * number_of_documents)
        pool.shutdown()
        self.logger.info('Finished classification of {} documents against the model {} with version {}'.format(
            number_of_documents, model_name, model_version))
        classification_results = list(results)
        if not silent:
            self._validate_results(results, 'Some documents could not be successfully classified')
        return classification_results

    # Training
    def create_dataset(self):
        """
        Creates an empty dataset
        :return: Object containing the dataset id
        """
        self.logger.debug('Creating a new dataset')
        response = self.session.post(self.path_to_url(DATASETS_ENDPOINT))
        raise_for_status_with_logging(response)
        self.logger.info('Successfully created a new dataset')
        return response.json()

    def delete_dataset(self, dataset_id):
        """
        Deletes a dataset with a given ID
        :param dataset_id: The ID of the dataset to delete
        :return: Object containing the ID of the deleted dataset and the number of documents deleted
        """
        self.logger.debug('Deleting the dataset {}'.format(dataset_id))
        response = self.session.delete(self.path_to_url(DATASET_ENDPOINT(dataset_id=dataset_id)))
        raise_for_status_with_logging(response)
        self.logger.info('Successfully deleted the dataset {}'.format(dataset_id))
        return response.json()

    def delete_training_document(self, dataset_id, document_id):
        """
        Deletes a training document from a dataset
        :param dataset_id: The ID of the dataset where the document is located
        :param document_id: The reference ID of the document
        :return: Empty object
        """
        self.logger.debug('Deleting the document {} from the dataset {}'.format(document_id, dataset_id))
        response = self.session.delete(
            self.path_to_url(DATASET_DOCUMENT_ENDPOINT(dataset_id=dataset_id, document_id=document_id)))
        raise_for_status_with_logging(response)
        self.logger.info('Successfully deleted the document {} from the dataset {}'.format(document_id, dataset_id))
        return response.json()

    def get_dataset_info(self, dataset_id):
        """
        Gets statistical information about a dataset with a given ID
        :param dataset_id: The ID of the dataset
        :return: Summary information about the dataset that includes the number of documents in different processing
        stages
        """
        self.logger.debug('Getting information about the dataset {}'.format(dataset_id))
        response = self.session.get(self.path_to_url(DATASET_ENDPOINT(dataset_id=dataset_id)))
        raise_for_status_with_logging(response)
        self.logger.info('Successfully got the information about the dataset {}'.format(dataset_id))
        return response.json()

    def get_datasets_info(self):
        """
        Gets summary information about the existing datasets
        :return: Object containing an array of datasets
        """
        self.logger.debug('Getting information about datasets')
        response = self.session.get(self.path_to_url(DATASETS_ENDPOINT))
        raise_for_status_with_logging(response)
        self.logger.info('Successfully got the information about the datasets')
        return response.json()

    def get_dataset_documents_info(self, dataset_id, top=None, skip=None, count=None):
        """
        Gets the information about all the documents in a specific dataset
        :param dataset_id: The ID of an existing dataset
        :param top: Pagination: number of documents to be fetched in the current request
        :param skip: Pagination: number of documents to skip for the current request
        :param count: Flag to show count of number of documents in the dataset
        :return: Object that contains array of the documents
        """
        params = {}
        if top is not None:
            params[API_PAGINATION_TOP_PARAM] = top
        if skip is not None:
            params[API_PAGINATION_SKIP_PARAM] = skip
        if count is not None:
            params[API_PAGINATION_COUNT_PARAM] = count
        self.logger.debug('Getting information about the documents in the dataset {}'.format(dataset_id))
        response = self.session.get(self.path_to_url(DATASET_DOCUMENTS_ENDPOINT(dataset_id=dataset_id)), params=params)
        raise_for_status_with_logging(response)
        self.logger.info('Successfully got the information about the documents in the dataset {}'.format(dataset_id))
        return response.json()

    def get_classification_documents_info(self, model_name, model_version):
        """
        Gets the information about recently classified documents
        :param model_name: The name of the model against which the documents were classified
        :param model_version: The version of the model against which the documents were classified
        :return: Object containing an array of documents, information about each document includes its reference ID
        and the classification status
        """
        self.logger.debug('Getting information about documents that were recently classified against the model {} '
                          'with version {}'.format(model_name, model_version))
        response = self.session.get(
            self.path_to_url(DOCUMENTS_ENDPOINT(modelName=model_name, modelVersion=model_version)))
        raise_for_status_with_logging(response)
        self.logger.debug('Successfully got the information about the documents that were recently classified against '
                          'the model {} with version {}'.format(model_name, model_version))
        return response.json()

    def upload_document_to_dataset(self, dataset_id, document_path, ground_truth, document_id=None, mime_type=None):
        """
        Uploads a single document and its ground truth to a specific dataset
        :param dataset_id: The ID of the dataset
        :param document_path: The path to the PDF document
        :param ground_truth: Path to the ground truth JSON file or an object representing the ground truth
        :param document_id: The reference ID of the document
        :param mime_type: The file type of the document
        :return: Object containing information about the uploaded document
        """
        if type(ground_truth) is str:
            ground_truth_json = json.load(open(ground_truth, 'r'))
        elif type(ground_truth) is dict:
            ground_truth_json = ground_truth
        else:
            raise Exception('Wrong argument type string (path to ground truth file) or a dictionary (ground truth is '
                            'JSON format) are expected for ground_truth argument')
        data = {'groundTruth': ground_truth_json, 'mimeType': mime_type}
        if document_id:
            data['documentId'] = document_id
        self.logger.debug('Uploading the document {} with ground truth {} to the dataset {}'.format(
            document_path, str(ground_truth_json), dataset_id))
        response = self.session.post(self.path_to_url(DATASET_DOCUMENTS_ENDPOINT(dataset_id=dataset_id)),
                                     files={'document': open(document_path, 'rb')},
                                     data={'parameters': json.dumps(data)})
        raise_for_status_with_logging(response)
        self.logger.debug('Successfully uploaded the document {} with ground truth {} to the dataset {}, waiting for '
                          'the document processing'.format(document_path, str(ground_truth_json), dataset_id))
        return self._poll_for_url(
            self.path_to_url(DATASET_DOCUMENT_ENDPOINT(dataset_id=dataset_id,
                                                       document_id=response.json()["documentId"]))).json()

    def _upload_document_to_dataset_wrap_errors(self, dataset_id, document_path, ground_truth, document_id=None):
        result = self._function_wrap_errors(self.upload_document_to_dataset, dataset_id, document_path, ground_truth,
                                            document_id)
        result['document_path'] = document_path
        return result

    def upload_documents_directory_to_dataset(self, dataset_id, path, silent=False):
        """
        :param dataset_id: The dataset_id of dataset to upload the documents to
        :param path: The path has to contain document data files and JSON file with GT with corresponding names
        :param silent: If set to True will not throw exception when upload of one of the documents fails,
        in this case the upload statuses in the results array have to be validated manually
        :return: Array with the upload results
        """
        files = self._find_files(path)
        files_id = [os.path.splitext(os.path.basename(f))[0] for f in files]
        assert len(files_id) > 0, 'No training data found'
        ground_truth_files = [os.path.join(path, f + '.json') for f in files_id]
        assert len(files_id) == len(ground_truth_files), 'The folder has a different number of documents and ' \
                                                             'ground truths'
        return self.upload_documents_to_dataset(dataset_id=dataset_id,
                                                documents_paths=files,
                                                ground_truths_paths=ground_truth_files,
                                                silent=silent)

    def upload_documents_to_dataset(self, dataset_id, documents_paths, ground_truths_paths, silent=False):
        """

        :param dataset_id: The dataset_id of dataset to upload the documents to
        :param documents_paths: The paths of the PDF files
        :param ground_truths_paths: The paths of the JSON files contining the ground truths
        :param silent: If set to True will not throw exception when upload of one of the documents fails,
        in this case the upload statuses in the results array have to be validated manually
        :return: Array with the upload results
        """
        number_of_documents = len(documents_paths)
        assert number_of_documents > 0, 'Please supply at least one document'
        self.logger.debug('Started uploading of {} documents to the dataset {} in parallel using {} threads'.format(
            number_of_documents, dataset_id, self.polling_threads))
        pool = ThreadPoolExecutor(min(self.polling_threads, len(documents_paths)))
        results = pool.map(self._upload_document_to_dataset_wrap_errors, [dataset_id] * number_of_documents,
                           documents_paths, ground_truths_paths)
        pool.shutdown()
        self.logger.info('Finished uploading of {} documents to the dataset {}'.format(number_of_documents, dataset_id))
        if not silent:
            self._validate_results(results, 'Some documents could not be successfully uploaded to the dataset')
        return results

    # Model training and management
    def train_model(self, model_name, dataset_id):
        """
        Trigger the process to train a new model version for documents classification, based on the documents in the
        specific dataset and wait until this process is finished. The process may take significant time to complete
        depending on the size of the dataset.
        :param model_name: The name of the new model to train
        :param dataset_id: The name of existing dataset containing enough documents for training
        :return: Object containing the statistical data about the trained model, including accuracy, recall and
        precision
        """
        self.logger.debug('Triggering training of the model {} from the dataset {}'.format(model_name, dataset_id))
        response = self.session.post(self.path_to_url(MODEL_TRAINING_JOBS_ENDPOINT(modelName=model_name)),
                                     json={"datasetId": dataset_id})
        if response.status_code == 409:
            time.sleep(self.polling_long_sleep)
            return self.train_model(model_name, dataset_id)
        raise_for_status_with_logging(response)
        self.logger.info('Triggered training of the model {} from the dataset {}, waiting for the training to '
                         'complete'.format(model_name, dataset_id))
        response_json = response.json()
        return self._poll_for_url(self.path_to_url(
            TRAINED_MODEL_ENDPOINT(model_name=response_json['modelName'], model_version=response_json['modelVersion'])),
            sleep_interval=self.polling_long_sleep).json()

    def delete_trained_model(self, model_name, model_version):
        """
        Deletes an existing trained model
        :param model_name: Name of the existing model to delete
        :param model_version: Version of the existing model to delete
        :return:
        """
        self.logger.debug('Triggering deletion of the model {} with version {}'.format(model_name, model_version))
        response = self.session.delete(
            self.path_to_url(TRAINED_MODEL_ENDPOINT(model_name=model_name, model_version=model_version)))
        raise_for_status_with_logging(response)
        self.logger.info('Successfully deleted the model {} with version {}'.format(model_name, model_version))
        return response.json()

    def get_trained_models_info(self):
        """
        Gets information about all trained models
        :return: Object containing the array of trained models, each model information contains training status and
        training accuracy data
        """
        self.logger.debug('Getting information about all trained models')
        response = self.session.get(self.path_to_url(TRAINED_MODELS_ENDPOINT))
        raise_for_status_with_logging(response)
        self.logger.info('Successfully got information about all trained models')
        return response.json()

    def get_trained_model_info(self, model_name, model_version):
        """
        Gets information about a specific trained model
        :param model_name: The name of the model
        :param model_version: The version  of the model
        :return: Object containing the training status and training accuracy data
        """
        self.logger.debug('Getting information about the model {} with version {}'.format(model_name, model_version))
        response = self.session.get(
            self.path_to_url(TRAINED_MODEL_ENDPOINT(model_name=model_name, model_version=model_version)))
        raise_for_status_with_logging(response)
        self.logger.info('Successfully got the information about the model {} with version {}'.format(
            model_name, model_version))
        return response.json()

    # Model deployment
    def deploy_model(self, model_name, model_version):
        """
        Deploys a trained model to be available for inference
        :param model_name: The name of the trained model
        :param model_version: The version of the trained model
        :return: Object containing information about the deployed model serving
        """
        self.logger.debug('Triggering the deployment of the model {} with version {}'.format(model_name, model_version))
        response = self.session.post(self.path_to_url(DEPLOYMENTS_ENDPOINT),
                                     json={
                                         "modelVersion": model_version,
                                         "modelName": model_name
                                     })
        if response.status_code == 409:
            # TODO: Change the API to differ between the 409 codes, see: DIGITALCONTENTPROCESSING-709
            if 'model is already deployed' in response.text:
                raise_for_status_with_logging(response)
            time.sleep(self.polling_long_sleep)
            return self.deploy_model(model_name, model_version)
        raise_for_status_with_logging(response)
        self.logger.info('Successfully triggered the deployment of the model {} with version {}, waiting for '
                         'the deployment completion'.format(model_name, model_version))
        return self._poll_for_url(self.path_to_url(
            MODEL_DEPLOYMENT_ENDPOINT(deployment_id=response.json()["deploymentId"])),
            sleep_interval=self.polling_long_sleep).json()

    def get_deployed_models_info(self):
        """
        Gets information about all deployed model servings
        :return: Object containing the array of all deployed model servings
        """
        self.logger.debug('Getting information about all deployed models')
        response = self.session.get(self.path_to_url(DEPLOYMENTS_ENDPOINT))
        raise_for_status_with_logging(response)
        self.logger.info('Successfully got information about all deployed models')
        return response.json()

    def get_deployed_model_info(self, model_name_or_deployment_id, model_version=None):
        """
        Gets information about a specific deployed model serving. This method can be called either with the ID of the
        deployed model or with the model name and version
        :param model_name_or_deployment_id: ID of the deployed model or the model name, if the model name is provided,
        version has to be provided as well
        :param model_version: The version of the deployed model
        :return: Object containing the information about the deployed model serving
        """
        if model_version:
            self.logger.debug('Getting the deployment of the model {} with version {}'.format(
                model_name_or_deployment_id, model_version))
            deployed_models = self.get_deployed_models_info()['deployments']
            models = [
                model for model in deployed_models
                if model['modelName'] == model_name_or_deployment_id and model['modelVersion'] == model_version
            ]
            assert len(models) == 1, "Model with name {} and version {} does not exist, or more than one deployment " \
                                     "exists for given name and version".format(model_name_or_deployment_id,
                                                                                model_version)
            self.logger.info('Successfully got information about the deployment of the model {} with version {}'.format(
                model_name_or_deployment_id, model_version))

            return models[0]
        else:
            self.logger.debug('Getting the deployment of the model with ID {}'.format(model_name_or_deployment_id))
            response = self.session.get(
                self.path_to_url(MODEL_DEPLOYMENT_ENDPOINT(deployment_id=model_name_or_deployment_id)))
            raise_for_status_with_logging(response)
            self.logger.info('Successfully got information about the deployment of the model with ID {}'.format(
                model_name_or_deployment_id))
            return response.json()

    def undeploy_model(self, model_name_or_deployment_id, model_version=None):
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
                                                                       model_version)['deploymentId']
        self.logger.debug(
            'Triggering the removal of the model deployment with ID {}'.format(model_name_or_deployment_id))
        response = self.session.delete(
            self.path_to_url(MODEL_DEPLOYMENT_ENDPOINT(deployment_id=model_name_or_deployment_id)))
        raise_for_status_with_logging(response)
        self.logger.info('Successfully triggered the removal of the model deployment with ID {}, waiting for '
                         'the deployment completion'.format(model_name_or_deployment_id))
        return self._poll_for_url(
            self.path_to_url(MODEL_DEPLOYMENT_ENDPOINT(deployment_id=model_name_or_deployment_id)), None, False, 404,
            200).json()

    @staticmethod
    def _validate_results(results, error_message):
        failed_results = []
        for result in results:
            if result[API_STATUS_FIELD] != STATUS_SUCCEEDED:
                if result.get(API_DOCUMENT_EXTRACTED_TEXT_FIELD):
                    result[API_DOCUMENT_EXTRACTED_TEXT_FIELD] = result[
                                                                    API_DOCUMENT_EXTRACTED_TEXT_FIELD][
                                                                :50] + ' ... truncated'
                failed_results.append(result)
        if len(failed_results) > 0:
            raise Exception(error_message + ': ' + str(failed_results))

    @staticmethod
    def _find_files(directory):
        return [os.path.join(directory, name) for name in os.listdir(directory)
                if name.lower().endswith(FILE_EXTENSIONS_FOR_FOLDER_UPLOAD)]


