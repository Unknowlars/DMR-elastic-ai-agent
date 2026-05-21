# Specs

This directory contains the structured source-of-truth definitions that can be validated and synced into Kibana Agent Builder.

Start with the root [README](../README.md) for the showcase overview, then use this directory when reviewing or changing the deployable Agent Builder assets.

## Agent spec contract

Required fields:

- `kind`: must be `agent`
- `id`
- `name`
- `description`
- `tool_ids`

Instruction content is provided by either:

- `instructions`
- `instructions_file`

## Tool spec contract

Required fields:

- `kind`: must be `tool`
- `id`
- `type`: `esql`, `index_search`, or `workflow`
- `description`
- `configuration`

The JSON structure is intentionally close to the Kibana API payload, so sync scripts can stay simple and reviewable.

Validate specs before syncing:

```bash
npm run validate:specs
```
