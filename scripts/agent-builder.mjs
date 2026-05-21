#!/usr/bin/env node
import { kibanaGet, kibanaPost, testConnection } from "./lib/kibana-client.mjs";

const API_BASE = "/api/agent_builder";

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg.startsWith("--")) {
      const key = arg.slice(2).replace(/-/g, "_");
      const next = argv[i + 1];
      if (next && !next.startsWith("--")) {
        args[key] = next;
        i++;
      } else {
        args[key] = true;
      }
    } else {
      args._.push(arg);
    }
  }
  return args;
}

function printUsage() {
  console.error(`Usage:
  node scripts/agent-builder.mjs test
  node scripts/agent-builder.mjs list-agents
  node scripts/agent-builder.mjs list-tools
  node scripts/agent-builder.mjs get-agent --id <agent-id>
  node scripts/agent-builder.mjs chat --id <agent-id> --message <text>`);
}

async function listAgents() {
  const response = await kibanaGet(`${API_BASE}/agents`);
  const agents = response.results || response;
  console.log(`Agents (${agents.length}):`);
  for (const agent of agents) {
    const toolCount = agent.configuration?.tools?.[0]?.tool_ids?.length || 0;
    const skillCount = agent.configuration?.skill_ids?.length || 0;
    const mode = agent.readonly ? "readonly" : "editable";
    console.log(`- ${agent.id}: ${agent.name} (${toolCount} tools, ${skillCount} skills, ${mode})`);
  }
}

async function listTools() {
  const response = await kibanaGet(`${API_BASE}/tools`);
  const tools = response.results || response;
  console.log(`Tools (${tools.length}):`);
  for (const tool of tools) {
    const tags = tool.tags?.length ? ` [${tool.tags.join(", ")}]` : "";
    console.log(`- ${tool.id}${tags}`);
  }
}

async function getAgent(args) {
  if (!args.id) throw new Error("--id is required.");
  const agent = await kibanaGet(`${API_BASE}/agents/${encodeURIComponent(args.id)}`);
  console.log(JSON.stringify(agent, null, 2));
}

async function chat(args) {
  if (!args.id) throw new Error("--id is required.");
  if (!args.message) throw new Error("--message is required.");

  const response = await kibanaPost(`${API_BASE}/converse/async`, {
    agent_id: args.id,
    input: args.message,
  });

  if (!response?.body && !response?.events && typeof response !== "string") {
    console.log(JSON.stringify(response, null, 2));
    return;
  }

  console.log(response);
}

const args = parseArgs(process.argv.slice(2));
const command = args._[0];

try {
  switch (command) {
    case "test":
      await testConnection();
      break;
    case "list-agents":
      await listAgents();
      break;
    case "list-tools":
      await listTools();
      break;
    case "get-agent":
      await getAgent(args);
      break;
    case "chat":
      await chat(args);
      break;
    default:
      printUsage();
      process.exit(1);
  }
} catch (error) {
  console.error(`Error: ${error.message}`);
  process.exit(1);
}
