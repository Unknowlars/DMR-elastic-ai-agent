import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
export const repoRoot = path.resolve(__dirname, "..", "..");
export const agentSpecDir = path.join(repoRoot, "specs", "agents");
export const toolSpecDir = path.join(repoRoot, "specs", "tools");
export const skillSpecDir = path.join(repoRoot, "specs", "skills");

export function relFromRepo(targetPath) {
  return path.relative(repoRoot, targetPath) || ".";
}

async function loadJson(filePath) {
  const raw = await fs.readFile(filePath, "utf8");
  return JSON.parse(raw);
}

async function listJsonFiles(dirPath) {
  const entries = await fs.readdir(dirPath, { withFileTypes: true });
  return entries
    .filter((entry) => entry.isFile() && entry.name.endsWith(".json"))
    .map((entry) => path.join(dirPath, entry.name))
    .sort();
}

export async function loadAgentSpecs() {
  const files = await listJsonFiles(agentSpecDir);
  const specs = [];
  for (const filePath of files) {
    const spec = await loadJson(filePath);
    specs.push({ filePath, spec });
  }
  return specs;
}

export async function loadToolSpecs() {
  const files = await listJsonFiles(toolSpecDir);
  const specs = [];
  for (const filePath of files) {
    const spec = await loadJson(filePath);
    specs.push({ filePath, spec });
  }
  return specs;
}

export async function loadSkillSpecs() {
  let files;
  try {
    files = await listJsonFiles(skillSpecDir);
  } catch {
    return [];
  }
  const specs = [];
  for (const filePath of files) {
    const spec = await loadJson(filePath);
    specs.push({ filePath, spec });
  }
  return specs;
}

export async function readInstructions(agentSpec) {
  if (agentSpec.instructions) {
    return agentSpec.instructions.trim();
  }

  if (!agentSpec.instructions_file) {
    return "";
  }

  const filePath = path.join(repoRoot, agentSpec.instructions_file);
  return (await fs.readFile(filePath, "utf8")).trim();
}

export async function buildAgentPayload(agentSpec) {
  const instructions = await readInstructions(agentSpec);
  const configuration = {
    instructions,
    tools: [{ tool_ids: agentSpec.tool_ids }],
  };
  if (agentSpec.skill_ids?.length) {
    configuration.skill_ids = agentSpec.skill_ids;
  }
  return {
    id: agentSpec.id,
    name: agentSpec.name,
    description: agentSpec.description,
    configuration,
  };
}

export function buildSkillPayload(skillSpec) {
  return {
    id: skillSpec.id,
    name: skillSpec.name,
    description: skillSpec.description,
    content: skillSpec.content || "",
    referenced_content: skillSpec.referenced_content || [],
    tool_ids: skillSpec.tool_ids || [],
  };
}

export function buildToolPayload(toolSpec) {
  const configuration = { ...toolSpec.configuration };
  // Strip 'default' from params — kept in spec for documentation but not accepted by Agent Builder API
  if (configuration.params) {
    configuration.params = Object.fromEntries(
      Object.entries(configuration.params).map(([k, v]) => {
        const { default: _dropped, ...rest } = v;
        return [k, rest];
      })
    );
  }
  return {
    id: toolSpec.id,
    type: toolSpec.type,
    description: toolSpec.description,
    configuration,
    ...(toolSpec.tags ? { tags: toolSpec.tags } : {})
  };
}

function validateCommonId(id, label, errors) {
  if (!id || typeof id !== "string") {
    errors.push(`${label}: missing string id`);
    return;
  }
  if (!/^[a-z0-9][a-z0-9._-]*$/.test(id)) {
    errors.push(`${label}: id "${id}" must match ^[a-z0-9][a-z0-9._-]*$`);
  }
}

export async function validateAgentSpec(filePath, spec) {
  const errors = [];
  const label = relFromRepo(filePath);

  if (spec.kind !== "agent") {
    errors.push(`${label}: kind must be "agent"`);
  }

  validateCommonId(spec.id, label, errors);

  if (!spec.name || typeof spec.name !== "string") {
    errors.push(`${label}: missing string name`);
  }

  if (!spec.description || typeof spec.description !== "string") {
    errors.push(`${label}: missing string description`);
  }

  if (!Array.isArray(spec.tool_ids) || spec.tool_ids.length === 0) {
    errors.push(`${label}: tool_ids must be a non-empty array`);
  }

  if (!spec.instructions && !spec.instructions_file) {
    errors.push(`${label}: provide instructions or instructions_file`);
  }

  if (spec.instructions_file) {
    const instructionPath = path.join(repoRoot, spec.instructions_file);
    try {
      await fs.access(instructionPath);
    } catch {
      errors.push(`${label}: instructions_file not found: ${spec.instructions_file}`);
    }
  }

  if (spec.skill_ids !== undefined && !Array.isArray(spec.skill_ids)) {
    errors.push(`${label}: skill_ids must be an array when provided`);
  }

  if (spec.tags && !Array.isArray(spec.tags)) {
    errors.push(`${label}: tags must be an array when provided`);
  }

  return errors;
}

