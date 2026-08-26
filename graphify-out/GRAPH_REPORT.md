# Graph Report - PixelDevs  (2026-08-27)

## Corpus Check
- 11 files · ~242,076 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 107 nodes · 149 edges · 20 communities (14 shown, 6 thin omitted)
- Extraction: 84% EXTRACTED · 15% INFERRED · 1% AMBIGUOUS · INFERRED: 23 edges (avg confidence: 0.81)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1d0e59d7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- nodes.py
- Multi-Agent System
- Project Dependencies
- Graphify
- script.js
- PixelDevs
- opencode.json
- utils.py
- graphify.js
- server.py
- Output Deck
- Supervisor Agent Avatar Image
- tester.png (image - unreadable)
- test_smoke.py
- AgentState
- state.py
- get_file

## God Nodes (most connected - your core abstractions)
1. `AgentState` - 14 edges
2. `developer_node()` - 9 edges
3. `Project Dependencies` - 9 edges
4. `reviewer_node()` - 8 edges
5. `Multi-Agent System` - 8 edges
6. `create_workflow()` - 7 edges
7. `get_file()` - 6 edges
8. `extract_files_from_artifact()` - 6 edges
9. `validate_code_syntax()` - 6 edges
10. `get_agent_model()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `create_workflow()` --indirect_call--> `developer_node()`  [INFERRED]
  graph.py → nodes.py
- `developer_node()` --uses--> `AgentState`  [INFERRED]
  nodes.py → state.py
- `reviewer_node()` --calls--> `get_agent_model()`  [EXTRACTED]
  nodes.py → config.py
- `reviewer_node()` --calls--> `get_system_rules()`  [EXTRACTED]
  nodes.py → config.py
- `create_workflow()` --indirect_call--> `reviewer_node()`  [INFERRED]
  graph.py → nodes.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Graphify Knowledge Graph Concepts** — agents_md_knowledge_graph, agents_md_god_nodes, agents_md_community_structure, agents_md_cross_file_relationships [EXTRACTED 1.00]
- **Project Tech Stack** — requirements_txt_langgraph, requirements_txt_langchain_core, requirements_txt_google_generativeai, requirements_txt_python_dotenv, requirements_txt_supabase, requirements_txt_watchdog, requirements_txt_tenacity, requirements_txt_fastapi, requirements_txt_uvicorn [EXTRACTED 1.00]
- **Multi-Agent Workflow** — static_index_html_supervisor_agent, static_index_html_developer_agent, static_index_html_reviewer_agent, static_index_html_tester_agent [INFERRED 0.85]

## Communities (20 total, 6 thin omitted)

### Community 0 - "nodes.py"
Cohesion: 0.27
Nodes (7): get_agent_model(), get_system_rules(), Returns the Gemma model. We use this because it has a 30 RPM limit, preventing…, Returns the strict rules for the agent. We inject these directly into the user…, developer_node(), Write a file into the VFS. Returns a new state dict (immutable-safe)., set_file()

### Community 1 - "Multi-Agent System"
Cohesion: 0.24
Nodes (11): Developer Agent, Download Button, Generated Artifact, Initialize Agents Button, Language Select, Multi-Agent System, Project Requirement Input, Reviewer Agent (+3 more)

### Community 2 - "Project Dependencies"
Cohesion: 0.24
Nodes (10): Project Dependencies, FastAPI, Google Generative AI, LangChain Core, LangGraph, Python Dotenv, Supabase, Tenacity (+2 more)

### Community 3 - "Graphify"
Cohesion: 0.25
Nodes (8): Community Structure, Cross-file Relationships, God Nodes, graph.json, GRAPH_REPORT.md, Graphify, Knowledge Graph, wiki/index.md

### Community 4 - "script.js"
Cohesion: 0.39
Nodes (5): delay(), handleEvent(), resetAll(), startProcess(), typeWriter()

### Community 5 - "PixelDevs"
Cohesion: 0.40
Nodes (5): AI Brain, DB Local, Mission Control, PixelDevs, style.css

### Community 6 - "opencode.json"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

### Community 7 - "utils.py"
Cohesion: 0.25
Nodes (6): apply_search_replace_patch(), CodeRunner, Execute files in E2B cloud sandbox. Requires E2B_API_KEY for secure execution., Apply a localized search-and-replace patch to the original content., Runs Python code safely in an isolated subprocess., run_in_e2b_sandbox()

### Community 16 - "test_smoke.py"
Cohesion: 0.21
Nodes (11): parametrize, _backend_path(), Smoke tests verifying backend modules import without syntax errors., test_backend_module_compiles(), test_backend_module_imports(), test_extract_files_from_artifact(), test_validate_code_syntax(), extract_files_from_artifact() (+3 more)

### Community 17 - "AgentState"
Cohesion: 0.62
Nodes (6): create_workflow(), reviewer_node(), supervisor_node(), tester_node(), AgentState, TypedDict

### Community 18 - "state.py"
Cohesion: 0.29
Nodes (6): delete_file(), get_active_file(), list_files(), Remove a file from the VFS. Clears active_file if it matches. Returns a new…, Return sorted list of all file paths in the VFS., Return the currently active file path, or empty string.

## Ambiguous Edges - Review These
- `reviewer.png` → `reviewer.png`  [AMBIGUOUS]
  static/reviewer.png · relation: references

## Knowledge Gaps
- **24 isolated node(s):** `$schema`, `.opencode/plugins/graphify.js`, `Supervisor Agent Avatar Image`, `Download Button`, `Language Select` (+19 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `reviewer.png` and `reviewer.png`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `extract_files_from_artifact()` connect `test_smoke.py` to `nodes.py`, `utils.py`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `validate_code_syntax()` connect `test_smoke.py` to `nodes.py`, `AgentState`, `utils.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `AgentState` connect `AgentState` to `nodes.py`, `state.py`, `get_file`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `AgentState` (e.g. with `create_workflow()` and `developer_node()`) actually correct?**
  _`AgentState` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `developer_node()` (e.g. with `create_workflow()` and `AgentState`) actually correct?**
  _`developer_node()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `reviewer_node()` (e.g. with `create_workflow()` and `AgentState`) actually correct?**
  _`reviewer_node()` has 2 INFERRED edges - model-reasoned connections that need verification._