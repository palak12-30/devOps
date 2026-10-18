# DevOps Lab Assignment

This repository contains my work for the ten DevOps labs. I ran the commands in PowerShell on Windows, with Docker Desktop for the container labs. For the AppArmor lab, I also used Ubuntu through WSL. Each section below includes the commands I ran, the problems I encountered, and the results I checked.

| Lab | Report | Files |
| --- | --- | --- |
| 1 | [Nginx Pod on Kubernetes](#lab-1-running-nginx-on-kubernetes) | [lab-01](lab-01/) |
| 2 | [Flask on Minikube](#lab-2-deploying-flask-on-minikube) | [lab-02](lab-02/) |
| 3 | [Scaling with a ReplicaSet](#lab-3-scaling-a-flask-app-with-a-replicaset) | [lab-03](lab-03/) |
| 4 | [Docker networking](#lab-4-docker-networking-with-flask-mysql-and-redis) | [lab-04](lab-04/) |
| 5 | [Docker security with AppArmor](#lab-5-docker-security-with-apparmor-and-python) | [lab-05](lab-05/) |
| 6 | [Delivery monitoring and alerts](#lab-6-delivery-monitoring) | [lab-06](lab-06/) |
| 7 | [Installing Jenkins](#lab-7-installing-jenkins) | [lab-07](lab-07/) |
| 8 | [Hello World Jenkins job](#lab-8-hello-world-jenkins-job) | [lab-08](lab-08/) |
| 9 | [Multi-stage Flask pipeline](#lab-9-multi-stage-flask-pipeline) | [lab-09](lab-09/) |
| 10 | [Multiple apps on three nodes](#lab-10-multiple-applications-on-three-kubernetes-nodes) | [lab-10](lab-10/) |

## Lab 1: Running Nginx on Kubernetes

I started with an Nginx container on Minikube. The aim was to get a Pod running and open its welcome page in the browser.

### 1. Checked Docker and Minikube

I first checked that Docker was using Linux containers and confirmed the Minikube version.

```powershell
docker info --format '{{.OSType}}'
C:\minikube\minikube.exe version
```

Docker returned `linux`, and Minikube was version `v1.39.0`.

### 2. Started the Kubernetes cluster

My first attempt used the default Minikube profile:

```powershell
C:\minikube\minikube.exe start --driver=docker
```

This failed with `GUEST_DRIVER_MISMATCH` because the existing profile was configured for Hyper-V. I used a separate profile called `devops-lab` with the Docker driver:

```powershell
C:\minikube\minikube.exe start -p devops-lab --driver=docker
```

Minikube downloaded the required image and started Kubernetes `v1.37.0`.

### 3. Waited for the node to become ready

```powershell
kubectl --context=devops-lab get nodes
kubectl --context=devops-lab wait --for=condition=Ready node/devops-lab --timeout=180s
kubectl --context=devops-lab get nodes
```

The node initially showed `NotReady`. After waiting, its status changed to `Ready`.

### 4. Created the Nginx Pod

```powershell
kubectl --context=devops-lab run hello-k8s --image=nginx --port=80
kubectl --context=devops-lab wait --for=condition=Ready pod/hello-k8s --timeout=180s
kubectl --context=devops-lab get pods -o wide
```

The Pod was created successfully. It showed `1/1` ready, a status of `Running`, and `0` restarts on the `devops-lab` node.

### 5. Exposed the Pod using a Service

```powershell
kubectl --context=devops-lab expose pod hello-k8s --type=NodePort --port=80
kubectl --context=devops-lab get service hello-k8s
```

The Service was named `hello-k8s`. It mapped port `80` to node port `30789`, shown as `80:30789/TCP`.

### 6. Opened the Nginx welcome page

```powershell
C:\minikube\minikube.exe -p devops-lab service hello-k8s
```

Minikube started a tunnel and opened `http://127.0.0.1:57067` in the browser. I kept the PowerShell window open to keep the tunnel running.

The browser displayed **Welcome to nginx!**, confirming that I could access the application running in Kubernetes.

![Nginx welcome page](lab-01/nginx-welcome.png)


### 7. Uploaded the lab to GitHub

From the local repository folder, I pushed the committed lab files:

```powershell
git push origin main
```

The push completed successfully with commit `f573bbd`.

I also included the [Pod YAML](lab-01/pod.yaml) and [Service YAML](lab-01/service.yaml) so the same resources can be created from files. In this run, I created them with the commands above.

### Additional screenshots

![Docker driver mismatch and separate Minikube profile](lab-01/cluster-setup.png)

![Ready node, running Nginx Pod and service tunnel](lab-01/pod-service.png)

## Lab 2: Deploying Flask on Minikube

Next, I deployed a small Flask app that returns `Hello from Flask on Kubernetes!` on port `15000`. The app, Dockerfile and Kubernetes YAML are in [lab-02](lab-02/).

### 1. Built the application image

From the repository folder, I built the image using the files in `lab-02`:

```powershell
docker build -t flask-app:lab02 .\lab-02
```

The first build was cancelled while installing dependencies. I ran it again with detailed output:

```powershell
docker build --progress=plain -t flask-app:lab02 .\lab-02
```

The second build finished and created `flask-app:lab02`, using Python 3.12 and Flask 3.1.3.

### 2. Loaded the image into Minikube

```powershell
C:\minikube\minikube.exe -p devops-lab image load flask-app:lab02
```

I loaded the image into the existing cluster so Kubernetes could use it locally. The manifest uses `imagePullPolicy: Never` with the same image tag.

### 3. Created the Deployment and Service

```powershell
kubectl --context=devops-lab apply -f .\lab-02\flask-deployment.yaml
kubectl --context=devops-lab rollout status deployment/flask-app --timeout=180s
```

Kubernetes created the `flask-app` Deployment and `flask-app-service` Service. The rollout completed successfully.

### 4. Checked the application

```powershell
kubectl --context=devops-lab get pods -l app=flask-app -o wide
kubectl --context=devops-lab get service flask-app-service
kubectl --context=devops-lab get deployments
kubectl --context=devops-lab describe deployment flask-app
kubectl --context=devops-lab logs deployment/flask-app
```

The Pod `flask-app-7fcfcddc4d-6ftjk` showed `1/1` ready, `Running`, and zero restarts. The Deployment had one available replica. The logs confirmed that Flask was listening on port `15000`.

The NodePort Service mapped port `15000` to node port `30856`, shown as `15000:30856/TCP`.

### 5. Opened the Flask application

```powershell
C:\minikube\minikube.exe -p devops-lab service flask-app-service --url
```

Minikube returned `http://127.0.0.1:52623`. I kept the terminal open and opened the URL in my browser. The page displayed **Hello from Flask on Kubernetes!**.

![Flask application running on Kubernetes](lab-02/flask-welcome.png)

### Additional screenshots

![Completed Flask Docker image build](lab-02/image-build.png)

![Available Flask deployment using port 15000](lab-02/deployment-details.png)

## Lab 3: Scaling a Flask App with a ReplicaSet

For the scaling lab, I used the flash-sale Flask app from the exercise. It has `/`, `/buy`, and `/health` endpoints. I ran it on the same single-node cluster, first with three Pods and then with five. The files are in [lab-03](lab-03/).

### 1. Built and uploaded the image

I built the image with a local tag and a Docker Hub tag:

```powershell
docker build --progress=plain -t flashsale:1.0 -t avstark/flashsale:1.0 .\lab-03
docker push avstark/flashsale:1.0
```

The build and Docker Hub upload completed successfully. I then loaded the local image into Minikube:

```powershell
C:\minikube\minikube.exe -p devops-lab image load flashsale:1.0
```

### 2. Started three replicas

```powershell
kubectl --context=devops-lab apply -f .\lab-03\flashsale-replicaset.yaml
kubectl --context=devops-lab wait --for=condition=Ready pod -l app=flashsale --timeout=180s
kubectl --context=devops-lab get rs flashsale-rs
kubectl --context=devops-lab get pods -l app=flashsale -o wide
```

This created the `flashsale-rs` ReplicaSet and `flashsale-svc` Service. The ReplicaSet showed `3` desired, `3` current, and `3` ready Pods. All three Pods were running on `devops-lab`.

### 3. Scaled from three Pods to five

```powershell
kubectl --context=devops-lab scale rs flashsale-rs --replicas=5
kubectl --context=devops-lab wait --for=condition=Ready pod -l app=flashsale --timeout=180s
kubectl --context=devops-lab get rs flashsale-rs
kubectl --context=devops-lab get pods -l app=flashsale -o wide
```

Kubernetes created two additional Pods, `flashsale-rs-9qkb5` and `flashsale-rs-hc4ff`. The ReplicaSet then showed `5` desired, `5` current, and `5` ready Pods.

### 4. Deleted a Pod and checked its replacement

```powershell
kubectl --context=devops-lab delete pod flashsale-rs-b54pr
kubectl --context=devops-lab wait --for=condition=Ready pod -l app=flashsale --timeout=180s
kubectl --context=devops-lab get rs flashsale-rs
kubectl --context=devops-lab get pods -l app=flashsale -o wide
```

After I deleted `flashsale-rs-b54pr`, the ReplicaSet created `flashsale-rs-rkhvh` to replace it. The replacement became ready, bringing the total back to five running Pods with zero restarts.

| Pod after replacement | Status | Node |
| --- | --- | --- |
| flashsale-rs-9qkb5 | 1/1 Running | devops-lab |
| flashsale-rs-bnm8n | 1/1 Running | devops-lab |
| flashsale-rs-gd6fl | 1/1 Running | devops-lab |
| flashsale-rs-hc4ff | 1/1 Running | devops-lab |
| flashsale-rs-rkhvh | 1/1 Running | devops-lab |

Deleting a Pod did not reduce the replica count permanently: Kubernetes created a replacement to bring it back to five. All five copies ran on the same node because this was still a single-node cluster.

### Additional screenshots

![Completed flashsale image build and tags](lab-03/image-build.png)

![Successful flashsale image push to Docker Hub](lab-03/dockerhub-push.png)

![Five running replicas after scaling](lab-03/scaled-replicas.png)

![All five replicas ready after replacement of the deleted Pod](lab-03/replicas-ready.png)

## Lab 4: Docker Networking with Flask, MySQL and Redis

I used a custom bridge network to connect a Flask API, MySQL and Redis. The main checks were whether Flask responded from my laptop and whether its container could reach the other two containers by name. The Flask files are in [lab-04](lab-04/).

### 1. Created and inspected the network

I checked the existing containers and networks before creating the lab network:

```powershell
docker ps -a
docker network ls
docker network create --driver bridge my-bridge-net
docker network ls
docker network inspect my-bridge-net
```

Docker created `my-bridge-net` with the bridge driver, subnet `172.19.0.0/16` and gateway `172.19.0.1`. No containers were attached at this point.

### 2. Built the Flask image

The Flask app serves `/about` on port `5001`. I used `host='0.0.0.0'` so it could accept requests through the container network. The Dockerfile also installs `ping` for the connectivity tests.

```powershell
docker build --progress=plain -t flask-api:lab04 .\lab-04
```

The first build got stuck downloading Debian packages and reported connection timeouts. I switched the repository URLs to HTTPS, added retry limits in the Dockerfile, and ran the build again. That build finished.

### 3. Started the three containers

```powershell
docker run -d --name mysql --network my-bridge-net -e "MYSQL_ROOT_PASSWORD=<redacted>" -e MYSQL_DATABASE=devopsdb mysql:latest
docker run -d --name redis --network my-bridge-net redis:latest
docker run -d --name flask --network my-bridge-net -p 5001:5001 flask-api:lab04
docker ps
```

All three containers stayed running. I have replaced the local test password with `<redacted>` in these recorded commands.

### 4. Tested Flask from the host

```powershell
curl.exe http://localhost:5001/about
```

The response was:

```json
{"description":"This is a simple REST API built with Flask.","name":"Simple REST API","version":"1.0"}
```

The `-p 5001:5001` option forwards port `5001` on my laptop to port `5001` inside the Flask container.

### 5. Checked container-to-container communication

```powershell
docker network inspect my-bridge-net
docker exec flask ping -c 3 mysql
docker exec flask ping -c 3 redis
```

The network inspection listed all three containers:

| Container | IP address |
| --- | --- |
| mysql | 172.19.0.2 |
| redis | 172.19.0.3 |
| flask | 172.19.0.4 |

Both `ping mysql` and `ping redis` worked from the Flask container, with **0% packet loss**. I could use the container names because they were on the same custom bridge network. The `--network` option connected each container to that network.

### 6. Verified Redis and MySQL

```powershell
docker exec redis redis-cli ping
docker exec mysql mysql -uroot '-p<redacted>' -e "SHOW DATABASES;"
```

Redis returned `PONG`. MySQL listed `devopsdb`, `information_schema`, `mysql`, `performance_schema` and `sys`.

Only Flask needed a published host port for these tests. MySQL and Redis communicated within the bridge network. A bridge gives containers their own network namespaces; host networking shares the host's network namespace.

### 7. Cleaned up the lab

```powershell
docker stop mysql redis flask
docker rm mysql redis flask
docker network rm my-bridge-net
docker ps -a
docker network ls
```

Docker stopped and removed all three lab containers, then removed `my-bridge-net`. The final checks confirmed that the lab containers and custom network were gone.

### 8. Captured the final connectivity screenshot

I recreated the lab network and its three containers using the existing images to capture the results. For this run, I used MySQL's random-password option rather than putting a password in the command:

```powershell
docker network create --driver bridge my-bridge-net
docker run -d --name mysql --network my-bridge-net -e MYSQL_RANDOM_ROOT_PASSWORD=yes -e MYSQL_DATABASE=devopsdb mysql:latest
docker run -d --name redis --network my-bridge-net redis:latest
docker run -d --name flask --network my-bridge-net -p 5001:5001 flask-api:lab04
curl.exe http://localhost:5001/about
docker exec flask ping -c 3 mysql
docker exec flask ping -c 3 redis
```

Flask returned the expected API details again. MySQL resolved to `172.20.0.2` and Redis to `172.20.0.3` on this recreated network. Both ping tests received all three replies with zero packet loss. These addresses differ from the first run because Docker assigned a subnet when the network was recreated.

![Flask response and successful MySQL and Redis connectivity tests](lab-04/network-connectivity.png)

### Additional screenshots

![Bridge network inspection before containers were attached](lab-04/bridge-network.png)

![Flask container attached to the custom bridge network](lab-04/network-containers.png)

## Lab 5: Docker Security with AppArmor and Python

In this lab, I applied an AppArmor profile to a Flask container and used Python's Docker SDK to test it. Getting the profile to actually enforce the restrictions needed extra setup in WSL. The app, profile and scripts are in [lab-05](lab-05/).

The commands in this section use my current checkout at `C:\Users\PALAK\Documents\devOps`. The image archive is saved in Documents, outside the repository. The screenshots record the original runs; updating these command paths does not represent a new execution of the labs.

### 1. Enabled AppArmor in WSL

I checked the Docker security options and the Ubuntu kernel:

```powershell
docker info --format '{{json .SecurityOptions}}'
wsl --list --verbose
wsl -d Ubuntu-22.04 -- uname -r
wsl -d Ubuntu-22.04 -- cat /sys/module/apparmor/parameters/enabled
```

AppArmor was initially disabled (`N`). I added the following to `%USERPROFILE%\.wslconfig`, quit Docker Desktop, and restarted WSL:

```ini
[wsl2]
kernelCommandLine=apparmor=1 security=apparmor
```

```powershell
wsl --shutdown
wsl -d Ubuntu-22.04 -- cat /sys/module/apparmor/parameters/enabled
```

The result changed to `Y`. After reopening Docker Desktop, its security options also listed AppArmor.

### 2. Loaded the custom profile

Ubuntu already had `apparmor_parser`. I mounted the security filesystem, copied the profile and loaded it:

```powershell
wsl -d Ubuntu-22.04 -u root -- mount -t securityfs securityfs /sys/kernel/security
wsl -d Ubuntu-22.04 -u root -- cp /mnt/c/Users/PALAK/Documents/devOps/lab-05/my-apparmor-profile /etc/apparmor.d/my-apparmor-profile
wsl -d Ubuntu-22.04 -u root -- apparmor_parser -r /etc/apparmor.d/my-apparmor-profile
wsl -d Ubuntu-22.04 -u root -- cat /sys/kernel/security/apparmor/profiles
```

The kernel listed `my-apparmor-profile (enforce)`. The profile denies reading `/etc`, reading or writing `/var`, executing programs under `/bin` and `/usr/bin`, and using the `sys_admin` capability. Python remains available under `/usr/local/bin`.

### 3. Built and checked the Flask image

```powershell
docker build --progress=plain -t flask-apparmor:lab05 .\lab-05
docker run -d --name lab05-flask --security-opt apparmor=my-apparmor-profile -p 5000:5000 flask-apparmor:lab05
docker inspect --format '{{.AppArmorProfile}}' lab05-flask
curl.exe http://localhost:5000
```

Flask started and returned the expected greeting, and Docker inspection showed the profile name. But the process label was still `unconfined`. The container could read `/etc/passwd` and run Bash, so the profile name alone did not prove that the restrictions were working.

I also mounted securityfs in `docker-desktop` and confirmed it could see the profile, but a fresh container remained unconfined. Its environment did not have `/sbin/apparmor_parser`. I used Ubuntu's own Docker engine for the working enforcement tests.

### 4. Set up Ubuntu's Docker engine and Python SDK

I saved the existing image, disabled Docker Desktop's Ubuntu-22.04 integration, and installed Docker in Ubuntu:

```powershell
docker save -o "$env:USERPROFILE\Documents\lab05-flask.tar" flask-apparmor:lab05
wsl -d Ubuntu-22.04 -u root -- apt-get update
wsl -d Ubuntu-22.04 -u root -- apt-get install -y python3.10-venv
wsl -d Ubuntu-22.04 -u root -- apt-get install -y docker.io
wsl -d Ubuntu-22.04 -u root -- sh -c 'mountpoint -q /sys/kernel/security || mount -t securityfs securityfs /sys/kernel/security'
wsl -d Ubuntu-22.04 -u root -- apparmor_parser -r /etc/apparmor.d/my-apparmor-profile
wsl -d Ubuntu-22.04 -u root -- service docker restart
wsl -d Ubuntu-22.04 -u root -- docker info --format 'Server={{.ServerVersion}} OS={{.OperatingSystem}} Security={{json .SecurityOptions}}'
wsl -d Ubuntu-22.04 -u root -- docker load -i /mnt/c/Users/PALAK/Documents/lab05-flask.tar
```

This engine reported Docker `29.1.3`, Ubuntu `22.04.5 LTS`, and AppArmor support. The saved image loaded successfully.

I created a virtual environment and installed the Docker SDK:

```powershell
wsl -d Ubuntu-22.04 -- python3 -m venv /tmp/devops-lab5-venv
wsl -d Ubuntu-22.04 -- /tmp/devops-lab5-venv/bin/pip install -r /mnt/c/Users/PALAK/Documents/devOps/lab-05/sdk-requirements.txt
```

My first attempt to create the virtual environment failed because `ensurepip` was missing. After installing `python3.10-venv`, I created it again. I also changed the SDK script to use the existing image because rebuilding it from WSL had failed with a Windows credential-helper error.

### 5. Verified the profile and restricted actions using Python

```powershell
wsl -d Ubuntu-22.04 -u root -- /tmp/devops-lab5-venv/bin/python /mnt/c/Users/PALAK/Documents/devOps/lab-05/apply_apparmor.py
wsl -d Ubuntu-22.04 -u root -- /tmp/devops-lab5-venv/bin/python /mnt/c/Users/PALAK/Documents/devOps/lab-05/test_restricted_actions.py
```

The first script confirmed the kernel label `my-apparmor-profile (enforce)` and received the Flask greeting while the profile was active.

The restriction tests produced:

| Action from the confined Python process | Result |
| --- | --- |
| Read `/etc/passwd` | Exit code 1; `PermissionError: Permission denied` |
| Launch `/bin/bash` using `subprocess.run` | Exit code 1; `PermissionError: Permission denied` |

Running Bash directly through Docker exec was still allowed. To check what the confined app could do, I tested a Bash launch from Python after confirming Python's enforcing label. That attempt failed with `PermissionError`, as did reading `/etc/passwd`.

The script printed `Both restricted actions were denied as expected.` Both SDK scripts removed their temporary containers after running.

![AppArmor enforcing and denying both restricted actions](lab-05/apparmor-restrictions.png)

### Additional screenshots

![SDK verification of the enforcing AppArmor profile and Flask response](lab-05/apparmor-sdk.png)

## Lab 6: Delivery Monitoring

For this lab, I simulated delivery activity in Python, collected its metrics with Prometheus, and viewed them in Grafana. Jenkins started the services. I used the four metrics from the handout: total deliveries, pending deliveries, on-the-way deliveries, and delivery times. For average delivery time, the dashboard divides the Summary's total time by its observation count.

I added the missing metrics Dockerfile and used Docker Compose to start the three services on one network. Prometheus scrapes `metrics:8000`, and Grafana connects to `http://prometheus:9090`. These Docker service names replace the handout's fixed Linux host IP. I saved Grafana's data source and dashboard in configuration files so the pipeline can recreate them.

I created a Pipeline job named `Delivery-Monitoring`, pasted `lab-06/Jenkinsfile` into the Pipeline script field, and ran it with `USE_LOCAL_SOURCE` checked and `ALERT_DEMO` unchecked.

Build #1 failed after a network interruption left the Prometheus and Grafana image layers incomplete (`short read ... unexpected EOF`). I downloaded both images from PowerShell:

```powershell
docker pull prom/prometheus:latest
docker pull grafana/grafana:latest
```

After both images downloaded, I used Build with Parameters to run the job again with the same settings.

Build #2 built all three images. `promtool` validated `prometheus.yml` and found both alert rules. Jenkins started the services and checked the running stack:

| Check in build #2 | Result |
| --- | --- |
| Grafana health | OK |
| Prometheus delivery-service scrape target | UP |
| Total deliveries | 64 |
| Pending deliveries | 19 |
| On-the-way deliveries | 14 |
| Average delivery time | About 25.71 seconds |

These were the simulated values when the check ran; they change as the app runs. At that point, no alerts were firing. The console ended with `Monitoring verification passed.` and `Finished: SUCCESS`.

The services were available at `http://localhost:8001/metrics`, `http://localhost:9090`, and `http://localhost:3000`. The metrics container still listens on port 8000; Docker publishes it on host port 8001.

I opened Grafana's Delivery Operations dashboard and checked that all four charts displayed data. The alert-count panel shows how many Prometheus alerts are firing; it does not identify them by name.


I then ran build #3 with both `USE_LOCAL_SOURCE` and `ALERT_DEMO` checked. The demo mode raises pending deliveries to 50–100 and delivery times to 35–45 seconds. It recreates the metrics container with that setting and waits for both rules to fire.

The check reported 50 pending deliveries and an average delivery time of about 40.00 seconds. Prometheus reported both `HighPendingDeliveries` (warning) and `HighAverageDeliveryTime` (critical) as firing. Both rules require their conditions to stay true for 15 seconds; I added the missing duration to the average-time rule so it matches the handout's description.

Build #3 also finished successfully, this time with both alerts firing. I checked the alerts through Prometheus and the Grafana count panel. I did not set up email or chat notifications for this exercise.

I refreshed Grafana after the demo run. The pending-deliveries chart rose into the 50–100 range, the average-time chart moved to about 40 seconds, and the firing-alert count reached 2.

![Higher delivery counts during the alert simulation](lab-06/alert-demo-deliveries.png)

![Two firing alerts and the higher average delivery time](lab-06/alert-demo-firing.png)

### Additional screenshots

![Successful Grafana image download after the interrupted pull](lab-06/grafana-image-pull.png)

## Lab 7: Installing Jenkins

I ran Jenkins in Docker. I built the image with Java 21, Python, Git, the Docker CLI, and the Pipeline and Git plugins because the other exercises needed these tools too.

From the repository folder in PowerShell, I ran:

```powershell
docker build --progress=plain -t devops-jenkins:lab07 .\lab-07
docker run -d --name jenkins --restart unless-stopped --group-add 0 -p 127.0.0.1:8081:8080 -v devops-jenkins-home:/var/jenkins_home -v /var/run/docker.sock:/var/run/docker.sock --mount "type=bind,source=$($PWD.Path),target=/opt/devops-labs,readonly" devops-jenkins:lab07
docker ps -a --filter "name=^/jenkins$"
```

I used port 8081 because another app was already using 8080. The `devops-jenkins-home` volume stores Jenkins's settings. I mounted the Docker socket so Jenkins could run the container commands, and mounted the repository read-only at `/opt/devops-labs` for the first local tests.

I opened `http://localhost:8081/`. Reading the initial password file returned `No such file or directory`, so I checked the startup log locally with `docker logs jenkins` and used the generated password shown there to unlock Jenkins. I kept the password out of this repository.

I installed the suggested plugins, created my administrator account, kept the Jenkins URL as `http://localhost:8081/`, and finished setup. The welcome dashboard opened successfully and showed Jenkins 2.580.1.

![Jenkins dashboard after setup](lab-07/jenkins-dashboard.png)

### Additional screenshots

![Jenkins startup and plugin initialization](lab-07/jenkins-startup.png)

## Lab 8: Hello World Jenkins Job

I created a Freestyle project named `HelloWorld`. For the first run, I left Source Code Management as `None` and added an Execute shell build step:

```sh
sh /opt/devops-labs/lab-08/hello-world.sh
```

This used the script from the repository folder mounted into Jenkins. I clicked Save, then Build Now, and opened build #1's Console Output. It printed:

```text
Hello, Jenkins!
Finished: SUCCESS
```

This run verified the local script. GitHub checkout was not used for this build.

![HelloWorld build 1 console output](lab-08/hello-world-console.png)

After uploading the remaining lab files to GitHub, I changed HelloWorld's Source Code Management to Git, entered `https://github.com/palak12-30/devOps.git`, left credentials unset for the public repository, and selected branch `*/main`. I changed the Execute shell step to use the script from the checked-out workspace:

```sh
sh lab-08/hello-world.sh
```

Build #3 fetched the script from GitHub at commit `2730b3f` on `origin/main`. It printed `Hello, Jenkins!` and finished successfully, so I had checked both the local script and the GitHub checkout.

## Lab 9: Multi-Stage Flask Pipeline

I created a Pipeline job named `Python-MultiStage-Pipeline`. I copied `lab-09/Jenkinsfile` into the Pipeline script field and kept the Groovy sandbox enabled. For build #1, `USE_LOCAL_SOURCE` was enabled, so Jenkins copied the application files from `/opt/devops-labs/lab-09` into its workspace.

I used all five stages from the exercise. Python was already installed in my Jenkins image, and the Build stage installed Flask 3.1.3 in a virtual environment.

| Stage | What happened in build #1 |
| --- | --- |
| Build | Created `.venv` and installed Flask and its dependencies. |
| Test | Ran `test_home`; the response status and greeting matched, and the test passed. |
| Deploy | Copied `app.py` and `requirements.txt` into the workspace's `lab-09/python-app-deploy` folder as a mock deployment. |
| Run Application | Started the copied Flask application in the background. |
| Test Application | Requested the running server and received `HTTP 200: Hello, Jenkins Multi-Stage Pipeline!`. |

The post-build step stopped the Flask process, removed its PID file, and archived `app.log`. The console ended with `Pipeline completed successfully!` and `Finished: SUCCESS`.

This verified the pipeline using the mounted local files. Build #1 did not check out the application from GitHub.

![Successful multi-stage pipeline build](lab-09/pipeline-success.png)

After pushing the files, I changed the job's Definition to `Pipeline script from SCM`, selected Git, entered `https://github.com/palak12-30/devOps.git`, set the branch to `*/main`, and used `lab-09/Jenkinsfile` as the Script Path. I ran Build with Parameters with `USE_LOCAL_SOURCE` unchecked.

Build #2 read the Jenkinsfile and application source from GitHub at commit `2730b3f`. All five stages passed again. The unit test was `OK`, and the running server returned `HTTP 200: Hello, Jenkins Multi-Stage Pipeline!`. Jenkins then stopped the server and saved its log. The final result was `Finished: SUCCESS`.

## Lab 10: Multiple Applications on Three Kubernetes Nodes

I created a separate Minikube profile for the multi-node exercise:

```powershell
C:\minikube\minikube.exe start -p devops-multinode --driver=docker --nodes=3 --cpus=2 --memory=2000
kubectl --context=devops-multinode wait --for=condition=Ready nodes --all --timeout=300s
kubectl --context=devops-multinode get nodes
```

Minikube reported a connection warning for `registry.k8s.io` while starting the third node, but cluster creation completed. The third node was initially `NotReady`; it finished starting without a configuration change. The wait command then succeeded for all three nodes.

| Node | Status | Role |
| --- | --- | --- |
| devops-multinode | Ready | Control plane |
| devops-multinode-m02 | Ready | Worker |
| devops-multinode-m03 | Ready | Worker |

All three nodes ran Kubernetes v1.37.0 with containerd 2.3.4.

I used the handout's Product Catalog and Shopping Cart Flask applications, with Python 3.12 and Flask 3.1.3. The catalog serves `/products`; the cart supports GET and POST requests at `/cart`.

From the repository folder, I built both images and loaded them into the multi-node profile:

```powershell
docker build -t product-catalog:latest -f .\lab-10\Dockerfile.product .\lab-10
docker build -t shopping-cart:latest -f .\lab-10\Dockerfile.shopping .\lab-10
C:\minikube\minikube.exe -p devops-multinode image load product-catalog:latest
C:\minikube\minikube.exe -p devops-multinode image load shopping-cart:latest
```

Both images built, and the load commands finished without errors. I loaded the images directly into Minikube's node runtimes, so I did not need to enable the registry add-on.

I created the `devops-exercise` namespace and applied the manifests:

```powershell
kubectl --context=devops-multinode apply -f .\lab-10\namespace.yaml
kubectl --context=devops-multinode apply -f .\lab-10\
kubectl --context=devops-multinode rollout status deployment/product-catalog --timeout=180s
kubectl --context=devops-multinode -n devops-exercise rollout status deployment/shopping-cart --timeout=180s
kubectl --context=devops-multinode get pods -A -l 'app in (product-catalog,shopping-cart)' -o wide
```

I put Product Catalog in `default` and Shopping Cart in `devops-exercise`. The handout's shopping-cart Service used a different namespace from its Deployment, so I corrected them to match. The Pod anti-affinity rule keeps copies of the same app on different nodes. I also added readiness checks and CPU/memory requests and limits.

Both rollouts succeeded. All five Pods were `1/1 Running` with zero restarts:

| Application | Pod suffix | Node |
| --- | --- | --- |
| Product Catalog | lmfpz | devops-multinode-m02 |
| Product Catalog | ps22b | devops-multinode-m03 |
| Shopping Cart | 569n6 | devops-multinode-m02 |
| Shopping Cart | 6zm89 | devops-multinode |
| Shopping Cart | dgqpx | devops-multinode-m03 |

I opened a separate PowerShell window for each service tunnel and left both running:

```powershell
C:\minikube\minikube.exe -p devops-multinode service product-catalog-service --url
C:\minikube\minikube.exe -p devops-multinode service shopping-cart-service -n devops-exercise --url
```

The catalog tunnel returned `http://127.0.0.1:54415` and the cart tunnel returned `http://127.0.0.1:57906`. These ports were assigned for this run and may change after restarting a tunnel.

In another PowerShell window, I tested both applications:

```powershell
curl.exe http://127.0.0.1:54415/products
curl.exe http://127.0.0.1:57906/cart
Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:57906/cart" -Method Post -ContentType "application/json" -Body '{"id":1,"name":"Laptop","quantity":1}' | Select-Object StatusCode, Content
```

The catalog returned Laptop (1200), Phone (800), and Headphones (150). The initial cart response was `[]`. Adding a Laptop returned HTTP `201` with the added item in the response.

![Product list, empty cart and successful HTTP 201 cart request](lab-10/service-tests.png)

The apps responded through their Services, and the Pod listing showed the required placement across nodes. Each cart replica keeps its own list in memory. A later request may reach another replica and show a different cart; shared storage was not part of this sample app.


### Additional screenshots

![Minikube started the control plane and two workers](lab-10/cluster-start.png)

![Completed product catalog image build](lab-10/catalog-build.png)

![Completed shopping cart image build](lab-10/cart-build.png)

![Product and cart replicas running across the three nodes](lab-10/pod-distribution.png)

## Uploading the Assignment to GitHub

After running the labs, I committed and pushed the source files, Dockerfiles, Kubernetes manifests, Jenkinsfiles, screenshots and this report from the repository folder:

```powershell
git add -A
git commit -m "Add remaining DevOps labs and update lab reports"
git push origin main
```

The push succeeded with commit `2730b3f` on `main`. I then used that GitHub commit for the successful HelloWorld and multi-stage pipeline checkout runs described in Labs 8 and 9.

Repository: [palak12-30/devOps](https://github.com/palak12-30/devOps)
