# Technical Writer's Guide to Reformatters Knowledge Base

**For**: Human technical writers continuing the documentation work
**Created**: 2026-01-15
**Status**: Active documentation project

## Executive Summary

This knowledge base has been significantly improved but needs ongoing expansion. This guide provides a structured outline for creating comprehensive documentation that helps developers quickly answer questions about the reformatters codebase.

## Current State (What's Been Done)

### ✅ Completed Content

**Guides** (6 documents):
- Getting Started Guide
- Dataset Integration Guide
- FAQ (60+ questions/answers)
- Common Errors Guide (30+ error patterns)
- CLI Cheatsheet
- Architecture Overview

**Playbooks** (5 documents):
- Backfill Failures
- AWS Credentials Errors
- Validation Failures
- Memory and Resource Issues
- Running Backfills (Operations)

**Examples** (3 code samples):
- Minimal TemplateConfig
- Minimal RegionJob
- Custom Validator

### 📊 Content Statistics

- **Total documents**: 14
- **Total lines**: ~2,800 (6x increase from original 438)
- **Guides**: 6
- **Playbooks**: 5
- **Examples**: 3

### 🎯 Current Gaps

Major areas still needing documentation (priority order):

1. **More code examples** (5-10 more needed)
2. **More operational playbooks** (10+ needed)
3. **Provider-specific guides** (one per provider)
4. **Dataset-specific documentation** (per dataset)
5. **Video tutorials/walkthroughs**
6. **Visual diagrams** (architecture, data flow)
7. **API reference** (auto-generated from code)

---

## Documentation Priorities (High to Low)

### Priority 1: Critical Operational Playbooks

These are the highest-value additions - practical guides for common tasks.

#### Operations Playbooks to Create

1. **`knowledge/playbooks/operations/deploying-new-datasets.md`**
   - Complete checklist for production deployment
   - Pre-flight checks
   - Deployment steps
   - Post-deployment validation
   - Rollback procedures

2. **`knowledge/playbooks/operations/monitoring-datasets.md`**
   - What to monitor
   - Setting up alerts
   - Dashboard recommendations
   - Response procedures

3. **`knowledge/playbooks/operations/updating-templates.md`**
   - When to update templates
   - How to version templates
   - Migration strategies
   - Testing template changes

4. **`knowledge/playbooks/operations/managing-credentials.md`**
   - Credential lifecycle
   - Rotation procedures
   - Kubernetes secrets management
   - Security best practices

5. **`knowledge/playbooks/operations/cost-optimization.md`**
   - Understanding costs
   - Reducing storage costs
   - Optimizing compute usage
   - Choosing parallelism levels

#### Troubleshooting Playbooks to Create

6. **`knowledge/playbooks/troubleshooting/networking-issues.md`**
   - DNS resolution failures
   - Timeouts
   - Connection refused errors
   - Proxy configuration

7. **`knowledge/playbooks/troubleshooting/data-corruption.md`**
   - Detecting corruption
   - Recovery procedures
   - Preventing corruption
   - Partial data loss

8. **`knowledge/playbooks/troubleshooting/template-mismatches.md`**
   - Detecting template issues
   - Fixing mismatches
   - Regenerating data
   - Version conflicts

9. **`knowledge/playbooks/troubleshooting/performance-issues.md`**
   - Slow backfills
   - Slow reads/writes
   - Network bottlenecks
   - CPU/memory inefficiencies

10. **`knowledge/playbooks/troubleshooting/kubernetes-issues.md`**
    - Pod scheduling failures
    - Node issues
    - Service account problems
    - RBAC errors

---

### Priority 2: Code Examples

Practical, copy-paste ready code examples.

#### Examples to Create

1. **`knowledge/examples/complete-dataset-integration.py`**
   - Full working example from start to finish
   - All three classes implemented
   - Comments explaining every section
   - Based on real dataset (e.g., NOAA GFS)

2. **`knowledge/examples/storage-configurations.py`**
   - LocalStorageConfig example
   - S3StorageConfig example
   - SourceCoopDatasetStorageConfig example
   - Custom storage backend example

3. **`knowledge/examples/advanced-template-config.py`**
   - Derived coordinates
   - Complex chunking strategies
   - Custom compression
   - Multiple coordinate systems

4. **`knowledge/examples/advanced-region-job.py`**
   - Parallel downloads
   - Incremental processing
   - Error handling
   - Cleanup strategies

5. **`knowledge/examples/data-transformations.py`**
   - Deaccumulation
   - Unit conversions
   - Regridding
   - Data rounding

