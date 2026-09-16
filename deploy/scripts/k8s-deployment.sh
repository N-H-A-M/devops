#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
K8S_DIR="$PROJECT_ROOT/deploy/k8s"
ENV_FILE="$K8S_DIR/base/.env.secret"

echo "Restarting Minikube cluster..."
minikube delete
minikube start

echo "Applying namespaces and image pull secret..."
minikube kubectl -- apply -f "$K8S_DIR/base"

minikube kubectl -- create secret docker-registry ghcr-secrets \
  --docker-server=ghcr.io \
  --docker-username=$(grep GHCR_USERNAME "$ENV_FILE" | cut -d '=' -f2) \
  --docker-password=$(grep GHCR_PAT "$ENV_FILE"  | cut -d '=' -f2) \
  --namespace=application \
  --dry-run=client -o yaml | minikube kubectl -- apply -f -

minikube kubectl -- create secret generic backend-db-secret \
  --from-literal=DATABASE_URL=$(grep DATABASE_URL "$ENV_FILE" | cut -d '=' -f2-) \
  --namespace=application \
  --dry-run=client -o yaml | minikube kubectl -- apply -f -


minikube kubectl -- create secret generic postgres-secret \
  --from-literal=POSTGRES_DB=$(grep DB_NAME "$PROJECT_ROOT/.env" | cut -d '=' -f2) \
  --from-literal=POSTGRES_USER=$(grep DB_USER "$PROJECT_ROOT/.env" | cut -d '=' -f2) \
  --from-literal=POSTGRES_PASSWORD=$(grep DB_PASSWORD "$PROJECT_ROOT/.env" | cut -d '=' -f2) \
  --namespace=database \
  --dry-run=client -o yaml | minikube kubectl -- apply -f -

echo "Deploying database layer..."
minikube kubectl -- apply -f "$K8S_DIR/database"

echo "Deploying application layer..."
minikube kubectl -- apply -f "$K8S_DIR/application"

echo "Waiting for pods to initialize..."
sleep 5

echo "Current Cluster Status:"
minikube kubectl -- get pods --all-namespaces