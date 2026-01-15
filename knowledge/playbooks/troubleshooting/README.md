# Troubleshooting Playbooks

Diagnostic and resolution guides for common problems.

## Available Playbooks

### Backfill Failures (`backfill-failures.md`)

Diagnose and resolve common backfill failures.

**Common Issues:**
- Job failures
- Download errors
- Memory issues
- Timeout errors
- Data validation failures

---

### AWS Credentials Errors (`aws-credentials-errors.md`)

Resolve AWS credentials and permissions errors.

**Common Errors:**
- 403 Forbidden
- NoCredentialsError
- AccessDenied
- InvalidAccessKeyId

---

### Validation Failures (`validation-failures.md`)

Troubleshoot dataset validation failures.

**Common Failures:**
- Stale data
- Recent NaN values
- Missing shards
- Incorrect metadata

---

### Memory and Resource Issues (`memory-and-resource-issues.md`)

Address out-of-memory, CPU, and disk space issues.

**Common Problems:**
- OOMKilled pods
- MemoryError
- Disk full
- Job timeouts
- CPU throttling

---

## Planned Playbooks

### High Priority

- **Networking Issues**: DNS, timeouts, connectivity
- **Data Corruption**: Detection and recovery
- **Template Mismatches**: Version conflicts
- **Performance Issues**: Slow operations
- **Kubernetes Issues**: Pod and node problems

### Additional Topics

- Source data unavailability
- Storage backend issues
- Permission problems
- Configuration errors
- Integration issues

---

## Quick Troubleshooting

### General Debugging Steps

1. **Check logs**:
   ```bash
   kubectl logs <pod-name>
   ```

2. **Check pod status**:
   ```bash
   kubectl describe pod <pod-name>
   ```

3. **Check recent events**:
   ```bash
   kubectl get events --sort-by='.lastTimestamp'
   ```

4. **Test locally**:
   ```bash
   uv run main <dataset-id> backfill-local <date>
   ```

### Common Error → Playbook Map

| Error Type | See Playbook |
|------------|--------------|
| 403 Forbidden | AWS Credentials Errors |
| OOMKilled | Memory and Resource Issues |
| Validation failed | Validation Failures |
| Download failed | Backfill Failures |
| Timeout | Memory and Resource Issues |
| Missing data | Validation Failures |

---

## Contributing

To add a troubleshooting playbook:

1. Identify a common problem
2. Document symptoms and error messages
3. Create step-by-step troubleshooting process
4. Include actual solutions that work
5. Add prevention tips
6. Test by reproducing and solving the issue
7. Submit PR

Use the template from `TECHNICAL_WRITER_GUIDE.md`.

---

## Related Documentation

- [Common Errors Guide](../../guides/common-errors.md)
- [FAQ](../../guides/faq.md)
- [Operations Playbooks](../operations/)
