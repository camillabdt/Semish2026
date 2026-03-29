import pandas as pd
import os
import time
from groq import Groq
from dotenv import load_dotenv

CSV_FILES = [
    "mapeamento_redflags_extraidas.csv",
    "mapeamento_redflags_extraidas1.csv",
    "mapeamento_redflags_extraidas3.csv",
]

OUTPUT_CLUSTERS = "clusters_redflags_amostra.txt"

JUIZ_MODELO = "openai/gpt-oss-20b"

SYSTEM_PROMPT = (
    "Você é um pesquisador em segurança de IA. "
    "Seu objetivo é AGRUPAR red flags (sinais de alerta) em poucas categorias conceituais "
    "coerentes, que possam servir como base para uma taxonomia."
)

USER_PROMPT_TEMPLATE = (
    "Abaixo está uma lista de Red Flags extraídas de prompts maliciosos para LLMs.\n"
    "TAREFA:\n"
    "1) Agrupe essas Red Flags em UM NÚMERO PEQUENO de categorias (por exemplo, 6 a 10).\n"
    "2) Para cada categoria, dê:\n"
    "   - Um NOME CURTO para a categoria.\n"
    "   - Uma DESCRIÇÃO sucinta.\n"
    "   - Uma LISTA das Red Flags que pertencem a essa categoria (usando exatamente o texto original de cada Red Flag).\n\n"
    "IMPORTANTE:\n"
    "- NÃO invente novas Red Flags.\n"
    "- Use APENAS as Red Flags fornecidas abaixo.\n\n"
    "LISTA DE RED FLAGS:\n{lista_flags}\n\n"
    "Agora produza a saída seguindo este formato EXATO (sem comentários):\n\n"
    "CATEGORIA 1: <nome_categoria_1>\n"
    "DESCRIÇÃO: <texto_curto>\n"
    "REDFLAGS:\n"
    "- <redflag 1 exatamente como fornecida>\n"
    "- <redflag 2 exatamente como fornecida>\n"
    "...\n\n"
    "CATEGORIA 2: <nome_categoria_2>\n"
    "DESCRIÇÃO: <texto_curto>\n"
    "REDFLAGS:\n"
    "- <redflag X>\n"
    "- <redflag Y>\n"
    "..."
)


def extrair_redflags_unicas_dos_csvs():
    dfs = [pd.read_csv(f) for f in CSV_FILES]
    df = pd.concat(dfs, ignore_index=True)

    redflags = set()

    for txt in df["red_flags_detectadas"].astype(str):
        for linha in txt.splitlines():
            linha = linha.strip()
            if linha.startswith("- "):
                item = linha[2:].strip()
                if ":" in item:
                    nome = item.split(":", 1)[0].strip()
                else:
                    nome = item
                if nome:
                    redflags.add(nome)

    redflags_list = sorted(redflags)
    print(f"⚙️ Extraídas {len(redflags_list)} red flags únicas dos CSVs.")
    return redflags_list


def main():
    load_dotenv()
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    redflags = extrair_redflags_unicas_dos_csvs()

    # Amostra para caber no contexto do modelo (ajuste o tamanho se precisar)
    amostra = pd.Series(redflags).sample(300, random_state=42).tolist()

    lista_flags_str = "\n".join(f"- {f}" for f in amostra)
    user_prompt = USER_PROMPT_TEMPLATE.format(lista_flags=lista_flags_str)

    chat = client.chat.completions.create(
        model=JUIZ_MODELO,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    resposta = chat.choices[0].message.content

    with open(OUTPUT_CLUSTERS, "w", encoding="utf-8") as f:
        f.write(resposta)

    print(f"✅ Clustering salvo em {OUTPUT_CLUSTERS}.")
    print("Revise os nomes e descrições das categorias que o modelo propôs.")


if __name__ == "__main__":
    main()
