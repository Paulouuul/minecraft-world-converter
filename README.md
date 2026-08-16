# Minecraft World Converter

Conjunto de ferramentas em Python para conversão, gerenciamento, backup e sincronização de mundos do **Minecraft Bedrock Edition**.

O projeto atualmente permite converter mundos Bedrock para arquivos `.mcworld` e sincronizar os dados com a instalação local do Minecraft. A conversão de Bedrock Edition para Java Edition está planejada para uma versão futura e ainda não está implementada.

## Índice

* [Visão Geral](#visão-geral)
* [Status do Projeto](#status-do-projeto)
* [Requisitos](#requisitos)
* [Instalação](#instalação)
* [Configuração](#configuração)
* [Como Usar](#como-usar)
* [Scripts Disponíveis](#scripts-disponíveis)
* [Estrutura de Pastas](#estrutura-de-pastas)
* [Fluxo de Trabalho](#fluxo-de-trabalho)
* [Processamento Paralelo](#processamento-paralelo)
* [Backup](#backup)
* [Solução de Problemas](#solução-de-problemas)
* [Logs](#logs)
* [Git e Arquivos Ignorados](#git-e-arquivos-ignorados)
* [Funcionalidades Futuras](#funcionalidades-futuras)
* [Licença](#licença)

---

## Visão Geral

O **Minecraft World Converter** foi desenvolvido para facilitar o gerenciamento de mundos do Minecraft Bedrock Edition.

Atualmente, o projeto permite:

* Converter pastas de mundos Bedrock para arquivos `.mcworld`.
* Processar múltiplos mundos em paralelo.
* Selecionar mundos específicos para conversão.
* Sincronizar dados do Minecraft entre diretórios de backup e a instalação local.
* Realizar operações de cópia utilizando múltiplos workers.
* Gerenciar backups dos dados originais.
* Configurar caminhos e parâmetros através de um arquivo `.env`.
* Funcionar sem dependências externas obrigatórias.

A conversão de mundos **Bedrock Edition para Java Edition ainda não está implementada**. Existe um script preliminar relacionado a essa funcionalidade, porém ele foi gerado como uma tentativa inicial e não representa um conversor funcional. A implementação definitiva está planejada para o futuro.

---

## Status do Projeto

| Funcionalidade                          | Status           |
| --------------------------------------- | ---------------- |
| Conversão de mundos para `.mcworld`     | Implementada     |
| Conversão paralela para `.mcworld`      | Implementada     |
| Seleção de mundos específicos           | Implementada     |
| Sincronização com Minecraft Bedrock     | Implementada     |
| Gerenciamento de backups                | Implementado     |
| Configuração via `.env`                 | Implementada     |
| Funcionamento sem dependências externas | Implementado     |
| Conversão Bedrock → Java                | Planejada        |
| Conversor Bedrock → Java funcional      | Não implementado |

---

## Requisitos

### Software

* **Python 3.8 ou superior**
* **Minecraft Bedrock Edition** instalado
* Minecraft Bedrock executado pelo menos uma vez para que sua estrutura de diretórios seja criada
* **Windows**, devido à integração com a instalação local do Minecraft Bedrock

### Dependências

O projeto **não possui dependências externas obrigatórias** para as funcionalidades atualmente implementadas.

O funcionamento básico utiliza exclusivamente bibliotecas que fazem parte da biblioteca padrão do Python, incluindo:

```text
shutil
pathlib
datetime
concurrent.futures
threading
argparse
sys
os
time
json
zipfile
hashlib
```

Portanto, para utilizar as funcionalidades atuais, basta ter o Python instalado.

### `requirements.txt`

O projeto possui um arquivo `requirements.txt` para documentar dependências opcionais e futuras.

Atualmente, não há nenhuma dependência obrigatória nesse arquivo.

Dependências opcionais previstas incluem:

* `python-dotenv` — alternativa para carregamento de variáveis de ambiente.
* `psutil` — monitoramento de recursos e possível identificação automática da quantidade ideal de workers.

Essas dependências não são necessárias para o funcionamento básico do projeto.

---

## Instalação

### 1. Clone ou baixe o projeto

```bash
git clone https://github.com/seu-usuario/minecraft-world-converter.git
cd minecraft-world-converter
```

### 2. Python

Certifique-se de que o Python está instalado:

```bash
python --version
```

O projeto requer Python 3.8 ou superior.

Como não existem dependências externas obrigatórias, não é necessário executar `pip install` para utilizar as funcionalidades básicas.

Caso queira instalar as dependências opcionais documentadas no `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Crie o arquivo `.env`

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

No Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Depois, ajuste os valores de acordo com sua instalação.

---

## Configuração

A configuração principal do projeto é realizada através do arquivo `.env`.

### Exemplo

```env
# ============================================================
# PASTAS DO PROJETO
# ============================================================
DEFAULT_WORLDS_PATH=MINECRAFTDATA/com.mojang/minecraftWorlds
OUTPUT_MCWORLD_PATH=MUNDOS_MCWORLD
OUTPUT_JAVA_PATH=MUNDOS_JAVA
BACKUP_PATH=BACKUP_MUNDOS
TEMP_PATH=temp_conversao
SOURCE_MCWORLD_PATH=MINECRAFTDATA/com.mojang

# ============================================================
# CAMINHOS DO MINECRAFT BEDROCK
# ============================================================
MINECRAFT_BEDROCK_PATH=~/AppData/Roaming/Minecraft Bedrock
MINECRAFT_USER_ID=16283763834770312692

# ============================================================
# ARQUIVOS DE LOG
# ============================================================
LOG_FILE_MCWORLD=mcworld_converter_log.txt
LOG_FILE_JAVA=java_converter_log.txt
LOG_FILE_GENERAL=converter_log.txt
LOG_FILE_SYNC=minecraft_sync_log.txt
LOG_FILE_PARALLEL=parallel_converter_log.txt

# ============================================================
# CONFIGURAÇÕES
# ============================================================
TIMEOUT_SECONDS=7200
COMPRESSION_LEVEL=6
MAX_WORKERS=8
SYNC_WORKERS=8
SYNC_FORCE=false

# ============================================================
# MAPEAMENTO DE PASTAS
# ============================================================
PASTAS_SHARED=behavior_packs,development_behavior_packs,development_resource_packs,development_skin_packs,resource_packs,skin_packs,world_templates
PASTAS_USER=minecraftWorlds,custom_skins,minecraftpe,Screenshots
```

### Arquivo `.env`

O `.env` é utilizado para configurações específicas do ambiente local e não deve ser versionado.

O arquivo `.env.example` deve permanecer no repositório como modelo para novas instalações.

---

## Estrutura do Minecraft Bedrock

A integração com a instalação local do Minecraft utiliza uma estrutura semelhante a:

```text
C:\Users\[usuario]\AppData\Roaming\Minecraft Bedrock\
└── Users\
    ├── Shared\
    │   └── games\
    │       └── com.mojang\
    │           ├── behavior_packs\
    │           ├── resource_packs\
    │           ├── skin_packs\
    │           └── world_templates\
    │
    └── [SEU_USER_ID]\
        └── games\
            └── com.mojang\
                ├── minecraftWorlds\
                ├── custom_skins\
                ├── minecraftpe\
                └── Screenshots\
```

A pasta `Shared` contém dados compartilhados da instalação, enquanto o diretório associado ao `MINECRAFT_USER_ID` contém os dados específicos do usuário, incluindo os mundos.

---

## Como Usar

### Converter mundos para `.mcworld`

Para realizar uma conversão sequencial:

```bash
python converter_para_mcworld.py
```

Para utilizar processamento paralelo:

```bash
python main_parallel.py --workers 8
```

Para converter apenas mundos específicos:

```bash
python main_parallel.py --only "Mundo1" "Mundo2"
```

Os arquivos gerados são armazenados no diretório definido por:

```env
OUTPUT_MCWORLD_PATH=MUNDOS_MCWORLD
```

---

### Sincronizar mundos com o Minecraft

Para realizar a sincronização:

```bash
python sync_minecraft.py --workers 16
```

Para forçar a sobrescrita de arquivos existentes:

```bash
python sync_minecraft.py --workers 16 --force
```

Recomenda-se fechar o Minecraft durante a sincronização para evitar conflitos ou arquivos bloqueados pelo processo do jogo.

---

## Scripts Disponíveis

| Script                      | Função                                                            | Status           |
| --------------------------- | ----------------------------------------------------------------- | ---------------- |
| `main_parallel.py`          | Converte mundos para `.mcworld` utilizando processamento paralelo | Implementado     |
| `converter_para_mcworld.py` | Converte mundos para `.mcworld` sequencialmente                   | Implementado     |
| `sync_minecraft.py`         | Sincroniza os arquivos com a instalação do Minecraft Bedrock      | Implementado     |
| `config.py`                 | Centraliza as configurações do projeto                            | Implementado     |
| `bedrock_java_converter.py` | Tentativa preliminar de conversão Bedrock → Java                  | Não implementado |

O arquivo `bedrock_java_converter.py` não deve ser considerado uma funcionalidade disponível atualmente.

Ele representa uma tentativa preliminar de implementação e ainda precisa ser completamente desenvolvido, validado e integrado ao projeto.

### Parâmetros

| Parâmetro          | Descrição                                                               |
| ------------------ | ----------------------------------------------------------------------- |
| `--workers N`      | Define o número de operações paralelas                                  |
| `--force`          | Força a sobrescrita durante a sincronização                             |
| `--only "Mundo1"`  | Processa somente os mundos especificados                                |
| `--path "caminho"` | Permite utilizar um caminho personalizado, quando suportado pelo script |

---

## Estrutura de Pastas

```text
minecraft-world-converter/
│
├── MINECRAFTDATA/
│   └── com.mojang/
│       ├── behavior_packs/
│       ├── custom_skins/
│       ├── minecraftWorlds/
│       ├── resource_packs/
│       └── ...
│
├── MUNDOS_MCWORLD/
│   └── *.mcworld
│
├── MUNDOS_JAVA/
│   └── ...
│
├── BACKUP_MUNDOS/
│   └── ...
│
├── temp_conversao/
│   └── ...
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── config.py
├── converter_para_mcworld.py
├── main_parallel.py
├── sync_minecraft.py
├── bedrock_java_converter.py
└── README.md
```

As pastas de dados e arquivos gerados localmente não devem ser versionados.

---

## Fluxo de Trabalho

O fluxo principal do projeto é:

```text
┌──────────────────────────────────────────────┐
│ Mundos Bedrock de origem                     │
│ MINECRAFTDATA/com.mojang/minecraftWorlds     │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ Conversão para .mcworld                      │
│ python main_parallel.py --workers 8          │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ Arquivos .mcworld                            │
│ MUNDOS_MCWORLD/                              │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ Sincronização com Minecraft Bedrock          │
│ python sync_minecraft.py --workers 16        │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ Mundos disponíveis no Minecraft              │
└──────────────────────────────────────────────┘
```

A conversão para Java não faz parte do fluxo atual.

---

## Processamento Paralelo

O projeto possui suporte à execução paralela para reduzir o tempo necessário para processar grandes quantidades de arquivos.

Exemplo:

```bash
python main_parallel.py --workers 8
```

O número de workers pode ser ajustado conforme o hardware:

```bash
python main_parallel.py --workers 4
python main_parallel.py --workers 8
python main_parallel.py --workers 16
```

O mesmo princípio pode ser utilizado na sincronização:

```bash
python sync_minecraft.py --workers 16
```

A quantidade ideal de workers depende principalmente da capacidade do armazenamento, CPU e quantidade de arquivos envolvidos.

---

## Backup

O diretório de backup é definido através de:

```env
BACKUP_PATH=BACKUP_MUNDOS
```

A utilização de backups permite preservar os dados originais antes de operações que possam modificar ou sobrescrever arquivos.

É recomendado manter uma cópia dos mundos originais antes de realizar operações em grande escala.

---

## Solução de Problemas

### Pasta do Minecraft não encontrada

Verifique:

1. Se o Minecraft Bedrock foi executado pelo menos uma vez.
2. Se `MINECRAFT_BEDROCK_PATH` está configurado corretamente.
3. Se a pasta `Users` existe.
4. Se `MINECRAFT_USER_ID` corresponde ao usuário correto.

Exemplo:

```env
MINECRAFT_BEDROCK_PATH=~/AppData/Roaming/Minecraft Bedrock
MINECRAFT_USER_ID=16283763834770312692
```

### `Permission denied`

Verifique as permissões das pastas utilizadas pelo projeto.

Também é recomendado:

* Fechar o Minecraft antes da sincronização.
* Verificar se outro processo está utilizando os arquivos.
* Executar o terminal com permissões adequadas quando necessário.

### `ModuleNotFoundError`

As funcionalidades básicas não devem exigir módulos externos.

Caso um módulo externo seja solicitado por alguma funcionalidade opcional, verifique se ele está documentado no `requirements.txt` e instale as dependências correspondentes:

```bash
pip install -r requirements.txt
```

### Conversão não termina

Caso uma conversão apresente problemas:

1. Verifique os arquivos de log.
2. Verifique o espaço disponível no disco.
3. Verifique se os arquivos não estão sendo utilizados por outro processo.
4. Feche o Minecraft.
5. Reduza a quantidade de workers.

Por exemplo:

```bash
python main_parallel.py --workers 4
```

---

## Logs

Os scripts podem gerar arquivos de log para auxiliar na identificação de problemas.

| Arquivo                      | Finalidade                                  |
| ---------------------------- | ------------------------------------------- |
| `mcworld_converter_log.txt`  | Conversão para `.mcworld`                   |
| `parallel_converter_log.txt` | Conversão paralela                          |
| `minecraft_sync_log.txt`     | Sincronização com Minecraft                 |
| `java_converter_log.txt`     | Reservado para a futura conversão para Java |
| `converter_log.txt`          | Log geral                                   |

Os arquivos de log não devem ser versionados.

---

## Git e Arquivos Ignorados

O projeto utiliza `.gitignore` para impedir que arquivos locais, logs, dados do Minecraft e arquivos temporários sejam adicionados ao repositório.

Exemplo:

```gitignore
.venv/
venv/
ENV/
env/
/MINECRAFTDATA
/__pycache__
/MUNDOS_MCWORLD
/temp_conversao

minecraft_sync_log.txt
parallel_converter_log.txt
converter_log.txt
java_converter_log.txt
mcworld_converter_log.txt
.env
```

---

## Funcionalidades Futuras

### Conversão Bedrock → Java

A conversão de mundos Bedrock Edition para Java Edition está planejada para uma etapa futura do projeto.

O arquivo `bedrock_java_converter.py` existente não representa uma implementação funcional dessa funcionalidade. Ele foi gerado como uma tentativa preliminar e ainda precisa ser desenvolvido, validado e integrado corretamente.

Também não existe atualmente uma dependência chamada `mcc-toolchest` que faça parte do projeto.

A estratégia, biblioteca ou ferramenta que será utilizada para a conversão Bedrock → Java ainda deverá ser definida durante a implementação dessa funcionalidade.

Quando o conversor estiver efetivamente desenvolvido e testado, suas dependências, limitações, instruções de instalação e utilização deverão ser adicionadas a esta documentação.

---

## Licença

Este projeto é destinado a uso pessoal e pode ser modificado e adaptado conforme a necessidade.
