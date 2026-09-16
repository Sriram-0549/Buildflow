# BuildFlow Design Decisions

## 1. Local Kubernetes Instead of Cloud Infrastructure

The project was designed to run completely on local infrastructure
using Minikube.

This keeps the project reproducible and avoids dependence on cloud
resources.

## 2. Separate Diagnosis From Remediation

The Root Cause Engine only determines the probable cause.

The Remediation Engine is responsible for executing changes.

This prevents diagnosis logic from directly modifying infrastructure.

## 3. Human Approval Before Remediation

Potentially risky infrastructure changes require explicit approval.

This creates a safety boundary between automated diagnosis and
infrastructure modification.

## 4. Evidence-Based Root Cause Analysis

The Root Cause Engine uses structured evidence rather than generating
a diagnosis from a single metric.

Evidence may include:

- Kubernetes state
- Events
- Restart counts
- Exit codes
- Metrics
- Logs

## 5. Independent Recovery Verification

BuildFlow does not assume that a successful Kubernetes patch means
the incident has been resolved.

The Recovery Verifier independently checks workload and application
health.

## 6. Rule-Based Initial RCA

The first version uses transparent rule-based diagnosis instead of
an opaque AI model.

This makes the reasoning explainable and easy to debug.

The architecture can later support more advanced analysis.

## 7. Structured JSON Artifacts

Each stage produces machine-readable JSON data.

This allows components to remain loosely coupled and makes incident
history easier to inspect and process.
