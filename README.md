# CI/CD Pipeline with Dynamic Kustomize

## Overview

This pipeline automates the **containerization, deployment, and management** of Kubernetes manifests while allowing developers to apply **runtime modifications dynamically**.

It integrates with:

- **JFrog Artifactory** for **building, testing, and pushing Docker images**.
- **Kustomize** for **managing Kubernetes manifests dynamically**.
- **GitHub Actions Secrets** for **secure authentication**.
- **Atlas Repository** for **storing updated Kubernetes manifests**.
- **AWS Region and Environment Configuration via Kubernetes ConfigMap.**.


### **🔹 Testing the Pipeline**
- If you want to **test only the Kustomize manifest generation** without deploying a real application, **run the pipeline from the `feature/kustomize` branch** and use any placeholder like `github.com` for the Atlas repository reference.
- If you want to **test both the Docker image build and push to Artifactory along with the Kustomize part**, **use the `feature/docker` branch**, which includes a sample `go-api` application for testing.

---

## **📌 Integration Instructions**
To use this pipeline in your project, follow these steps:

### **Option 1: Manually Copy the Workflow**
1. **Create the necessary directory structure** in your repository:
   ```sh
   mkdir -p .github/workflows
   ```
2. **Create the workflow file**:
   ```sh
   touch .github/workflows/k8s-kustomize-argocd.yaml
   ```
3. **Copy and paste the contents** of the pipeline YAML into this file.
4. **Commit and push** the changes to your repository.

### **Option 2: Clone and Integrate via Git Submodules (Recommended)**
For better maintainability and updates, you can **clone this pipeline** into your repository as a Git submodule:

1. **Run the following command in your repository:**
   ```sh
   git submodule add <GIT_REPO_URL_OF_PIPELINE> .github/workflows/k8s-kustomize
   ```
2. **Ensure the submodule updates correctly:**
   ```sh
   git submodule update --init --recursive
   ```
3. This approach allows you to **pull updates** from the main pipeline repository without manually copying files.

### **Final Setup: Add Secrets**
Once the workflow is in place, add the required **GitHub Actions Secrets**:

| Secret Name            | Description                                                   |
|------------------------|---------------------------------------------------------------|
| `ARTIFACTORY_URL`      | Your JFrog Artifactory instance URL.                          |
| `ARTIFACTORY_USER`     | Your JFrog Artifactory username.                              |
| `ARTIFACTORY_PASSWORD` | Your JFrog API key or password.                              |
| `ATLAS_GITHUB_PAT`     | GitHub PAT for pushing Kubernetes manifests to Atlas.        |

After setting up the workflow file and secrets, trigger the pipeline from GitHub Actions.

---

## **🚀 Features**

✅ **Build and Push Docker Images to Artifactory** *(Now Functional!)*\
✅ **Dynamic Modifications for Kubernetes Manifests**\
✅ **Push Manifests to Atlas Repository** *(Now Functional!)*\
✅ **Validates Kubernetes Manifests Before Deployment**\
✅ **Dynamically Generates AWS ConfigMap to Inject Region & Environment** *(New Fix! 🎉)*\
🛠 **ArgoCD Auto-Sync for Deployments (Future Step)**\
🛠 **Slack Notifications for Post-Deployment (Future Step)**

---

## **🛠 Workflow Dispatch Inputs**

| Input Name | Description | Required | Default |
| --- | --- | --- | --- |
| `application` | Select application type (e.g., go-api, backend). | ✅ | N/A |
| `aws_region` | Select the AWS region to use in the ConfigMap. | ✅ | N/A |
| `env_name` | Select the environment name (dev, test, prod) for the ConfigMap. | ✅ | N/A |
| `modifications` | Enter runtime modifications as JSON (for go-api & java-api only). | ❌ | `{}` |
| `atlas_repository` | The Atlas repository where manifests should be pushed. | ✅ | N/A |

---

## **🛠 Job Breakdown (Pipeline Flow Order)**

### **1️⃣ Build and Push Docker Image (JFrog Artifactory)**

### ✅ **Status: Fully Working**

This job **builds a Docker image**, runs **tests**, and **pushes it to JFrog Artifactory**.

### **🔹 Steps**

1️⃣ **Checkout Code** – Fetches the latest code from the repository.

2️⃣ **Setup Docker Buildx** – Enables multi-platform builds for optimized Docker images.

3️⃣ **Build Docker Image** – Uses the latest commit SHA to tag the image.

4️⃣ **Login to Artifactory** – Uses **GitHub Actions Secrets** (`ARTIFACTORY_USER`, `ARTIFACTORY_PASSWORD`, `ARTIFACTORY_URL`).

5️⃣ **Tag and Push Image to Artifactory** – Stores the Docker image in Artifactory.

### **🔹 Required Secrets**

| Secret Name | Description |
| --- | --- |
| `ARTIFACTORY_URL` | Your JFrog Artifactory URL (e.g., `your-instance.jfrog.io`). |
| `ARTIFACTORY_USER` | Your Artifactory username. |
| `ARTIFACTORY_PASSWORD` | Your Artifactory API Key or Password. |

