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

PDF_MIME_TYPE = 'pdf'

MAX_POLLING_THREADS = 15
MIN_POLLING_INTERVAL = 0.2
