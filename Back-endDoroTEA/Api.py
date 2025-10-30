from flask import Flask, jsonify, request, send_file, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import cv2
from fer.fer import FER
import time
import os
import re
import mimetypes
import threading
from threading import Lock 

# --- Configuração principal ---
app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Configurações do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urso.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Lista de códigos de urso válidos
codigos_urso_validos = ['URSO-ALPHA', 'URSO-BETA', 'URSO-GAMA', 'URSO-DELTA']

# --- Configuração do diretório de upload ---
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- Modelos do Banco de Dados ---
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    codigo_urso = db.Column(db.String(120), nullable=False)
    musics = db.relationship('Musica', backref='user', lazy=True)
    humor_events = db.relationship('HumorEvent', backref='user', lazy=True)
    selected_music = db.relationship('SelecaoMusica', backref='user', uselist=False, lazy=True) # Relação 1:1

class CodigoUrso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(120), unique=True, nullable=False)
    usado = db.Column(db.Boolean, default=False)

class Musica(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    artist = db.Column(db.String(255), nullable=True)
    audio_url = db.Column(db.String(255), nullable=False)
    is_deletable = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

class HumorEvent(db.Model):
    __tablename__ = 'humor_event'
    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.String(80), nullable=False)
    duracao = db.Column(db.Float)
    humor = db.Column(db.String(80), nullable=False)
    mudanca = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    def __repr__(self):
        return f'<HumorEvent {self.humor}>'

class SelecaoMusica(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), unique=True, nullable=False)
    selected_type = db.Column(db.String(10), default='default', nullable=False) 
    # Em modo de teste, selected_music_id guarda o nome do arquivo.
    selected_music_id = db.Column(db.String(255), nullable=True) 
    selected_music_url = db.Column(db.String(255), nullable=False, default="default") 

# --- Inicializações ---
# Atenção: Esta URL pode causar timeouts. Se der erro, mude para CAMERA_URL = 0
CAMERA_URL = "rtsp://admin:admin@192.168.40.20:554/stream1"
PROCESS_SCALE = 0.5
USE_MTCNN = True
detector = FER(mtcnn=USE_MTCNN)

cap = None 
latest_snapshot_buffer = None 
snapshot_lock = Lock() 
DETECTION_INTERVAL = 1.0  
PERSISTENCE_COUNT = 3     

# --- Criar o banco de dados e as tabelas ---
with app.app_context():
    db.create_all()
    for codigo in codigos_urso_validos:
        if not CodigoUrso.query.filter_by(codigo=codigo).first():
            db.session.add(CodigoUrso(codigo=codigo))
    db.session.commit()

# --- Funções de Validação ---
def validar_email(email):
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(padrao, email) is not None

def validar_senha(senha):
    return len(senha) >= 6 and any(char.isdigit() for char in senha)

# --- Funções de Humor ---
def salvar_evento(humor_atual, humor_anterior, duracao, user_id):
    evento = HumorEvent(
        data_hora=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        humor=humor_atual,
        mudanca=humor_anterior,
        duracao=duracao,
        user_id=user_id
    )
    db.session.add(evento)
    db.session.commit()
    print(f"[OK] Evento salvo: {humor_anterior} -> {humor_atual} ({duracao}s)")

def detectar_emocao(frame):
    small = cv2.resize(frame, (0, 0), fx=PROCESS_SCALE, fy=PROCESS_SCALE)
    detections = detector.detect_emotions(small)
    if not detections:
        return None
    emocao, _ = max(detections[0]["emotions"].items(), key=lambda i: i[1])
    return emocao

def flush_rtsp_buffer(cap, max_frames=10):
    for _ in range(max_frames):
        ret, frame = cap.read()
        if not ret:
            break
        time.sleep(0.01) 
    print(f"[INFO] Buffer RTSP esvaziado ({max_frames} frames lidos/descartados).")

