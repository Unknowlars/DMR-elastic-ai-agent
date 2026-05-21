#!/usr/bin/env node
import fs from "node:fs/promises";
import { kibanaFetch, testConnection } from "./lib/kibana-client.mjs";

function apiVersionHeaders() {
  return { "Elastic-Api-Version": "2023-10-31" };
}

async function loadJson(filePath) {
  return JSON.parse(await fs.readFile(filePath, "utf8"));
}

async function dashboardGet(id) {
  return kibanaFetch(`/api/dashboards/${encodeURIComponent(id)}`, {
    method: "GET",
    headers: apiVersionHeaders(),
  });
}

async function dashboardUpdate(id, definition) {
  const body = definition.data
    ? definition.data
    : (() => {
        const { id: _id, spaces: _spaces, ...rest } = definition;
        return rest;
      })();

  return kibanaFetch(`/api/dashboards/${encodeURIComponent(id)}`, {
    method: "PUT",
    headers: apiVersionHeaders(),
    body: JSON.stringify(body),
  });
}

async function upsertDashboard(id, filePath) {
  const definition = await loadJson(filePath);
  const result = await dashboardUpdate(id, definition);
  if (!result.success) {
    throw new Error(result.error || `HTTP ${result.status}`);
  }
  console.log(`Upserted dashboard ${id}`);
}

function usage() {
  console.error(`Usage:
  node scripts/kibana-dashboards.mjs test
  node scripts/kibana-dashboards.mjs get <dashboard-id>
  node scripts/kibana-dashboards.mjs upsert <dashboard-id> <dashboard-json>`);
}

const [command, id, filePath] = process.argv.slice(2);

try {
  if (command === "test") {
    await testConnection();
  } else if (command === "get" && id) {
    const result = await dashboardGet(id);
    if (!result.success) throw new Error(result.error || `HTTP ${result.status}`);
    console.log(JSON.stringify(result.data, null, 2));
  } else if (command === "upsert" && id && filePath) {
    await upsertDashboard(id, filePath);
  } else {
    usage();
    process.exit(1);
  }
} catch (error) {
  console.error(`Error: ${error.message}`);
  process.exit(1);
}
