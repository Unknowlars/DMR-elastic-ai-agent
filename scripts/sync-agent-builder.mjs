import { kibanaGet, kibanaPost, kibanaPut } from "./lib/kibana-client.mjs";
import { buildAgentPayload, buildSkillPayload, buildToolPayload, loadAgentSpecs, loadSkillSpecs, loadToolSpecs } from "./lib/specs.mjs";

const shouldApply = process.argv.includes("--apply");

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

function arraysEqual(left, right) {
  return JSON.stringify(left || []) === JSON.stringify(right || []);
}

function agentNeedsUpdate(local, remote) {
  return (
    local.name !== remote.name ||
    local.description !== remote.description ||
    local.instructions !== remote.instructions ||
    !arraysEqual(local.tool_ids, remote.tool_ids) ||
    !arraysEqual(local.skill_ids, remote.skill_ids) ||
    !arraysEqual(local.tags, remote.tags)
  );
}

function skillNeedsUpdate(local, remote) {
  return (
    local.name !== remote.name ||
    local.description !== remote.description ||
    local.content !== remote.content ||
    JSON.stringify(local.referenced_content) !== JSON.stringify(remote.referenced_content) ||
    !arraysEqual(local.tool_ids, remote.tool_ids)
  );
}

function toolNeedsUpdate(local, remote) {
  return (
    local.type !== remote.type ||
    local.description !== remote.description ||
    JSON.stringify(local.configuration) !== JSON.stringify(remote.configuration) ||
    !arraysEqual(local.tags, remote.tags)
  );
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
      console.warn("Skills API not available — skipping skill sync. Requires Kibana 9.4+.");
    }
    return new Map();
  }
}

const [agentSpecs, toolSpecs, skillSpecs, remoteAgentResponse, remoteToolResponse] = await Promise.all([
  loadAgentSpecs(),
  loadToolSpecs(),
  loadSkillSpecs(),
  kibanaGet("/api/agent_builder/agents"),
  kibanaGet("/api/agent_builder/tools"),
]);

const remoteAgents = new Map((remoteAgentResponse.results || remoteAgentResponse).map((agent) => [agent.id, normalizeAgent(agent)]));
const remoteTools = new Map((remoteToolResponse.results || remoteToolResponse).map((tool) => [tool.id, normalizeTool(tool)]));
const remoteSkills = await loadRemoteSkills(skillSpecs);

console.log(shouldApply ? "Applying Agent Builder sync." : "Dry run only. Re-run with --apply to write changes.");

for (const { spec } of skillSpecs) {
  const payload = buildSkillPayload(spec);
  const local = normalizeSkill(payload);
  const remote = remoteSkills.get(spec.id);

  if (!remote) {
    console.log(`create skill ${spec.id}`);
    if (shouldApply) {
      await kibanaPost("/api/agent_builder/skills", payload);
    }
    continue;
  }

  if (skillNeedsUpdate(local, remote)) {
    console.log(`update skill ${spec.id}`);
    if (shouldApply) {
      await kibanaPut(`/api/agent_builder/skills/${encodeURIComponent(spec.id)}`, {
        name: payload.name,
        description: payload.description,
        content: payload.content,
        referenced_content: payload.referenced_content,
        tool_ids: payload.tool_ids,
      });
    }
  } else {
    console.log(`keep skill ${spec.id}`);
  }
}

for (const { spec } of toolSpecs) {
  const payload = buildToolPayload(spec);
  const local = normalizeTool(payload);
  const remote = remoteTools.get(spec.id);

  if (!remote) {
    console.log(`create tool ${spec.id}`);
    if (shouldApply) {
      await kibanaPost("/api/agent_builder/tools", payload);
    }
    continue;
  }

  if (toolNeedsUpdate(local, remote)) {
    console.log(`update tool ${spec.id}`);
    if (shouldApply) {
      await kibanaPut(`/api/agent_builder/tools/${encodeURIComponent(spec.id)}`, {
        description: payload.description,
        configuration: payload.configuration,
        tags: payload.tags || []
      });
    }
  } else {
    console.log(`keep tool ${spec.id}`);
  }
}

for (const { spec } of agentSpecs) {
  const payload = await buildAgentPayload(spec);
  const local = normalizeAgent(payload);
  const remote = remoteAgents.get(spec.id);

  if (!remote) {
    console.log(`create agent ${spec.id}`);
    if (shouldApply) {
      await kibanaPost("/api/agent_builder/agents", payload);
    }
    continue;
  }

  if (agentNeedsUpdate(local, remote)) {
    console.log(`update agent ${spec.id}`);
    if (shouldApply) {
      await kibanaPut(`/api/agent_builder/agents/${encodeURIComponent(spec.id)}`, {
        description: payload.description,
        configuration: payload.configuration
      });
    }
  } else {
    console.log(`keep agent ${spec.id}`);
  }
}

if (!shouldApply) {
  console.log("No changes were written.");
}
