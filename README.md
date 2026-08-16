# Minecraft World Converter

Conjunto de ferramentas em Python para conversão, gerenciamento e sincronização de mundos do **Minecraft Bedrock Edition**.

O projeto tem como objetivo automatizar o processamento de mundos Bedrock, incluindo a conversão para arquivos `.mcworld` e a sincronização dos dados com a instalação local do Minecraft.

> **Status:** em desenvolvimento. A conversão de Bedrock Edition para Java Edition ainda não foi implementada e está planejada para uma versão futura.

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
* Realizar operações de cópia de arquivos utilizando múltiplos workers.
* Configurar caminhos e parâmetros através de um arquivo `.env`.
* Manter backups dos dados originais antes das operações de sincronização.

A conversão de mundos **Bedrock Edition para Java Edition ainda não está implementada**. Existe um script relacionado a essa funcionalidade que foi criado durante o desenvolvimento como uma tentativa inicial, porém ele não representa uma implementação funcional do conversor e não deve ser considerado uma funcionalidade disponível atualmente.

---

## Status do Projeto

| Funcionalidade                      | Status           |
| ----------------------------------- | ---------------- |
| Conversão de mundos para `.mcworld` | Implementada     |
| Conversão paralela para `.mcworld`  | Implementada     |
| Seleção de mundos específicos       | Implementada     |
| Sincronização com Minecraft Bedrock | Implementada     |
| Backup dos dados                    | Implementada     |
| Configuração via `.env`             | Implementada     |
| Conversão Bedrock → Java            | Planejada        |
| Conversor Bedrock → Java funcional  | Não implementado |

A conversão para Java será desenvolvida e implementada futuramente após a definição da estratégia e da ferramenta de conversão adequada.

---

## Requisitos

### Software

* Python 3.8 ou superior.
* Minecraft Bedrock Edition instalado.
* Minecraft Bedrock executado pelo menos uma vez para que sua estrutura de diretórios seja criada.
* Windows, devido à integração com a instalação local do Minecraft Bedrock.

### Dependências Python

As dependências utilizadas pelo projeto devem ser instaladas através do arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

Não existe uma biblioteca Python chamada `mcc-toolchest` utilizada pelo projeto.

A conversão Bedrock → Java **não possui atualmente uma dependência definida**, pois essa funcionalidade ainda está em fase de planejamento e desenvolvimento.

---

## Instalação

### 1. Clone ou baixe o projeto

```bash
git clone https://github.com/seu-usuario/minecraft-world-converter.git
cd minecraft-world-converter
```

### 2. Crie o arquivo `.env`

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

No Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Depois, ajuste as configurações de acordo com o ambiente local.

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Prepare as pastas

A estrutura básica esperada é:

```text
minecraft-world-converter/
├── MINECRAFTDATA/
│   └── com.mojang/
│       └── minecraftWorlds/
├── MUNDOS_MCWORLD/
├── MUNDOS_JAVA/
└── BACKUP_MUNDOS/
```

As pastas de saída e backup podem ser criadas automaticamente pelos scripts, dependendo da implementação atual.

---

## Configuração

A configuração principal do projeto é realizada através do arquivo `.env`.

### Exemplo de `.env`

```env
# PASTAS DO PROJETO
DEFAULT_WORLDS_PATH=MINECRAFTDATA/com.mojang/minecraftWorlds
OUTPUT_MCWORLD_PATH=MUNDOS_MCWORLD
OUTPUT_JAVA_PATH=MUNDOS_JAVA
BACKUP_PATH=BACKUP_MUNDOS
TEMP_PATH=temp_conversao
SOURCE_MCWORLD_PATH=MINECRAFTDATA/com.mojang

# CAMINHOS DO MINECRAFT BEDROCK
MINECRAFT_BEDROCK_PATH=~/AppData/Roaming/Minecraft Bedrock
MINECRAFT_USER_ID=16283763834770312692

# ARQUIVOS DE LOG
LOG_FILE_MCWORLD=mcworld_converter_log.txt
LOG_FILE_JAVA=java_converter_log.txt
LOG_FILE_GENERAL=converter_log.txt
LOG_FILE_SYNC=minecraft_sync_log.txt
LOG_FILE_PARALLEL=parallel_converter_log.txt

# CONFIGURAÇÕES
TIMEOUT_SECONDS=7200
COMPRESSION_LEVEL=6
MAX_WORKERS=8
SYNC_WORKERS=8
SYNC_FORCE=false

# MAPEAMENTO DE PASTAS
PASTAS_SHARED=behavior_packs,development_behavior_packs,development_resource_packs,development_skin_packs,resource_packs,skin_packs,world_templates
PASTAS_USER=minecraftWorlds,custom_skins,minecraftpe,Screenshots
```