6. **`knowledge/examples/testing-strategies.py`**
   - Unit tests for TemplateConfig
   - Integration tests for RegionJob
   - Mocking S3
   - Test fixtures

7. **`knowledge/examples/kubernetes-configs/`**
   - Job YAML examples
   - CronJob examples
   - Resource limits
   - Service accounts

---

### Priority 3: Provider-Specific Guides

One guide per data provider explaining their specific quirks.

#### Provider Guides to Create

1. **`knowledge/guides/providers/noaa-guide.md`**
   - NOAA data sources overview
   - Access patterns
   - Update schedules
   - Common issues
   - Datasets: GFS, GEFS, HRRR, NAM

2. **`knowledge/guides/providers/ecmwf-guide.md`**
   - ECMWF data access
   - API requirements
   - CDS vs. MARS
   - Datasets: ERA5, IFS

3. **`knowledge/guides/providers/dwd-guide.md`**
   - DWD data sources
   - ICON specifics
   - Rotated grids
   - Update frequency

4. **`knowledge/guides/providers/nasa-guide.md`**
   - NASA data portals
   - Authentication
   - Datasets: MERRA-2, GEOS-FP

---

### Priority 4: Conceptual Guides

Deeper explanations of concepts.

#### Conceptual Guides to Create

1. **`knowledge/guides/understanding-zarr.md`**
   - What is Zarr v3?
   - Chunks vs. shards
   - Compression options
   - Access patterns
   - When to use Zarr

2. **`knowledge/guides/chunking-strategies.md`**
   - How chunking works
   - Optimizing for time series access
   - Optimizing for spatial access
   - Chunk size calculations
   - Trade-offs

3. **`knowledge/guides/kubernetes-for-reformatters.md`**
   - Kubernetes basics
   - Jobs vs. CronJobs
   - Resource management
   - Monitoring
   - Common patterns

4. **`knowledge/guides/testing-best-practices.md`**
   - Unit testing strategies
   - Integration testing
   - Testing with real data
   - CI/CD integration
   - Test data management

5. **`knowledge/guides/security-best-practices.md`**
   - Credential management
   - IAM policies
   - Network security
   - Audit logging
   - Compliance

---

### Priority 5: Reference Documentation

#### Reference Docs to Create

1. **`knowledge/reference/template-config-api.md`**
   - Complete API reference
   - All properties
   - All methods
   - Examples for each

2. **`knowledge/reference/region-job-api.md`**
   - Complete API reference
   - Lifecycle methods
   - Helper utilities
   - Extension points

3. **`knowledge/reference/dynamical-dataset-api.md`**
   - Complete API reference
   - Configuration options
   - Deployment methods
   - Validators

4. **`knowledge/reference/cli-reference.md`**
   - Complete CLI documentation
   - All commands
   - All options
   - Output formats

5. **`knowledge/reference/environment-variables.md`**
   - All environment variables
   - Default values
   - When to set them
   - Examples

---

## Content Structure Templates

Use these templates when creating new documentation.

### Template: Troubleshooting Playbook

```markdown
# [Title] - Troubleshooting Playbook

**Category**: Troubleshooting
**Severity**: [Low/Medium/High/Critical]
**Last Updated**: [YYYY-MM-DD]

## Overview

[2-3 sentences describing the issue]

## Common Symptoms

- [Symptom 1]
- [Symptom 2]
- [Symptom 3]

## Error Examples

```
[Actual error message]
```

## Troubleshooting Steps

### Step 1: [Action]

[Description of what to do]

```bash
# Command examples
```

**What to look for**: [Expected output or signs]

### Step 2: [Action]

[Continue pattern]

## Common Solutions

### Solution 1: [Description]

[When to use this solution]

```bash
# Commands or code
```

### Solution 2: [Description]

[Alternative solution]

## Prevention

1. [How to prevent in future]
2. [Monitoring to set up]
3. [Best practices]

## Validation

[How to verify the fix worked]

```bash
# Verification commands
```

## Checklist

- [ ] [Task 1]
- [ ] [Task 2]
- [ ] [Task 3]

## Related Documentation

- [Link to related doc 1]
- [Link to related doc 2]

## Notes

[Additional context, edge cases, gotchas]
```

### Template: Operations Playbook

