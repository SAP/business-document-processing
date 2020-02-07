#!/usr/bin/env bash
pip install --user pylint twine pydoc-markdown
pylint sap-document-classification-client/
pydocmd simple sap-document-classification-client+ sap-document-classification-client.dc_api_client++ > API.md
python setup.py sdist
twine upload dist/*