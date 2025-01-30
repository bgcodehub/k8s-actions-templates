# CI/CD Pipeline with Dynamic Kustomize

## Overview

This pipeline automates the **containerization, deployment, and management** of Kubernetes manifests while allowing developers to apply **runtime modifications dynamically**.

It integrates with:

- **JFrog Artifactory** for **building, testing, and pushing Docker images**.
- **Kustomize** for **managing Kubernetes manifests dynamically**.
- **GitHub Actions Secrets** for **secure authentication**.
- **Atlas Repository** for **storing updated Kubernetes manifests**.

### **🔹 Testing the Pipeline**
- If you want to **test only the Kustomize manifest generation** without deploying a real application, **run the pipeline from the `feature/kustomize` branch** and use any placeholder like `github.com` for the Atlas repository reference.
- If you want to **test both the Docker image build and push to Artifactory along with the Kustomize part**, **use the `feature/docker` branch**, which includes a sample `go-api` application for testing.

---

## **🚀 Features**

✅ **Build and Push Docker Images to Artifactory** *(Now Functional!)*\
✅ **Dynamic Modifications for Kubernetes Manifests**\
✅ **Push Manifests to Atlas Repository** *(Now Functional!)*\
✅ **Validates Kubernetes Manifests Before Deployment**\
🛠 **ArgoCD Auto-Sync for Deployments (Future Step)**\
🛠 **Slack Notifications for Post-Deployment (Future Step)**

---

## **🛠 Workflow Dispatch Inputs**

| Input Name         | Description                                                       | Required | Default |
| ------------------ | ----------------------------------------------------------------- | -------- | ------- |
| `application`      | Select application type (e.g., go-api, backend).                  | ✅        | N/A     |
| `modifications`    | Enter runtime modifications as JSON (for go-api & java-api only). | ❌        | `{}`    |
| `atlas_repository` | The Atlas repository where manifests should be pushed.            | ✅        | N/A     |

---

## **🛠 Job Breakdown (Pipeline Flow Order)**

### **1️⃣ Build and Push Docker Image (JFrog Artifactory)**

#### ✅ **Status: Fully Working**

This job **builds a Docker image**, runs **tests**, and **pushes it to JFrog Artifactory**.

#### **🔹 Steps**

1️⃣ **Checkout Code** – Fetches the latest code from the repository.\
2️⃣ **Setup Docker Buildx** – Enables multi-platform builds for optimized Docker images.\
3️⃣ **Build Docker Image** – Uses the latest commit SHA to tag the image.\
4️⃣ **Login to Artifactory** – Uses **GitHub Actions Secrets** (`ARTIFACTORY_USER`, `ARTIFACTORY_PASSWORD`, `ARTIFACTORY_URL`).\
5️⃣ **Tag and Push Image to Artifactory** – Stores the Docker image in Artifactory.

#### **🔹 Required Secrets**

| Secret Name            | Description                                                  |
| ---------------------- | ------------------------------------------------------------ |
| `ARTIFACTORY_URL`      | Your JFrog Artifactory URL (e.g., `your-instance.jfrog.io`). |
| `ARTIFACTORY_USER`     | Your Artifactory username.                                   |
| `ARTIFACTORY_PASSWORD` | Your Artifactory API Key or Password.                        |

#### **🔹 How to Find These Values in JFrog Artifactory**

1️⃣ **Login to Artifactory** → Go to **User Profile** → Find **API Key**.\
2️⃣ Use **"docker login" credentials** (same as the ones used for `docker login`).

---

### **2️⃣ Manage Kubernetes Manifests (Kustomize)**

#### ✅ **Status: Fully Working**

This job applies **runtime modifications**, validates Kubernetes manifests, and pushes updated configurations to the **Atlas repository**.

#### **🔹 Steps**

1️⃣ **Checkout Kustomize Repository** – Fetches the base Kubernetes configurations.\
2️⃣ **Install Dependencies** – Installs `kustomize`, `jq`, `yq`, and `kubeconform`.\
3️⃣ **Validate Application Customization** – Ensures **only `go-api`** and **`java-api`** can have modifications.\
4️⃣ **Apply Runtime Modifications** – Dynamically modifies `deploy.yaml` & `hpa.yaml` using `yq`.\
5️⃣ **Apply Kustomize Overlays** – Generates the final Kubernetes manifests.\
6️⃣ **Validate Kubernetes Manifests** – Ensures manifests conform to Kubernetes standards.\
7️⃣ **Push Updated Manifests to Atlas Repository** *(Now Working! 🎉)*

#### **🔹 Example Runtime Modifications JSON**

For `go-api`:

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

For `java-api`:

```json
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