# --- Thread de detecção contínua ---
def loop_deteccao_continua(user_id=1):
    global cap, latest_snapshot_buffer, snapshot_lock
    cap = cv2.VideoCapture(CAMERA_URL)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) 
    erro_count = 0
    humor_anterior = None
    inicio_tempo = time.time()
    last_detection_time = time.time() 
    pending_humor = None
    consecutive_count = 0
    print("[INFO] Loop de detecção contínua iniciado.")
    
    if cap.isOpened():
        flush_rtsp_buffer(cap) 
    
    while True:
        if not cap.isOpened():
            print("[ERRO] Reconectando à câmera...")
            cap = cv2.VideoCapture(CAMERA_URL)
            if cap.isOpened():
                flush_rtsp_buffer(cap) 
            time.sleep(5)
            continue

        ret, frame = cap.read()
        if not ret:
            erro_count += 1
            if erro_count >= 5:
                print("[ERRO] Falha na leitura do frame. Tentando reabrir o cap.")
                cap.release()
                cap = cv2.VideoCapture(CAMERA_URL)
                erro_count = 0
            time.sleep(0.1)
            continue
        
        erro_count = 0 
        ret_enc, buffer = cv2.imencode('.jpg', frame)
        if ret_enc:
            with snapshot_lock:
                latest_snapshot_buffer = buffer.tobytes()

        current_time = time.time()
        if current_time - last_detection_time >= DETECTION_INTERVAL:
            humor_atual = detectar_emocao(frame)
            if humor_atual is not None:
                print(f"[DEBUG] Emoção detectada: {humor_atual} | Última Confirmada: {humor_anterior} | Pendente: {pending_humor} ({consecutive_count}/{PERSISTENCE_COUNT})")
                
                if humor_atual == humor_anterior:
                    pending_humor = None
                    consecutive_count = 0
                elif humor_atual == pending_humor:
                    consecutive_count += 1
                    if consecutive_count >= PERSISTENCE_COUNT:
                        duracao = current_time - inicio_tempo 
                        if humor_anterior is not None:
                            with app.app_context(): 
                                salvar_evento(humor_atual, humor_anterior, round(duracao, 2), user_id)
                        print(f"[CONFIRMADO] Alteração para {humor_atual} após {PERSISTENCE_COUNT}s de persistência.")
                        humor_anterior = humor_atual
                        inicio_tempo = current_time 
                        pending_humor = None
                        consecutive_count = 0
                else:
                    pending_humor = humor_atual
                    consecutive_count = 1
            last_detection_time = current_time 
        time.sleep(0.01)

# --- Rotas de Vídeo e Snapshot ---
@app.route('/snapshot')
def snapshot():
    global latest_snapshot_buffer, snapshot_lock
    with snapshot_lock:
        if latest_snapshot_buffer is None:
            return 'A câmera ainda está inicializando ou indisponível.', 503 
        return Response(latest_snapshot_buffer, mimetype='image/jpeg')

# --- Rotas de Seleção de Música ---
# ROTA DE TESTE SIMPLIFICADA CORRIGIDA
@app.route('/select_music', methods=['POST'])
def set_selected_music():
    # 1. Tratamento robusto do corpo da requisição
    try:
        dados = request.get_json()
        if dados is None:
            return jsonify({'erro': 'Corpo da requisição inválido. Esperado JSON.'}), 400
    except Exception:
        # Se houver erro de decodificação JSON, é um erro 400
        return jsonify({'erro': 'Erro na leitura do JSON.'}), 400

    # music_id: ID interna (padrão, ex: 'dorotea') ou filename (custom)
    music_id = dados.get('music_id') 
    is_user_music = dados.get('is_user_music', False)
    
    user_id = 1 # Fixo para testes
    
    # 2. Determinação da URL e Tipo (LÓGICA CORRIGIDA AQUI)
    if is_user_music:
        # MÚSICA CUSTOMIZADA
        if not music_id:
             return jsonify({'erro': 'O campo music_id é obrigatório para músicas customizadas.'}), 400
             
        music_url = f"{request.url_root}uploads/{music_id}"
        selected_type = 'custom'
        # music_id já contém o nome do arquivo (ex: 'artista_titulo.mp3')
    else:
        # MÚSICA PADRÃO (O Flutter enviou a ID, ex: 'dorotea')
        
        # Se não houver ID para a música padrão, tratamos como 'default' genérico.
        # Caso contrário, usamos a ID enviada pelo Flutter (ex: 'dorotea').
        if not music_id:
             music_id = "generic_default"
             
        music_url = 'default' 
        selected_type = 'default'
        
        # CHAVE DA CORREÇÃO: Não sobrescrever music_id = None
        # O music_id enviado ('dorotea') será salvo no banco!

    # 3. Busca ou Criação do Registro de Seleção de Música
    selecao = SelecaoMusica.query.filter_by(user_id=user_id).first()
    if not selecao:
        selecao = SelecaoMusica(user_id=user_id)
        db.session.add(selecao)

    # 4. Atualização dos dados do objeto
    selecao.selected_type = selected_type
    # AQUI music_id pode ser 'dorotea' ou 'artista_titulo.mp3'
    selecao.selected_music_id = music_id 
    selecao.selected_music_url = music_url
    
    # 5. Commit e Tratamento de Erro
    try:
        db.session.commit()
        
        db.session.remove() 
        
        # Mudar a resposta para mostrar a music_id salva
        return jsonify({
            'mensagem': 'Música selecionada com sucesso!', 
            'selected_type': selected_type,
            'selected_url': music_url,
            'selected_music_id_saved': music_id # Novo campo de debug
        }), 200

    except Exception as e:
        db.session.rollback() 
        db.session.remove()
        
        print(f"[ERRO DB] Falha ao salvar seleção de música para user {user_id}: {str(e)}")
        return jsonify({'erro': 'Erro interno ao salvar a seleção de música.', 'detalhes': str(e)}), 500

