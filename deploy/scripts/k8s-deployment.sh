#!/bin/bash

# Exit immediately if a command fails
set -e

# Path to your Kubernetes manifests folder
K8S_DIR="${1:-./k8s}"

echo "🚀 Restarting Minikube cluster..."
minikube delete
minikube start

echo "🔍 Validating Kubernetes files in $K8S_DIR..."
kubectl apply -f "$K8S_DIR" --dry-run=client

# Step 1: Deploy namespaces first
if [ -f "$K8S_DIR/namespaces.yaml" ] || [ -f "$K8S_DIR/namespace.yaml" ]; then
    echo "📁 Applying namespaces..."
    kubectl apply -f "$K8S_DIR/namespaces.yaml" 2>/dev/null || kubectl apply -f "$K8S_DIR/namespace.yaml"
else
    echo "⚠️  No dedicated namespace.yaml file found. Applying all files directly."
fi

# Step 2: Deploy all remaining Kubernetes files
echo "📦 Deploying all remaining Kubernetes resources..."
kubectl apply -f "$K8S_DIR" --recursive

echo "⏳ Waiting for pods to initialize..."
sleep 5

echo "📊 Current Cluster Status:"
kubectl get pods --all-namespaces