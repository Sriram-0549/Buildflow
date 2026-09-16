# BuildFlow Testing

## End-to-End Test Scenario

### Failure Injection

A controlled CrashLoopBackOff condition was introduced in the
crash-test Deployment using:

command: ["sh", "-c"]
args: ["exit 1"]

### Detection

The Incident Detector identified the failing Pod using the actual
CrashLoopBackOff state.

### Evidence Collection

The Evidence Collector captured:

- CrashLoopBackOff state
- Restart count
- Exit code 1
- Startup command
- Startup arguments
- BackOff event
- Prometheus restart metric

### Root Cause Analysis

The Root Cause Engine identified:

Container startup process is failing

Evidence score:

90

### Decision

The Decision Engine selected:

Action:
Inspect and correct container startup configuration

Risk:
Medium

Mode:
Human approval

### Remediation

After approval, the Remediation Engine patched the Kubernetes
Deployment and removed the invalid startup override.

### Recovery Verification

The Recovery Verifier confirmed:

- Pod Running
- Restart count stable
- `/health` returned HTTP 200
- Response was `healthy`

### Final Result

Recovery confirmed and the incident was recorded as resolved.
