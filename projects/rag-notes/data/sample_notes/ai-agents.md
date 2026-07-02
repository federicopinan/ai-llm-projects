# AI Agents

An AI agent is a language model wrapped in a loop that lets it observe a
state, decide on an action, execute that action, and observe the result
before deciding what to do next. The loop continues until the model decides
the goal is reached or hits a stopping condition.

## Anatomy of an agent

Most agents share the same skeleton.

First, a **goal** expressed in natural language or a structured prompt. This
is what the agent is trying to accomplish.

Second, a set of **tools** the agent can call. Tools are usually ordinary
functions exposed through a schema the model can fill in: a search tool, a
file reader, a calculator, a code interpreter.

Third, a **memory** of past steps. Short-term memory is the recent
conversation; long-term memory can be a vector store or a structured
database.

Fourth, a **controller loop** that decides when to call a tool, when to ask
the user, and when to stop.

## Common patterns

- **Single-shot tool use**: the model picks one tool, reads the result, and
  answers. Useful for retrieval-augmented generation.
- **ReAct**: the model alternates between reasoning steps and tool calls,
  exposing its thinking between actions.
- **Planner-executor**: one model breaks the goal into sub-tasks and another
  model executes them.
- **Multi-agent**: several specialized agents collaborate, each owning a
  slice of the problem.

## Why they matter for notes

Agents turn a notes database from a passive archive into an active
collaborator. Instead of grep, you can ask: "Summarize what I learned about
distributed systems last month, including open questions." The agent
retrieves, condenses, and can even draft follow-up notes.

## Failure modes

Agents can loop forever, call tools with bad arguments, or hide
uncertainty behind confident language. A well-designed agent surfaces its
tool calls, lets the user cancel, and refuses to invent information that is
not in the retrieved context.

## A small working definition

If a system can decide which tool to use, given only a goal, it is an
agent. If every step is hard-coded, it is a workflow.