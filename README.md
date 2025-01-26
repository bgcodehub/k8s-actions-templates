### **Pipeline Overview and Documentation**

This updated pipeline fully supports applications with and without patches (`go-api`, `java-api`, etc.) and streamlines Kubernetes deployments by automating validation, building, manifest management, and deployment. Below is a **detailed explanation and documentation** to help developers understand and use the pipeline effectively.

---

## **What Does the Pipeline Do?**

The pipeline consists of multiple stages to automate the CI/CD process for Kubernetes deployments. Here's how it works:

### **1. Triggering the Pipeline**
The pipeline is manually triggered using the **GitHub Actions `workflow_dispatch` event**, which requires developers to specify:
- `application` (e.g., `backend`, `frontend`, `go-api`, `java-api`).
- `environment` (e.g., `dev`, `staging`, `prod`).
- Optional parameters like:
  - `replicas`: Number of replicas for the application.
  - `cpu_limit`: CPU limit for the application container.
  - `memory_limit`: Memory limit for the application container.

### **2. Validate Commit Messages (`validate-commit`)**
This stage:
- Ensures commit messages follow a consistent format (e.g., `feat:`, `fix:`).
- Prevents merging of poorly documented commits into the main branch.
- **Why It Helps**: Improves collaboration and code traceability.

---

### **3. Build and Test Application (`build-and-test`)**
This stage:
1. **Builds a Docker image** of the application based on the provided code.
2. **Runs application tests** inside a Docker container to ensure stability.
3. **Pushes the Docker image** to an Artifactory registry for use in deployment.

**Why It Helps**:
- Eliminates manual Docker image builds and pushes.
- Ensures code quality through automated testing.

---

### **4. Manage Kubernetes Manifests (`manage-manifests`)**
This is the most critical stage for Kubernetes deployment:
1. **Fetches the feeder repository**:
   - The feeder repo contains the base Kubernetes manifests and the `kustomization.yaml` files.
2. **Handles ConfigMap Generation**:
   - For `go-api` and `java-api`, it dynamically generates a ConfigMap (`generated-config.yaml`) using the values provided in the pipeline (e.g., `cpu_limit`, `memory_limit`).
   - Applications without patches skip this step.
3. **Applies Kustomize Overlays**:
   - Combines the base manifests, patches, and ConfigMap to generate environment-specific Kubernetes manifests.
4. **Validates the Manifests**:
   - Uses `kubeval` to ensure the generated manifests are valid.
5. **Pushes the Manifests**:
   - Commits and pushes the generated manifests to the Atlas repository (watched by ArgoCD).

**Why It Helps**:
- Automates the generation of customized Kubernetes manifests.
- Prevents human errors in Kubernetes configurations.
- Saves developers from manually editing YAML files for each environment.

---

### **5. Trigger ArgoCD Deployment (`trigger-argocd`)**
This stage:
1. Notifies ArgoCD to sync the latest manifests from the Atlas repository.
2. Ensures the Kubernetes cluster is updated with the new deployment.

**Why It Helps**:
- Removes the need for developers to manually trigger ArgoCD syncs.
- Ensures deployments are consistent and reliable.

---

### **6. Post-Deployment Verification (`post-deployment`)**
This stage:
1. Pulls the deployed Docker image from Artifactory to ensure it matches expectations.
2. Runs smoke tests to verify that the application is running correctly in the cluster.
3. Sends a Slack notification to the team about the deployment status.

**Why It Helps**:
- Provides automated validation of deployments.
- Notifies developers immediately of success or failure.

---

## **How This Pipeline Saves Time and Effort**

### **Before the Pipeline**
Developers had to:
1. Manually validate commits.
2. Build and test Docker images locally.
3. Edit Kubernetes manifests manually for each environment.
4. Validate manifests and push them to a GitOps repository.
5. Trigger ArgoCD deployments manually.
6. Perform manual smoke tests to verify deployments.

### **With the Pipeline**
- **Automated**: All steps are automated, ensuring speed, accuracy, and consistency.
- **Dynamic Configurations**: Developers simply provide input parameters, and the pipeline handles the rest.
- **Error Prevention**: Validations at every step catch issues early, saving debugging time.
- **Consistency**: Every deployment follows the same standardized process, eliminating inconsistencies.

---

## **Step-by-Step Guide for Developers**

### **Prerequisites**
1. Ensure the application repository contains:
   - A `Dockerfile` for building Docker images.
   - Tests that can run inside a container (e.g., `npm test`).
2. Confirm that the feeder repository contains:
   - Base Kubernetes manifests and `kustomization.yaml` files.
   - Patches folder for applications that need it (`go-api`, `java-api`).
3. Set up the required secrets in GitHub Actions:
   - `DOCKER_USER`, `DOCKER_PASSWORD` (Artifactory credentials).
   - `ARGOCD_SERVER`, `ARGOCD_TOKEN` (ArgoCD access).
   - `SLACK_WEBHOOK` (Slack notification).

---

### **How to Trigger the Pipeline**
1. Go to the **GitHub Actions** tab in your repository.
2. Select the **CI/CD Pipeline** workflow.
3. Click **Run Workflow** and provide the following inputs:
   - `application`: Choose the application (e.g., `go-api`, `java-api`, etc.).
   - `environment`: Choose the environment (e.g., `dev`, `prod`).
   - Optional:
     - `replicas`: Specify the number of replicas (default: 1).
     - `cpu_limit`: Specify the CPU limit (default: 500m).
     - `memory_limit`: Specify the memory limit (default: 256Mi).

---

### **What Happens After Triggering**
1. **Pipeline Execution**:
   - The pipeline runs all stages automatically.
   - Logs are visible in the GitHub Actions UI for each step.

2. **Post-Deployment**:
   - Check Slack for deployment success notifications.
   - Validate the deployment manually (if needed).

---

## **Future Improvements**
- **Error Reporting**: Enhance Slack notifications with detailed error logs.
- **Environment Overrides**: Allow overrides for environment-specific configurations in the feeder repository.
- **Auto-Rollback**: Add functionality to revert deployments if smoke tests fail.

---

This pipeline drastically reduces manual work for developers, ensures consistent deployments, and provides immediate feedback, making it an indispensable tool for your team. Let me know if you'd like further enhancements or explanations! 🚀