```markdown
# [Title] - Operations Playbook

**Category**: Operations
**Last Updated**: [YYYY-MM-DD]

## Overview

[What this playbook covers]

## Prerequisites

- [ ] [Requirement 1]
- [ ] [Requirement 2]

## Phase 1: [Phase Name]

### Step 1: [Action]

[Description]

```bash
# Commands
```

**Expected outcome**: [What should happen]

### Step 2: [Action]

[Continue pattern]

## Phase 2: [Next Phase]

[Continue with phases and steps]

## Troubleshooting

| Issue | Quick Fix |
|-------|-----------|
| [Issue] | [Solution] |

## Best Practices

### Do's
- ✅ [Do this]

### Don'ts
- ❌ [Don't do this]

## Checklist

### Pre-Operation
- [ ] [Item]

### During Operation
- [ ] [Item]

### Post-Operation
- [ ] [Item]

## Related Documentation

- [Link]
```

### Template: Code Example

```python
"""
[Title]

[2-3 sentence description of what this example demonstrates]
"""

# Imports
from reformatters.base import ...

# [Section 1]
# ============================================================================
# [Section description]
# ============================================================================

class Example:
    """[Description]"""

    def method(self):
        """
        [What this method does]

        Args:
            arg1: [Description]

        Returns:
            [Description]
        """
        # Implementation with detailed comments
        pass


# ============================================================================
# Usage Example
# ============================================================================

if __name__ == "__main__":
    """[What this usage example shows]"""

    # Step-by-step example
    pass
```

### Template: Conceptual Guide

```markdown
# [Title]

[Opening paragraph explaining what this guide covers and why it matters]

## Table of Contents

- [Section 1]
- [Section 2]

## Introduction

[More detailed introduction]

## Core Concepts

### Concept 1

[Explanation]

**Key Points:**
- [Point 1]
- [Point 2]

**Example:**
```
[Code or command example]
```

### Concept 2

[Continue pattern]

## How It Works

[Step-by-step explanation]

```
[Diagrams or ASCII art if helpful]
```

## Common Patterns

### Pattern 1: [Name]

**When to use**: [Scenario]

**How to implement**: [Steps]

**Example**:
```
[Code]
```

## Best Practices

1. **[Practice 1]**: [Description]
2. **[Practice 2]**: [Description]

## Common Pitfalls

- **Pitfall 1**: [Description and how to avoid]
- **Pitfall 2**: [Description and how to avoid]

## Advanced Topics

[Optional section for deeper content]

## Related Documentation

- [Links]
```

---

## Writing Guidelines

### General Principles

1. **Be concise**: Get to the point quickly
2. **Be specific**: Use actual commands, not placeholders when possible
3. **Be practical**: Include working examples
4. **Be thorough**: Cover edge cases and gotchas
5. **Be current**: Include last updated date

### Style Guidelines

**Do:**
- Use active voice ("Run this command" not "This command should be run")
- Use present tense ("The system does X" not "The system will do X")
- Include actual error messages
- Provide copy-paste ready commands
- Add explanatory comments to code
- Link to related documentation
- Include checklists for multi-step processes

**Don't:**
- Assume knowledge - explain jargon
- Use vague language ("might", "could", "possibly")
- Leave out error handling in examples
- Forget to test your examples
- Use outdated commands or syntax

### Code Examples Standards

```python
# ✅ Good: Clear, commented, complete
def process_data(source_file: Path) -> np.ndarray:
    """
    Process source data file and return array.

    Args:
        source_file: Path to GRIB2 file

    Returns:
        Numpy array with shape (time, lat, lon)
    """
    # Open file with xarray
    ds = xr.open_dataset(source_file, engine="cfgrib")

    # Extract variable
    data = ds["temperature_2m"].values

    # Clean up
    ds.close()

    return data
```

```python
# ❌ Bad: No comments, no types, incomplete
def process(f):
    ds = xr.open_dataset(f)
    return ds["temperature_2m"].values
```

---

## Research and Information Gathering

### Where to Find Information

1. **Existing codebase**:
   ```bash
   cd /path/to/reformatters
   # Look at actual implementations
   ls src/reformatters/noaa/gfs/forecast/
   ```

2. **GitHub Issues**: Common problems and solutions
3. **GitHub Discussions**: Design decisions and Q&A
4. **Provider documentation**: NOAA, ECMWF, etc. official docs
5. **Team members**: Interview engineers about common issues
6. **Support tickets**: Patterns in support requests

### Interview Questions for Engineers

When talking to engineers about their work:

1. "What was the hardest part of implementing [dataset]?"
2. "What do you wish you knew when you started?"
3. "What's the most common mistake you see?"
4. "What questions do new team members always ask?"
5. "What would you document differently?"

---

## Quality Checklist

Before publishing any documentation:

