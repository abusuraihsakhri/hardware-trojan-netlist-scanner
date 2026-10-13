"use strict";

/**
 * Deterministic record-triage rules matching agents/workers.py.
 * These rules classify supplied metrics; they do NOT parse HDL or detect Trojans.
 */
function evaluateRecord(record) {
  const primary = Number(record.primary_metric);
  const secondary = Number(record.secondary_metric);
  if (record.primary_metric === null || record.secondary_metric === null ||
      typeof record.primary_metric === "boolean" || typeof record.secondary_metric === "boolean" ||
      String(record.primary_metric).trim() === "" || String(record.secondary_metric).trim() === "" ||
      !Number.isFinite(primary) || !Number.isFinite(secondary)) {
    throw new Error("Both metrics must be finite numbers.");
  }
  const taskId = String(record.task_id || "").trim();
  const targetId = String(record.target_identifier || "").trim();
  if (!taskId || !targetId) {
    throw new Error("Task ID and target identifier are required.");
  }
  const descriptor = String(record.status_descriptor || "");
  const critical = record.is_critical_flag === true;
  const alerts = [];
  function add(origin, urgency, summary, details, action) {
    alerts.push({
      origin_worker: origin,
      urgency,
      summary,
      technical_details: details,
      actionable_remediation: action
    });
  }
  if (primary > 25) {
    add("InvariantQCWorker", "ELEVATED_RISK",
      "Primary Metric Threshold Exceeded",
      `Primary measurement (${primary.toFixed(2)}) exceeds upper reference limit (25.00).`,
      "Review the supplied metric and its threshold.");
  }
  if (secondary > 12 || critical) {
    add("SafetyEscalationWorker", critical ? "CRITICAL_STAT_PANIC" : "ELEVATED_RISK",
      "Critical Safety Interlock Triggered",
      `CriticalFlag=${critical} with secondary index ${secondary.toFixed(2)}.`,
      "Review the critical flag and secondary metric.");
  }
  if (["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"]
      .some(word => descriptor.toUpperCase().includes(word))) {
    add("ProtocolConformanceWorker", "ELEVATED_RISK",
      "Protocol Conformance Discordance Detected",
      `Descriptor '${descriptor}' matches an alert keyword.`,
      "Review the descriptor and source record.");
  }
  const criticalCount = alerts.filter(a => a.urgency === "CRITICAL_STAT_PANIC").length;
  const overall = criticalCount ? "CRITICAL_STAT_PANIC" :
    alerts.length ? "ELEVATED_RISK" : "ROUTINE";
  return {
    evaluation_mode: "LOCAL_DETERMINISTIC_METRIC_TRIAGE",
    task_id: taskId,
    target_identifier: targetId,
    overall_urgency: overall,
    integrity_status: criticalCount ? "RECALIBRATION_REQUIRED" :
      alerts.length ? "DISCORDANT_ANOMALY" : "VALIDATED_OPTIMAL",
    total_alerts: alerts.length,
    critical_alerts_count: criticalCount,
    alerts,
    note: "Heuristic metric classification only. Not a hardware Trojan detection or HDL verification result."
  };
}

if (typeof document !== "undefined") {
  let count = 0;
  let alertCount = 0;
  let lastResult = null;
  const get = id => document.getElementById(id);
  const output = get("outputConsole");
  const form = get("audit-form");
  const download = get("download");
  form.addEventListener("submit", event => {
    event.preventDefault();
    try {
      const result = evaluateRecord({
        task_id: get("task_id").value,
        target_identifier: get("target_id").value,
        primary_metric: get("primary_metric").value,
        secondary_metric: get("secondary_metric").value,
        status_descriptor: get("status_descriptor").value,
        is_critical_flag: get("is_critical").checked
      });
      lastResult = result;
      count += 1;
      alertCount += result.total_alerts;
      get("m-tasks").textContent = String(count);
      get("m-audit").textContent = String(alertCount);
      get("m-status").textContent = result.overall_urgency === "ROUTINE" ? "ROUTINE" :
        result.overall_urgency === "ELEVATED_RISK" ? "ELEVATED" : "CRITICAL";
      output.textContent = JSON.stringify(result, null, 2);
      download.disabled = false;
    } catch (error) {
      lastResult = null;
      download.disabled = true;
      output.textContent = "Input error: " + error.message;
      get("m-status").textContent = "INVALID";
    }
  });
  download.addEventListener("click", () => {
    if (!lastResult) return;
    const blob = new Blob([JSON.stringify(lastResult, null, 2) + "\n"], {type: "application/json"});
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "metric-triage-report.json";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  });
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = {evaluateRecord};
}
