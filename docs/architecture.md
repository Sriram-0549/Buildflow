# BuildFlow Architecture

## Overview

BuildFlow is a local autonomous Kubernetes operations platform designed
to detect, investigate, diagnose, remediate, and verify Kubernetes incidents.

The platform focuses on operational automation rather than application
development.

## Core Flow

Incident Detector
        ↓
Evidence Collector
        ↓
Root Cause Engine
        ↓
Decision Engine
        ↓
Human Approval
        ↓
Remediation Engine
        ↓
Recovery Verifier
        ↓
Incident Report

## Components

### 1. Incident Detector

The Incident Detector monitors Kubernetes-related Prometheus metrics
and identifies abnormal workload conditions such as CrashLoopBackOff.

### 2. Evidence Collector

The Evidence Collector gathers operational evidence from:

- Kubernetes API
- Prometheus
- Loki

Collected information includes:

- Pod status
- Container state
- Restart count
- Exit code
- Container command and arguments
- Kubernetes events
- Prometheus metrics
- Application logs

The evidence is stored as structured JSON.

### 3. Root Cause Engine

The Root Cause Engine analyzes the collected evidence using multiple
rule-based failure scenarios.

Current rules include:

- Container startup failure
- Out-of-memory termination
- Image pull failure
- Readiness failure

Each rule produces an evidence score and reasoning.

### 4. Decision Engine

The Decision Engine converts the root cause diagnosis into an action.

Each decision contains:

- Recommended action
- Risk level
- Execution mode

The current system uses a human approval gate for remediation.

### 5. Remediation Engine

The Remediation Engine uses the Kubernetes Python client to perform
controlled changes against Kubernetes workloads.

The current test remediation patches a Deployment to correct an
invalid container startup configuration.

### 6. Recovery Verifier

The Recovery Verifier confirms whether remediation actually recovered
the workload.

It checks:

- Pod status
- Restart count stability
- Application health endpoint

Recovery is confirmed only when the required checks pass.

### 7. Incident History and Reports

BuildFlow stores incident records and generates investigation reports
containing the incident lifecycle, root cause, decision, remediation,
and recovery information.

## Technology Stack

- Python
- Flask
- Docker
- Kubernetes
- Minikube
- Prometheus
- Loki
- Kubernetes Python Client
- JSON
- YAML

## Design Principle

BuildFlow separates detection, diagnosis, decision, remediation, and
verification so that automation can be controlled and independently
validated.
