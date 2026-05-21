#!/usr/bin/env node
try {
  process.loadEnvFile();
} catch {}

function getElasticConfig() {
  const url = process.env.ELASTICSEARCH_URL?.replace(/\/$/, "");
  const apiKey = process.env.ELASTICSEARCH_API_KEY;
  const username = process.env.ELASTICSEARCH_USERNAME;
  const password = process.env.ELASTICSEARCH_PASSWORD;
  const insecure = process.env.ELASTICSEARCH_INSECURE === "true";

  if (!url) throw new Error("Set ELASTICSEARCH_URL.");
  if (!apiKey && !(username && password)) {
    throw new Error("Set ELASTICSEARCH_API_KEY or ELASTICSEARCH_USERNAME + ELASTICSEARCH_PASSWORD.");
  }

  return { url, apiKey, username, password, insecure };
}

function getHeaders(config) {
  const headers = { "Content-Type": "application/json", Accept: "application/json" };
  if (config.apiKey) {
    headers.Authorization = `ApiKey ${config.apiKey}`;
  } else {
    headers.Authorization = `Basic ${Buffer.from(`${config.username}:${config.password}`).toString("base64")}`;
  }
  return headers;
}

async function request(config, path, options = {}) {
  if (config.insecure) process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";
  const response = await fetch(`${config.url}${path}`, {
    ...options,
    headers: { ...getHeaders(config), ...options.headers },
  });
  const text = await response.text();
  const data = text ? JSON.parse(text) : {};
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${JSON.stringify(data)}`);
  }
  return data;
}

function printTsv(data) {
  const columns = data.columns?.map((column) => column.name) || [];
  console.log(columns.join("\t"));
  for (const row of data.values || []) {
    console.log(row.map((value) => value ?? "").join("\t"));
  }
}

function usage() {
  console.error(`Usage:
  node scripts/esql.mjs test
  node scripts/esql.mjs raw '<ES|QL query>' [--tsv]
  node scripts/esql.mjs schema <index-pattern>`);
}

const [command, firstArg, ...rest] = process.argv.slice(2);

try {
  const config = getElasticConfig();

  if (command === "test") {
    const info = await request(config, "/");
    console.log(`Connected to Elasticsearch ${info.version?.number || "unknown"}`);
  } else if (command === "raw" && firstArg) {
    const data = await request(config, "/_query", {
      method: "POST",
      body: JSON.stringify({ query: firstArg }),
    });
    if (rest.includes("--tsv")) {
      printTsv(data);
    } else {
      console.log(JSON.stringify(data, null, 2));
    }
  } else if (command === "schema" && firstArg) {
    const data = await request(config, `/${encodeURIComponent(firstArg)}/_mapping`, { method: "GET" });
    console.log(JSON.stringify(data, null, 2));
  } else {
    usage();
    process.exit(1);
  }
} catch (error) {
  console.error(`Error: ${error.message}`);
  process.exit(1);
}
