# Security Team Module

**Mission:** Protect the system and user data through active monitoring, risk assessment, and policy enforcement.

## Agents
*   **RiskAssessmentAgent:** Evaluates the danger level of proposed actions (e.g., `rm -rf`).
*   **FileSystemGuardian:** Monitors file access patterns for unauthorized changes.
*   **InfiniteLoopGuardian:** Detects and terminates runaway processes.

## Responsibilities
1.  **Pre-Execution Screening:** Governance checks on all sensitive commands.
2.  **Runtime Monitoring:** Watching for anomalies in file I/O and process behavior.
3.  **Incident Response:** Auto-blocking malicious actions and logging audits.

## KPIs
*   **Detection Rate:** 100% of high-risk commands flagged.
*   **False Positive Rate:** < 1%.
*   **Response Time:** < 10ms for blocking action.
