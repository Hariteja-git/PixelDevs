# Graph Report - PixelDevs  (2026-08-26)

## Corpus Check
- 17 files · ~240,092 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 79 nodes · 104 edges · 16 communities (10 shown, 6 thin omitted)
- Extraction: 76% EXTRACTED · 23% INFERRED · 1% AMBIGUOUS · INFERRED: 24 edges (avg confidence: 0.81)
- Token cost: 1,200 input · 320 output

## Community Hubs (Navigation)
- Backend Core
- Frontend UI
- Tech Stack Dependencies
- Graphify Documentation
- Frontend Script Logic
- UI Layout & Styling
- OpenCode Configuration
- Code Execution Utils
- Graphify Plugin
- API Endpoints
- Output Deck
- Supervisor Avatar
- Tester Avatar

## God Nodes (most connected - your core abstractions)
1. `AgentState` - 9 edges
2. `Project Dependencies` - 9 edges
3. `tester_node()` - 8 edges
4. `Multi-Agent System` - 8 edges
5. `create_workflow()` - 7 edges
6. `developer_node()` - 7 edges
7. `get_agent_model()` - 6 edges
8. `get_system_rules()` - 6 edges
9. `reviewer_node()` - 6 edges
10. `supervisor_node()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `tester_node()` --uses--> `CodeRunner`  [INFERRED]
  nodes.py → utils.py
- `create_workflow()` --indirect_call--> `developer_node()`  [INFERRED]
  graph.py → nodes.py
- `create_workflow()` --indirect_call--> `reviewer_node()`  [INFERRED]
  graph.py → nodes.py
- `create_workflow()` --indirect_call--> `supervisor_node()`  [INFERRED]
  graph.py → nodes.py
- `create_workflow()` --indirect_call--> `tester_node()`  [INFERRED]
  graph.py → nodes.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Multi-Agent Workflow** — static_index_html_supervisor_agent, static_index_html_developer_agent, static_index_html_reviewer_agent, static_index_html_tester_agent [INFERRED 0.85]
- **Project Tech Stack** — requirements_txt_langgraph, requirements_txt_langchain_core, requirements_txt_google_generativeai, requirements_txt_python_dotenv, requirements_txt_supabase, requirements_txt_watchdog, requirements_txt_tenacity, requirements_txt_fastapi, requirements_txt_uvicorn [EXTRACTED 1.00]
- **Graphify Knowledge Graph Concepts** — agents_md_knowledge_graph, agents_md_god_nodes, agents_md_community_structure, agents_md_cross_file_relationships [EXTRACTED 1.00]

## Communities (16 total, 6 thin omitted)

### Community 0 - "Backend Core"
Cohesion: 0.28
Nodes (12): get_agent_model(), get_system_rules(), Returns the Gemma model. We use this because it has a 30 RPM limit, preventing…, Returns the strict rules for the agent. We inject these directly into the user…, create_workflow(), developer_node(), extract_code(), reviewer_node() (+4 more)

### Community 1 - "Frontend UI"
Cohesion: 0.24
Nodes (11): Developer Agent, Download Button, Generated Artifact, Initialize Agents Button, Language Select, Multi-Agent System, Project Requirement Input, Reviewer Agent (+3 more)

### Community 2 - "Tech Stack Dependencies"
Cohesion: 0.24
Nodes (10): Project Dependencies, FastAPI, Google Generative AI, LangChain Core, LangGraph, Python Dotenv, Supabase, Tenacity (+2 more)

### Community 3 - "Graphify Documentation"
Cohesion: 0.25
Nodes (8): Community Structure, Cross-file Relationships, God Nodes, graph.json, GRAPH_REPORT.md, Graphify, Knowledge Graph, wiki/index.md

### Community 4 - "Frontend Script Logic"
Cohesion: 0.39
Nodes (5): delay(), handleEvent(), resetAll(), startProcess(), typeWriter()

### Community 5 - "UI Layout & Styling"
Cohesion: 0.40
Nodes (5): AI Brain, DB Local, Mission Control, PixelDevs, style.css

### Community 6 - "OpenCode Configuration"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

## Ambiguous Edges - Review These
- `reviewer.png` → `reviewer.png`  [AMBIGUOUS]
  static/reviewer.png · relation: references

## Knowledge Gaps
- **24 isolated node(s):** `$schema`, `.opencode/plugins/graphify.js`, `God Nodes`, `Community Structure`, `Cross-file Relationships` (+19 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `reviewer.png` and `reviewer.png`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `tester_node()` connect `Backend Core` to `Code Execution Utils`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `AgentState` (e.g. with `create_workflow()` and `developer_node()`) actually correct?**
  _`AgentState` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `tester_node()` (e.g. with `create_workflow()` and `AgentState`) actually correct?**
  _`tester_node()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Multi-Agent System` (e.g. with `Initialize Agents Button` and `Language Select`) actually correct?**
  _`Multi-Agent System` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `create_workflow()` (e.g. with `developer_node()` and `reviewer_node()`) actually correct?**
  _`create_workflow()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `.opencode/plugins/graphify.js`, `God Nodes` to the rest of the system?**
  _24 weakly-connected nodes found - possible documentation gaps or missing edges._