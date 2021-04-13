#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2020 2019-2020 SAP SE
#
# SPDX-License-Identifier: Apache-2.0

wget https://repo.anaconda.com/archive/Anaconda3-2019.10-Linux-x86_64.sh
bash Anaconda3-2019.10-Linux-x86_64.sh
rm Anaconda3-2019.10-Linux-x86_64.sh

conda update -n base -c defaults conda
conda create --name jupyterlab
conda activate jupyterlab
conda install -c conda-forge jupyterlab

jupyter lab