@app.route('/get_selected_music/<int:user_id>', methods=['GET'])
def get_selected_music(user_id):
    selecao = SelecaoMusica.query.filter_by(user_id=user_id).first()

    if not selecao or selecao.selected_type == 'default':
        return jsonify({
            'selected_type': 'default', 
            'music_url': 'default' 
        }), 200
    
    return jsonify({
        'selected_type': selecao.selected_type,
        'music_url': selecao.selected_music_url,
        'music_id': selecao.selected_music_id
    }), 200

# ROTA MODIFICADA PARA INCLUIR O NOME DA MÚSICA SELECIONADA
@app.route('/ultima_emocao', methods=['GET'])
def get_ultima_emocao():
    # 1. Busca o último evento de humor
    ultimo_evento = HumorEvent.query.order_by(HumorEvent.id.desc()).first()
    
    # 2. Busca a música selecionada (para user_id=1, fixo para testes)
    user_id_teste = 1
    selecao = SelecaoMusica.query.filter_by(user_id=user_id_teste).first()

    # 3. Determina o nome/ID da música (usa selected_music_id que armazena o filename)
    # Se não houver seleção ou se for None, assume 'default'
    musica_selecionada = selecao.selected_music_id if selecao and selecao.selected_music_id else 'default'
    
    # 4. Determina a última emoção
    ultima_emocao = ultimo_evento.humor if ultimo_evento else "Nenhuma emoção registrada ainda."

    # 5. Retorna o JSON combinado
    return jsonify({
        "ultima_emocao": ultima_emocao,
        # O nome do arquivo (ou 'default') agora está incluído
        "musica_selecionada": musica_selecionada 
    }), 200

# --- Rotas de CRUD, login, cadastro, músicas etc. ---

# Rota para listar todos os eventos (mantida a lógica anterior)
@app.route('/eventos', methods=['GET'])
def listar_eventos():
    eventos = HumorEvent.query.order_by(HumorEvent.id.desc()).all()
    dados = [{
        "id": e.id, "user_id": e.user_id, "humor": e.humor, "mudanca": e.mudanca, "duracao": e.duracao, "data_hora": e.data_hora
    } for e in eventos]
    return jsonify({"total_eventos": len(dados), "eventos": dados}), 200

@app.route('/downloadable_files', methods=['GET'])
def list_downloadable_files():
    try:
        arquivos = os.listdir(app.config['UPLOAD_FOLDER'])
        musics_list = []
        for filename in arquivos:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                # Importante: A rota de teste usa o FILENAME como 'music_id'
                musics_list.append({'filename': filename, 'url': f"{request.url_root}uploads/{filename}"})
        return jsonify({"musics": musics_list})
    except Exception as e:
        return jsonify({"erro": "Erro ao listar arquivos para download.", "detalhes": str(e)}), 500

