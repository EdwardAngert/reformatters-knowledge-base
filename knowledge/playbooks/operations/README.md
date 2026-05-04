# Operations Playbooks

Step-by-step guides for operational tasks.

## Available Playbooks

### Running Backfills (`running-backfills.md`)

Complete guide for running dataset backfills from planning through validation.

**Covers:**
- Planning and resource estimation
- Testing before production
- Running large backfills
- Monitoring progress
- Handling failures
- Post-backfill validation
- Setting up operational updates

**Use when:** You need to backfill historical data for a dataset

---

## Planned Playbooks

### High Priority

- **Deploying New Datasets**: Complete deployment checklist
- **Monitoring Datasets**: Setting up monitoring and alerts
- **Updating Templates**: Template versioning and migration
- **Managing Credentials**: Credential lifecycle and rotation
- **Cost Optimization**: Reducing storage and compute costs

### Additional Topics

- Disaster recovery procedures
- Scaling operations
- Multi-region deployment
- Dataset deprecation
- Performance tuning

---

## Contributing

To add an operations playbook:

1. Copy the template from `TECHNICAL_WRITER_GUIDE.md`
2. Fill in all sections with specific, tested steps
3. Include actual commands and examples
4. Add troubleshooting section
5. Test by following your own playbook
6. Submit PR

## Related Documentation

- [Troubleshooting Playbooks](../troubleshooting/)
- [Technical Writer's Guide](../../TECHNICAL_WRITER_GUIDE.md)
- [Getting Started](../../guides/getting-started.md)
