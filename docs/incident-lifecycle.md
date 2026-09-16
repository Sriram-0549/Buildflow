# BuildFlow Incident Lifecycle

## Incident Lifecycle

BuildFlow follows a closed-loop incident handling process:

Detect → Investigate → Diagnose → Decide → Approve → Remediate → Verify → Record

## 1. Detect

Prometheus metrics are queried to identify abnormal Kubernetes workload
conditions.

Example:

CrashLoopBackOff detected for a crash-test Pod.

## 2. Investigate

The Evidence Collector gathers:

- Pod state
- Container status
- Restart count
- Exit code
- Commands and arguments
- Kubernetes events
- Prometheus metrics
- Loki logs

## 3. Diagnose

The Root Cause Engine evaluates multiple rules and generates possible
root causes with evidence scores and reasoning.

Example:

Container startup process is failing
Confidence: 90

## 4. Decide

The Decision Engine determines the recommended response.

Example:

Action: Inspect and correct container startup configuration
Risk: Medium
Mode: Human approval

## 5. Approve

The remediation is not executed blindly.

A human approval gate determines whether the proposed action can be
executed.

## 6. Remediate

The Remediation Engine uses the Kubernetes API to apply the approved
change.

## 7. Verify

The Recovery Verifier checks:

- Pod is Running
- Restart count remains stable
- Application health endpoint returns HTTP 200 and healthy

## 8. Record

The complete incident lifecycle is stored in an investigation report.

## Example Incident

CrashLoopBackOff
    ↓
Evidence collected
    ↓
Startup failure diagnosed
    ↓
Startup remediation selected
    ↓
Human approval
    ↓
Deployment patched
    ↓
Pod recovered
    ↓
Recovery confirmed
    ↓
Incident resolved
