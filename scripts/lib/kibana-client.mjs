try {
  process.loadEnvFile();
} catch {}

const RETRY_DELAYS_SECONDS = [5, 10, 20];

export function getKibanaConfig() {
  const url = process.env.KIBANA_URL;
  const apiKey = process.env.KIBANA_API_KEY;
  const username = process.env.KIBANA_USERNAME || process.env.ELASTICSEARCH_USERNAME;
  const password = process.env.KIBANA_PASSWORD || process.env.ELASTICSEARCH_PASSWORD;
  const spaceId = process.env.KIBANA_SPACE_ID;
  const insecure = process.env.KIBANA_INSECURE === "true";

  if (!url) {
    throw new Error("Set KIBANA_URL.");
  }

  if (!apiKey && !username && !password && process.env.KIBANA_NO_AUTH !== "true") {
    throw new Error("Set KIBANA_API_KEY or KIBANA_USERNAME + KIBANA_PASSWORD.");
  }

  if (!apiKey && ((username && !password) || (!username && password))) {
    throw new Error("Set both KIBANA_USERNAME and KIBANA_PASSWORD for basic auth.");
  }

  return { url, apiKey, username, password, spaceId, insecure };
}

function getHeaders(config) {
  const headers = {
    "Content-Type": "application/json",
    "kbn-xsrf": "true",
    "User-Agent": "dmr-agent-builder-showcase",
  };

  if (config.apiKey) {
    headers.Authorization = `ApiKey ${config.apiKey}`;
  } else if (config.username && config.password) {
    headers.Authorization = `Basic ${Buffer.from(`${config.username}:${config.password}`).toString("base64")}`;
  }

  return headers;
}

function getBasePath(config, space) {
  let basePath = config.url.replace(/\/$/, "");
  const effectiveSpace = space || config.spaceId;
  if (effectiveSpace && effectiveSpace !== "default") {
    basePath += `/s/${effectiveSpace}`;
  }
  return basePath;
}

export async function kibanaFetch(path, options = {}) {
  const config = getKibanaConfig();
  const { space, params, ...fetchOpts } = options;
  const basePath = getBasePath(config, space);

  let url = `${basePath}${path}`;
  if (params) {
    const searchParams = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
      if (value === undefined || value === null) continue;
      if (Array.isArray(value)) {
        for (const item of value) searchParams.append(key, String(item));
      } else {
        searchParams.append(key, String(value));
      }
    }
    const queryString = searchParams.toString();
    if (queryString) url += `?${queryString}`;
  }

  if (config.insecure) {
    process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";
  }

  const requestOptions = {
    ...fetchOpts,
    headers: {
      ...getHeaders(config),
      ...fetchOpts.headers,
    },
  };

  for (let attempt = 0; attempt <= RETRY_DELAYS_SECONDS.length; attempt++) {
    const response = await fetch(url, requestOptions);

    if (response.status === 429 && attempt < RETRY_DELAYS_SECONDS.length) {
      const delay = RETRY_DELAYS_SECONDS[attempt];
      console.error(`Rate limited, retrying in ${delay}s...`);
      await new Promise((resolve) => setTimeout(resolve, delay * 1000));
      continue;
    }

    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json") ? await response.json() : await response.text();

    if (!response.ok) {
      return {
        success: false,
        status: response.status,
        error: data?.message || data?.error || `HTTP ${response.status}`,
        details: data,
      };
    }

    return { success: true, data };
  }
}

async function unwrap(result) {
  if (!result.success) {
    const details = typeof result.details === "string" ? result.details : JSON.stringify(result.details);
    throw new Error(`${result.error}${details ? `: ${details}` : ""}`);
  }
  return result.data;
}

export async function kibanaGet(path, params, space) {
  return unwrap(await kibanaFetch(path, { method: "GET", params, space }));
}

export async function kibanaPost(path, body, space) {
  return unwrap(await kibanaFetch(path, {
    method: "POST",
    body: body === undefined ? undefined : JSON.stringify(body),
    space,
  }));
}

export async function kibanaPut(path, body, space) {
  return unwrap(await kibanaFetch(path, {
    method: "PUT",
    body: body === undefined ? undefined : JSON.stringify(body),
    space,
  }));
}

export async function kibanaDelete(path, space) {
  return unwrap(await kibanaFetch(path, { method: "DELETE", space }));
}

export async function testConnection(space) {
  const status = await kibanaGet("/api/status", undefined, space);
  const version = typeof status.version === "object" ? status.version?.number : status.version;
  console.log(`Connected to Kibana: ${status.name || "unknown"}`);
  console.log(`Version: ${version || "unknown"}`);
}
