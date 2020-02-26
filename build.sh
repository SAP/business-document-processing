#!/usr/bin/env bash
rm -rf dist
python -m pip install --user pylint twine pydoc-markdown
python -m pylint sap_document_classification_client/
python -m pydocmd simple sap_document_classification_client+ sap_document_classification_client.dc_api_client++ > API.md
sed -i 's/:param/- Argument/g' API.md
sed -i 's/:return/\n**Returns**/g' API.md
python setup.py sdist
python -m twine upload dist/*