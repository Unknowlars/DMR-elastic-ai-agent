import fs from "node:fs/promises";
import path from "node:path";
import { repoRoot } from "./lib/specs.mjs";

try {
  process.loadEnvFile();
} catch {}

function authMode(prefix) {
  const apiKey = process.env[`${prefix}_API_KEY`];
  const username = process.env[`${prefix}_USERNAME`];
  const password = process.env[`${prefix}_PASSWORD`];

  if (apiKey) {
    return "api_key";
  }
  if (username && password) {
    return "basic";
  }
  return "missing";
}

async function exists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

const checks = [];
const warnings = [];
const errors = [];

const agentBuilderCli = path.join(repoRoot, "scripts", "agent-builder.mjs");
checks.push(["Agent Builder CLI", await exists(agentBuilderCli) ? "ok" : "missing"]);

if (process.env.KIBANA_URL) {
  checks.push(["KIBANA_URL", process.env.KIBANA_URL]);
  try {
    const kibanaUrl = new URL(process.env.KIBANA_URL);
    if (kibanaUrl.port === "9200") {
      errors.push("KIBANA_URL points at port 9200, which is normally Elasticsearch. Use the Kibana URL, usually port 5601.");
    }
  } catch {
    errors.push("KIBANA_URL is not a valid URL");
  }
} else {
  errors.push("KIBANA_URL is not set");
}

const kibanaAuth = authMode("KIBANA");
if (kibanaAuth === "missing") {
  errors.push("Set KIBANA_API_KEY or KIBANA_USERNAME + KIBANA_PASSWORD");
} else {
  checks.push(["Kibana auth", kibanaAuth]);
}

if (process.env.KIBANA_SPACE_ID) {
  checks.push(["KIBANA_SPACE_ID", process.env.KIBANA_SPACE_ID]);
}

if (process.env.ELASTICSEARCH_URL) {
  checks.push(["ELASTICSEARCH_URL", process.env.ELASTICSEARCH_URL]);
  const elasticAuth =
    process.env.ELASTICSEARCH_API_KEY ? "api_key" :
    process.env.ELASTICSEARCH_USERNAME && process.env.ELASTICSEARCH_PASSWORD ? "basic" :
    "fallback";
  checks.push(["Elasticsearch auth", elasticAuth]);
} else {
  warnings.push("ELASTICSEARCH_URL is not set; npm run export:indices will not work until you provide it");
}

for (const [name, status] of checks) {
  console.log(`${name}: ${status}`);
}

for (const warning of warnings) {
  console.warn(`Warning: ${warning}`);
}

if (errors.length > 0) {
  for (const error of errors) {
    console.error(`Error: ${error}`);
  }
  process.exit(1);
}

console.log("Environment validation passed.");