### Content Quality
- [ ] Technical accuracy verified (code/commands tested)
- [ ] Examples are complete and runnable
- [ ] Error messages are actual/current
- [ ] Commands use correct syntax
- [ ] Links work and point to correct locations
- [ ] Code follows project conventions

### Structure Quality
- [ ] Has clear title and metadata (category, date)
- [ ] Table of contents for docs > 200 lines
- [ ] Logical section organization
- [ ] Consistent heading hierarchy
- [ ] Checklist for multi-step processes

### Writing Quality
- [ ] Clear and concise language
- [ ] Active voice used
- [ ] Jargon explained or linked
- [ ] No spelling/grammar errors
- [ ] Code formatting consistent
- [ ] Proper markdown syntax

### Completeness
- [ ] Covers common use cases
- [ ] Includes troubleshooting section
- [ ] Links to related documentation
- [ ] Has examples or code samples
- [ ] Includes "last updated" date

---

## Contributing Workflow

### 1. Choose a Topic

Pick from priority list above or identify a gap:
```bash
# Search existing docs for coverage
grep -r "keyword" knowledge/

# List what we have
find knowledge -name "*.md" | sort
```

### 2. Research and Outline

- Gather information from sources above
- Create outline following templates
- Identify code examples needed
- Note questions for engineers

### 3. Write First Draft

- Follow templates and style guide
- Include code examples (test them!)
- Add links to related docs
- Use checklists for procedures

### 4. Review and Test

- Test all commands and code
- Verify links work
- Check for clarity
- Run through checklist above

### 5. Submit

```bash
# Create file
vim knowledge/playbooks/operations/new-playbook.md

# Test search works
# (MCP server will automatically index it)

# Commit
git add knowledge/
git commit -m "Add playbook: [title]"
git push
```

---

## Measuring Success

Track these metrics to measure documentation effectiveness:

### Quantitative Metrics
- Number of documents
- Total word count
- Search queries (if tracked)
- Time to find answers
- Support ticket reduction

### Qualitative Metrics
- Team feedback on usefulness
- Accuracy (errors found and fixed)
- Completeness (gaps identified)
- Clarity (confusion in questions)

### Goals (6 months)
- [ ] 50+ total documents
- [ ] 10,000+ words of documentation
- [ ] All common errors covered
- [ ] All operational tasks documented
- [ ] One guide per dataset
- [ ] 50% reduction in "how do I..." questions

---

## Quick Start for New Writers

Your first contribution:

1. **Pick something small**: Start with a single error message from [Common Errors](knowledge/guides/common-errors.md) that needs more detail

2. **Research it**: Find the error in code, ask engineers, test reproduction

3. **Create a playbook**: Use troubleshooting template

4. **Test it**: Walk through your own playbook

5. **Submit it**: Commit and push

**Estimated time**: 2-4 hours for first playbook

---

## Questions and Support

- **For content questions**: Ask engineering team
- **For structure questions**: Refer to templates above
- **For technical issues**: Test in actual environment
- **For priority questions**: Focus on Priority 1 items first

---

## Appendix: Document Inventory

### Current Documents

**Guides** (`knowledge/guides/`):
1. `getting-started.md` - ✅ Complete
2. `dataset-integration-guide.md` - ✅ Complete
3. `faq.md` - ✅ Complete (60+ Q&A)
4. `common-errors.md` - ✅ Complete (30+ errors)
5. `cli-cheatsheet.md` - ✅ Complete
6. `architecture/overview.md` - ✅ Complete

**Playbooks** (`knowledge/playbooks/`):
1. `troubleshooting/backfill-failures.md` - ✅ Complete
2. `troubleshooting/aws-credentials-errors.md` - ✅ Complete
3. `troubleshooting/validation-failures.md` - ✅ Complete
4. `troubleshooting/memory-and-resource-issues.md` - ✅ Complete
5. `operations/running-backfills.md` - ✅ Complete

**Examples** (`knowledge/examples/`):
1. `minimal-template-config.py` - ✅ Complete
2. `minimal-region-job.py` - ✅ Complete
3. `custom-validator.py` - ✅ Complete

### Planned Documents (High Priority)

See Priority 1 and Priority 2 sections above for next ~20 documents to create.

---

## Version History

- **v1.0** (2026-01-15): Initial technical writer's guide created
  - 14 documents completed
  - ~2,800 lines of documentation
  - Comprehensive outline for future work
  - Templates and guidelines established

---

**Remember**: The goal is to make it easy for anyone to get quick, accurate answers about reformatters. Focus on practical, tested, copy-paste ready content.

Good luck! 🚀