@app.route('/cadastro', methods=['POST'])
def cadastrar_usuario():
    try:
        dados = request.get_json()
    except Exception:
        return jsonify({'erro': 'Formato de requisição inválido. O corpo da requisição deve ser JSON.'}), 400

    campos_obrigatorios = ['nome_completo', 'email', 'senha', 'confirme_senha', 'codigo_urso']
    campos_faltando = [campo for campo in campos_obrigatorios if campo not in dados or not dados[campo]]

    if campos_faltando:
        return jsonify({'erro': f'Os seguintes campos são obrigatórios: {", ".join(campos_faltando)}.'}), 400

    nome = dados['nome_completo']
    email = dados['email']
    senha = dados['senha']
    confirma_senha = dados['confirme_senha']
    codigo_urso = dados['codigo_urso']

    codigo_db = CodigoUrso.query.filter_by(codigo=codigo_urso).first()
    if not codigo_db:
        return jsonify({'erro': 'Código do Urso inválido.'}), 400
    if codigo_db.usado:
        return jsonify({'erro': 'Este Código do Urso já foi utilizado.'}), 400

    if not validar_email(email):
        return jsonify({'erro': 'Email inválido.'}), 400
    if not validar_senha(senha):
        return jsonify({'erro': 'A senha deve ter pelo menos 6 caracteres e incluir no mínimo um número.'}), 400
    if senha != confirma_senha:
        return jsonify({'erro': 'As senhas não coincidem.'}), 400

    if Usuario.query.filter_by(email=email).first():
        return jsonify({'erro': 'Email já cadastrado.'}), 409

    senha_hash = generate_password_hash(senha)
    novo_usuario = Usuario(nome_completo=nome, email=email, senha_hash=senha_hash, codigo_urso=codigo_urso)

    db.session.add(novo_usuario)
    codigo_db.usado = True
    db.session.commit()

    return jsonify({'mensagem': 'Usuário cadastrado com sucesso!', 'usuario': {'nome_completo': nome, 'email': email}}), 201

@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    usuarios_db = Usuario.query.all()
    lista_limpa = [{'nome_completo': u.nome_completo, 'email': u.email, 'codigo_urso': u.codigo_urso} for u in usuarios_db]
    return jsonify(lista_limpa)

@app.route('/usuarios/<string:email>', methods=['DELETE'])
def apagar_usuario(email):
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado.'}), 404

    codigo_urso_usado = CodigoUrso.query.filter_by(codigo=usuario.codigo_urso).first()
    if codigo_urso_usado:
        codigo_urso_usado.usado = False

    db.session.delete(usuario)
    db.session.commit()
    return jsonify({'mensagem': 'Usuário apagado com sucesso e código do urso resetado!'}), 200

@app.route('/usuarios/<string:email>', methods=['PUT'])
def modificar_usuario(email):
    try:
        dados = request.get_json()
    except Exception:
        return jsonify({'erro': 'Formato de requisição inválido. O corpo da requisição deve ser JSON.'}), 400

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado.'}), 404

    if 'nome_completo' in dados:
        usuario.nome_completo = dados['nome_completo']
    if 'senha' in dados:
        if not validar_senha(dados['senha']):
            return jsonify({'erro': 'Nova senha inválida.'}), 400
        usuario.senha_hash = generate_password_hash(dados['senha'])
    if 'codigo_urso' in dados:
        usuario.codigo_urso = dados['codigo_urso']

    db.session.commit()
    return jsonify({'mensagem': 'Usuário modificado com sucesso!', 'usuario': {'nome_completo': usuario.nome_completo, 'email': usuario.email, 'codigo_urso': usuario.codigo_urso}}), 200

@app.route('/usuario/<email>', methods=['GET'])
def get_usuario(email):
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado.'}), 404
    return jsonify({'nome_completo': usuario.nome_completo, 'email': usuario.email, 'codigo_urso': usuario.codigo_urso}), 200

