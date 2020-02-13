#!/usr/bin/env bash
rm -rf dist
pip install --user pylint twine pydoc-markdown
pylint sap_document_classification_client/
pydocmd simple sap_document_classification_client+ sap_document_classification_client.dc_api_client++ > API.md
python setup.py sdist
twine upload dist/*