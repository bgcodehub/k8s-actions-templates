# **CI/CD Pipeline with Dynamic Kustomize**

## **📌 Overview**

This pipeline automates the **containerization, deployment, and management** of Kubernetes manifests while allowing developers to apply **runtime modifications dynamically**.

### **🔹 Integrations**

- **JFrog Artifactory** → For **building, testing, and pushing Docker images**.
- **Kustomize** → For **managing Kubernetes manifests dynamically**.
- **GitHub Actions Secrets** → For **secure authentication**.
- **Atlas Repository** → For **storing updated Kubernetes manifests**.
- **AWS ConfigMap** → Dynamically injects **AWS region and environment** into Kubernetes deployments.
- **Dockerfile Automation** → Automatically generates **enterprise-grade Dockerfiles** tailored to your application.

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

✅ **Automated Dockerfile Generation** *(New! 🎉)* 

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
| `dockerfile` | Enable automatic Dockerfile generation (`true`) or use a custom one (`false`). | ✅ | N/A |
| `application` | Select application type (e.g., go-api, backend). | ✅ | N/A |
| `aws_region` | Select the AWS region to use in the ConfigMap. | ✅ | N/A |
| `env_name` | Select the environment name (dev, test, prod) for the ConfigMap. | ✅ | N/A |
| `modifications` | Enter runtime modifications as JSON (for go-api & java-api only). | ❌ | `{}` |
| `atlas_repository` | The Atlas repository where manifests should be pushed. | ✅ | N/A |

---

## **🛠 New Feature: Automated Dockerfile Generation**

### **What It Does**
The **`Create Dockerfile`** option (`dockerfile: true`) automates the creation of production-ready Dockerfiles tailored to your application’s language and structure. This feature eliminates the need for app development teams to write their own Dockerfiles, ensuring consistency, security, and compatibility with your Kubernetes cluster.

