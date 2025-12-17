from __future__ import annotations

from app.policy import build_system_prompt


def test_policy_contains_key_constraints():
    p = build_system_prompt("en")
    assert "factual" in p.lower()
    assert "do not provide medical advice".lower() in p.lower()
    assert "tools" in p.lower()


