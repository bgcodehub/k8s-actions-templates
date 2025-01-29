# CI/CD Pipeline with Dynamic Kustomize

## Overview
This pipeline is designed to automate the deployment of Kubernetes manifests while allowing developers to apply runtime modifications dynamically. It integrates with [Kustomize](https://github.com/kubernetes-sigs/kustomize) to generate overlays and deploy configurations, enabling a flexible and robust continuous deployment system.

## Features
- **Select Application Type**: Supports multiple application types (go-api, java-api, python-api, frontend, backend).
- **Dynamic Modifications**: Allows runtime modifications for `go-api` and `java-api` without manually editing YAML files.
- **Containerized Deployment** (future step): Supports Docker image building, testing, and pushing.
- **Customizable Deployment**: Uses Kustomize to build and validate Kubernetes manifests.
- **Manifest Validation**: Ensures generated Kubernetes manifests are syntactically correct.
- **Integration with Atlas Repository** (future step): Pushes the modified configurations to a specified Atlas repository for deployment.
- **ArgoCD Integration** (future step): Syncs deployments automatically with ArgoCD.

## Workflow Dispatch Inputs
| Input Name         | Description                                        | Required | Default |
|--------------------|----------------------------------------------------|----------|---------|
| `application`      | Select application type (e.g., go-api, backend).   | ✅        | N/A     |
| `modifications`    | Enter runtime modifications as JSON (for go-api & java-api only). | ❌ | `{}` |
| `atlas_repository` | The Atlas repository where manifests should be pushed. | ✅ | N/A |

## Supported Runtime Modifications
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

## Jobs and Steps

### 1. **Build and Test Application** (future step)
This job builds and tests the application using Docker.

#### **Step 1: Checkout Code**
- Pulls the latest version of the repository.

#### **Step 2: Setup Docker**
- Installs and configures Docker Buildx for building containerized applications.

#### **Step 3: Build Docker Image**
- Builds a Docker image for the application using the latest commit SHA.

#### **Step 4: Run Tests**
- Runs containerized tests to validate the application functionality.

#### **Step 5: Push Image to Artifactory**
- Logs in to the Docker registry and pushes the built image.

### 2. **Manage Kubernetes Manifests**
This job handles everything related to managing Kubernetes manifests, applying runtime modifications, and validating the generated configurations.

#### **Step 1: Checkout Kustomize Repository**
- This step pulls the [Kustomize overlays repository](https://github.com/bgcodehub/kustomize-application) which contains the base Kubernetes configurations.

#### **Step 2: Install Dependencies**
- Installs required tools like Kustomize, `jq` (for JSON processing), `yq` (for YAML editing), and `kubeconform` (for manifest validation).

#### **Step 3: Validate Application Customization**
- Ensures that runtime modifications are only applied to `go-api` and `java-api`. If modifications are provided for unsupported applications, the pipeline exits with an error.

#### **Step 4: Apply Runtime Modifications**
- **Modifications are applied dynamically using `yq`** to update key values in `deploy.yaml` and `hpa.yaml`.
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

#### **Step 5: Apply Kustomize Overlays and Output New Configuration**
- Runs `kustomize build` to generate the final Kubernetes manifests after applying modifications.
- Outputs the generated configuration for verification.

#### **Step 6: Validate Kubernetes Manifests**
- Uses `kubeconform` to check if the generated manifests are valid and conform to Kubernetes standards.
- Errors occur if any field has incorrect types or syntax.

#### **Step 7: Push Manifests to Atlas Repository (Future Step - Currently Commented Out)**
- This step clones the developer’s specified Atlas repository and commits the updated Kubernetes manifests for deployment.

#### **Step 8: Trigger ArgoCD Deployment (Future Step - Currently Commented Out)**
- If enabled, this step would trigger ArgoCD to sync with the updated manifests in the Atlas repository.

#### **Step 9: Post-Deployment Verification (Future Step - Currently Commented Out)**
- Sends a Slack notification upon successful deployment.

---

## How to Trigger the Pipeline
1. Navigate to the **GitHub Actions** tab in your repository.
2. Select the **CI/CD Pipeline with Dynamic Kustomize** workflow.
3. Click **Run Workflow** and provide the following inputs:
   - **Application**: Choose from `go-api`, `java-api`, `python-api`, `frontend`, or `backend`.
   - **Modifications (Optional)**: Enter runtime modifications in JSON format.
   - **Atlas Repository**: Provide the URL of the repository where the manifests should be pushed.

## Future Enhancements
- **Enable ArgoCD Integration**: Once tested, the ArgoCD sync step will be uncommented.
- **Automated Testing**: The build-and-test job will be uncommented once testing is re-enabled.
- **Better Error Handling**: Improved handling of invalid JSON modifications.

This pipeline provides a **scalable and flexible** approach to Kubernetes manifest management, reducing manual configuration errors and streamlining deployments. 🚀
