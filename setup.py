from distutils.core import setup
setup(
  name='sap-business-document-processing',
  packages=['sap_business_document_processing'],
    version='0.1.0',
  license='apache-2.0',
  description='Python client library for convenient usage of SAP Business Document Processing services',
  author='Alexander Bolshakov',
  author_email='alexander.bolshakov@sap.com',
  url='https://github.com/sap/business_document_processing',
  download_url='https://pypi.org/project/sap-business-document-processing',
  keywords=['SAP', 'business', 'document', 'processing', 'classification', 'information', 'extraction', 'machine learning'],
  install_requires=[
          'requests==2.23.0',
          'requests_oauthlib==1.3.0'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3'
  ],
)
