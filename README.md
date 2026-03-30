# Extração e Mapeamento de Red Flags em Prompts de Jailbreak

Este repositório contém os scripts utilizados no experimento de identificação automática de **Red Flags** em prompts de jailbreak de modelos de linguagem, parte de um trabalho submetido ao SEMISH/CSBC.

Os códigos realizam:
- leitura de um dataset em formato Parquet contendo prompts de jailbreak;
- chamada a um modelo de linguagem (via API Groq) para identificar Red Flags em cada prompt;
- geração de um arquivo CSV com o “caderno de notas” das Red Flags detectadas;
- uso opcional de um utilitário para visualizar arquivos Parquet em linha de comando.

## Estrutura do repositório

- `redflagspj.py`: script principal de extração e mapeamento de Red Flags a partir do dataset de jailbreaks.
- `mapeamento_redflags_extraidas1.csv`: exemplo de saída já gerada, contendo os prompts analisados e as Red Flags identificadas.
- `abrirparquet.py`: utilitário **opcional** para abrir e visualizar integralmente arquivos `.parquet` no terminal.
- arquivos `*.sample`, `.gitignore`: arquivos padrão de configuração do Git, sem impacto direto no experimento.

## Dependências

Antes de executar os scripts, instale as dependências Python:

```bash
pip install pandas pyarrow python-dotenv groq
```

- `pandas` e `pyarrow` para leitura de arquivos Parquet.
- `python-dotenv` para carregar variáveis de ambiente (chave da API).
- `groq` para acesso ao modelo de linguagem usado como “juiz” de Red Flags.

## Configuração

1. Crie um arquivo `.env` na raiz do projeto com a sua chave de API da Groq:

   ```bash
   GROQ_API_KEY=seu_token_aqui
   ```

2. Coloque o arquivo Parquet com o dataset de jailbreaks no mesmo diretório dos scripts e ajuste o nome em `INPUT_PARQUET` dentro de `redflagspj.py`, se necessário:

   ```python
   INPUT_PARQUET = "0000 (2).parquet"
   ```

3. Opcionalmente, altere o nome do arquivo de saída:

   ```python
   OUTPUT_MAPPING = "mapeamento_redflags_extraidas.csv"
   ```

## Script principal: `redflagspj.py`

### Objetivo

Executar um pipeline de extração em que um modelo de linguagem (atuando como “juiz”) analisa cada prompt de jailbreak e retorna uma lista de Red Flags curtas, com breve descrição.

### Lógica

1. Carrega o dataset Parquet contendo a coluna `jailbreak_query`.
2. Define um conjunto de modelos “juízes” (no código, `qwen/qwen3-32b`, com possibilidade de incluir outros).
3. Usa um `SYSTEM_PROMPT` que posiciona o modelo como especialista em segurança cibernética e detecção de padrões de risco.
4. Usa um `PROMPT_MAPEAMENTO` que instrui explicitamente a devolver apenas uma lista de nomes curtos de Red Flags com descrições sucintas.
5. Itera sobre todas as linhas do dataset (há amostra comentada para rodar em subset) e faz chamadas à API da Groq, com espera de 2 segundos entre requisições.
6. Para cada item, registra:
   - `id_original`: índice da linha no dataset,
   - `modelo_extrator`: identificador do modelo “juiz”,
   - `prompt_analisado`: início do texto do prompt,
   - `red_flags_detectadas`: texto retornado pelo modelo.
7. Ao final, salva tudo em `OUTPUT_MAPPING` no formato CSV.

### Execução

```bash
python redflagspj.py
```

Ao término, o script imprime uma mensagem de confirmação indicando o caminho do CSV gerado.

O arquivo CSV resultante terá estrutura semelhante a `mapeamento_redflags_extraidas1.csv`.

## Arquivo de exemplo: `mapeamento_redflags_extraidas1.csv`

Este arquivo ilustra o tipo de saída obtida pelo pipeline: cada linha corresponde a um prompt de jailbreak analisado por um modelo “juiz” (por exemplo, um modelo da família LLaMA), com a lista de Red Flags em linguagem natural.

Colunas principais:

- `id_original`: índice do prompt no dataset original.
- `modelo_extrator`: modelo utilizado para a extração das Red Flags.
- `prompt_analisado`: trecho inicial do prompt de jailbreak.
- `red_flags_detectadas`: texto livre com as Red Flags identificadas e suas descrições.

Este CSV é utilizado na etapa posterior de consolidação da taxonomia final de Red Flags (por exemplo, redução para 16 categorias) descrita no artigo.

## Utilitário opcional: `abrirparquet.py`

### Objetivo

Este script é um utilitário **opcional** para inspeção manual dos dados de entrada em formato Parquet diretamente no terminal.

### Lógica

1. Recebe o caminho de um arquivo `.parquet` via linha de comando.
2. Lê o arquivo com `pandas.read_parquet`.
3. Configura as opções de exibição para mostrar todas as linhas e colunas.
4. Imprime o DataFrame completo.
5. Trata erros simples, como arquivo não encontrado.

### Execução

```bash
python abrirparquet.py arquivo.parquet
```

Exemplo:

```bash
python abrirparquet.py "0000 (2).parquet"
```

## Fluxo de uso típico no experimento

1. (Opcional) Inspecionar o dataset Parquet de jailbreaks:

   ```bash
   python abrirparquet.py "0000 (2).parquet"
   ```

2. Rodar o pipeline de extração de Red Flags:

   ```bash
   python redflagspj.py
   ```

3. Utilizar o CSV gerado (por exemplo, `mapeamento_redflags_extraidas1.csv`) como insumo para análise qualitativa e consolidação da taxonomia final de Red Flags descrita no artigo.
