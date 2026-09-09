# devops_lab

# Kubernetes Getting Started

## Objective

Deploy an Nginx application as a Kubernetes Pod using Minikube and verify that it is running successfully.

## Steps

### 1. Install Minikube

Minikube was installed on macOS using Homebrew.

```bash
brew install minikube
2. Start Minikube

Start the local Kubernetes cluster using:

minikube start

Minikube uses Docker as the driver for running the Kubernetes cluster.

3. Create the Nginx Pod

Create an Nginx Pod using the following command:

kubectl run hello-k8s --image=nginx --port=80

This command creates a Kubernetes Pod named hello-k8s using the official Nginx image.

4. Verify the Pod

Check the status of the Pod using:

kubectl get pods

The Pod should show a status of Running.
5. Access the Nginx Application

Access the Nginx application through Minikube.

Run:

minikube service hello-k8s

This opens the Nginx application in the browser.

The browser should display the default:

Welcome to nginx!

This confirms that the Nginx Pod was successfully deployed and is running inside the Kubernetes cluster.

Result

Successfully deployed and accessed an Nginx application using Kubernetes and Minikube.

Technologies Used
Kubernetes
Minikube
Docker
Nginx
kubectl