### **🔹 How to Find These Values in JFrog Artifactory**

1️⃣ **Login to Artifactory** → Go to **User Profile** → Find **API Key**.

2️⃣ Use **"docker login" credentials** (same as the ones used for `docker login`).

---

### **2️⃣ Manage Kubernetes Manifests (Kustomize)**

### ✅ **Status: Fully Working**

This job applies **runtime modifications**, dynamically generates an **AWS ConfigMap**, validates Kubernetes manifests, and pushes updated configurations to the **Atlas repository**.

---

### **🔹 New Addition: AWS ConfigMap Generation**

The pipeline now **dynamically generates an AWS ConfigMap** to **inject AWS region and environment name into the deployment**.

This ensures that **each deployment automatically inherits the correct AWS region and environment type**, removing the need for manual configuration changes.

### **🔹 Example AWS ConfigMap Output**

```yaml
yaml
CopyEdit
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-config
  namespace: default
data:
  AWS_REGION: "us-east-1"
  ENV_NAME: "dev"

```

### **🔹 Steps**

1️⃣ **Checkout Kustomize Repository** – Fetches the base Kubernetes configurations.

2️⃣ **Install Dependencies** – Installs `kustomize`, `jq`, `yq`, and `kubeconform`.

3️⃣ **Validate Application Customization** – Ensures **only `go-api`** and **`java-api`** can have modifications.

4️⃣ **Apply Runtime Modifications** – Dynamically modifies `deploy.yaml` & `hpa.yaml` using `yq`.

5️⃣ **Generate AWS ConfigMap** – Dynamically creates a Kubernetes ConfigMap containing `AWS_REGION` and `ENV_NAME`.

6️⃣ **Update Kustomization to Include ConfigMap** – Ensures the generated ConfigMap is included in Kubernetes manifests.

7️⃣ **Apply Kustomize Overlays** – Generates the final Kubernetes manifests.

8️⃣ **Validate Kubernetes Manifests** – Ensures manifests conform to Kubernetes standards.

9️⃣ **Push Updated Manifests to Atlas Repository** *(Now Working! 🎉)*

---

### **🔹 Deployment Changes**

The **Deployment YAML** is now dynamically updated to reference the AWS ConfigMap:

```yaml
yaml
CopyEdit
- name: AWS_REGION
  valueFrom:
    configMapKeyRef:
      key: AWS_REGION
      name: aws-config
- name: ENV_NAME
  valueFrom:
    configMapKeyRef:
      key: ENV_NAME
      name: aws-config

```

✅ **This ensures that AWS_REGION and ENV_NAME are always correctly set in the deployment.**

---

### **🔹 Example Runtime Modifications JSON**

For `go-api`:

```json
json
CopyEdit
{
  "cpu_limit": "2300m",
  "memory_limit": "1Gi",
  "cpu_request": "1300m",
  "memory_request": "612Mi",
  "timeout_seconds": 5,
  "initial_delay_seconds": 15,
  "revision_history_limit": 3
}

```

For `java-api`:

```json
json
CopyEdit
{
  "termination_grace_period_seconds": 60,
  "max_replicas": 15
}

```

---

### **3️⃣ Push Manifests to Atlas Repository**

#### ✅ **Status: Fully Working**

This step **pushes the final Kubernetes manifests to the user-specified Atlas repository**.

#### **🔹 Steps**

1️⃣ **Authenticate with GitHub Token (`ATLAS_GITHUB_PAT`)**\
2️⃣ **Clone the Atlas Repository**\
3️⃣ **Copy Updated Kubernetes Manifests**\
4️⃣ **Commit and Push Changes**

#### **🔹 Required Secrets**

| Secret Name        | Description                                                          |
| ------------------ | -------------------------------------------------------------------- |
| `ATLAS_GITHUB_PAT` | Personal Access Token (PAT) for pushing changes to Atlas repository. |

#### **🔹 How to Generate `ATLAS_GITHUB_PAT`**

1️⃣ **Go to GitHub** → Navigate to **Settings** → **Developer Settings** → **Personal Access Tokens**.\
2️⃣ Click **"Generate new token (classic)"**.\
3️⃣ **Select Scopes**:

- ✅ `repo` (Full control of private repositories)
- ✅ `workflow` (Update GitHub Action workflows)
- ✅ `write:packages` (Upload packages to GitHub Package Registry)
  4️⃣ **Generate & Copy Token** → Add to **GitHub Actions Secrets** as `ATLAS_GITHUB_PAT`.

---

## **🚀 Future Enhancements**

- **Enable ArgoCD Integration** – Sync deployments automatically.
- **Automated Testing** – Add pre-deployment validation.
- **Slack Notifications** – Notify on successful deployments.

This pipeline provides a **scalable and flexible** approach to Kubernetes manifest management, reducing manual configuration errors and streamlining deployments. 🚀