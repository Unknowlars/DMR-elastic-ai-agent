import fs from "node:fs/promises";
import path from "node:path";
import { repoRoot } from "./lib/specs.mjs";

try {
  process.loadEnvFile();
} catch {}

function getElasticConfig() {
  const url = process.env.ELASTICSEARCH_URL;
  if (!url) {
    throw new Error("ELASTICSEARCH_URL is required");
  }

  const apiKey = process.env.ELASTICSEARCH_API_KEY || process.env.KIBANA_API_KEY;
  const username =
    process.env.ELASTICSEARCH_USERNAME ||
    process.env.KIBANA_USERNAME;
  const password =
    process.env.ELASTICSEARCH_PASSWORD ||
    process.env.KIBANA_PASSWORD ||
    process.env.ELASTICSEARCH_PASSWORD;

  if (!apiKey && !(username && password)) {
    throw new Error("Set ELASTICSEARCH_API_KEY or ELASTICSEARCH_USERNAME + ELASTICSEARCH_PASSWORD");
  }

  return { url: url.replace(/\/$/, ""), apiKey, username, password };
}

function getHeaders(config) {
  const headers = { "Content-Type": "application/json" };
  if (config.apiKey) {
    headers.Authorization = `ApiKey ${config.apiKey}`;
  } else {
    const auth = Buffer.from(`${config.username}:${config.password}`).toString("base64");
    headers.Authorization = `Basic ${auth}`;
  }
  return headers;
}

async function elasticGet(config, requestPath) {
  const response = await fetch(`${config.url}${requestPath}`, {
    method: "GET",
    headers: getHeaders(config)
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`HTTP ${response.status}: ${text}`);
  }

  return response.json();
}

const config = getElasticConfig();
const outputDir = path.join(repoRoot, "catalog", "raw");
await fs.mkdir(outputDir, { recursive: true });

const indices = await elasticGet(config, "/_cat/indices?format=json&expand_wildcards=all&h=health,status,index,docs.count,store.size");

const snapshot = {
  exported_at: new Date().toISOString(),
  cluster_url: config.url,
  indices
};

const outPath = path.join(outputDir, "indices.snapshot.json");
await fs.writeFile(outPath, JSON.stringify(snapshot, null, 2));

console.log(`Exported ${indices.length} indices.`);
console.log(`Wrote ${path.relative(repoRoot, outPath)}`);
