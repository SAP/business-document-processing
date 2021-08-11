<!--
SPDX-FileCopyrightText: 2020 2019-2020 SAP SE

SPDX-License-Identifier: Apache-2.0
-->

# Python Client Library for the SAP AI Business Services: Document Classification and Document Information Extraction

[![REUSE status](https://api.reuse.software/badge/github.com/SAP/business-document-processing)](https://api.reuse.software/info/github.com/SAP/business-document-processing)

This repository contains the [source code](sap_business_document_processing) of a Python client library to facilitate the use of the SAP AI Business Services: [Document Classification](https://help.sap.com/dc) and [Document Information Extraction](https://help.sap.com/dox). The client library provides two API Client classes that contain convenient methods to access these services and issue calls to the [Document Classification REST API](https://help.sap.com/viewer/ca60cd2ed44f4261a3ae500234c46f37/SHIP/en-US/c1045a561faf4ba0ae2b0e7713f5e6c4.html) and [Document Information Extraction REST API](https://help.sap.com/viewer/5fa7265b9ff64d73bac7cec61ee55ae6/SHIP/en-US/ded7d34e60f1422ba2e04e892a7f0e25.html) respectively. To use the library you need to [have access to SAP Business Technology Platform](https://www.sap.com/products/cloud-platform/get-started.html).

Check out the [**usage examples**](./examples), they are very useful to get started with the services.

Have a look at [**API documentation**](./API.md) in order to use the library.

### Notes for users of the sap-document-classification-client library
This library includes all the capabilities of the sap-document-classification-client, which will not be developed further. However, the code is still available [here](https://github.com/SAP/business-document-processing/tree/master).
If you want to switch to this library, you have to be aware of the following changes:

* The DCApiClient can now be imported directly from the top module via: ```from sap_business_document_processing import DCApiClient```
* The functions ```classifiy_documents```, ```upload_documents_to_dataset```, ```upload_documents_directory_to_dataset``` now return an iterator instead of a list. You can either analyze individual results using with ```result = next(iterator)``` within a try-catch block (e.g. to handle each failed document) or use ```results = list(iterator)``` to turn it to a list. The latter will raise an error if at least one document failed.
* The function ```get_datasets_info``` now returns a list which is the "dataset" part of the API response json. (You just need to delete the \["dataset"\] from the response to work with it as until now)
* The function ```get_classification_documents_info``` now returns a list which is the "results" part of the API response json.
* The function ```get_training_models_info``` now returns a list which is the "models" part of the API response json.
* The function ```get_deployed_models_info``` now returns a list which is the "deployments" part of the API response json.
* The library now raises the following custom exceptions:
    - **BDPApiException**: Base exception for all exceptions of this library. Raise when no other exception is applicable.
    - **BDPClientException**: Raised when an HTTP response with status code between 400 and 500 is returned. Usually means incorrect user input. (Replaces some HTTPErrors)
    - **BDPServerException**: Raised when an HTTP response with status code between 500 and 600 is returned. Usually means that the server had some internal error. (Replaces some HTTPErrors)
    - **BDPUnauthorizedException**: Raised when an HTTP response with status code 401 is returned. Usually means that a wrong OAuth credentials were provided.
    - **BDPFailedAsynchronousOperationException**: Raised when an asynchronous job failed during processing. (Replaces FailedCallException)
    - **BDPPollingTimeoutException**: Raised when an asynchronous job exceeds the set polling_max_attempts. (Replaces PollingTimeoutException)
* The function ```_poll_for_url``` now doesn`t expect an 'url' and 'payload' parameters, but 'path' and 'json' parameters instead.


## Requirements

This library requires properly setup [Python](https://www.python.org/downloads/) 3.6 (or higher version) environment.

## Download and Installation

This Python library should be consumed in the standard way by running

```pip install sap-business-document-processing```

or adding the library as a dependency of your code in `requirements.txt` file.

## Demo usage

Prerequisites:
* [Get a Free Account on SAP BTP Trial](https://developers.sap.com/tutorials/hcp-create-trial-account.html)
* [Create Service Instance for Document Classification with Trial Account](https://developers.sap.com/tutorials/cp-aibus-dc-service-instance.html)
* [Create Service Instance for Document Information Extraction](https://developers.sap.com/tutorials/cp-aibus-dox-service-instance.html)

#### Document Classification

To try out the Document classification service using the document classification client
library you can also run the two demo links below:
* Try out classification using default model [demo](https://mybinder.org/v2/gh/SAP/business-document-processing/main?filepath=examples%2Fdocument_classification_examples%2Fclassification_default_model.ipynb)
* Try out training and classification using custom model [demo](https://mybinder.org/v2/gh/SAP/business-document-processing/main?filepath=examples%2Fdocument_classification_examples%2Ftrain_and_evaluate_custom_model.ipynb) (requires an enterprise account, trial account is **not** sufficient)

#### Document Information Extraction

Try out the Document Information Extraction service with this [showcase](https://mybinder.org/v2/gh/SAP/business-document-processing/main?filepath=examples%2Fdocument_information_extraction_examples%2Finformation_extraction_showcase.ipynb)

- [Exercises](doc_inf_ext_exercises/)
    - [Exercise 1 - Set up Document Information Extraction Service and UI](doc_inf_ext_exercises#exercise-1---set-up-document-information-extraction-service-and-ui)
    - [Exercise 2 - Upload a document for extraction using UI application](doc_inf_ext_exercises#exercise-2---upload-documents-for-extraction-using-ui-application)
    - [Exercise 3 - Visualize, correct extraction results and confirm document using UI application](doc_inf_ext_exercises#exercise-3---visualize-correct-extraction-results-and-confirm-document-using-ui-application)
    - [Exercise 4 - Get Auth token to use Document Information Extraction Rest API](doc_inf_ext_exercises#exercise-4---get-auth-token-to-use-document-information-extraction-rest-api)
    - [Exercise 5 - Get extraction results of document using Rest API](doc_inf_ext_exercises#exercise-5---get-extraction-results-of-document-using-rest-api)
    - [Exercise 6 - Upload supplier Data for matching](doc_inf_ext_exercises#exercise-6---upload-supplier-data-for-matching)
    - [Exercise 7 - Upload document through Rest API to enrich the extraction Results with supplier data](doc_inf_ext_exercises#exercise-7---upload-document-through-rest-api-to-enrich-the-extraction-results-with-supplier-data)

## Known Issues

Please see the [issues section](https://github.com/SAP/business-document-processing/issues).

## How to obtain support

In case you would like to contribute to this project, ask any questions or get support, please open an issue containing the description of your question or planned contribution in GitHub and we will get in touch.

## Licensing

Please see our [LICENSE](https://github.com/SAP/business-document-processing/blob/main/LICENSE) for copyright and license information. Detailed information including third-party components and their licensing/copyright information is available via the [REUSE tool](https://api.reuse.software/info/github.com/SAP/business-document-processing).
