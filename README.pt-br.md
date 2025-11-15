# TeleStream PyQt6

Uma aplicação simples construída em Python para transmitir arquivos de vídeo locais ou vídeos do YouTube para um servidor RTMP, como o Telegram, usando `ffmpeg`.

## Recursos

-   **Fontes de Vídeo**: Transmita um arquivo de vídeo local ou um vídeo do YouTube.
-   **Servidores Favoritos**: Salve, edite e remova servidores de streaming favoritos (Nome, URL e Chave de Stream) para acesso rápido.
-   **Interface com Temas**: Alterne entre um tema claro e escuro para se adequar à sua preferência.
-   **Controle de Loop**: Escolha se deseja reproduzir um vídeo uma vez ou em loop infinito. Isso funciona tanto para arquivos locais quanto para streams do YouTube.
-   **Predefinições de Qualidade**: Selecione entre várias predefinições de resolução e bitrate (1080p, 720p, 480p ou qualidade de origem) para gerenciar sua largura de banda e qualidade de stream.
-   **Modo Live Story**: Formata automaticamente seu vídeo em uma proporção de aspecto vertical de 9:16 com um fundo desfocado, perfeito para plataformas mobile. Este modo agora respeita as predefinições de qualidade para resolução e bitrate.
-   **Gerenciamento de Logs**: Visualize os logs da aplicação e do `ffmpeg` em uma janela dedicada, com opções para limpar o log ou salvá-lo em um arquivo com data e hora.
-   **Aceleração de Hardware (RPi)**: Inclui uma opção específica para usuários de Raspberry Pi para usar o codec `h264_v4l2m2m` para codificação de vídeo acelerada por hardware.

<p align="center">
<img width="933" height="700" alt="pyqt61" src="https://github.com/user-attachments/assets/dc136e17-9b51-42c5-98ac-3549944186e0" />

<img width="836" height="627" alt="pyqt62" src="https://github.com/user-attachments/assets/fac15e40-e52c-42e4-8fff-89842c7fac8d" />
</p>

## Pré-requisitos

-   **Python 3.7+**
-   **ffmpeg**: Você precisa ter o `ffmpeg` instalado e acessível no `PATH` do seu sistema.
    -   Para Windows (usando Winget): `winget install ffmpeg`
    -   Para Debian/Ubuntu: `sudo apt update && sudo apt install ffmpeg`
    -   Para Arch Linux: `sudo pacman -S ffmpeg`
    -   Para macOS (usando Homebrew): `brew install ffmpeg`

## Instalação

1.  Clone este repositório ou baixe os arquivos.
2.  Navegue até o diretório do projeto:
    ```bash
    cd telestream-pyqt6
    ```
3.  Crie um ambiente virtual:
    ```bash
    python3 -m venv venv
    ```
4.  Ative o ambiente virtual:
    ```bash
    source venv/bin/activate
    # Se você estiver usando Windows, use o comando `.\venv\Scripts\activate` (sem a palavra `source`) para ativar o ambiente virtual.
    ```
5.  Instale as dependências Python necessárias:
    ```bash
    pip install -r requirements.txt
    ```
6.  Execute a aplicação:
    ```bash
    python3 app.py
    # No Windows, pode ser necessário usar explicitamente o executável Python do ambiente virtual: `.\venv\Scripts\python.exe app.py`
    ```

## Como Usar

1.  **Fonte de Vídeo**:
    *   **Caminho do Vídeo**: Insira o caminho absoluto para um arquivo de vídeo local.
    *   **Ou URL do YouTube**: Cole a URL de um vídeo do YouTube.

2.  **Detalhes do Servidor**:
    *   **Servidor Favorito**: Selecione um servidor pré-salvo neste menu para preencher automaticamente a URL and a Chave.
    *   **URL do Servidor**: A URL RTMP/RTMPS do servidor de streaming.
    *   **Chave de Stream**: Sua chave de stream privada. Clique no ícone de olho para mostrar/ocultar.

3.  **Opções**:
    *   **Modo RPi**: Marque para usar o codec `h264_v4l2m2m`, recomendado para aceleração de hardware no Raspberry Pi.
    *   **Modo Loop**: Escolha "Loop Infinito" para repetir o vídeo quando ele terminar, ou "Reproduzir Uma Vez" para transmiti-lo uma única vez.
    *   **Live Story**: Marque para ativar o formato de vídeo vertical 9:16.
    *   **Predefinição de Qualidade**: Selecione uma resolução e bitrate para sua stream. "Qualidade de Origem" não redimensionará ou recodificará o bitrate do vídeo.

4.  **Streaming**:
    *   Pressione **Iniciar Stream** para começar.
    *   Pressione **Parar Stream** para encerrar a transmissão.

5.  **Utilitários**:
    *   **Mostrar Log**: Abre uma janela para visualizar logs detalhados da aplicação e do `ffmpeg`. Você também pode limpar o log a partir desta janela.
    *   **Salvar Log**: Salva a sessão de log atual em um arquivo `.txt` com data e hora no diretório raiz da aplicação.
    *   **Gerenciar Favoritos**: Abre um diálogo para adicionar, editar ou remover suas configurações de servidor salvas.
    *   **Sobre/Doar**: Mostra informações sobre a aplicação e opções de doação.
    *   **Alternar Tema**: Alterna a aplicação entre os temas claro and escuro.
