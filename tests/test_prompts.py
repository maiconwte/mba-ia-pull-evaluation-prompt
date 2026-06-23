"""
Testes automatizados para validacao do prompt otimizado v2.

Sao 6 testes obrigatorios definidos na spec (.cursor/docs/specs.md):
  1. test_prompt_has_system_prompt
  2. test_prompt_has_role_definition
  3. test_prompt_mentions_format
  4. test_prompt_has_few_shot_examples
  5. test_prompt_no_todos
  6. test_minimum_techniques

Rodar: pytest tests/test_prompts.py -v
"""
import pytest
import yaml
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def load_prompts(file_path):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_system_text(data: dict) -> str:
    """Extrai o conteudo do system prompt do formato messages[]."""
    for msg in data.get("messages", []):
        if isinstance(msg, dict) and "system" in msg:
            return msg["system"] or ""
    return ""


def get_full_text(data: dict) -> str:
    """Concatena todo o texto do prompt (system + human + ...)."""
    parts = []
    for msg in data.get("messages", []):
        if not isinstance(msg, dict):
            continue
        for value in msg.values():
            if value:
                parts.append(str(value))
    return "\n".join(parts)


@pytest.fixture(scope="module")
def prompt_data():
    return load_prompts(PROMPT_FILE)


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system' existe nas messages e nao esta vazio."""
        system_text = get_system_text(prompt_data)
        assert system_text.strip(), "O system prompt esta ausente ou vazio"

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex.: 'Voce e um Product Owner')."""
        system_text = get_system_text(prompt_data)
        assert "Você é" in system_text, (
            "O system prompt nao define uma persona. "
            "Use 'Voce e um [papel]' para definir o papel do assistente."
        )

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrao."""
        system_text = get_system_text(prompt_data)
        format_indicators = [
            "Como um",
            "Critérios de Aceitação",
            "Given",
            "Dado que",
            "Quando",
            "Então",
            "Markdown",
            "##",
        ]
        found = [kw for kw in format_indicators if kw in system_text]
        assert found, (
            "O prompt nao especifica o formato de saida esperado. "
            f"Nenhum dos indicadores encontrados: {format_indicators}"
        )

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contem exemplos de entrada/saida (Few-shot)."""
        system_text = get_system_text(prompt_data)
        has_bug_example = (
            "BUG REPORT:" in system_text or "bug_report" in system_text.lower()
        )
        has_story_example = (
            "USER STORY:" in system_text or "Como um" in system_text
        )
        assert has_bug_example and has_story_example, (
            "O prompt nao contem exemplos de few-shot. "
            "Inclua pelo menos um par BUG REPORT / USER STORY no system prompt."
        )

    def test_prompt_no_todos(self, prompt_data):
        """Garante que nao restou nenhum [TODO]/FIXME/XXX no texto."""
        full_text = get_full_text(prompt_data)
        todo_markers = ["[TODO]", "TODO", "FIXME", "XXX"]
        found = [marker for marker in todo_markers if marker in full_text]
        assert not found, (
            f"O prompt contem marcadores inacabados: {found}. "
            "Remova ou substitua antes de publicar."
        )

    def test_minimum_techniques(self, prompt_data):
        """Verifica se pelo menos 2 tecnicas de prompt engineering foram aplicadas."""
        system_text = get_system_text(prompt_data)
        full_text = get_full_text(prompt_data)

        techniques_found: list[str] = []

        if "Você é" in system_text:
            techniques_found.append("Role Prompting")

        few_shot_markers = ["BUG REPORT:", "USER STORY:", "---"]
        if sum(1 for m in few_shot_markers if m in system_text) >= 2:
            techniques_found.append("Few-Shot Prompting")

        if any(kw in system_text for kw in ["SEMPRE", "NUNCA", "obrigatório", "REGRAS"]):
            techniques_found.append("Explicit Rules")

        if any(
            kw in system_text
            for kw in ["edge case", "Edge Case", "EDGE CASE", "Se o bug", "Se o relato"]
        ):
            techniques_found.append("Edge Case Handling")

        if any(
            kw in full_text
            for kw in ["raciocine", "pense", "antes de escrever", "raciocínio", "passo a passo"]
        ):
            techniques_found.append("Chain-of-Thought")

        if any(
            kw in system_text
            for kw in ["Como um", "Dado que", "Quando", "Então", "Given", "When", "Then"]
        ):
            techniques_found.append("Explicit Output Format")

        assert len(techniques_found) >= 2, (
            f"Apenas {len(techniques_found)} tecnica(s) detectada(s): {techniques_found}. "
            "O minimo exigido sao 2 tecnicas de prompt engineering."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
