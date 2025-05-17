import os
import speech_recognition as sr
import subprocess


def extrair_audio(input_video, output_audio):
    """Extrai o áudio de um arquivo MP4 e converte para WAV."""
    print("Extraindo áudio do vídeo...")
    command = f"ffmpeg -i {input_video} -ac 1 -ar 16000 {output_audio} -y"
    subprocess.run(command, shell=True, check=True)
    print("Áudio extraído com sucesso!")

def dividir_audio(input_video):
    """rodar esse comnado para dividir em partes de 5 minutos . WAV"""
    print("Extraindo áudio do vídeo...")
    command = f"ffmpeg -i {input_video} -f segment -segment_time 300 -c copy ./Audios/part_%03d.wav -y"
    subprocess.run(command, shell=True, check=True)
    print("Áudio extraído com sucesso!")

def transcrever_partes(diretorio, output_txt):
    recognizer = sr.Recognizer()
    transcricao = []

    for arquivo in sorted(os.listdir(diretorio)):
        if arquivo.endswith(".wav"):
            caminho = os.path.join(diretorio, arquivo)
            print(f"Processando: {caminho}")
            with sr.AudioFile(caminho) as source:
                audio_data = recognizer.record(source)
                try:
                    texto = recognizer.recognize_google(audio_data, language="pt-BR")
                    transcricao.append(texto)
                except sr.UnknownValueError:
                    print(f"Áudio não reconhecido: {caminho}")
                except sr.RequestError as e:
                    print(f"Erro de conexão: {e}")
    
    # Salvar a transcrição
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(transcricao))
    print(f"Transcrição salva em {output_txt}")

# Diretório com as partes do áudio
diretorio_partes = "./Audios"

# Configuração dos arquivos
input_mp4 = "audio.mp4"  # Substitua pelo caminho do seu arquivo MP4
output_wav = "audio_extraido.wav"  # Nome do áudio extraído
output_txt = "transcricao.txt"  # Nome do arquivo de saída de texto

# Execução
extrair_audio(input_mp4, output_wav)
dividir_audio(output_wav)
transcrever_partes(diretorio_partes, "transcricao_final.txt")