### Observação sobre o `.env`

O arquivo `.env` deve ser utilizado apenas para configurações específicas do ambiente local.

Ele não deve ser versionado no Git.

O arquivo `.env.example` deve permanecer no repositório como modelo de configuração.

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

Para realizar a conversão utilizando processamento paralelo:

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
| `bedrock_java_converter.py` | Tentativa inicial de conversão Bedrock → Java                     | Não implementado |

O arquivo `bedrock_java_converter.py` não deve ser considerado uma funcionalidade disponível. Ele representa uma implementação preliminar que ainda precisa ser completamente desenvolvida, validada e integrada ao projeto.

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
├── config.py
├── converter_para_mcworld.py
├── main_parallel.py
├── sync_minecraft.py
├── bedrock_java_converter.py
└── README.md
```

As pastas `MINECRAFTDATA`, `MUNDOS_MCWORLD`, `MUNDOS_JAVA`, `BACKUP_MUNDOS` e `temp_conversao` são destinadas aos dados locais e não devem ser versionadas.

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

A conversão para Java não faz parte desse fluxo atualmente.

---

## Processamento Paralelo

O projeto possui suporte à execução paralela para reduzir o tempo necessário para processar grandes quantidades de arquivos.

Exemplo:

```bash
python main_parallel.py --workers 8
```

O número de workers pode ser ajustado:

```bash
python main_parallel.py --workers 4
python main_parallel.py --workers 8
python main_parallel.py --workers 16
```

O mesmo princípio pode ser aplicado à sincronização:

```bash
python sync_minecraft.py --workers 16
```

A quantidade ideal de workers depende do hardware utilizado, principalmente da velocidade do armazenamento, CPU e quantidade de arquivos envolvidos.

---

## Backup

O diretório de backup é configurado através de:

```env
BACKUP_PATH=BACKUP_MUNDOS
```

A utilização de backups permite preservar os dados originais antes de operações que possam sobrescrever ou modificar arquivos.

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

---

### `Permission denied`

Verifique as permissões das pastas utilizadas pelo projeto.

Também é recomendado:

* Fechar o Minecraft antes da sincronização.
* Verificar se outro processo está utilizando os arquivos.
* Executar o terminal com permissões adequadas quando necessário.

---

### `ModuleNotFoundError`

Instale as dependências do projeto:

```bash
pip install -r requirements.txt
```

Caso esteja utilizando um ambiente virtual:

```bash
python -m venv .venv
```

No Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Depois:

```bash
pip install -r requirements.txt
```

---

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
# Arquivos de ambiente
.env
.env.local
.env.*.local

# Logs
*.log
*_log.txt
minecraft_sync_log.txt
parallel_converter_log.txt
converter_log.txt
java_converter_log.txt
mcworld_converter_log.txt

# Dados do projeto
/MINECRAFTDATA
/MUNDOS_MCWORLD
/MUNDOS_JAVA
/BACKUP_MUNDOS
/temp_conversao
/__pycache__

# Python
*.pyc
*.pyo
*.pyd
.Python

# IDE
.vscode/
.idea/
*.swp
*.swo

# Windows
Thumbs.db
desktop.ini
```

---

## Funcionalidades Futuras

### Conversão Bedrock → Java

A conversão de mundos Bedrock Edition para Java Edition está planejada para uma etapa futura do projeto.

O arquivo `bedrock_java_converter.py` existente não representa uma implementação funcional dessa funcionalidade. Ele foi criado como uma tentativa preliminar e ainda precisa ser desenvolvido, validado e integrado corretamente.

Antes da implementação definitiva, será necessário definir uma solução confiável para a conversão dos formatos de mundo e avaliar suas limitações e compatibilidade.

Essa funcionalidade será documentada neste README quando estiver efetivamente implementada e testada.

---

## Licença

Este projeto é destinado a uso pessoal e pode ser modificado e adaptado conforme a necessidade.
