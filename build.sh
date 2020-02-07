#!/usr/bin/env bash
pip install --user pylint
pylint sap-document-classification-client/

pip install --user pydoc-markdown
pydocmd simple sap-document-classification-client+ sap-document-classification-client.dc_api_client++ > API.md