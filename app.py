from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from main import extrair_audio, dividir_audio, transcrever_partes, setup_directories, AUDIO_DIR
from pathlib import Path
from flask_cors import CORS
import shutil
import glob

# Configurar o caminho base do aplicativo
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'

# Configurar diretórios de trabalho
UPLOAD_DIR = BASE_DIR / 'uploads'
AUDIO_DIR = BASE_DIR / 'Audios'
OUTPUT_DIR = BASE_DIR / 'output'

# Extensões permitidas
ALLOWED_EXTENSIONS = {
    # Formatos de vídeo
    'mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm',
    # Formatos de áudio
    'mp3', 'wav', 'ogg', 'm4a', 'wma', 'aac', 'flac','waptt'
}

# Criar diretórios se não existirem
UPLOAD_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app = Flask(__name__, 
           template_folder=str(TEMPLATE_DIR),
           static_folder=str(STATIC_DIR))
CORS(app)

# Configurações do aplicativo
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max-limit

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def limpar_diretorios_trabalho():
    """Limpa todos os diretórios de trabalho."""
    try:
        print("\nIniciando limpeza dos diretórios...")
        print(f"Diretório atual: {BASE_DIR}")

        # Função auxiliar para limpar diretório
        def limpar_diretorio(diretorio: Path, extensao: str = "*"):
            for arquivo in diretorio.glob(f"*.{extensao}"):
                try:
                    arquivo.unlink()
                    print(f"Arquivo removido: {arquivo}")
                except Exception as e:
                    print(f"Erro ao remover {arquivo}: {e}")

        # Limpar diretório de uploads
        print("\nLimpando diretório de uploads...")
        for ext in ALLOWED_EXTENSIONS:
            limpar_diretorio(UPLOAD_DIR, ext)

        # Limpar diretório de áudios
        print("\nLimpando diretório de áudios...")
        limpar_diretorio(AUDIO_DIR, "wav")

        # Limpar diretório de saída
        print("\nLimpando diretório de saída...")
        limpar_diretorio(OUTPUT_DIR, "txt")

        print("\nLimpeza concluída com sucesso!")
    except Exception as e:
        print(f"Erro durante a limpeza: {e}")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(str(STATIC_DIR),
                             'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    # Limpar diretórios ao carregar a página
    limpar_diretorios_trabalho()
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Erro ao carregar template: {str(e)}", 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Limpar diretórios antes de começar
        limpar_diretorios_trabalho()

        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'Formato de arquivo não suportado. Formatos aceitos: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

        # Preparar caminhos dos arquivos
        filename = secure_filename(file.filename)
        input_file = UPLOAD_DIR / filename
        output_wav = UPLOAD_DIR / "audio_extraido.wav"
        output_txt = OUTPUT_DIR / "transcricao_final.txt"
        
        # Salvar e processar arquivo
        file.save(str(input_file))
        print(f"\nArquivo salvo em: {input_file}")

        extrair_audio(str(input_file), str(output_wav))
        print(f"Áudio extraído para: {output_wav}")

        dividir_audio(str(output_wav))
        print(f"Áudios divididos salvos em: {AUDIO_DIR}")

        transcrever_partes(AUDIO_DIR, str(output_txt))
        print(f"Transcrição salva em: {output_txt}")

        # Ler resultado
        if not output_txt.exists():
            raise FileNotFoundError(f"Arquivo de transcrição não foi criado: {output_txt}")
        
        with open(output_txt, 'r', encoding='utf-8') as f:
            transcricao = f.read()

        return jsonify({'transcricao': transcricao})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Limpar diretórios ao iniciar o servidor
    limpar_diretorios_trabalho()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 