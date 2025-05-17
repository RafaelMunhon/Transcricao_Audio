import os
import speech_recognition as sr
import subprocess
import logging
from typing import List
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('transcricao.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Configurações globais
AUDIO_DIR = Path("./Audios")
SEGMENT_TIME = 300  # 5 minutos em segundos

# Determinar o caminho do FFmpeg baseado no ambiente
if os.environ.get('VERCEL_ENV'):
    FFMPEG_PATH = 'ffmpeg'  # No Vercel, ffmpeg está no PATH
else:
    FFMPEG_PATH = Path("C:/ffmpeg/bin/ffmpeg.exe")  # Local Windows path

def verificar_ffmpeg() -> bool:
    """Verifica se o FFmpeg está instalado no sistema."""
    try:
        ffmpeg_cmd = 'ffmpeg' if os.environ.get('VERCEL_ENV') else str(FFMPEG_PATH)
        subprocess.run([ffmpeg_cmd, '-version'], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def setup_directories() -> None:
    """Cria os diretórios necessários para o projeto."""
    try:
        AUDIO_DIR.mkdir(exist_ok=True)
        logger.info(f"Diretório '{AUDIO_DIR}' verificado/criado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao criar diretório: {e}")
        raise

def extrair_audio(input_video: str, output_audio: str) -> None:
    """Extrai o áudio de um arquivo MP4 e converte para WAV."""
    try:
        print("Extraindo áudio do vídeo...")
        result = subprocess.run(
            [str(FFMPEG_PATH), '-i', input_video, '-ac', '1', '-ar', '16000', output_audio, '-y'],
            capture_output=True,
            text=True,
            encoding='latin-1',
            errors='replace'
        )
        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode,
                result.args,
                result.stdout,
                result.stderr
            )
        print("Áudio extraído com sucesso!")
    except Exception as e:
        print(f"Erro ao extrair áudio: {e}")
        raise

def dividir_audio(input_audio: str) -> None:
    """Divide o áudio em segmentos de 5 minutos."""
    try:
        print("Dividindo áudio em partes...")
        
        result = subprocess.run(
            [str(FFMPEG_PATH), '-i', input_audio, '-f', 'segment', 
             '-segment_time', '300', '-c', 'copy',
             str(AUDIO_DIR / 'part_%03d.wav'), '-y'],
            capture_output=True,
            text=True,
            encoding='latin-1',
            errors='replace'
        )
        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode,
                result.args,
                result.stdout,
                result.stderr
            )
        print("Áudio dividido com sucesso!")
    except Exception as e:
        print(f"Erro ao dividir áudio: {e}")
        raise

def transcrever_partes(diretorio: Path, output_txt: str) -> None:
    """Transcreve todas as partes do áudio para texto."""
    recognizer = sr.Recognizer()
    transcricao = []

    try:
        arquivos_audio = sorted(list(Path(diretorio).glob("*.wav")))
        if not arquivos_audio:
            raise FileNotFoundError(f"Nenhum arquivo WAV encontrado em {diretorio}")

        total_arquivos = len(arquivos_audio)
        print(f"Iniciando transcrição de {total_arquivos} arquivos...")
        
        for idx, arquivo in enumerate(arquivos_audio, 1):
            print(f"Processando arquivo {idx}/{total_arquivos}: {arquivo.name}")
            
            with sr.AudioFile(str(arquivo)) as source:
                audio_data = recognizer.record(source)
                try:
                    texto = recognizer.recognize_google(audio_data, language="pt-BR")
                    transcricao.append(texto)
                    print(f"Transcrição bem-sucedida para {arquivo.name}")
                except sr.UnknownValueError:
                    print(f"Áudio não reconhecido: {arquivo.name}")
                except sr.RequestError as e:
                    print(f"Erro na API do Google Speech Recognition: {e}")
                    raise
        
        # Salvar a transcrição
        output_path = Path(output_txt)
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(transcricao))
        print(f"Transcrição completa salva em {output_txt}")
        
    except Exception as e:
        print(f"Erro durante a transcrição: {e}")
        raise

def main():
    """Função principal que coordena o processo de transcrição."""
    try:
        # Verificar FFmpeg
        if not verificar_ffmpeg():
            logger.error(f"FFmpeg não encontrado no caminho: {FFMPEG_PATH}")
            print("\nVerifique se o caminho do FFmpeg está correto na configuração:")
            print(f"Caminho atual: {FFMPEG_PATH}")
            return

        # Configuração dos arquivos
        input_mp4 = "audio.mp4"
        output_wav = "audio_extraido.wav"
        output_txt = "transcricao_final.txt"

        # Verificar se o arquivo de entrada existe
        if not os.path.exists(input_mp4):
            logger.error(f"Arquivo de entrada '{input_mp4}' não encontrado")
            print(f"\nPor favor, coloque o arquivo '{input_mp4}' no diretório do projeto.")
            print("O arquivo deve estar no mesmo diretório que o script main.py")
            return

        # Criar estrutura de diretórios
        setup_directories()

        # Executar pipeline de processamento
        extrair_audio(input_mp4, output_wav)
        dividir_audio(output_wav)
        transcrever_partes(AUDIO_DIR, output_txt)

        # Limpar arquivos temporários
        if os.path.exists(output_wav):
            os.remove(output_wav)
            logger.info("Arquivo temporário de áudio removido")

        logger.info("Processo de transcrição concluído com sucesso!")
        print(f"\nTranscrição concluída! O resultado está em: {output_txt}")

    except Exception as e:
        logger.error(f"Erro durante a execução: {e}")
        print("\nOcorreu um erro durante a execução. Verifique o arquivo 'transcricao.log' para mais detalhes.")

if __name__ == "__main__":
    main()