- **How It Works**: When `dockerfile` is set to `true`, the pipeline fetches a Python script from a GitHub Gist, detects your application’s language (e.g., Go, Java, Python, Node.js), and generates a Dockerfile optimized for production use.
- **Source**: The script is hosted at:  
  [https://gist.githubusercontent.com/bgcodehub/9057942959e961954cc71eb22e084d7d/raw/d4fb707c46d2be690818f177bdf324a15996809d/generate_dockerfile.py](https://gist.githubusercontent.com/bgcodehub/9057942959e961954cc71eb22e084d7d/raw/d4fb707c46d2be690818f177bdf324a15996809d/generate_dockerfile.py)

### **Key Benefits**
- **Ease of Use**: Teams only need standard project files (e.g., `go.mod`, `package.json`)—no Dockerfile expertise required.
- **Robustness**: Supports multiple languages (Go, Java, Python, Node.js, Ruby, PHP, Rust) with framework-specific optimizations (e.g., Gunicorn for Python, Maven/Gradle for Java).
- **Production-Ready**: Generates Dockerfiles with:
  - Multi-stage builds for smaller images.
  - Non-root user execution for security.
  - Health checks for K8s liveness/readiness probes.
  - Dynamic port and entrypoint detection.
- **Fallback**: Uses the `application` input (e.g., `go-api`) if file-based detection fails.

### **Example Generated Dockerfile (Go Application)**
```dockerfile
FROM golang:1.20-alpine AS build
WORKDIR /app
COPY . .
RUN go mod download && go build -o main
FROM alpine:latest
WORKDIR /app
RUN apk add --no-cache curl
COPY --from=build /app/main .
RUN adduser -D appuser && chown appuser:appuser /app
USER appuser
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:8080/health || exit 1
CMD "./main"
```

### **Customization**
- **Language Detection**: Automatically detects based on files or falls back to `application` input.
- **Overrides**: Use environment variables in the workflow to customize:
  - `PORT`: Change the exposed port (default: 8080 for Go/Java).
  - `ENTRYPOINT`: Specify the main file (e.g., `cmd/server/main.go`).
  - `CMD`: Override the default command (e.g., `["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]`).
  - `<LANG>_VERSION`: Set a specific runtime version (e.g., `GO_VERSION=1.21`).

### **When to Use**
- Set `dockerfile: true` for teams who want an automated Dockerfile.
- Set `dockerfile: false` if you provide a custom Dockerfile in the repo root.

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

### **1️⃣ Extract Application Metadata**
- Extracts the app name and namespace from the `atlas_repository` input for use in subsequent jobs.

### **2️⃣ Build and Test Application (JFrog Artifactory)**

✅ **Status: Fully Working**

This job **generates a Dockerfile (if enabled)**, builds a Docker image, and pushes it to JFrog Artifactory.

#### **Steps**
1. **Checkout Code** – Fetches the latest code from the repository.
2. **Setup Python** – Prepares the environment for Dockerfile generation (if `dockerfile: true`).
3. **Fetch Dockerfile Generator** – Downloads the script from the Gist.
4. **Generate Dockerfile** – Creates a tailored Dockerfile based on the app type and files.
5. **Setup Docker Buildx** – Enables multi-platform builds.
6. **Build Docker Image** – Builds the image with the commit SHA as the tag.
7. **Login to Artifactory** – Authenticates using secrets.
8. **Tag and Push Image** – Stores the image in Artifactory.

#### **Required Secrets**
| Secret Name            | Description                              |
|-----------------------|------------------------------------------|
| `ARTIFACTORY_URL`     | Artifactory URL (e.g., `your-instance.jfrog.io`) |
| `ARTIFACTORY_USER`    | Artifactory username                     |
| `ARTIFACTORY_PASSWORD`| Artifactory API key or password          |

### **3️⃣ Manage Kubernetes Manifests (Kustomize)**

✅ **Status: Fully Working**

This job applies **runtime modifications**, generates an **AWS ConfigMap**, validates Kubernetes manifests, and pushes them to the Atlas repository.

#### **New Addition: AWS ConfigMap Generation**
Dynamically injects `AWS_REGION` and `ENV_NAME` into the deployment.

#### **Example AWS ConfigMap Output**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-config
data:
  AWS_REGION: "us-east-1"
  ENV_NAME: "dev"
```

#### **Steps**
1. **Checkout Kustomize Repository** – Fetches base Kubernetes configs.
2. **Install Dependencies** – Sets up `kustomize`, `jq`, `yq`, and `kubeconform`.
3. **Validate Application Customization** – Restricts modifications to `go-api` and `java-api`.
4. **Apply Runtime Modifications** – Updates `deploy.yaml` and `hpa.yaml` dynamically.
   - Example JSON for `go-api`:
     ```json
     {
       "cpu_limit": "2300m",
       "memory_limit": "1Gi",
       "timeout_seconds": 5
     }
     ```
5. **Generate AWS ConfigMap** – Creates a ConfigMap with region and env.
6. **Update Kustomization** – Adds the ConfigMap to manifests.
7. **Update Deployment** – Links ConfigMap to the deployment.
8. **Update Image** – Sets the Artifactory image URL.
9. **Apply Kustomize Overlays** – Generates final manifests.
10. **Validate Manifests** – Ensures Kubernetes compliance.
11. **Push to Atlas Repository** – Commits and pushes manifests.

#### **Required Secrets**
| Secret Name         | Description                              |
|--------------------|------------------------------------------|
| `ATLAS_GITHUB_PAT` | GitHub PAT for Atlas repository access   |

---

## **🚀 Future Enhancements**

- **ArgoCD Integration** – Automate deployment syncing.
- **Automated Testing** – Add pre-deployment validation.
- **Slack Notifications** – Notify teams on deployment success.

---

This pipeline provides a **scalable, flexible, and automated** solution for containerization and Kubernetes manifest management, reducing manual effort and ensuring production-ready deployments. With the new Dockerfile generation feature, app teams can focus on coding while the pipeline handles the heavy lifting. 🚀

---