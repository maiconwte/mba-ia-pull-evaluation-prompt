"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

Usa Client.pull_prompt do langsmith (API canonica na versao 0.2.x)
e serializa a ChatPromptTemplate em um formato YAML reutilizavel pelo
restante do pipeline (push_prompts.py e tests/test_prompts.py).
"""

import sys
from dotenv import load_dotenv
from langsmith import Client
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

SOURCE_PROMPT = "leonanluppi/bug_to_user_story_v1"
TARGET_YAML = "prompts/bug_to_user_story_v1.yml"


def prompt_to_dict(prompt) -> dict:
    """Converte ChatPromptTemplate em dict serializavel para YAML.

    Estrutura de saida:
        input_variables: [<vars>]
        messages:
          - <role>: <template>
          - ...
    """
    messages = []
    for msg in prompt.messages:
        role = msg.__class__.__name__.replace("MessagePromptTemplate", "").lower()
        template = msg.prompt.template
        messages.append({role: template})

    return {
        "input_variables": list(prompt.input_variables),
        "messages": messages,
    }


def pull_prompts_from_langsmith() -> bool:
    """Faz pull do prompt v1 do Hub e salva em YAML local."""
    print(f"Conectando ao LangSmith e puxando '{SOURCE_PROMPT}'...")

    client = Client()
    prompt = client.pull_prompt(SOURCE_PROMPT)

    data = prompt_to_dict(prompt)
    success = save_yaml(data, TARGET_YAML)

    if success:
        print(f"   ✓ Prompt salvo em {TARGET_YAML}")
        print(f"   Variaveis: {data['input_variables']}")
        print(f"   Mensagens: {len(data['messages'])}")
    return success


def main() -> int:
    """Funcao principal."""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    try:
        if pull_prompts_from_langsmith():
            print("\n✅ Pull concluido com sucesso!")
            return 0
        print("\n❌ Pull falhou ao salvar o YAML.")
        return 1
    except Exception as e:
        print(f"\n❌ Erro ao fazer pull: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
