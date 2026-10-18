# DevOps Lab Assignment

This repository contains my work for ten DevOps labs. I ran the commands in PowerShell on Windows, using Docker Desktop for the container labs and Ubuntu through WSL for AppArmor.

Each lab folder contains its report, required source and configuration files, and screenshots. The reports describe the commands I ran, the problems I encountered, and the results I checked.

| Lab | Topic | Report |
| --- | --- | --- |
| 1 | Nginx Pod on Kubernetes | [lab-01](lab-01/README.md) |
| 2 | Flask on Minikube | [lab-02](lab-02/README.md) |
| 3 | Scaling a Flask app with a ReplicaSet | [lab-03](lab-03/README.md) |
| 4 | Docker networking with Flask, MySQL and Redis | [lab-04](lab-04/README.md) |
| 5 | Docker security with AppArmor and Python | [lab-05](lab-05/README.md) |
| 6 | Delivery monitoring and alerts | [lab-06](lab-06/README.md) |
| 7 | Installing Jenkins | [lab-07](lab-07/README.md) |
| 8 | Hello World Jenkins job | [lab-08](lab-08/README.md) |
| 9 | Multi-stage Flask pipeline | [lab-09](lab-09/README.md) |
| 10 | Multiple applications on three Kubernetes nodes | [lab-10](lab-10/README.md) |

## Using the reports

Unless a step specifies another directory, run its commands from the repository root:

```powershell
cd "$env:USERPROFILE\Documents\devOps"
```

The screenshots record the original lab runs. Assigned ports, container IDs and Pod names can change on another run.

Repository: [palak12-30/devOps](https://github.com/palak12-30/devOps)
