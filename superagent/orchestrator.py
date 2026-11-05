import asyncio
from .agents import AGENTS, project_system_prompt
from .config import get_settings
from .github import audit_repository
from .llm import chat
from .projects import PROJECTS, get_project
from .store import save_run


async def _audit_one(project):
    try:
        facts = await audit_repository(project.repository)
        summary = await chat(
            project_system_prompt(project, "auditor"),
            "Review this live GitHub metadata snapshot. Give: current state, open PR/branch risks, next 3 actions, and confidence. "
            "Do not infer source-code correctness from metadata.\n\n" + str(facts),
        )
        return {"project_key": project.key, "name": project.name, "status": "audited", "facts": facts, "analysis": summary}
    except Exception as exc:
        return {"project_key": project.key, "name": project.name, "status": "blocked", "blocker": str(exc)}


async def portfolio_audit() -> dict:
    semaphore = asyncio.Semaphore(max(1, get_settings().max_parallel_repos))
    async def bounded(project):
        async with semaphore:
            return await _audit_one(project)
    results = await asyncio.gather(*(bounded(p) for p in PROJECTS))
    result = {"projects_total": len(PROJECTS), "audited": sum(x["status"] == "audited" for x in results),
              "blocked": sum(x["status"] == "blocked" for x in results), "projects": results}
    save_run(None, "portfolio_audit", "completed" if not result["blocked"] else "partial", "Audit all 11 ERP repositories", result)
    return result


async def run_project_task(project_key: str, request: str, role: str = "router") -> dict:
    project = get_project(project_key)
    if not project:
        raise ValueError(f"Unknown project key: {project_key}")
    if role not in AGENTS:
        raise ValueError(f"Unknown agent role: {role}")
    facts = await audit_repository(project.repository)
    prompt = (
        f"User request: {request}\n\nVerified GitHub metadata: {facts}\n\n"
        "Return a practical, ordered work plan with acceptance criteria, impacted files to inspect next, "
        "branch name suggestion, security considerations, and validation steps. Do not claim implementation, "
        "commits, tests or merges have happened. State explicitly what requires a checkout or write-enabled worker."
    )
    answer = await chat(project_system_prompt(project, role), prompt)
    result = {"project_key": project.key, "repository": project.repository, "role": role,
              "verified_metadata": facts, "plan": answer, "execution_state": "plan_only"}
    save_run(project.key, role, "completed", request, result)
    return result
