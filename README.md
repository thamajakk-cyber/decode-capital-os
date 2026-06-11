# Decode Capital OS

**Project:** Captain Mod SMC Pro Max
**Owner:** thamajakk-cyber
**Status:** Foundation — GitHub Verified

---

## Purpose

Decode Capital OS is the operating system for the Captain Mod SMC Pro Max project.
This repository is the **source of truth** for all project documentation, infrastructure,
prompts, SOPs, and audit evidence.

## Governance Rules

### Evidence First
Every conclusion must include evidence. No exceptions.

| Rule | Standard |
|------|----------|
| NO EVIDENCE | = FAIL |
| NO VERIFICATION | = FAIL |
| NO ASSUMPTION | = FAIL |
| NO FAKE PASS | = FAIL |

### Installation Control
No component is installed without passing its readiness gate.
Readiness gates require verified evidence from all prerequisite phases.

---

## Repository Structure

```
decode-capital-os/
├── /docs/              # Architecture docs, runbooks, ADRs
├── /prompts/           # AI prompt templates and versions
├── /sops/              # Standard Operating Procedures
├── /infrastructure/    # IaC, server configs, networking
├── /docker/            # Dockerfiles, docker-compose configs
├── /hermes/            # Hermes Agent configs, skills, plugins
├── /knowledge/         # Knowledge base, wikis, references
├── /audits/            # Audit reports with evidence
├── /evidence/          # Evidence artifacts
├── README.md           # This file
└── .gitignore          # Git ignore rules
```

---

**CAPTAIN MOD SMC PRO MAX — Evidence First. Always.**
