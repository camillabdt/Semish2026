import pandas as pd
from groq import Groq
import os
from dotenv import load_dotenv

def descobrir_taxonomia(input_csv):
    load_dotenv()
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    df = pd.read_csv(input_csv)
    
    # Pegamos uma amostra diversificada das flags detectadas
    # Se o dataset for muito grande, pegamos os textos únicos mais frequentes
    amostra_flags = df['red_flags_detectadas'].astype(str).unique()
    texto_para_analise = "\n---\n".join(amostra_flags[:60]) # Ajuste o limite conforme o contexto

    SYSTEM_PROMPT = (
        "Você é um especialista em segurança de IA e taxonomia de ameaças cibernéticas. "
        "Sua tarefa é analisar uma lista de 'Red Flags' extraídas de prompts de jailbreak e "
        "identificar as categorias fundamentais que as definem."
    )

    PROMPT_DESCOBERTA = (
        "Analise os dados abaixo e crie uma taxonomia exaustiva, mas sem redundâncias. "
        "Não force um número específico de categorias. Agrupe padrões similares em uma única Red Flag. \n\n"
        f"DADOS BRUTOS:\n{texto_para_analise}\n\n"
        "Para cada Red Flag identificada, retorne:\n"
        "1. Nome Técnico da Flag\n"
        "2. Descrição concisa (o que a caracteriza)\n"
        "3. Exemplo curto de gatilho (trigger)\n\n"
        "Responda de forma estruturada para que eu possa usar isso como um 'Codebook' de pesquisa."
    )

    try:
        print("🔍 Analisando padrões para determinar o número de flags...")
        completion = client.chat.completions.create(
            model="qwen-72b-誠", # Modelos maiores são melhores para categorização
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": PROMPT_DESCOBERTA}
            ],
            temperature=0.3 
        )
        
        taxonomia = completion.choices[0].message.content
        
        with open("proposta_taxonomia.txt", "w", encoding="utf-8") as f:
            f.write(taxonomia)
            
        print("✅ Proposta de taxonomia salva em 'proposta_taxonomia.txt'")
        return taxonomia

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    descobrir_taxonomia("mapeamento_redflags_extraidas.csv")