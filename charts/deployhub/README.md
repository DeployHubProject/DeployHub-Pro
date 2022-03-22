# DeployHub Pro

Microservice Configuration Management - Track, Version, Find, Share and Deploy Microservices

[Overview of DeployHub](https://www.deployhuyb.com)

## TL;DR

```console
$ openssl genpkey -out jwt.pri -algorithm RSA -pkeyopt rsa_keygen_bits:2048
$ openssl pkey -in jwt.pri -pubout -out jwt.pub
$ helm repo add deployhub https://deployhubproject.github.io/DeployHub-Pro/
$ helm install my-release deployhub/deployhub --set dh-postgres.DBPassword=my_db_password --set dh-ms-nginx.SSLType=OFF --set dh-postgres.DBHost=deployhubdb.us-east-1.rds.amazonaws.com --set-file dh-jwt.JwtPrivateKey=jwt.pri --set-file dh-jwt.JwtPublicKey=jwt.pub
```

## Introduction

This chart deploys all of the required secrets, services, and deployments on a [Kubernetes](https://kubernetes.io) cluster using the [Helm](https://helm.sh) package manager.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- Public/Private RSA PKCS#8 Key Pair for JWT Tokens
- External Postgres Database

## Installing the Chart

To install the chart with the release name `my-release`:

```console
helm install my-release deployhub/deployhub --set dh-postgres.DBPassword=my_db_password --set dh-postgres.DBHost=deployhubdb.us-east-1.rds.amazonaws.com --set dh-ms-nginx.SSLType=OFF --set-file dh-jwt.JwtPrivateKey=jwt.pri --set-file dh-jwt.JwtPublicKey=jwt.pub
```

The command deploys DeployHub on the Kubernetes cluster using the following parameters:
- dh-postgres.DBPassword = Postgres Database Password
- dh-postgres.DBHost = Postgres Database Hostname
- dh-ms-nginx.SSLType = OFF (Disable the use of SSL certificates)
- dh-jwt.JwtPrivateKey = Private RSA PKCS#8 Key for creating the JWT Token
- dh-jwt.JwtPublicKey = Public RSA PKCS#8 Key for creating the JWT Token

> **Tip**: List all releases using `helm list`

## Uninstalling the Chart

To uninstall/delete the `my-release` deployment:

```console
helm delete my-release
```

The command removes all the Kubernetes components associated with the chart and deletes the release.

## Parameters

### Common parameters

| Name                     | Description                                                                                  | Value           |
| ------------------------ | -------------------------------------------------------------------------------------------- | --------------- |
| `kubeVersion`            | Override Kubernetes version                                                                  | `""`            |


> NOTE: Once this chart is deployed, it is not possible to change the application's access credentials, such as usernames or passwords, using Helm. To change these application credentials after deployment, delete any persistent volumes (PVs) used by the chart and re-deploy it, or use the application's built-in administrative tools if available.

Alternatively, a YAML file that specifies the values for the above parameters can be provided while installing the chart. For example,

```console
helm install my-release -f values.yaml deployhub/deployhub
```

> **Tip**: You can use the default [values.yaml](values.yaml)
