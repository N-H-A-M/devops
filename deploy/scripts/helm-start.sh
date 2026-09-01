#!/usr/bin/env bash
set -e

# Define release and chart configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CHART_PATH="$PROJECT_ROOT/deploy/helm/credit-compare" 
RELEASE_NAME="credit-compare"
NAMESPACE="application"
export SOPS_AGE_KEY_FILE="$HOME/.age/key.txt"
export HELM_SECRETS_DECRYPT_SECRET_IN_MEM=true

if [ ! -f "$SOPS_AGE_KEY_FILE" ]; then
    echo "Error: Private key file not found at $SOPS_AGE_KEY_FILE"
    exit 1
fi

if [ ! -f "$CHART_PATH/secrets.enc.yaml" ]; then
    echo "Error: Encrypted secrets file not found at $CHART_PATH/secrets.enc.yaml"
    exit 1
fi

echo "=== Deploying $RELEASE_NAME via Helm + SOPS ==="

helm secrets  upgrade --install "$RELEASE_NAME" "$CHART_PATH" \
  --namespace "$NAMESPACE" \
  --create-namespace \
  --wait \
  --timeout 5m\
  -f "$CHART_PATH/values.yaml"\
  -f "$CHART_PATH/secrets.enc.yaml"

echo "=== Deployment Complete ==="

# 2. Check release status and running pods
helm list -n "$NAMESPACE"
minikube kubectl --  get pods -n "$NAMESPACE"
minikube kubectl -- port-forward svc/frontend-service 8080:3000 -n application