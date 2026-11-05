#!/usr/bin/env node
/**
 * Compare a Lighthouse JSON report with lighthouse-budget.json.
 *
 * Lighthouse 13 no longer exposes the old `--budget-path`/`--assert` CLI
 * combination, so the budget is evaluated here. Sizes in the budget file are
 * KiB, timings are milliseconds, and cumulative layout shift is unitless.
 */
import { readFileSync } from "node:fs";

const reportPath = process.argv[2] ?? "lighthouse-report.json";
const budgetPath = process.argv[3] ?? "lighthouse-budget.json";

const report = JSON.parse(readFileSync(reportPath, "utf8"));
const budgets = JSON.parse(readFileSync(budgetPath, "utf8"));
const budget = budgets[0];

const resourceItems = report.audits?.["resource-summary"]?.details?.items ?? [];
const resourceByType = new Map(
  resourceItems.map((item) => [item.resourceType, item]),
);
const thirdPartyCount =
  report.audits?.["third-party-summary"]?.details?.items?.length ?? 0;

const failures = [];
const rows = [];

for (const entry of budget.resourceSizes ?? []) {
  const item = resourceByType.get(entry.resourceType);
  const actualKb = item ? Math.round(item.transferSize / 1024) : 0;
  rows.push(
    `size ${entry.resourceType}: ${actualKb} KiB (budget ${entry.budget} KiB)`,
  );
  if (actualKb > entry.budget) {
    failures.push(
      `${entry.resourceType} size ${actualKb} KiB exceeds ${entry.budget} KiB`,
    );
  }
}

for (const entry of budget.resourceCounts ?? []) {
  const actual =
    entry.resourceType === "third-party"
      ? thirdPartyCount
      : (resourceByType.get(entry.resourceType)?.requestCount ?? 0);
  rows.push(
    `count ${entry.resourceType}: ${actual} (budget ${entry.budget})`,
  );
  if (actual > entry.budget) {
    failures.push(
      `${entry.resourceType} count ${actual} exceeds ${entry.budget}`,
    );
  }
}

for (const entry of budget.timings ?? []) {
  const audit = report.audits?.[entry.metric];
  if (!audit || typeof audit.numericValue !== "number") {
    failures.push(`${entry.metric} was not measured by Lighthouse`);
    continue;
  }
  const actual = audit.numericValue;
  rows.push(
    `timing ${entry.metric}: ${actual.toFixed(2)} (budget ${entry.budget})`,
  );
  if (actual > entry.budget) {
    failures.push(
      `${entry.metric} ${actual.toFixed(2)} exceeds budget ${entry.budget}`,
    );
  }
}

for (const row of rows) {
  console.log(row);
}

if (failures.length > 0) {
  console.error("\nLighthouse budget failed:");
  for (const failure of failures) {
    console.error(`  - ${failure}`);
  }
  process.exit(1);
}

console.log("\nLighthouse budget passed.");