@app.route('/login', methods=['POST'])
def login_usuario():
    try:
        dados = request.get_json()
    except Exception:
        return jsonify({'erro': 'Formato de requisição inválido. O corpo da requisição deve ser JSON.'}), 400

    if 'email' not in dados or 'senha' not in dados:
        return jsonify({'erro': 'Os campos "email" e "senha" são obrigatórios.'}), 400

    usuario = Usuario.query.filter_by(email=dados['email']).first()
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado.'}), 404
    if not check_password_hash(usuario.senha_hash, dados['senha']):
        return jsonify({'erro': 'Senha incorreta.'}), 401

    return jsonify({'mensagem': 'Login realizado com sucesso!', 'usuario': {'nome_completo': usuario.nome_completo, 'email': usuario.email, 'codigo_urso': usuario.codigo_urso, 'user_id': usuario.id}}), 200 

@app.route('/musics/<email>', methods=['GET'])
def get_user_musics(email):
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado.'}), 404

    musicas = Musica.query.filter_by(user_id=usuario.id).all()
    # Importante: O music_id aqui será o ID real do banco de dados (que pode ser diferente do nome do arquivo).
    musicas_json = [{'id': m.id, 'title': m.title, 'artist': m.artist, 'audioUrl': m.audio_url, 'isSelected': False, 'isDeletable': m.is_deletable} for m in musicas]
    return jsonify({'musics': musicas_json}), 200

@app.route('/add_music', methods=['POST'])
def add_music():
    if 'file' not in request.files:
        return jsonify({'erro': 'Nenhum arquivo enviado.'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'erro': 'Nome do arquivo inválido.'}), 400

    email = request.form.get('email')
    title = request.form.get('title')
    artist = request.form.get('artist')

    if not email or not title or not artist:
        return jsonify({'erro': 'Campos obrigatórios: email, title, artist.'}), 400

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado.'}), 404

    try:
        if Musica.query.filter_by(title=title, artist=artist, user_id=usuario.id).first():
            return jsonify({'erro': 'Essa música já foi adicionada para este usuário.'}), 409

        base_name = re.sub(r'[^a-zA-Z0-9_-]', '_', f"{artist}_{title}")
        ext = os.path.splitext(file.filename)[1]
        filename = secure_filename(f"{base_name}{ext}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if os.path.exists(file_path):
            return jsonify({'erro': 'Já existe um arquivo salvo com esse nome.'}), 409

        file.save(file_path)
        file_url = f"{request.url_root}uploads/{filename}"

        nova_musica = Musica(title=title, artist=artist, audio_url=file_url, is_deletable=True, user_id=usuario.id)
        db.session.add(nova_musica)
        db.session.commit()

        return jsonify({'mensagem': 'Música enviada e adicionada com sucesso!', 'url': file_url}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao adicionar música.', 'detalhes': str(e)}), 500

@app.route('/delete_music/<int:music_id>', methods=['DELETE'])
def delete_music(music_id):
    musica = Musica.query.get(music_id)
    if not musica:
        return jsonify({'erro': 'Música não encontrada.'}), 404
    try:
        db.session.delete(musica)
        db.session.commit()
        return jsonify({'mensagem': 'Música deletada com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao deletar música.', 'detalhes': str(e)}), 500

@app.route('/arquivos', methods=['GET'])
def listar_arquivos():
    try:
        pasta_uploads = app.config['UPLOAD_FOLDER']
        
        if not os.path.exists(pasta_uploads):
            return jsonify({'erro': 'Pasta de uploads não encontrada.'}), 404

        arquivos = [f for f in os.listdir(pasta_uploads) if os.path.isfile(os.path.join(pasta_uploads, f))]

        if not arquivos:
            return jsonify({'mensagem': 'Nenhum arquivo encontrado.'}), 200

        return jsonify({'arquivos': arquivos}), 200

    except Exception as e:
        return jsonify({'erro': 'Erro ao listar arquivos.', 'detalhes': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({'erro': 'Arquivo não encontrado.'}), 404

    mime_type, _ = mimetypes.guess_type(file_path)
    return send_file(file_path, mimetype=mime_type or 'application/octet-stream', as_attachment=False)

# --- Executa o aplicativo ---
if __name__ == '__main__':

    # Inicia o thread de detecção contínua em segundo plano
    thread = threading.Thread(target=loop_deteccao_continua, args=(1,), daemon=True)
    thread.start()

    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
