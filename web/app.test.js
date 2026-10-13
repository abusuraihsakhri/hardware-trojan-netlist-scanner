"use strict";

const {test} = require("node:test");
const assert = require("node:assert/strict");
const {evaluateRecord} = require("./app.js");

const base = {
  task_id: "T-1",
  target_identifier: "NET-1",
  primary_metric: 5,
  secondary_metric: 3,
  status_descriptor: "NOMINAL",
  is_critical_flag: false
};

test("nominal input returns routine with no alerts", () => {
  const result = evaluateRecord(base);
  assert.equal(result.overall_urgency, "ROUTINE");
  assert.equal(result.total_alerts, 0);
});

test("threshold boundaries are strict", () => {
  const result = evaluateRecord({...base, primary_metric: 25, secondary_metric: 12});
  assert.equal(result.total_alerts, 0);
});

test("primary, secondary, descriptor rules each raise one elevated alert", () => {
  const result = evaluateRecord({...base, primary_metric: 25.1, secondary_metric: 12.1, status_descriptor: "ANOMALY"});
  assert.equal(result.total_alerts, 3);
  assert.equal(result.overall_urgency, "ELEVATED_RISK");
});

test("critical flag dominates overall classification", () => {
  const result = evaluateRecord({...base, is_critical_flag: true});
  assert.equal(result.overall_urgency, "CRITICAL_STAT_PANIC");
  assert.equal(result.critical_alerts_count, 1);
});

test("blank and nonfinite metrics and identifiers fail closed", () => {
  for (const input of [
    {...base, primary_metric: ""},
    {...base, secondary_metric: "Infinity"},
    {...base, primary_metric: "abc"},
    {...base, task_id: "   "}
  ]) {
    assert.throws(() => evaluateRecord(input));
  }
});
