### **Pipeline Overview and Documentation**

This updated pipeline dynamically supports Kubernetes overlays for applications with and without patches (`go-api`, `java-api`, etc.), automates manifest customization at runtime, and streamlines deployments through GitHub Actions. Below is the **updated explanation and documentation** to reflect recent enhancements.

---

## **What Does the Pipeline Do?**

The pipeline automates the CI/CD process for Kubernetes deployments, ensuring consistency, reliability, and flexibility through dynamic input customization. Here's how it works:

---

### **1. Triggering the Pipeline**
The pipeline is manually triggered using the **GitHub Actions `workflow_dispatch` event**, which allows developers to specify:
- `application` (e.g., `backend`, `frontend`, `go-api`, `java-api`).
- `environment` (e.g., `dev`, `test`, `prod`).
- Additional customizable parameters:
  - `replicas`: Number of replicas for the application.
  - `cpu_limit`: CPU limit for the application container.
  - `memory_limit`: Memory limit for the application container.
  - `env_vars`: Environment variables as JSON (e.g., `[{ "name": "ENV_KEY", "value": "value" }]`).
  - `hpa_enabled`: Enable Horizontal Pod Autoscaler (`true`/`false`).
  - `hpa_max_replicas`: Maximum replicas for HPA.

**What’s New?** 
- Developers can now fully customize Kubernetes overlays at runtime, removing the need to manually edit YAML files.
- Supports advanced features like Horizontal Pod Autoscaling (HPA) for scalable deployments.

---

### **2. Validate Commit Messages (`validate-commit`)**
This stage:
- Ensures commit messages follow a consistent format (e.g., `feat:`, `fix:`).
- Prevents merging of poorly documented commits into the main branch.
  
**Why It Helps**: Improves collaboration and code traceability.

---

### **3. Build and Test Application (`build-and-test`)**
This stage:
1. **Builds a Docker image** of the application.
2. **Runs application tests** inside a Docker container to ensure stability.
3. **Pushes the Docker image** to an Artifactory registry for deployment.

**Why It Helps**:
- Ensures code quality through automated testing.
- Simplifies Docker image management.

---

### **4. Manage Kubernetes Manifests (`manage-manifests`)**
This is the heart of the pipeline and includes the following:

1. **Fetches the feeder repository**:
   - Contains the base Kubernetes manifests and `kustomization.yaml` files.

2. **Dynamic YAML Generation**:
   - Uses a helper script (`generate-patch.sh`) to generate environment-specific Kubernetes overlays dynamically based on pipeline inputs.
   - Supports customization of replicas, resource limits, environment variables, and HPA.

3. **Applies Kustomize Overlays**:
   - Combines base manifests, patches, and runtime inputs into a single deployment manifest for the specified environment.

4. **Validates the Manifests**:
   - Uses `kubeval` to ensure the generated manifests are valid and conform to Kubernetes standards.

5. **Pushes the Manifests**:
   - Commits and pushes the customized manifests to the feeder repository, which is watched by ArgoCD.

**Why It Helps**:
- Automates the generation of Kubernetes manifests with environment-specific configurations.
- Reduces manual errors and saves time by eliminating the need for YAML editing.

---

### **5. Trigger ArgoCD Deployment (`trigger-argocd`)**
This stage:
1. Triggers ArgoCD to sync the latest manifests from the feeder repository.
2. Ensures the Kubernetes cluster is updated with the new deployment.

**Why It Helps**:
- Removes the need for developers to manually trigger ArgoCD syncs.
- Ensures deployments are consistent and reliable.

---

### **6. Post-Deployment Verification (`post-deployment`)**
This stage:
1. Pulls the deployed Docker image from Artifactory to verify deployment consistency.
2. Runs smoke tests to validate the application is running correctly in the cluster.
3. Sends a Slack notification to the team about the deployment status.

**Why It Helps**:
- Provides automated validation of deployments.
- Keeps the team informed of deployment results.

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
- **Dynamic Configurations**: Developers provide input parameters, and the pipeline handles the rest.
- **Error Prevention**: Validations at every step catch issues early, saving debugging time.
- **Scalability**: Supports advanced features like HPA for production workloads.

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
     - `env_vars`: Add environment variables in JSON format.
     - `hpa_enabled`: Enable HPA (`true`/`false`).
     - `hpa_max_replicas`: Specify the maximum replicas for HPA (default: 10).

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
- **Environment Overrides**: Allow developers to override default environment settings directly in the feeder repository.
- **Auto-Rollback**: Add functionality to revert deployments if smoke tests fail.

---

This updated pipeline empowers developers with flexible and automated Kubernetes deployment capabilities, minimizing manual effort while ensuring reliability. 🚀