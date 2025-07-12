# 🛠️ EKS Cluster and ALB Controller Installation Guide

This guide provides step-by-step instructions to create an EKS cluster and install the AWS ALB Ingress Controller.

---

## 🚀 EKS Cluster Creation

### Step 1: Create EKS Cluster (Without Node Group)

```bash
eksctl create cluster --name=eks-cluster \
                      --region=us-east-1 \
                      --version=1.30 \
                      --without-nodegroup
```

Step 2: Associate IAM OIDC Provider
```bash
eksctl utils associate-iam-oidc-provider \
    --region us-east-1 \
    --cluster eks-cluster \
    --approve
```
Step 3: Create Managed Node Group
```bash
eksctl create nodegroup --cluster=eks-cluster \
                       --region=us-east-1 \
                       --name=eks-cluster \
                       --node-type=t2.medium \
                       --nodes=1 \
                       --nodes-min=1 \
                       --nodes-max=2 \
                       --node-volume-size=29 \
                       --ssh-access \
                       --ssh-public-key=EC2-Connect-ramya
```
Step 4: Update Kubeconfig
```bash
aws eks update-kubeconfig --region us-east-1 --name eks-cluster
```

🌐 ALB Ingress Controller Installation
Step 1: Download IAM Policy

```bash
curl -O https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.11.0/docs/install/iam_policy.json
```

✏️ Important: Before proceeding, edit the downloaded iam_policy.json file and add the following permission to the "Action" array in the existing policy:

```json
"ec2:DescribeRouteTables"
```

Save the file after editing.

Step 2: Create IAM Policy
```bash
aws iam create-policy \
    --policy-name AWSLoadBalancerControllerIAMPolicy \
    --policy-document file://iam_policy.json
```

Step 3: Create IAM Service Account
⚠️ Note: Before creating the service account, check the AWS CloudFormation console and delete any existing stacks created by previous ALB add-ons to avoid resource conflicts.

```bash
eksctl create iamserviceaccount \
  --cluster=eks-cluster \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --role-name AmazonEKSLoadBalancerControllerRole \
  --attach-policy-arn=arn:aws:iam::515966510834:policy/AWSLoadBalancerControllerIAMPolicy \
  --approve \
  --override-existing-serviceaccounts
```

Step 4:Install Helm
```bash

curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm
```

Step 5: Add Helm Repo
```bash
helm repo add eks https://aws.github.io/eks-charts
helm repo update eks
```

Step 6: Install ALB Controller (Update VPC ID)
```bash
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=eks-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller \
  --set region=us-east-1 \
  --set vpcId=vpc-0d3cb48c85bdfaf04
```

🔁 Replace vpc-0d3cb48c85bdfaf04 with your actual VPC ID.

Step 7: Verify Controller Deployment
```bash
kubectl get deployment -n kube-system aws-load-balancer-controller
```
✅ Setup Complete
You now have a fully functional EKS cluster with the AWS ALB Ingress Controller ready to manage external traffic!

---

Delete eks cluster:
```bash
eksctl delete cluster --name eks-cluster --region us-east-1
```




