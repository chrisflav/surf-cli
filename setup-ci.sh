#!/bin/bash
# Run this script to set up GitHub Actions CI
# Requires git access with the `workflows` permission
set -e
mkdir -p .github/workflows
cp .github-template/workflows/ci.yml .github/workflows/ci.yml
echo "CI workflow installed at .github/workflows/ci.yml"
echo "Please commit and push this file to enable CI."
