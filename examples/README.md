In order to use the example `train_and_evaluate_custom_model.ipynb` example two prerequisites are:

1. You have access to a service key for the SAP AI Busniess Services Document Classification service
2. You need either a Jupyterhub instance (below are the instructions for setup either locally on your laptop in in SAP converged cloud instance)

### Service key

You will need to have access to SAP Cloud Plattform given via the [SAP Cloud Platform Enterprise Agreement](https://wiki.scn.sap.com/wiki/pages/viewpage.action?pageId=489198716)

In order to get a service key please have a look at this [SAP Help Portal article](https://help.sap.com/viewer/65de2977205c403bbc107264b8eccf4b/Cloud/en-US/4514a14ab6424d9f84f1b8650df609ce.html)

### Example how to set up local Jupyterlab instance

#### Install anaconda

```
wget https://repo.anaconda.com/archive/Anaconda3-2019.10-Linux-x86_64.sh
bash Anaconda3-2019.10-Linux-x86_64.sh
rm Anaconda3-2019.10-Linux-x86_64.sh
```

Note: This guide was performed with default installation path querried after the `bash` command. Anaconda is used as the Python package manager as recommended by the Jupyterhub team. You will be asked whether `conda init` should be run. Answer with yes or run it afterwards yourself. Once you log off and back in again you should see `base` in front of your shell prompt indicating sucessfull installation.

Check for updated version before download [here](https://www.anaconda.com/distribution/)

#### Install jupyterlab via conda

```
conda update -n base -c defaults conda
conda create --name jupyterlab
conda activate jupyterlab
conda install -c conda-forge jupyterlab
```
Then we can start jupyter lab

```
jupyter lab
```

Instructions should be displayed in the terminal on how to access the server.
