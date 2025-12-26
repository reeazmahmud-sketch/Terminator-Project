# Operations Team Module

**Mission:** Maintain system stability, optimize resource usage, and ensure continuous availability.

## Agents
*   **ResourceManagerAgent:** Monitors CPU, RAM, and Disk usage; applies throttling.
*   **InfrastructureCoordinator:** Manages external services (Docker, Cloud Run).
*   **ErrorMonitorAgent:** Aggregates logs and detects system-wide failure patterns.

## Responsibilities
1.  **Health Monitoring:** Continuous telemetry collection.
2.  **Resource Optimization:** Dynamic scaling and load shedding.
3.  **Self-Healing:** Restarting crashed services and clearing caches.

## KPIs
*   **Uptime:** > 99.9%.
*   **Resource Efficiency:** CPU/RAM usage within target thresholds (e.g., < 80%).
*   **MTTR (Mean Time To Recovery):** < 30 seconds for service restarts.
