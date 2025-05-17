# Transcritor de Áudio
Este projeto é um transcritor de áudio que converte arquivos MP4 em texto usando reconhecimento de fala.

## Funcionalidades
- Extração de áudio de arquivos MP4
- Divisão do áudio em segmentos de 5 minutos
- Transcrição do áudio para texto usando Google Speech Recognition
- Suporte para língua portuguesa (pt-BR)

## Pré-requisitos
- Python 3.6 ou superior
- FFmpeg instalado no sistema
- Conexão com internet (para o Google Speech Recognition)

## Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_SEU_REPOSITORIO]
cd [NOME_DO_DIRETORIO]
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Instale o FFmpeg:
   - **Windows**: Baixe do [site oficial](https://ffmpeg.org/download.html) ou use o Chocolatey:
     ```bash
     choco install ffmpeg
     ```
     Colocar os arquivos do FFmpeg na pasta C:/ffmpeg
   - **Linux**:
     ```bash
     sudo apt-get install ffmpeg
     ```
   - **macOS**:
     ```bash
     brew install ffmpeg
     ```

## Como Usar

1. Coloque seu arquivo MP4 no diretório do projeto
2. Execute o script:
```bash
python main.py
```

3. O script irá:
   - Extrair o áudio do vídeo
   - Dividir em partes de 5 minutos
   - Realizar a transcrição
   - Salvar o resultado em 'transcricao_final.txt'

## Estrutura do Projeto
```
.
├── main.py              # Script principal
├── requirements.txt     # Dependências do projeto
├── Audios/             # Diretório para arquivos de áudio processados
└── README.md           # Esta documentação
```

## Limitações
- Arquivos muito grandes podem demorar para processar
- Necessita de conexão com internet para transcrição
- Qualidade da transcrição depende da qualidade do áudio

## Contribuições
Contribuições são bem-vindas! Por favor, sinta-se à vontade para enviar um Pull Request.

## Licença
Este projeto está sob a licença MIT.
