from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "create-econ-paper-video"


def test_skill_frontmatter_and_interface():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\n")
    _, frontmatter, body = text.split("---", 2)
    metadata = yaml.safe_load(frontmatter)
    assert metadata["name"] == "create-econ-paper-video"
    assert set(metadata) == {"name", "description"}
    assert "TODO" not in body

    interface = yaml.safe_load((SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    prompt = interface["interface"]["default_prompt"]
    assert "$create-econ-paper-video" in prompt
