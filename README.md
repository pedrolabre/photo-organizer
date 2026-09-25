# Photo Organizer

Organizador e analisador local de bibliotecas fotográficas em Python. O sistema realiza varredura recursiva de diretórios, extrai metadados EXIF/GPS, calcula hashes de integridade (MD5 e perceptual), identifica duplicatas (exatas ou similares) e reorganiza as fotos em estruturas temporais personalizáveis (`ano`, `ano/mês` ou `ano/mês/dia`).

Disponibiliza três interfaces: uma interface gráfica desktop nativa moderna (GUI) com seleção visual de diretórios e processamento desacoplado em threads, um Dashboard Web local em Flask alinhado à documentação técnica e uma CLI para execução em lote ou automação.

---

## Recursos Principais

- **Varredura Recursiva & Inspeção**: Enumeração de arquivos de imagem suportados (JPEG, PNG, GIF, BMP, TIFF, HEIC, RAW/CR2/NEF/DNG) com validação de formato.
- **Extração Completa de Metadados**:
  - Leitura de tags EXIF (marca, modelo da câmera, abertura, tempo de exposição, ISO, distância focal).
  - Coordenadas geográficas (GPS) com conversão automática para graus decimais.
  - Parsing inteligente de data/hora (prioridade: `DateTimeOriginal` → `DateTimeDigitized` → data de modificação do arquivo).
- **Detecção de Duplicatas em Dois Níveis**:
  - **Duplicatas Exatas (MD5)**: Identificação rápida baseada em hash de conteúdo criptográfico.
  - **Duplicatas Similares (pHash)**: Comparação perceptual via distância de Hamming sobre hash visual (com limiar configurável).
- **Políticas de Retenção Flexíveis**: Ao encontrar duplicatas, escolha manter a de maior resolução (`highest_resolution`), a mais recente (`newest`), a mais antiga (`oldest`) ou a primeira encontrada (`first_found`).
- **Segurança de Dados**:
  - Operação configurável entre **cópia** (mantém o original intacto) ou **movimentação**.
  - Verificação de integridade pós-cópia através de validação de hashes.
  - Resolução automática de conflitos de nome (`foto_1.jpg`, `foto_2.jpg`).
  - Isolamento de duplicatas em pasta de quarentena dedicada (`output/quarantine/`).
  - Suporte completo ao modo simulação (`--dry-run`).
- **Persistência e Auditoria**:
  - Banco de dados SQLite local (`data/database/photo_organizer.db`) com indexação de hashes e metadados.
  - Geração de relatórios de duplicatas e sumários em JSON/CSV.

---

## Fluxo de Processamento (Pipeline)

```text
[Pastas de Entrada] 
        ↓
 [File Scanner] ─────────→ Enumera imagens suportadas
        ↓
[Metadata Reader] ───────→ Extrai EXIF, GPS e determina data de referência
        ↓
[Hash Calculator] ───────→ Gera MD5 (exato) e pHash (perceptual)
        ↓
[Database Storage] ──────→ Persiste metadados no SQLite local
        ↓
[Duplicate Detection] ───→ Identifica duplicatas e aplica política de retenção
        ↓
   ┌────┴──────────────────────────┐
   ↓                               ↓
[File Mover]                 [Quarentena]
Organização por data         Isolamento de duplicatas
(Ano / Mês / Dia)            (output/quarantine/groups/)
   ↓                               ↓
   └───────────────┬───────────────┘
                   ↓
           [Relatórios & Logs]
```

---

## Instalação e Requisitos

### Pré-requisitos
- Python 3.10 ou superior
- Ambiente virtual (`venv`) recomendado

### Passo a Passo

1. **Clonar o repositório:**
   ```bash
   git clone https://github.com/pedrolabre/photo-organizer.git
   cd photo-organizer
   ```

