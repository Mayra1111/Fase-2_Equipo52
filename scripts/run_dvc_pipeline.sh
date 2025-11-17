#!/bin/bash
# Helper script to run DVC pipelines from alternative YAML files
# Usage: run_dvc_pipeline.sh <pipeline_file> [dvc_args...]
# Example: run_dvc_pipeline.sh dvc_basic.yaml

set -e

PIPELINE_FILE="${1}"
shift  # Remove first argument, keep remaining as dvc_args

if [ -z "$PIPELINE_FILE" ]; then
    echo "ERROR: Pipeline file not specified"
    echo "Usage: $0 <pipeline_file> [dvc_args...]"
    echo "Example: $0 dvc_basic.yaml"
    exit 1
fi

if [ ! -f "$PIPELINE_FILE" ]; then
    echo "ERROR: Pipeline file not found: $PIPELINE_FILE"
    exit 1
fi

# Backup existing dvc.yaml if it exists
if [ -f "dvc.yaml" ]; then
    cp dvc.yaml dvc.yaml.bak
    echo "Backed up existing dvc.yaml to dvc.yaml.bak"
fi

# Copy the pipeline file to dvc.yaml
cp "$PIPELINE_FILE" dvc.yaml
echo "Running pipeline from: $PIPELINE_FILE"

# Run DVC repro with any additional arguments
dvc repro "$@"
EXIT_CODE=$?

# Restore original dvc.yaml if it was backed up
if [ -f "dvc.yaml.bak" ]; then
    mv dvc.yaml.bak dvc.yaml
    echo "Restored original dvc.yaml"
fi

exit $EXIT_CODE
