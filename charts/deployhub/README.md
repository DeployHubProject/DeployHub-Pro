# DeployHub Pro

![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/DeployHubProject/DeployHub-Pro)

DeployHub is a central evidence store of all your security and DevOps intelligence. It provides comprehensive, end-to-end insights across all of your clusters and logical applications from a single dashboard. Centrally view microservice and application level SBOMs, CVEs, deployed inventory, application to microservice dependencies, impact analysis, application versions, and the use of open-source packages across the entire organization.


[Overview of DeployHub](https://www.deployhub.com)
[Documentation](https://docs.deployhub.com)

## Additional Information

This chart deploys all of the required secrets, services, and deployments on a [Kubernetes](https://kubernetes.io) cluster using the [Helm](https://helm.sh) package manager.

## Prerequisites

* Kubernetes 1.19+
* Helm 3.2.0+

## Installing on Kind Cluster

1. Cluster Config - cluster.yaml

    ```yaml
    kind: Cluster
    apiVersion: kind.x-k8s.io/v1alpha4
    nodes:
    - role: control-plane
      kubeadmConfigPatches:
      - |
        kind: InitConfiguration
        nodeRegistration:
          kubeletExtraArgs:
            node-labels: "ingress-ready=true"
      extraPortMappings:
      - containerPort: 80
        hostPort: 80
        protocol: TCP
      - containerPort: 443
        hostPort: 443
        protocol: TCP
      extraMounts:
      - hostPath: /tmp/postgres
        containerPath: /pgdata
    ```

2. Create the cluster

    ```console
    mkdir /tmp/postgres
    kind create cluster --config cluster.yaml -n deployhub
    ```

3. Connect to the cluster

    ```kubectl cluster-info --context kind-deployhub```

4. Install DeployHub

    a. Using the internal Postgres database:

    ```console
    DEPLOYHUB_VERSION=10.0.335
    helm repo add deployhub https://deployhubproject.github.io/DeployHub-Pro/
    helm repo update
    helm upgrade --install my-release deployhub/deployhub --set dh-ms-general.dbpass=my_db_password --set global.postgresql.enabled=true  --set global.nginxController.enabled=true  --version "${DEPLOYHUB_VERSION}" --namespace deployhub --create-namespace
    ```

    > Note: This will install DeployHub persisting the Postgres data on the host system in /tmp/postgres

    b. Using the external Postgres database:

    ```console
    DEPLOYHUB_VERSION=10.0.335
    helm repo add deployhub https://deployhubproject.github.io/DeployHub-Pro/
    helm repo update
    helm upgrade --install my-release deployhub/deployhub --set dh-ms-general.dbpass=my_db_password --set dh-ms-general.dbuser=postgres --set dh-ms-general.dbhost=postgres.hosted.com --set-string dh-ms-general.dbport=5432 --set global.nginxController.enabled=true  --version "${DEPLOYHUB_VERSION}" --namespace deployhub --create-namespace
    ```

5. Access DeployHub UI

    ```http://localhost/dmadminweb/Home```

    > Note: default userid/pass is admin/admin

## Installing on Kubernetes on KillerCoda

1. Login to KillerCoda Kubernetes 1.27 Playground

2. Create the database storage directory

    ```console
    mkdir /tmp/postgres
    ```

3. Install DeployHub

    a. Using the internal Postgres database:

    ```console
    DEPLOYHUB_VERSION=10.0.335
    helm repo add deployhub https://deployhubproject.github.io/DeployHub-Pro/
    helm repo update
    helm upgrade --install my-release deployhub/deployhub --set dh-ms-general.dbpass=my_db_password --set global.postgresql.enabled=true --set dh-ms-nginx.ingress.nodePort=30000 --version "${DEPLOYHUB_VERSION}" --namespace deployhub --create-namespace
    ```

    > Note: This will install DeployHub persisting the Postgres data on the host system in /tmp/postgres

    b. Using the external Postgres database:

    ```console
    DEPLOYHUB_VERSION=10.0.335
    helm repo add deployhub https://deployhubproject.github.io/DeployHub-Pro/
    helm repo update
    helm upgrade --install my-release deployhub/deployhub --set dh-ms-general.dbpass=my_db_password --set dh-ms-general.dbuser=postgres --set dh-ms-general.dbhost=postgres.hosted.com --set-string dh-ms-general.dbport=5432 --set dh-ms-nginx.ingress.nodePort=30000  --version "${DEPLOYHUB_VERSION}" --namespace deployhub --create-namespace
    ```

4. Access DeployHub UI

    In Killercoda UI for your session, click on the 3 bars by your "Time Left", then "Traffic/Ports".  Enter in 30000 in the custom ports and then access the custom port.  This will start a new browser tab with DeployHub home page.  Use admin/admin to login.

## Installing on Google GKE

1. Generate Access keys for CLI, SDK, & API access

   * [Install gcloud](https://cloud.google.com/sdk/docs/install-sdk)
   * Set your gcloud config (Refer to [gcloud documentation](https://cloud.google.com/sdk/gcloud/reference/config/set) for how-to)

      ```toml
      [compute]
      zone = "us-central1-c"
      [container]
      cluster = "deployhub"
      [core]
      disable_usage_reporting = false
      project = "deployhub-sandbox"
      ```

2. Setup Environment Variables

   ```console
   CLUSTER_NAME=deployhub
   SERVICE_ACCOUNT=deployhub-k8s@deployhub-sandbox.iam.gserviceaccount.com
   PROJECT=deployhub-sandbox
   ```

3. Create the Cluster

   ```console
   gcloud container clusters create ${CLUSTER_NAME} --logging=SYSTEM,API_SERVER --num-nodes=3 --enable-autoupgrade --machine-type=e2-standard-2 --region=us-central1 --preemptible --service-account=${SERVICE_ACCOUNT}
   ```

4. Set kubectl config access

   ```console
   gcloud container clusters get-credentials ${CLUSTER_NAME} --zone=us-central1-c
   ```

5. Install DeployHub

    a. Using the external Postgres database:

    ```console
    DEPLOYHUB_VERSION=10.0.335
    DEPLOYHUB_DNSNAME=deployhub.example.com
    helm repo add deployhub https://deployhubproject.github.io/DeployHub-Pro/
    helm repo update
    helm upgrade --install my-release deployhub/deployhub --set dh-ms-general.dbpass=my_db_password --set dh-ms-general.dbuser=postgres --set dh-ms-general.dbhost=postgres.hosted.com --set-string dh-ms-general.dbport=5432 --set dh-ms-nginx.ingress.type=glb --set dh-ms-nginx.ingress.dnsname=${DEPLOYHUB_DNSNAME} --version "${DEPLOYHUB_VERSION}" --namespace deployhub --create-namespace
    ```

6. Access DeployHub UI

    ```https://${DEPLOYHUB_DNSNAME}/dmadminweb/Home```

    > Note: default userid/pass is admin/admin

## Installing on AWS EKS

1. Generate Access keys for CLI, SDK, & API access

   * [Create Access Key](https://us-east-1.console.aws.amazon.com/iam/home?region=us-east-1#/security_credentials)
      * `aws configure`
         * Set `AWS Access Key ID`
         * Set `AWS Secret Access Key`
         * Set `Default region name`

2. [Install eksctl](https://docs.aws.amazon.com/eks/latest/userguide/eksctl.html)

3. Setup Environment Variables

   ```console
   DEPLOYHUB_VERSION=10.0.335
   CLUSTER_NAME=deployhub
   ```

4. Create the Cluster

   ```bash
   cat <<EOF | eksctl create cluster -f -
   ---
   apiVersion: eksctl.io/v1alpha5
   kind: ClusterConfig
   metadata:
     name: ${CLUSTER_NAME}
     region: us-east-1
   cloudWatch:
     clusterLogging:
       enableTypes:
         - audit
         - authenticator
   managedNodeGroups:
     - name: ng-1
       amiFamily: AmazonLinux2
       instanceSelector:
         cpuArchitecture: x86_64
         memory: 2GiB
         vCPUs: 2
       instanceTypes:
         - t3.small
         - t3a.small
   iam:
     withOIDC: true
   addons:
     - name: aws-ebs-csi-driver
       version: v1.13.0-eksbuild.3
       attachPolicyARNs:
         - arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy
   EOF
   ```

5. Install DeployHub

    a. Using the external Postgres database:

    ```console
    DEPLOYHUB_VERSION=10.0.335
    DEPLOYHUB_DNSNAME=deployhub.example.com
    helm repo add deployhub https://deployhubproject.github.io/DeployHub-Pro/
    helm repo update
    helm upgrade --install my-release deployhub/deployhub --set dh-ms-general.dbpass=my_db_password --set dh-ms-general.dbuser=postgres --set dh-ms-general.dbhost=postgres.hosted.com --set-string dh-ms-general.dbport=5432 --set dh-ms-nginx.ingress.type=alb --set dh-ms-nginx.ingress.dnsname=${DEPLOYHUB_DNSNAME} --set-string 'dh-ms-nginx.ingress.alb_subnets=subnet-08c2def0d12544e2fd4\,subnet-0ff7730f35433930b32' --set-string 'dh-ms-nginx.ingress.alb_certificate_arn=arn\:aws\:acm\:us-east-1\:850343264173\:certificate\/8c2cb138-0172-477c-afb7-1d444eba2ec5' --version "${DEPLOYHUB_VERSION}" --namespace deployhub --create-namespace
    ```

6. Access DeployHub UI

    ```https://${DEPLOYHUB_DNSNAME}/dmadminweb/Home```

    > Note: default userid/pass is admin/admin

## Parameters

### Common parameters

| Name                | Description                 | Value       |
|---------------------|-----------------------------|-------------|
| `dh-ms-general.dbuser` | Postgres Database User Name | `postgres`  |
| `dh-ms-general.dbpass` | Postgres Database Password  | `postgres`  |
| `dh-ms-general.dbname` | Postgres Database Name      | `postgres`  |
| `dh-ms-general.dbhost` | Postgres Database Host Name | `localhost` |
| `dh-ms-general.dbport` | Postgres Database Port      | `5432`      |
| `dh-ms-nginx.ingress.type` | default nginx ingress,  AWS Load Balancer or Google Load Balancer | `ssloff, alb, glb, k3s` | `ssloff`  |
| `dh-ms-nginx.ingress.nodePort` | set the nodePort to access the service | >= 30000 | default is random port number  |
| `dh-ms-nginx.ingress.alb_subnets`    | String of comma delimited subnets for the ALB - required when  `dh-ms-nginx.ingress.type=alb`  |   |
| `dh-ms-nginx.ingress.alb_certificate_arn`    | ARN for the certificate from AWS Certificate Manager - required when  `dh-ms-nginx.ingress.type=alb` |  |
| `dh-ms-nginx.ingress.dnsname`   | DNS Name that matches the certificate from AWS Certificate Manager - required when  `dh-ms-nginx.ingress.type=alb` or `dh-ms-nginx.ingress.type=glb` |  |
| `dh-ms-nginx.ingress.scheme`    | ALB scheme - required when  `dh-ms-nginx.ingress.type=alb` |  `internal` or `internet-facing`  | `internal`|

> NOTE: Once this chart is deployed, it is not possible to change the application's access credentials, such as usernames or passwords, using Helm. To change these application credentials after deployment, delete any persistent volumes (PVs) used by the chart and re-deploy it, or use the application's built-in administrative tools if available.

Alternatively, a YAML file that specifies the values for the above parameters can be provided while installing the chart. For example,

```console
helm install my-release -f values.yaml deployhub/deployhub
```

## Accessing the DeployHub UI After the Chart Install using Port Forwarding

> Note: default userid/pass is admin/admin

* Use a port forward with kubectl to the dh-ms-nginx microservice service
* `kubectl port-forward TYPE/NAME [options] LOCAL_PORT:REMOTE_PORT`
* kubectl port-forward help

    ```console
    kubectl port-forward -h
    ```

* 8080 represents the local port on your machine `http://localhost:8080`

    ```console
    kubectl port-forward svc/dh-ms-nginx 8080:80 -n deployhub
    ```

- 8443 represents the local port on your machine `http://localhost:8443`

    ```console
    kubectl port-forward svc/dh-ms-nginx 8443:443 -n deployhub
    ```

## Uninstalling the Chart

To uninstall/delete the `my-release` deployment:

```console
helm delete my-release
    ```

The command removes all the Kubernetes components associated with the chart and deletes the release.
