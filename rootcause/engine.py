import json


# ==========================================
# LOAD EVIDENCE
# ==========================================

with open("evidence/evidence.json", "r") as file:
    evidence = json.load(file)


# ==========================================
# EXTRACT EVIDENCE
# ==========================================

pod = evidence.get("pod", {})
container = pod.get("container", {})

state = container.get("state")
reason = container.get("reason")
exit_code = container.get("last_exit_code")

restart_count = container.get("restart_count", 0)

command = pod.get("command")
args = pod.get("args")

events = evidence.get("events", [])


# ==========================================
# ROOT CAUSE CANDIDATES
# ==========================================

candidates = []


# ==========================================
# RULE 1 — STARTUP FAILURE
# ==========================================

score = 0
reasoning = []


if reason == "CrashLoopBackOff":
    score += 20
    reasoning.append(
        "Container is in CrashLoopBackOff"
    )


if exit_code == 1:
    score += 25
    reasoning.append(
        "Container exited with code 1"
    )


if args and "exit 1" in args:
    score += 30
    reasoning.append(
        "Container startup arguments explicitly contain 'exit 1'"
    )


for event in events:

    if event.get("reason") == "BackOff":
        score += 15
        reasoning.append(
            "Kubernetes reported repeated container restart backoff"
        )
        break


if score > 0:

    candidates.append({
        "root_cause": "Container startup process is failing",
        "score": score,
        "reasoning": reasoning
    })


# ==========================================
# RULE 2 — OOM
# ==========================================

score = 0
reasoning = []


if reason == "OOMKilled":

    score += 70

    reasoning.append(
        "Kubernetes reported OOMKilled"
    )


if reason == "OOMKilled" and restart_count > 3:

    score += 20

    reasoning.append(
        "Container has restarted repeatedly after memory termination"
    )


if score > 0:

    candidates.append({
        "root_cause": "Container exceeded its memory limit",
        "score": score,
        "reasoning": reasoning
    })


# ==========================================
# RULE 3 — IMAGE PULL FAILURE
# ==========================================

score = 0
reasoning = []


if reason == "ImagePullBackOff":

    score += 70

    reasoning.append(
        "Container is in ImagePullBackOff"
    )


for event in events:

    event_reason = event.get("reason", "")

    if event_reason in ["Failed", "ErrImagePull"]:

        score += 20

        reasoning.append(
            "Kubernetes reported an image retrieval failure"
        )

        break


if score > 0:

    candidates.append({
        "root_cause": "Container image could not be pulled",
        "score": score,
        "reasoning": reasoning
    })


# ==========================================
# RULE 4 — READINESS FAILURE
# ==========================================

score = 0
reasoning = []


if reason == "CrashLoopBackOff":

    # Look for readiness-related events

    for event in events:

        message = event.get("message", "").lower()

        if "readiness" in message:

            score += 60

            reasoning.append(
                "Kubernetes reported a readiness-related failure"
            )

            break


if score > 0:

    candidates.append({
        "root_cause": "Application is failing its readiness check",
        "score": score,
        "reasoning": reasoning
    })


# ==========================================
# SELECT BEST ROOT CAUSE
# ==========================================

if candidates:

    candidates.sort(
        key=lambda candidate: candidate["score"],
        reverse=True
    )

    best = candidates[0]

    confidence = min(best["score"], 100)

    result = {
        "root_cause": best["root_cause"],
        "confidence": confidence,
        "reasoning": best["reasoning"],
        "candidates": candidates
    }

else:

    result = {
        "root_cause": "Unknown",
        "confidence": 0,
        "reasoning": [
            "No known root-cause rule matched the available evidence"
        ],
        "candidates": []
    }


# ==========================================
# DISPLAY RESULT
# ==========================================

print("\n========================================")
print("        ROOT CAUSE ANALYSIS")
print("========================================")

print(
    json.dumps(
        result,
        indent=4
    )
)

with open("rootcause/result.json", "w") as file:
    json.dump(result, file, indent=4)
