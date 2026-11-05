from superagent.agents import AGENTS, project_system_prompt
from superagent.projects import PROJECTS, get_project


def test_registry_contains_exactly_eleven_projects():
    assert len(PROJECTS) == 11
    assert len({p.key for p in PROJECTS}) == 11
    assert len({p.repository for p in PROJECTS}) == 11


def test_all_projects_have_agent_context():
    for project in PROJECTS:
        prompt = project_system_prompt(project, "auditor")
        assert project.name in prompt
        assert project.repository in prompt
        assert "feature branch" in prompt


def test_specialist_roles_are_registered():
    assert {"router", "auditor", "competitor", "implementer", "reviewer"} <= set(AGENTS)


def test_unknown_project_returns_none():
    assert get_project("not-a-real-project") is None


def test_retail_and_pos_repositories_are_distinct():
    assert get_project("retail").repository == "senthilsrinivasanmuthaiyan1/retail"
    assert get_project("universal-pos").repository == "senthilsrinivasanmuthaiyan/universal-pos"