export async function validateToolSpec(filePath, spec) {
  const errors = [];
  const label = relFromRepo(filePath);

  if (spec.kind !== "tool") {
    errors.push(`${label}: kind must be "tool"`);
  }

  validateCommonId(spec.id, label, errors);

  if (!["esql", "index_search", "workflow"].includes(spec.type)) {
    errors.push(`${label}: type must be one of esql, index_search, workflow`);
  }

  if (!spec.description || typeof spec.description !== "string") {
    errors.push(`${label}: missing string description`);
  }

  if (!spec.configuration || typeof spec.configuration !== "object" || Array.isArray(spec.configuration)) {
    errors.push(`${label}: configuration must be an object`);
    return errors;
  }

  if (spec.type === "esql") {
    if (!spec.configuration.query || typeof spec.configuration.query !== "string") {
      errors.push(`${label}: esql tools require configuration.query`);
    }
    if (!Object.prototype.hasOwnProperty.call(spec.configuration, "params")) {
      errors.push(`${label}: esql tools require configuration.params even when empty`);
    }
    if (spec.configuration.params && typeof spec.configuration.params === "object") {
      const allowedParamTypes = new Set(["string", "integer", "float", "boolean", "date", "array"]);
      const allowedParamFields = new Set(["type", "description", "default"]);
      for (const [paramName, paramSpec] of Object.entries(spec.configuration.params)) {
        if (!paramSpec || typeof paramSpec !== "object" || Array.isArray(paramSpec)) {
          errors.push(`${label}: params.${paramName} must be an object`);
          continue;
        }
        if (!allowedParamTypes.has(paramSpec.type)) {
          errors.push(`${label}: params.${paramName}.type must be one of ${[...allowedParamTypes].join(", ")}`);
        }
        if (!paramSpec.description || typeof paramSpec.description !== "string") {
          errors.push(`${label}: params.${paramName}.description is required`);
        }
        for (const fieldName of Object.keys(paramSpec)) {
          if (!allowedParamFields.has(fieldName)) {
            errors.push(`${label}: params.${paramName}.${fieldName} is not supported by Agent Builder`);
          }
        }
      }
    }
  }

  if (spec.type === "index_search" && (!spec.configuration.pattern || typeof spec.configuration.pattern !== "string")) {
    errors.push(`${label}: index_search tools require configuration.pattern`);
  }

  if (spec.type === "workflow" && (!spec.configuration.workflow_id || typeof spec.configuration.workflow_id !== "string")) {
    errors.push(`${label}: workflow tools require configuration.workflow_id`);
  }

  if (spec.tags && !Array.isArray(spec.tags)) {
    errors.push(`${label}: tags must be an array when provided`);
  }

  return errors;
}

export async function validateSkillSpec(filePath, spec) {
  const errors = [];
  const label = relFromRepo(filePath);

  if (spec.kind !== "skill") {
    errors.push(`${label}: kind must be "skill"`);
  }

  validateCommonId(spec.id, label, errors);

  if (!spec.name || typeof spec.name !== "string") {
    errors.push(`${label}: missing string name`);
  }

  if (!spec.description || typeof spec.description !== "string") {
    errors.push(`${label}: missing string description`);
  }

  if (spec.description && spec.description.length > 1024) {
    errors.push(`${label}: description exceeds 1024 characters (${spec.description.length})`);
  }

  if (!spec.content || typeof spec.content !== "string") {
    errors.push(`${label}: missing string content (the main skill instruction field)`);
  }

  if (spec.referenced_content !== undefined) {
    if (!Array.isArray(spec.referenced_content)) {
      errors.push(`${label}: referenced_content must be an array when provided`);
    } else {
      for (const [i, block] of spec.referenced_content.entries()) {
        if (!block.name || typeof block.name !== "string") {
          errors.push(`${label}: referenced_content[${i}].name must be a string`);
        }
        if (!block.content || typeof block.content !== "string") {
          errors.push(`${label}: referenced_content[${i}].content must be a string`);
        }
      }
    }
  }

  if (spec.tool_ids !== undefined && !Array.isArray(spec.tool_ids)) {
    errors.push(`${label}: tool_ids must be an array when provided`);
  }

  return errors;
}

export function summarizeAgentSpec(spec) {
  const skillCount = spec.skill_ids?.length ?? 0;
  return `${spec.id} (${spec.tool_ids.length} tools${skillCount ? `, ${skillCount} skills` : ""})`;
}

export function summarizeToolSpec(spec) {
  return `${spec.id} [${spec.type}]`;
}

export function summarizeSkillSpec(spec) {
  const blocks = spec.referenced_content?.length ?? 0;
  return `${spec.id} (${blocks} content blocks)`;
}
