# **CI/CD Pipeline with Dynamic Kustomize**

## **📌 Overview**

This pipeline automates the **containerization, deployment, and management** of Kubernetes manifests while allowing developers to apply **runtime modifications dynamically**.

### **🔹 Integrations**

- **JFrog Artifactory** → For **building, testing, and pushing Docker images**.
- **Kustomize** → For **managing Kubernetes manifests dynamically**.
- **GitHub Actions Secrets** → For **secure authentication**.
- **Atlas Repository** → For **storing updated Kubernetes manifests**.
- **AWS ConfigMap** → Dynamically injects **AWS region and environment** into Kubernetes deployments.

---

## **🔹 Testing the Pipeline**

- To **test only the Kustomize manifest generation**, run the pipeline from the **`feature/kustomize`** branch and use any placeholder (e.g., `github.com`) for the Atlas repository reference.
- To **test both Docker image build and push to Artifactory**, use the **`feature/docker`** branch, which includes a sample **`go-api`** application for testing.

---

## **📌 Integration Instructions**

### **Option 1: Manually Copy the Workflow**

1. **Create the necessary directory structure** in your repository:
    
    ```
    mkdir -p .github/workflows
    
    ```
    
2. **Create the workflow file**:
    
    ```
    touch .github/workflows/k8s-kustomize-argocd.yaml
    
    ```
    
3. **Copy and paste the pipeline YAML** into this file.
4. **Commit and push** the changes to your repository.

### **Option 2: Clone and Integrate via Git Submodules (Recommended)**

For better maintainability and updates, you can **clone this pipeline** into your repository as a Git submodule:

```
git submodule add <GIT_REPO_URL_OF_PIPELINE> .github/workflows/k8s-kustomize
git submodule update --init --recursive

```

This allows you to **pull updates** from the main pipeline repository without manually copying files.

---

## **🔑 Required GitHub Actions Secrets**

Once the workflow is in place, add the required **GitHub Actions Secrets**:

| Secret Name | Description |
| --- | --- |
| `ARTIFACTORY_URL` | Your JFrog Artifactory instance URL. |
| `ARTIFACTORY_USER` | Your JFrog Artifactory username. |
| `ARTIFACTORY_PASSWORD` | Your JFrog API key or password. |
| `ATLAS_GITHUB_PAT` | GitHub PAT for pushing Kubernetes manifests to Atlas. |

---

## **🚀 Features**

✅ **Build and Push Docker Images to Artifactory** *(Fully Functional!)*

✅ **Dynamic Modifications for Kubernetes Manifests**

✅ **Push Manifests to Atlas Repository** *(Fully Functional!)*

✅ **Validates Kubernetes Manifests Before Deployment**

✅ **Dynamically Generates AWS ConfigMap for Region & Environment** *(New Fix! 🎉)*

🛠 **ArgoCD Auto-Sync for Deployments (Future Enhancement)**

🛠 **Slack Notifications for Post-Deployment (Future Enhancement)**

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

## **🛠 Supported Runtime Modifications**
### `go-api`
| Key                     | Description                                    |
|-------------------------|------------------------------------------------|
| `cpu_limit`             | CPU limit for the container (e.g., "2300m").  |
| `memory_limit`          | Memory limit for the container (e.g., "1Gi"). |
| `cpu_request`           | CPU request for the container.                 |
| `memory_request`        | Memory request for the container.              |
| `timeout_seconds`       | Liveness probe timeout.                        |
| `initial_delay_seconds` | Liveness probe initial delay.                  |
| `revision_history_limit` | Number of revision histories to keep.         |

### `java-api`
| Key                              | Description                                      |
|----------------------------------|--------------------------------------------------|
| `termination_grace_period_seconds` | Termination grace period for container shutdown. |
| `max_replicas`                   | Maximum replicas for Horizontal Pod Autoscaler. |


## **🛠 Job Breakdown (Pipeline Flow Order)**

### **1️⃣ Build and Push Docker Image (JFrog Artifactory)**

✅ **Status: Fully Working**

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

---

### **2️⃣ Manage Kubernetes Manifests (Kustomize)**

✅ **Status: Fully Working**

This job applies **runtime modifications**, dynamically generates an **AWS ConfigMap**, validates Kubernetes manifests, and pushes updated configurations to the **Atlas repository**.

### **🔹 New Addition: AWS ConfigMap Generation**

The pipeline now **dynamically generates an AWS ConfigMap** to **inject AWS region and environment name into the deployment**.

### **Example AWS ConfigMap Output**

```yaml
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

- Example modifications JSON for `go-api`:
  ```json
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
- Example modifications JSON for `java-api`:
  ```json
  {
    "termination_grace_period_seconds": 60,
    "max_replicas": 15
  }
  ```

5️⃣ **Generate AWS ConfigMap** – Dynamically creates a Kubernetes ConfigMap containing `AWS_REGION` and `ENV_NAME`.

6️⃣ **Update Kustomization to Include ConfigMap** – Ensures the generated ConfigMap is included in Kubernetes manifests.

7️⃣ **Apply Kustomize Overlays** – Generates the final Kubernetes manifests.

8️⃣ **Validate Kubernetes Manifests** – Ensures manifests conform to Kubernetes standards.

9️⃣ **Push Updated Manifests to Atlas Repository** *(Now Working! 🎉)*

---

### **3️⃣ Push Manifests to Atlas Repository**

✅ **Status: Fully Working**

This step **pushes the final Kubernetes manifests to the user-specified Atlas repository**.

### **🔹 Steps**

1️⃣ **Authenticate with GitHub Token (`ATLAS_GITHUB_PAT`)**

2️⃣ **Clone the Atlas Repository**

3️⃣ **Copy Updated Kubernetes Manifests**

4️⃣ **Commit and Push Changes**

---

## **🚀 Future Enhancements**

- **Enable ArgoCD Integration** – Sync deployments automatically.
- **Automated Testing** – Add pre-deployment validation.
- **Slack Notifications** – Notify on successful deployments.

This pipeline provides a **scalable and flexible** approach to Kubernetes manifest management, reducing manual configuration errors and streamlining deployments. 🚀

---