2. **Criar e ativar o ambiente virtual:**
   - **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
     *(Se houver restrição de execução de scripts, execute: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*
   - **Windows (CMD):**
     ```cmd
     python -m venv venv
     .\venv\Scripts\activate.bat
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Instalar as dependências:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## Configuração (`config.yaml`)

O comportamento do sistema é controlado pelo arquivo `config.yaml` na raiz do projeto:

```yaml
# Pastas de entrada (múltiplas fontes suportadas)
input_folders:
  - "./test_photos"

# Pastas de saída
output_folder: "./output/organized"
quarantine_folder: "./output/quarantine"

# Extensões suportadas
supported_extensions:
  - ".jpg"
  - ".jpeg"
  - ".png"
  - ".gif"
  - ".bmp"
  - ".tiff"
  - ".heic"
  - ".dng"

# Estrutura de organização: "year_month_day", "year_month" ou "year"
organization:
  structure: "year_month_day"
  folder_format:
    year: "%Y"
    month: "%Y-%m"
    day: "%Y-%m-%d"
  use_file_date_as_fallback: true
  create_no_date_folder: true

# Detecção de duplicatas
duplicates:
  detect_exact: true
  detect_similar: false
  similarity_threshold: 8       # Limiar de Hamming (menor = mais rigoroso)
  keep_policy: "highest_resolution"  # highest_resolution, newest, oldest, first_found

# Segurança operacional
safety:
  never_delete_originals: true
  file_operation: "copy"        # "copy" (seguro) ou "move"
  verify_after_copy: true       # Validação de integridade após escrita
  backup_database: true

# Logs
logging:
  level: "INFO"
  save_to_file: true
  use_colors: true
```

---

## Execução

### 1. Interface Gráfica Desktop (GUI)
Para iniciar a aplicação gráfica desktop nativa com seleção visual de pastas, configuração de parâmetros, árvore de pré-visualização e barra de progresso em tempo real:
```bash
python run_desktop.py
# ou alternativamente:
python gui.py
```

### 2. Interface Web (Dashboard)
Para iniciar o servidor local do dashboard e abrir o navegador automaticamente:
```bash
python run_web.py
# ou iniciar o servidor diretamente:
python app.py
```
Acesse no navegador: **[http://localhost:5000](http://localhost:5000)**.

### 3. Interface de Linha de Comando (CLI)
Para executar o processamento diretamente pelo terminal:

```bash
# Execução padrão (utiliza configurações do config.yaml)
python main.py

# Simulação sem movimentação física de arquivos
python main.py --dry-run

# Ajuste dinâmico do limiar de similaridade visual (0 a 64)
python main.py --threshold 10

# Especificação de arquivo de configuração alternativo
python main.py --config caminho/para/outro_config.yaml
```

---

## Estrutura do Código

```text
photo-organizer/
├── src/
│   ├── core/
│   │   ├── file_scanner.py         # Fachada de varredura de diretórios
│   │   ├── metadata_reader.py      # Fachada para extração unificada de metadados
│   │   ├── hash_calculator.py      # Cálculo de hashes MD5 e pHash
│   │   ├── parsers/                # Parsers de EXIF, GPS e datas
│   │   │   ├── datetime_parser.py
│   │   │   ├── exif_parser.py
│   │   │   └── gps_parser.py
│   │   └── scanners/               # Implementação do scanner e extração de atributos
│   │       ├── file_info.py
│   │       └── scanner.py
│   ├── database/
│   │   └── db_manager.py           # Gerenciador da base SQLite e consultas
│   ├── detection/
│   │   ├── bk_tree.py              # Árvore métrica Burkhard-Keller para indexação e busca
│   │   ├── exact_duplicates.py     # Detecção de duplicatas exatas por MD5
│   │   ├── similar_detector.py     # Detecção de similares visuais por pHash
│   │   └── keep_policy.py          # Regras de retenção (resolução, data, ordem)
│   ├── gui/
│   │   ├── desktop_app.py          # Controlador da interface desktop e despacho de eventos
│   │   ├── gui_model.py            # Modelos de dados e configurações da GUI
│   │   ├── styles.py               # Configuração de temas e estilos ttk
│   │   ├── view_components.py      # Cartões de seleção de diretórios e parâmetros
│   │   ├── views.py                # Visualização principal, barra de progresso e árvore
│   │   └── worker.py               # Execução assíncrona desacoplada em worker threads
│   ├── organization/
│   │   ├── file_mover.py           # Operações seguras de cópia/movimentação
│   │   ├── folder_organizer.py     # Criação de pastas e cálculo de árvore
│   │   └── operations/
│   │       ├── file_operations.py  # Manipulação atômica e verificação de hash
│   │       └── stats_tracker.py    # Contadores e estatísticas de transferência
│   ├── routes/
│   │   ├── api_routes.py           # Endpoints REST para o Dashboard
│   │   └── web_routes.py           # Rota principal da UI
│   ├── utils/
│   │   ├── config.py               # Leitura e validação central de configurações
│   │   ├── logger.py               # Sistema de logs com cores e rotação em arquivo
│   │   └── configs/                # Dataclasses tipadas de cada seção de config
│   └── processing.py               # Worker de execução em segundo plano
├── templates/
│   └── dashboard.html              # Template da interface web moderno
├── docs/                           # Documentação Web (GitHub Pages)
│   └── index.html
├── scripts/
│   ├── cleanup_generated.py        # Limpeza de relatórios, logs e caches locais
│   ├── export_hashes.py            # Exportação de distâncias e hashes para CSV/JSON
│   ├── generate_reports.py         # Geração de relatórios com metadados detalhados
│   └── package_reports.py          # Empacotamento de relatórios em arquivo ZIP
├── tests/
│   ├── test_bk_tree.py             # Teste de indexação e busca em BK-Tree
│   ├── test_db_manager.py          # Teste de pragmas WAL, batch inserts e backup
│   ├── test_exact_duplicates.py    # Teste de agrupamento por hash MD5
│   ├── test_file_mover.py          # Teste de cópia, integridade e resolução de conflitos
│   ├── test_folder_organizer.py    # Teste de preview de pastas e agrupamentos
│   ├── test_gui.py                 # Teste da interface gráfica desktop e worker assíncrono
│   ├── test_similar_detector.py    # Teste de cálculo de distância perceptual
│   └── test_web_routes.py          # Teste de renderização do dashboard e endpoints web
├── app.py                          # Ponto de entrada do Dashboard Web (Flask)
├── gui.py                          # Ponto de entrada da GUI Desktop
├── run_desktop.py                  # Script para abrir a versão desktop
├── run_web.py                      # Script para abrir a versão web e navegador
├── main.py                         # Ponto de entrada da CLI
├── config.yaml                     # Configuração padrão do sistema
├── requirements.txt                # Dependências do projeto
└── LICENSE                         # Licença MIT
```

---

## Testes Automatizados

A suíte de testes utiliza o framework `pytest`:

```bash
# Executar todos os testes
pytest

# Executar com saída detalhada
pytest -v
```

Formatação e análise de código:
```bash
# Formatar código
black .

# Análise estática com pylint
pylint src/
```

---

## Licença

Distribuído sob a Licença MIT. Consulte o arquivo [LICENSE](LICENSE) para obter detalhes.
