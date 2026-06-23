"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Le os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida estrutura minima do YAML
3. Faz push PUBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descricao, tecnicas utilizadas)

Os metadados (descricao + tags) ficam neste arquivo porque versionar
metadata junto com o conteudo do prompt no YAML obriga a republicar
toda vez que so a descricao muda.
"""

import os
import sys
import yaml
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import check_env_vars, print_section_header

load_dotenv()

PROMPT_METADATA = {
    "bug_to_user_story_v2": {
        "file": "prompts/bug_to_user_story_v2.yml",
        "description": (
            "Prompt otimizado para converter bug reports em User Stories ageis. "
            "Tecnicas aplicadas: Role Prompting (Product Owner senior), "
            "Few-Shot Learning (4 exemplos cobrindo SIMPLES/MEDIO/COMPLEXO), "
            "Chain of Thought via scratchpad implicito, Explicit Rules (SEMPRE/NUNCA), "
            "Edge Case Handling, Explicit Output Format (Given-When-Then em PT), "
            "Separacao System/User Prompt e Positive Framing."
        ),
        "tags": [
            "bug-analysis",
            "user-story",
            "product-owner",
            "few-shot",
            "chain-of-thought",
            "role-prompting",
            "edge-cases",
            "given-when-then",
            "agile",
            "optimized",
        ],
    }
}


def load_prompt_file(file_path: str) -> dict | None:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ Arquivo nao encontrado: {file_path}")
        return None
    except yaml.YAMLError as e:
        print(f"❌ Erro ao parsear YAML: {e}")
        return None


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """Valida estrutura minima do prompt antes do push.

    Returns:
        (is_valid, errors)
    """
    errors: list[str] = []

    if not prompt_data:
        return False, ["YAML vazio ou invalido"]

    messages = prompt_data.get("messages", [])
    if not messages:
        errors.append("Lista 'messages' vazia ou ausente")

    roles = [list(m.keys())[0] for m in messages if isinstance(m, dict) and m]
    if "system" not in roles:
        errors.append("system prompt ausente")
    if "human" not in roles:
        errors.append("human prompt ausente")

    full_text = " ".join(
        str(v) for m in messages if isinstance(m, dict) for v in m.values()
    )
    if "{bug_report}" not in full_text:
        errors.append("Variavel {bug_report} nao encontrada nas mensagens")

    system_text = next(
        (m["system"] for m in messages if isinstance(m, dict) and "system" in m), ""
    )
    if len(system_text.strip()) < 200:
        errors.append("system prompt muito curto (< 200 chars) — verifique o conteudo")

    for marker in ("[TODO]", "FIXME", "XXX"):
        if marker in full_text:
            errors.append(f"Encontrado marcador inacabado: {marker}")

    return (len(errors) == 0, errors)


def build_prompt_template(prompt_data: dict) -> ChatPromptTemplate:
    """Monta ChatPromptTemplate a partir do dict YAML."""
    pairs = []
    for msg in prompt_data.get("messages", []):
        if not isinstance(msg, dict):
            continue
        if "system" in msg:
            pairs.append(("system", msg["system"]))
        elif "human" in msg:
            pairs.append(("human", msg["human"]))
        elif "ai" in msg:
            pairs.append(("ai", msg["ai"]))
    return ChatPromptTemplate.from_messages(pairs)


def resolve_username(client: Client) -> str:
    """Obtem o handle do tenant para compor {user}/prompt_name.

    Preferencia: USERNAME_LANGSMITH_HUB do .env (alinhado com a spec).
    Fallback: client._get_settings().tenant_handle.
    """
    env_username = os.getenv("USERNAME_LANGSMITH_HUB", "").strip()
    if env_username:
        return env_username
    return client._get_settings().tenant_handle


def push_commit(
    prompt_name: str,
    template: ChatPromptTemplate,
    metadata: dict,
    client: Client,
) -> bool:
    """Faz push publico do prompt no LangSmith Hub."""
    username = resolve_username(client)
    full_name = f"{username}/{prompt_name}"

    try:
        url = client.push_prompt(
            full_name,
            object=template,
            is_public=True,
            description=metadata["description"],
            tags=metadata["tags"],
        )
        print(f"   ✓ Prompt publicado publicamente como {full_name}")
        print(f"   URL: {url}")
        return True
    except Exception as e:
        if "Nothing to commit" in str(e):
            print("   ℹ️  Sem mudancas desde o ultimo commit — prompt ja esta atualizado.")
            print(f"   URL: https://smith.langchain.com/hub/{full_name}")
            return True
        raise


def main() -> int:
    """Funcao principal."""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS PARA O LANGSMITH")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    client = Client()
    username = resolve_username(client)
    print(f"Username Hub: {username}")
    print(f"Prompts a publicar: {list(PROMPT_METADATA.keys())}\n")

    all_succeeded = True

    for prompt_name, metadata in PROMPT_METADATA.items():
        print_section_header(f"Prompt: {prompt_name}", char="-", width=40)

        print(f"Carregando {metadata['file']}...")
        prompt_data = load_prompt_file(metadata["file"])
        if prompt_data is None:
            all_succeeded = False
            continue

        print(f"Validando '{prompt_name}'...")
        is_valid, errors = validate_prompt(prompt_data)
        if not is_valid:
            print("❌ Validacao falhou:")
            for err in errors:
                print(f"   - {err}")
            all_succeeded = False
            continue
        print("   ✓ Validacao passou")

        template = build_prompt_template(prompt_data)

        try:
            push_commit(prompt_name, template, metadata, client)
        except Exception as e:
            print(f"❌ Erro ao fazer push: {e}")
            all_succeeded = False

    print()
    if all_succeeded:
        print("✅ Todos os prompts foram publicados com sucesso!")
        print("\nVerifique em: https://smith.langchain.com/prompts")
        return 0
    print("❌ Um ou mais prompts falharam no push.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
