#!/usr/bin/env bash
set -o errexit

# Upgrade pip, setuptools, and wheel before installing anything
pip install --upgrade pip setuptools wheel

# Install the project dependencies
pip install -r requirements.txt
