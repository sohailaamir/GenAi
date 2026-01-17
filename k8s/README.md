
# Kubernetes quickstart

```bash
# 1) Build the container image locally
docker build -t genai-router:latest ..

# 2) Create the secret with your Hugging Face token
kubectl create secret generic hf-secret --from-literal=HF_TOKEN=hf_xxx

# 3) Create the ConfigMap (model repo id)
kubectl apply -f configmap.yaml

# 4) Deploy the app and service
kubectl apply -f deployment.yaml

# 5) If using minikube, expose it
minikube service genai-router-svc
