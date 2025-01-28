#!/bin/bash

APPLICATION=$1
ENVIRONMENT=$2
REPLICAS=$3
CPU_LIMIT=$4
MEMORY_LIMIT=$5
ENV_VARS=$6
HPA_ENABLED=$7
HPA_MAX_REPLICAS=$8

# Create overlay directory
mkdir -p feeder-manifests/$APPLICATION/overlays/$ENVIRONMENT

# Generate deployment patch
cat <<EOF > feeder-manifests/$APPLICATION/overlays/$ENVIRONMENT/patch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deployment
spec:
  replicas: $REPLICAS
  template:
    spec:
      containers:
      - name: application-container
        resources:
          limits:
            cpu: "$CPU_LIMIT"
            memory: "$MEMORY_LIMIT"
        env:
EOF

# Append environment variables
echo "$ENV_VARS" | jq -r '.[] | "        - name: \(.name)\n          value: \(.value)"' >> feeder-manifests/$APPLICATION/overlays/$ENVIRONMENT/patch.yaml

# Append HPA configuration if enabled
if [[ "$HPA_ENABLED" == "true" ]]; then
  cat <<HPAYAML >> feeder-manifests/$APPLICATION/overlays/$ENVIRONMENT/patch.yaml
---
apiVersion: autoscaling/v2beta1
kind: HorizontalPodAutoscaler
metadata:
  name: hpa
spec:
  maxReplicas: $HPA_MAX_REPLICAS
HPAYAML
fi
