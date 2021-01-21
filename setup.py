from distutils.core import setup
setup(
  name='sap-document-classification-client',
  packages=['sap_document_classification_client'],
    version='0.1.18',
  license='apache-2.0',
  description='Python client library for convenient usage of SAP Document Classification service REST API',
  author='Alexander Bolshakov',
  author_email='alexander.bolshakov@sap.com',
  url='https://github.com/sap/document-classification-client',
  download_url='https://github.com/sap/document-classification-client/archive/v_01.tar.gz',
  keywords=['business', 'document', 'classification', 'machine learning', 'SAP'],
  install_requires=[
          'requests==2.23.0'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3'
  ],
)
