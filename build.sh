#!/usr/bin/env bash
# Render build script for Sentient Playground

set -o errexit

# Install Python dependencies
cd agent-service
pip install --upgrade pip
pip install -r requirements.txt
