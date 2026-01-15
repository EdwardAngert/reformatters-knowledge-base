# AWS Credentials and Permissions Errors

**Category**: Troubleshooting
**Severity**: High
**Last Updated**: 2026-01-15

## Overview

This playbook helps resolve AWS credentials and permissions errors when accessing S3 buckets for source data or target storage.

## Common Symptoms

- `403 Forbidden` errors when accessing S3
- `NoCredentialsError` or `PartialCredentialsError`
- `AccessDenied` errors during upload
- `InvalidAccessKeyId` or `SignatureDoesNotMatch`

## Error Examples

```
botocore.exceptions.ClientError: An error occurred (403) when calling the HeadObject operation: Forbidden

botocore.exceptions.NoCredentialsError: Unable to locate credentials

botocore.exceptions.ClientError: An error occurred (InvalidAccessKeyId) when calling the ListObjects operation
```

## Troubleshooting Steps

### Step 1: Verify Credentials Exist

**Local Development:**
```bash
# Check AWS config
aws configure list

# Test access
aws s3 ls s3://noaa-gfs-bdp-pds/ --no-sign-request  # Public bucket
aws s3 ls s3://your-target-bucket/  # Private bucket
```

**Kubernetes:**
```bash
# Check secret exists
kubectl get secret <dataset>-aws-credentials

# View secret (base64 encoded)
kubectl get secret <dataset>-aws-credentials -o yaml

# Describe deployment
kubectl describe deployment <dataset>-update
```

### Step 2: Verify Credentials Are Valid

```bash
# Test credentials directly
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"

aws sts get-caller-identity

# Should return your account info
```

### Step 3: Check IAM Permissions

Required permissions for source data (read-only):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::source-bucket/*",
        "arn:aws:s3:::source-bucket"
      ]
    }
  ]
}
```

Required permissions for target storage (read-write):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::target-bucket/*",
        "arn:aws:s3:::target-bucket"
      ]
    }
  ]
}
```

### Step 4: Check for Regional Issues

Some S3 buckets require specific regional endpoints:

```python
# In your storage config
s3_client = boto3.client(
    's3',
    region_name='us-east-1',  # Specify region
)
```

### Step 5: Verify Anonymous Access (Public Buckets)

For public buckets like NOAA data:

```bash
# Use --no-sign-request for public data
aws s3 ls s3://noaa-gfs-bdp-pds/ --no-sign-request
```

In code:
```python
from botocore import UNSIGNED
from botocore.client import Config

s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))
```

## Common Solutions

### Solution 1: Set Up Local Credentials

```bash
# Configure AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_DEFAULT_REGION="us-east-1"
```

### Solution 2: Create Kubernetes Secret

```bash
# Create secret from literal values
kubectl create secret generic <dataset>-aws-credentials \
  --from-literal=AWS_ACCESS_KEY_ID="your-key" \
  --from-literal=AWS_SECRET_ACCESS_KEY="your-secret"

# Or from file
cat > aws-creds.env << EOF
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
EOF

kubectl create secret generic <dataset>-aws-credentials --from-env-file=aws-creds.env

# Clean up
rm aws-creds.env
```

### Solution 3: Use IAM Roles (Recommended for Production)

For pods running on AWS EKS:

```yaml
# Use IAM Roles for Service Accounts (IRSA)
apiVersion: v1
kind: ServiceAccount
metadata:
  name: reformatters-sa
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT_ID:role/ReformattersRole
```

### Solution 4: Handle Public and Private Buckets

For datasets that read public source data but write to private storage:

```python
# Source client (unsigned for public data)
source_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))

# Target client (signed with credentials)
target_client = boto3.client('s3')
```

## Prevention

1. **Use IAM roles** instead of access keys when possible
2. **Rotate credentials** regularly
3. **Use separate credentials** for read vs. write operations
4. **Set up least-privilege permissions** per dataset
5. **Test credentials** before starting large backfills

## Validation

After fixing credentials:

```bash
# Test source access
aws s3 ls s3://source-bucket/path/to/data/

# Test target access
echo "test" > test.txt
aws s3 cp test.txt s3://target-bucket/test/
aws s3 rm s3://target-bucket/test/test.txt
rm test.txt

# Run a small backfill
uv run main <dataset-id> backfill-local <date> --filter-variable-names <var>
```

## Related Documentation

- [Getting Started Guide](../../guides/getting-started.md)
- [Deployment Guide](../../guides/dataset-integration-guide.md)
- [Backfill Failures Playbook](backfill-failures.md)

## Notes

- NOAA, ECMWF, and other public datasets typically don't require credentials for reading
- Always use IAM roles in production instead of hardcoded keys
- Different storage backends may require different credential formats
