import fs from "node:fs/promises";
import path from "node:path";
import { kibanaGet } from "./lib/kibana-client.mjs";
import { repoRoot } from "./lib/specs.mjs";

const outputDir = path.join(repoRoot, "catalog", "raw");
await fs.mkdir(outputDir, { recursive: true });

const [toolsResponse, agentsResponse] = await Promise.all([
  kibanaGet("/api/agent_builder/tools"),
  kibanaGet("/api/agent_builder/agents"),
]);

const tools = toolsResponse.results || toolsResponse;
const agents = agentsResponse.results || agentsResponse;
const customTools = tools.filter((tool) => !String(tool.id).startsWith("platform.core."));

let skills = [];
try {
  const skillsResponse = await kibanaGet("/api/agent_builder/skills");
  skills = skillsResponse.results || skillsResponse || [];
} catch {
  console.warn("Skills API not available — skipping skills export. Requires Kibana 9.4+.");
}

const snapshot = {
  exported_at: new Date().toISOString(),
  kibana_space_id: process.env.KIBANA_SPACE_ID || "default",
  tools,
  custom_tools: customTools,
  agents,
  skills,
};

const outPath = path.join(outputDir, "agent-builder-state.json");
await fs.writeFile(outPath, JSON.stringify(snapshot, null, 2));

console.log(`Exported ${tools.length} tools (${customTools.length} custom), ${agents.length} agents, ${skills.length} skills.`);
console.log(`Wrote ${path.relative(repoRoot, outPath)}`);
