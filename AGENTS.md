# AGENTS.md - PixelDevs Engineering Protocol

## 1. Project Overview & Identity
PixelDevs is an Autonomous Multi-Agent Software Agency engine. It uses a cyclical LangGraph state machine where specialized AI personas (Supervisor, Developer, Reviewer, Tester) collaborate to architect, implement, review, and test software. The project is styled as a 16-bit retro pixel-art office backed by an event-driven FastAPI WebSocket engine and a sandboxed browser preview canvas.

---

## 2. Component Ownership & Domain Boundaries
* `config.py` - AI Model configurations, system prompts, role constraints, and environment parameters.
* `state.py` - Typed definitions of AgentState, Virtual File System (VFS) schemas, and event payloads.
* `nodes.py` - Agent logic functions, LLM invoke wrappers, and AST/diff handlers.
* `graph.py` - LangGraph workflow compilation, cyclic conditional edge routing, and checkpoints.
* `server.py` - FastAPI WebSocket gateway, lifecycle events, and client communication.
* `utils.py` - Cloud sandboxing interfaces, execution runners, and diff parsers.
* `frontend/` - Next.js (App Router), Tailwind CSS, Framer Motion, and Retro UI components.

---

## 3. Absolute Rules: What AI Must NEVER Do
1. NEVER overwrite an entire file when applying a bug fix. Always perform localized search/replace or surgical diff patching.
2. NEVER use lazy placeholders like `# TODO: implement later` or `# ... rest of code unchanged ...`. Always generate complete, functional syntax.
3. NEVER mix modern smooth SaaS styles (rounded-xl, modern sans-serifs) with the 16-bit pixel aesthetic. Maintain the retro design system across all UI elements.
4. NEVER execute unvalidated arbitrary shell commands on the host machine. All untrusted code must route through isolated cloud micro-sandboxes.
5. NEVER proceed to subsequent tasks if a local unit test or CodeRabbit review flags an active regression.

---

## 4. Execution & Planning Protocol
Before modifying any files:
1. State the objective, affected files, and dependency impacts in a concise summary.
2. Formulate a step-by-step modification plan.
3. Apply changes strictly within the specified feature branch.
4. Run validation checks to ensure zero regressions before reporting completion.

---

## 5. Human-in-the-Loop (HITL) Checkpoints
Halt execution and request user approval in the following scenarios:
* Adding or modifying database schemas / migrations.
* Introducing new third-party paid APIs or cloud dependencies.
* Modifying core LangGraph routing logic or conditional edge rules.
* Deleting files or refactoring existing public API contracts.

---

## 6. Verification & Reporting Format
When reporting back after a task, use this format:
- **Status:** [SUCCESS / BLOCKED]
- **Files Modified:** List of file paths changed.
- **Verification Performed:** Execution output and test results.
- **Key Decisions:** Summary of structural changes made.
- **Next Step:** The immediate next action item on the roadmap.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
