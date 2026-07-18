# DocStamp Pro

Sistema profissional de carimbo de data em documentos PDF.  
Desenvolvido em Python com interface gráfica moderna (CustomTkinter).

---

## 📋 Funcionalidades

- 🔐 **Login por funcionário** — cada um com sua própria cor de carimbo
- 📁 **PDF único ou pasta inteira** — processa múltiplos arquivos de uma vez
- 🎨 **Cor e tamanho personalizáveis** — paleta de cores + campo hex customizado
- 📅 **Data configurável** — escolha qualquer data ou use a de hoje
- 📍 **Posição configurável** — Topo ou Rodapé do documento
- 👥 **Painel Admin** — cadastro e gerenciamento de funcionários
- 🛡️ **LGPD compliant** — log de auditoria de todos os carimbos realizados

---

## 🚀 Como Executar

### Pré-requisito
- Python 3.11 ou superior → [python.org](https://www.python.org/downloads/)

### 1. Instalar dependências (apenas na primeira vez)
```bash
pip install -r requirements.txt
```

### 2. Rodar o aplicativo
```bash
python main.py
```

### Credenciais padrão (primeira execução)
| Campo | Valor |
|-------|-------|
| E-mail | `admin@empresa.com` |
| Senha  | `Admin@123` |

> ⚠️ **Troque a senha do admin e cadastre seus funcionários antes de usar em produção!**

---

## 📂 Estrutura do Projeto

```
DocStampPro/
├── main.py               # Entry point do aplicativo
├── requirements.txt      # Dependências Python
├── build.bat             # Gera executável .exe (Windows)
├── database/
│   └── db.py             # Banco de dados SQLite + autenticação
├── core/
│   └── pdf_stamper.py    # Engine de carimbo de PDFs
├── ui/
│   ├── login_window.py   # Tela de login
│   ├── main_window.py    # Dashboard principal
│   └── admin_window.py   # Painel de administração
└── utils/
    └── helpers.py        # Utilitários gerais
```

---

## 🏗️ Gerar Executável .exe

Para distribuir para os funcionários sem precisar instalar Python:

```bash
build.bat
```

O arquivo `dist\DocStampPro.exe` será gerado. Copie apenas esse arquivo para os computadores da equipe.

---

## 🗂️ Onde os PDFs são salvos

Os PDFs originais **nunca são alterados**. Os carimbados são salvos em:
```
[pasta dos originais]/_carimbados/
```

---

## 🛡️ LGPD

- Senhas armazenadas com hash `bcrypt` (nunca em texto puro)
- Log de auditoria: usuário, arquivo, data, cor, tamanho — tudo registrado
- Processamento 100% local — nenhum dado sai do computador

---

## 📦 Dependências

| Pacote | Uso |
|--------|-----|
| `customtkinter` | Interface gráfica moderna |
| `PyMuPDF` | Manipulação e edição de PDFs |
| `bcrypt` | Hash seguro de senhas |
| `Pillow` | Suporte a imagens na UI |

---

## 👨‍💻 Tecnologias

- **Python 3.11+**
- **CustomTkinter** — UI dark mode
- **PyMuPDF (fitz)** — engine de PDF
- **SQLite** — banco de dados local
- **PyInstaller** — empacotamento em .exe
