In order to use the example [`train_and_evaluate_custom_model.ipynb`](train_and_evaluate_custom_model.ipynb) two prerequisites are required:

1. You have access to a service key for the SAP AI Busniess Services Document Classification service
2. You need a Jupyterlab instance (below are the instructions for setup locally on your laptop)

### Service key

You will need to have access to SAP Cloud Plattform given via the [SAP Cloud Platform Enterprise Agreement](https://wiki.scn.sap.com/wiki/pages/viewpage.action?pageId=489198716)

In order to get a service key please have a look at this general [SAP Help Portal article](https://help.sap.com/viewer/65de2977205c403bbc107264b8eccf4b/Cloud/en-US/4514a14ab6424d9f84f1b8650df609ce.html)

For our service specific documentation, please have a look at relevant entry in the [SAP Help Portal](https://help.sap.com/viewer/ca60cd2ed44f4261a3ae500234c46f37/SHIP/en-US/88bdee94c7c94bc99de8484f5c2db04a.html).

### Example how to set up local Jupyterlab instance

An example script to set up anaconda and start jupyterlab on your local machine is provided [here](./install_jupyterlab.sh).
This might need modifications based on OS version (example used is based on Ubuntu 16.04).
Please consult the [anaconda installation guide](https://docs.anaconda.com/anaconda/install/) for details regarding your OS.
