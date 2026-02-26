# 📂 Mac Organizer AI

> Um organizador de arquivos inteligente com interface moderna, projetado para manter sua pasta de Downloads impecável automaticamente.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blueviolet)
![Watchdog](https://img.shields.io/badge/Backend-Watchdog-orange)
![Status](https://img.shields.io/badge/Status-Functional-brightgreen)

## 🖼️ Preview

<img width="600" height="551" alt="image" src="https://github.com/user-attachments/assets/bc3fb005-a47f-4b5f-b5e6-51bf4f5c3d90" />


## 📖 Sobre o Projeto

Cansado da bagunça na pasta **Downloads**? O **Mac Organizer AI** é uma ferramenta de automação desktop que roda em segundo plano, monitorando novos arquivos e organizando-os instantaneamente em categorias (Imagens, Documentos, Instaladores, Códigos).

Diferente de scripts simples, este projeto possui uma **Interface Gráfica (GUI)** moderna e responsiva, permitindo ao usuário iniciar e pausar o monitoramento com um clique, visualizando logs em tempo real.

### ✨ Funcionalidades
* **👀 Monitoramento em Tempo Real:** Detecta o arquivo no milissegundo em que o download termina.
* **📂 Organização Inteligente:** Move arquivos automaticamente para subpastas:
    * `Imagens/` (.jpg, .png, .webp...)
    * `Documentos/` (.pdf, .docx, .xlsx...)
    * `Instaladores/` (.dmg, .zip, .pkg...)
    * `Codigos/` (.py, .js, .html...)
* **🎨 Interface Moderna:** Construída com `CustomTkinter` para um visual nativo e Dark Mode.
* **⚡ Multithreading:** O monitoramento roda em uma thread separada, garantindo que a interface nunca trave.
* **🛡️ Seguro:** Tratamento de conflitos de nomes (não sobrescreve arquivos existentes).

---

## 🛠️ Tecnologias Utilizadas

* **Python 3.x**: Linguagem base.
* **Watchdog**: Biblioteca para monitoramento de eventos do sistema de arquivos (FileSystem Events).
* **CustomTkinter**: Wrapper moderno do Tkinter para interfaces elegantes.
* **Threading**: Para execução paralela de processos.
* **Shutil & Pathlib**: Manipulação de arquivos e caminhos de alta performance.

---

## 🚀 Como Rodar o Projeto

### Pré-requisitos
* macOS (Testado em Apple Silicon M1/M2/M3).
* Python 3 instalado via Homebrew.

### Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/JoaoPaulo121212/organizador-arquivos.git](https://github.com/jotape12-Dev/organizador-arquivos.git)
    cd organizador-arquivos
    ```

2.  **Crie o ambiente virtual e instale as dependências:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install watchdog customtkinter
    ```

3.  **Correção para macOS (Se necessário):**
    Se você encontrar erros de `tcl/tk` ou `abort trap`, instale o pacote gráfico do Python:
    ```bash
    brew install python-tk
    ```

4.  **Execute o App:**
    ```bash
    python3 app.py
    ```

---

## 🧠 Como Funciona (Deep Dive)

O projeto utiliza o padrão de projeto **Observer**.
1.  A classe `OrganizadorHandler` herda de `FileSystemEventHandler` do Watchdog.
2.  Quando um evento `on_created` é detectado na pasta Downloads, o script verifica a extensão.
3.  Se for um arquivo válido (ignorando temporários como `.crdownload`), ele aplica a lógica de movimentação.
4.  A **GUI** roda no `MainLoop` principal, enquanto o **Observer** roda em uma `Thread` secundária (Daemon), permitindo que o botão "Parar/Iniciar" funcione instantaneamente sem congelar a tela.

---

## 📄 Licença

Este projeto está sob a licença MIT - sinta-se livre para usar e modificar.
