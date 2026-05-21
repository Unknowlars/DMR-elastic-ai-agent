---
title: Create and manage custom tools in Elastic Agent Builder
description: Learn how to create and manage custom tools in Agent Builder.
url: https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/tools/custom-tools
products:
  - Elastic Cloud Serverless
  - Elastic Observability
  - Elastic Security
  - Elasticsearch
  - Kibana
applies_to:
  - Elastic Cloud Serverless: Generally available
  - Elastic Stack: Generally available since 9.3, Preview in 9.2
---

# Create and manage custom tools in Elastic Agent Builder
You can extend the built-in tool catalog with your own custom tool definitions. Custom tools offer flexibility in how they interact with your data. This flexibility allows you to create tools that match your specific use cases and data access patterns.

## Tool types

Elastic Agent Builder supports several tool types:
- **[ES|QL tools](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/tools/esql-tools)**: Execute pre-defined ES|QL queries with parameterized inputs for precise, repeatable data retrieval.
- **[Index search tools](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/tools/index-search-tools)**: Scope searches to specific indices or patterns. The LLM dynamically constructs queries based on user requests.
- **[MCP tools](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/tools/mcp-tools)**: Connect to external Model Context Protocol servers, enabling agents to use remote tools and services.
- **[Workflow tools](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/tools/workflow-tools)**: Call pre-defined Workflows directly from the agent chat.


## Create custom tools in the UI

You can create custom tools in the Kibana UI.
To create a custom tool in the UI:
1. Navigate to the Tools page:
   <applies-switch>
   <applies-item title="{ stack: ga 9.4+, serverless: ga }" applies-to="Elastic Cloud Serverless: Generally available, Elastic Stack: Planned">
   Click **Manage components** at the bottom of the left sidebar, then select **Tools**. You can also reach this page from **Customize > Tools > Manage all tools**.
   </applies-item>

   <applies-item title="{ stack: ga =9.3 }" applies-to="Elastic Stack: Generally available in 9.3">
   Navigate to the **Tools** section from the key actions menu in the Agent Chat UI.
   </applies-item>
   </applies-switch>
2. Click **+ New tool**.

![New tool button for creating custom tools](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/images/new-tool-button.png)

1. Fill in the required fields:
   - **ID**: Enter a unique identifier for your tool (e.g., `get_customer_orders`). Agents use this ID to reference the tool. Refer to [Naming conventions](#naming-conventions) for recommended patterns.
- **Name**: Enter a descriptive name for your tool.
- **Description**: Write a clear explanation of what the tool does and when it should be used. Refer to [Writing effective tool descriptions](#writing-effective-tool-descriptions) for guidance.
- **Type**: Choose a tool type from the list.
- **Parameters**: For tools with ES|QL queries, define any parameters your query needs.
- **Labels**: (Optional) Add labels to categorize and organize your tools.
2. Choose how to save your tool:
   - Select **Save** to create the tool.
- Select **Save and test** to create the tool and immediately open the testing interface
   ![Save and Save and test buttons for tool creation](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/images/tool-save-save-and-test-buttons.png)


## Create custom tools with API

You can also create and manage tools programmatically. To learn more, refer to [Tools API](/docs/explore-analyze/ai-features/agent-builder/tools#tools-api).

## Test your tools

Before assigning tools to agents, verify they work correctly by testing them. Testing helps ensure your tool returns useful results and handles parameters correctly.
If you didn't select **Save and test** immediately:
1. Find your tool in the Tools list.
2. Click the test icon (play button) associated with your tool.

![Test icon (play button) for running tool tests](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/images/test-icon.png)

1. Enter test data based on your tool type:
   - **For ES|QL tools with parameters**: Enter realistic test values for each parameter in the **Inputs** section.
- **For Index search tools**: Enter a sample search query to test the search functionality.
2. Select **Submit** to run the test.
3. Review the Response section to verify:
   - The tool executes without errors.
- Results are returned in the expected format.
- The data matches your expectations.


## Assign tools to agents

To start using a custom tool, you must assign it to a [custom agent](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/custom-agents).
<applies-switch>
  <applies-item title="{ stack: ga 9.4+, serverless: ga }" applies-to="Elastic Cloud Serverless: Generally available, Elastic Stack: Planned">
    1. Select the agent from the agent selector in the left sidebar.
    2. Expand the **Customize** accordion and select **Tools**.
    3. Click **Add tool** and select the tools to assign.
  </applies-item>

  <applies-item title="{ stack: ga =9.3 }" applies-to="Elastic Stack: Generally available in 9.3">
    1. Navigate to the agent configuration page.
    2. Select the **Tools** tab.
    3. Add the desired tools to the agent.
    4. Save the agent configuration.
  </applies-item>
</applies-switch>


## Best practices

Follow these guidelines to create tools that agents can use effectively.

### Naming conventions

The Tool ID is a critical identifier. Use a namespace prefix to group tools logically, which helps the LLM understand tool relationships and prevents naming collisions.
**Recommended pattern**: `domain.action_entity` or `system.function`
**Examples**:
- `finance.search_ticker`
- `support.get_ticket_details`
- `ecommerce.cancel_order`


### Writing effective tool descriptions

A strong description explains what the tool does, when to use it, and what limitations exist. Include these components:
- **Core purpose**: A high-level summary of what the tool actually does.
- **Trigger**: When should this be called?
- **Action**: What specific data does it retrieve or modify?
- **Limitations**: Are there constraints (for example, "returns max 50 rows" or "data is 24 hours old")?
- **Relationships**: How does it relate to other tools?

<tip>
  Not sure whether logic belongs in a tool description or in the agent's custom instructions? Refer to [Custom instructions, tool descriptions, or user input](/docs/explore-analyze/ai-features/agent-builder/prompt-engineering#custom-instructions-tool-descriptions-or-user-input).
</tip>


#### Example: Customer support (retrieval)

- **Tool ID**: `support.search_articles`
- **Description**: "Searches the internal Knowledge Base for technical support articles. Use this tool when a user asks about error codes, troubleshooting steps, or product configurations.
  - Input: Requires a natural language query string.
- Limitations: Returns a maximum of 3 articles.
- Note: If this tool returns irrelevant results, try the `support.search_tickets` tool to see how similar historical issues were resolved."


#### Example: Finance (data fetching)

- **Tool ID**: `finance.get_transaction_history`
- **Description**: "Retrieves a list of transactions for a specific user account ID.
  - Parameters: `account_id` (required), `start_date` (optional, defaults to 30 days ago).
- Usage: Use this to analyze spending patterns or find specific charges.
- Constraint: Data is updated nightly; do not use it for real-time balance checks (use `finance.get_realtime_balance` for that)."


### Additional tips

- **Limit scope**: Focus each tool on a specific task rather than creating overly complex tools.
- **Use meaningful parameter names**: Choose names that clearly indicate what the parameter represents.
- **Include `LIMIT` clauses in ES|QL queries**: Prevent returning excessive results.
- **Use labels**: Add relevant labels to make tools easier to find and organize.
- **Limit tool count**: More tools are not always better. Keep each agent focused with a limited number of relevant tools.


## Related pages

- [Best practices for prompt engineering in Elastic Agent Builder](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/prompt-engineering)
- [Tools in Elastic Agent Builder](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/tools)
- [Elastic Agent Builder built-in tools reference](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/tools/builtin-tools-reference)
- [Elastic Agent Builder Kibana APIs overview > Tools APIs](/docs/explore-analyze/ai-features/agent-builder/kibana-api#tools-apis)