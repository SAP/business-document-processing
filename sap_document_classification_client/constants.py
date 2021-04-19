# SPDX-FileCopyrightText: 2020 2019-2020 SAP SE
#
# SPDX-License-Identifier: Apache-2.0

from functools import partial

DATASETS_ENDPOINT = 'datasets'
DATASET_ENDPOINT = partial('datasets/{dataset_id}'.format)
DATASET_DOCUMENTS_ENDPOINT = partial('datasets/{dataset_id}/documents'.format)
DATASET_DOCUMENT_ENDPOINT = partial('datasets/{dataset_id}/documents/{document_id}'.format)
DOCUMENTS_ENDPOINT = partial('classification/models/{modelName}/versions/{modelVersion}/documents'.format)
DOCUMENT_RESULT_ENDPOINT = partial('classification/models/{modelName}/versions/{modelVersion}/documents/{id}'.format)
MODEL_TRAINING_JOBS_ENDPOINT = partial('models/{modelName}/versions'.format)
MODEL_TRAINING_JOB_ENDPOINT = partial('models/{modelName}/versions/{modelVersion}'.format)
DEPLOYMENTS_ENDPOINT = 'deployments'
TRAINED_MODEL_ENDPOINT = partial('models/{model_name}/versions/{model_version}'.format)
TRAINED_MODELS_ENDPOINT = 'models'
MODEL_DEPLOYMENT_ENDPOINT = partial('deployments/{deployment_id}'.format)
MONITORING_HEALTH_CHECK_ENDPOINT = 'healthz'

API_PAGINATION_TOP_PARAM = 'top'
API_PAGINATION_SKIP_PARAM = 'skip'
API_PAGINATION_COUNT_PARAM = 'count'

API_MIME_TYPE_FIELD = 'mimeType'
API_DOCUMENT_EXTRACTED_TEXT_FIELD = 'extractedText'
API_DOCUMENT_ID_FIELD = 'documentId'
API_STATUS_FIELD = 'status'

# NOTE: Equivalent uppercase/mixed case will be picked up as well
FILE_EXTENSIONS_FOR_FOLDER_UPLOAD = ('.pdf', '.png', '.jpeg', '.jpg', '.tif', '.tiff')

MAX_POLLING_THREADS = 100
MIN_POLLING_INTERVAL = 0.2
