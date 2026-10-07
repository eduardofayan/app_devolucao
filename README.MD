# Sistema de Controle de Devoluções

Aplicação Desktop desenvolvida em Python para gerenciamento e controle de devoluções de caminhões, permitindo o registro de múltiplas OCs por devolução, controle de clientes por OC, histórico de devoluções e exportação para Excel.

---

## Recursos

- Login por conferente
- Controle de devoluções em aberto
- Controle de devoluções finalizadas
- Registro de múltiplas OCs por caminhão
- Cliente individual por OC
- Valor NF individual por OC
- Soma automática do valor total da devolução
- Controle de data e hora de abertura
- Controle de data e hora de finalização
- Histórico de devoluções
- Exportação Excel por período (Mês/Ano)
- Banco de dados SQLite
- Interface moderna com CustomTkinter
- Compatível com Windows
- Geração de executável (.exe)

---

## Regras de Negócio

### Devolução

Uma devolução representa um caminhão.

Cada devolução contém:

- Placa do Caminhão
- Motivo da Devolução
- Data/Hora de Abertura
- Data/Hora de Finalização
- Conferente de Abertura
- Conferente de Finalização
- Status

### OCs

Uma devolução pode possuir várias OCs.

Cada OC possui:

- Número da OC
- Cliente
- Valor da NF

Exemplo:

Placa: ABC1D23

OC: 123456  
Cliente: Fresenius  
Valor NF: R$ 1.000,00

OC: 565656  
Cliente: Havan  
Valor NF: R$ 500,00

Valor Total da Devolução:

R$ 1.500,00

---

## Atualização do Requirements

```powershell
pip freeze > requirements.txt
```

---

## Instalação

Criar ambiente virtual:

```powershell
python -m venv .venv
```

Ativar ambiente:

```powershell
.venv\Scripts\Activate.ps1
```

Instalar dependências:

```powershell
pip install -r requirements.txt
```

---

## Executar

```powershell
python app.py
```

---

## Estrutura do Projeto

```text
app_devolucao/
│
├── assets/
│   ├── icon.ico
│   └── logo.png
│
├── src/
│   ├── __init__.py
│   ├── database.py
│   ├── exporter.py
│   ├── resource_path.py
│   └── __pycache__/
│
├── .gitignore
├── app.py
├── README.md
└── requirements.txt
```

---

## Banco de Dados

O sistema utiliza SQLite.

### Tabela: devolucoes

```text
id
conferente_abertura
numero_oc
placa_caminhao
motivo
clientes
valor_nf
data_hora_inicio
data_hora_fim
conferente_finalizacao
status
```

### Tabela: ocs_devolucao

```text
id
devolucao_id
numero_oc
cliente
valor_nf
```

---

## Exportação Excel

A exportação é realizada através da seleção de:

- Mês
- Ano

Cada OC é exportada em uma linha distinta.

Exemplo:

```text
ID | NUMERO OC | CLIENTE   | PLACA    | VALOR NF

1  | 123456    | Fresenius | ABC1D23  | R$ 1.000,00
1  | 565656    | Havan     | ABC1D23  | R$   500,00
```

Caso o período selecionado não possua registros, o sistema exibirá um aviso e não gerará uma planilha vazia.

---

## Fluxo Operacional

1. Login do Conferente
2. Iniciar Nova Devolução
3. Inserir OCs
4. Informar Cliente de cada OC
5. Informar Valor NF de cada OC
6. Adicionar OCs à devolução
7. Informar Placa do Caminhão
8. Informar Motivo da Devolução
9. Iniciar Devolução
10. Finalizar Devolução quando concluída
11. Exportar histórico por período quando necessário

---

## Gerar Executável (Modo Pasta)

```powershell
python -m PyInstaller --clean --onedir --windowed --collect-all pandas --collect-all numpy --collect-all customtkinter --collect-all PIL --add-data "assets;assets" --icon=assets/icon.ico --name "App Controle Devolucoes" app.py
```

---

## Gerar Executável (Arquivo Único)

```powershell
python -m PyInstaller ^
--clean ^
--onefile ^
--windowed ^
--collect-all pandas ^
--collect-all numpy ^
--collect-all customtkinter ^
--collect-all PIL ^
--add-data "assets;assets" ^
--icon=assets/icon.ico ^
--name "Controle Devolucoes" ^
app.py
```

---

## Tecnologias Utilizadas

- Python
- CustomTkinter
- SQLite
- Pandas
- OpenPyXL
- Pillow
- PyInstaller

---

## Desenvolvedor

Eduardo Fayan

Jaguar Indústria e Comércio de Plásticos S.A.