import { kibanaGet } from "./lib/kibana-client.mjs";
import { buildAgentPayload, buildSkillPayload, buildToolPayload, loadAgentSpecs, loadSkillSpecs, loadToolSpecs } from "./lib/specs.mjs";

function normalizeAgent(agent) {
  return {
    id: agent.id,
    name: agent.name,
    description: agent.description,
    instructions: agent.configuration?.instructions || "",
    tool_ids: agent.configuration?.tools?.[0]?.tool_ids || [],
    skill_ids: agent.configuration?.skill_ids || [],
    tags: agent.tags || []
  };
}

function normalizeReferencedContent(referencedContent) {
  return (referencedContent || []).map((block) => ({
    name: block.name,
    content: block.content || "",
  }));
}

function normalizeSkill(skill) {
  return {
    id: skill.id,
    name: skill.name,
    description: skill.description,
    content: skill.content || "",
    referenced_content: normalizeReferencedContent(skill.referenced_content),
    tool_ids: skill.tool_ids || [],
  };
}

function normalizeTool(tool) {
  return {
    id: tool.id,
    type: tool.type,
    description: tool.description,
    configuration: tool.configuration || {},
    tags: tool.tags || []
  };
}

function sameArray(left, right) {
  return JSON.stringify([...left]) === JSON.stringify([...right]);
}

function diffAgent(local, remote) {
  const changes = [];
  if (local.name !== remote.name) changes.push("name");
  if (local.description !== remote.description) changes.push("description");
  if (local.instructions !== remote.instructions) changes.push("instructions");
  if (!sameArray(local.tool_ids, remote.tool_ids)) changes.push("tool_ids");
  if (!sameArray(local.skill_ids || [], remote.skill_ids || [])) changes.push("skill_ids");
  if (!sameArray(local.tags || [], remote.tags || [])) changes.push("tags");
  return changes;
}

function diffSkill(local, remote) {
  const changes = [];
  if (local.name !== remote.name) changes.push("name");
  if (local.description !== remote.description) changes.push("description");
  if (local.content !== remote.content) changes.push("content");
  if (JSON.stringify(local.referenced_content) !== JSON.stringify(remote.referenced_content)) changes.push("referenced_content");
  if (!sameArray(local.tool_ids || [], remote.tool_ids || [])) changes.push("tool_ids");
  return changes;
}

function diffTool(local, remote) {
  const changes = [];
  if (local.type !== remote.type) changes.push("type");
  if (local.description !== remote.description) changes.push("description");
  if (JSON.stringify(local.configuration) !== JSON.stringify(remote.configuration)) changes.push("configuration");
  if (!sameArray(local.tags || [], remote.tags || [])) changes.push("tags");
  return changes;
}

async function loadRemoteSkills(skillSpecs) {
  try {
    const skillResponse = await kibanaGet("/api/agent_builder/skills");
    const listedSkills = new Map((skillResponse.results || skillResponse || []).map((skill) => [skill.id, skill]));
    const fullSkills = await Promise.all(skillSpecs.map(async ({ spec }) => {
      if (!listedSkills.has(spec.id)) return null;
      try {
        return await kibanaGet(`/api/agent_builder/skills/${encodeURIComponent(spec.id)}`);
      } catch {
        return listedSkills.get(spec.id);
      }
    }));
    return new Map(fullSkills.filter(Boolean).map((skill) => [skill.id, normalizeSkill(skill)]));
  } catch {
    if (skillSpecs.length > 0) {
      console.warn("Skills API not available. Requires Kibana 9.4+.");
    }
    return new Map();
  }
}

const [agentSpecs, toolSpecs, skillSpecs, agentResponse, toolResponse] = await Promise.all([
  loadAgentSpecs(),
  loadToolSpecs(),
  loadSkillSpecs(),
  kibanaGet("/api/agent_builder/agents"),
  kibanaGet("/api/agent_builder/tools")
]);

const remoteAgents = new Map((agentResponse.results || agentResponse).map((agent) => [agent.id, normalizeAgent(agent)]));
const remoteTools = new Map((toolResponse.results || toolResponse).map((tool) => [tool.id, normalizeTool(tool)]));
const remoteSkills = await loadRemoteSkills(skillSpecs);

if (skillSpecs.length > 0) {
  console.log("Skill sync plan:");
  for (const { spec } of skillSpecs) {
    const payload = buildSkillPayload(spec);
    const local = normalizeSkill(payload);
    const remote = remoteSkills.get(spec.id);
    if (!remote) {
      console.log(`- create ${spec.id}`);
      continue;
    }
    const changes = diffSkill(local, remote);
    if (changes.length === 0) {
      console.log(`- keep ${spec.id}`);
    } else {
      console.log(`- update ${spec.id}: ${changes.join(", ")}`);
    }
  }
  console.log("");
}

console.log("Agent sync plan:");
for (const { spec } of agentSpecs) {
  const payload = await buildAgentPayload(spec);
  const local = normalizeAgent(payload);
  const remote = remoteAgents.get(spec.id);
  if (!remote) {
    console.log(`- create ${spec.id}`);
    continue;
  }
  const changes = diffAgent(local, remote);
  if (changes.length === 0) {
    console.log(`- keep ${spec.id}`);
  } else {
    console.log(`- update ${spec.id}: ${changes.join(", ")}`);
  }
}

console.log("");
console.log("Tool sync plan:");
if (toolSpecs.length === 0) {
  console.log("- no local custom tool specs yet");
} else {
  for (const { spec } of toolSpecs) {
    const payload = buildToolPayload(spec);
    const local = normalizeTool(payload);
    const remote = remoteTools.get(spec.id);
    if (!remote) {
      console.log(`- create ${spec.id}`);
      continue;
    }
    const changes = diffTool(local, remote);
    if (changes.length === 0) {
      console.log(`- keep ${spec.id}`);
    } else {
      console.log(`- update ${spec.id}: ${changes.join(", ")}`);
    }
  }
}
