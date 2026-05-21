import { loadAgentSpecs, loadSkillSpecs, loadToolSpecs, summarizeAgentSpec, summarizeSkillSpec, summarizeToolSpec, validateAgentSpec, validateSkillSpec, validateToolSpec } from "./lib/specs.mjs";

const errors = [];

const agentSpecs = await loadAgentSpecs();
const toolSpecs = await loadToolSpecs();
const skillSpecs = await loadSkillSpecs();

for (const { filePath, spec } of agentSpecs) {
  errors.push(...await validateAgentSpec(filePath, spec));
}

for (const { filePath, spec } of toolSpecs) {
  errors.push(...await validateToolSpec(filePath, spec));
}

for (const { filePath, spec } of skillSpecs) {
  errors.push(...await validateSkillSpec(filePath, spec));
}

if (errors.length > 0) {
  for (const error of errors) {
    console.error(error);
  }
  process.exit(1);
}

console.log(`Validated ${agentSpecs.length} agent specs:`);
for (const { spec } of agentSpecs) {
  console.log(`- ${summarizeAgentSpec(spec)}`);
}

console.log(`Validated ${toolSpecs.length} tool specs:`);
for (const { spec } of toolSpecs) {
  console.log(`- ${summarizeToolSpec(spec)}`);
}

if (skillSpecs.length > 0) {
  console.log(`Validated ${skillSpecs.length} skill specs:`);
  for (const { spec } of skillSpecs) {
    console.log(`- ${summarizeSkillSpec(spec)}`);
  }
}

console.log("Spec validation passed.");

