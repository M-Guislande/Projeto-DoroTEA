from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import re
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
# Configurações do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urso.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Lista de códigos de urso válidos
codigos_urso_validos = ['URSO-ALPHA', 'URSO-BETA', 'URSO-GAMA', 'URSO-DELTA']

# --- Modelos do Banco de Dados ---
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    codigo_urso = db.Column(db.String(50), nullable=False)

class CodigoUrso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    usado = db.Column(db.Boolean, default=False)
# --- Modelo do Banco de Dados para Músicas ---
class Musica(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    audio_url = db.Column(db.String(255), nullable=False)
    is_deletable = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    user = db.relationship('Usuario', backref=db.backref('musicas', lazy=True))
# --- Modelo do Banco de Dados para Eventos de Humor ---
class HumorEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.DateTime, nullable=False)
    musica = db.Column(db.String(255))
    duracao = db.Column(db.String(50))
    humor = db.Column(db.String(50), nullable=False)
    mudanca_humor = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    user = db.relationship('Usuario', backref=db.backref('humor_events', lazy=True))
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
    if len(senha) < 6:
        return False
    if not any(char.isdigit() for char in senha):
        return False
    return True

# --- Rota de Cadastro ---
@app.route('/cadastro', methods=['POST'])
def cadastrar_usuario():
    try:
        dados = request.get_json()
    except Exception as e:
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

    usuario_existente = Usuario.query.filter_by(email=email).first()
    if usuario_existente:
        return jsonify({'erro': 'Email já cadastrado.'}), 409

    senha_hash = generate_password_hash(senha)

    novo_usuario = Usuario(
        nome_completo=nome,
        email=email,
        senha_hash=senha_hash,
        codigo_urso=codigo_urso
    )
    db.session.add(novo_usuario)
    codigo_db.usado = True
    db.session.commit()

    return jsonify({'mensagem': 'Usuário cadastrado com sucesso!', 'usuario': {'nome_completo': nome, 'email': email}}), 201

# --- Rota para listar usuários ---
@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    usuarios_db = Usuario.query.all()
    lista_limpa = [{'nome_completo': u.nome_completo, 'email': u.email, 'codigo_urso': u.codigo_urso} for u in usuarios_db]
    return jsonify(lista_limpa)

# --- Rota para APAGAR um usuário ---
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

# --- Rota para MODIFICAR um usuário ---
@app.route('/usuarios/<string:email>', methods=['PUT'])
def modificar_usuario(email):
    try:
        dados = request.get_json()
    except Exception as e:
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
# --- Nova Rota para buscar dados do usuário ---
@app.route('/usuario/<email>', methods=['GET'])
def get_usuario(email):
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado.'}), 404
        
    usuario_data = {
        'nome_completo': usuario.nome_completo,
        'email': usuario.email,
        'codigo_urso': usuario.codigo_urso
    }
    return jsonify(usuario_data), 200
# --- NOVA ROTA para limpar códigos de urso ---
@app.route('/limpar_codigos_urso', methods=['POST'])
def limpar_codigos_urso():
    codigos_limpos_count = 0
    codigos_usados = CodigoUrso.query.filter_by(usado=True).all()
    
    for codigo_db in codigos_usados:
        usuario = Usuario.query.filter_by(codigo_urso=codigo_db.codigo).first()
        if not usuario:
            codigo_db.usado = False
            codigos_limpos_count += 1
            
    db.session.commit()
    return jsonify({'mensagem': f'{codigos_limpos_count} códigos de urso foram liberados com sucesso.'}), 200

# --- Rota de Login ---
@app.route('/login', methods=['POST'])
def login_usuario():
    try:
        dados = request.get_json()
    except Exception:
        return jsonify({'erro': 'Formato de requisição inválido. O corpo da requisição deve ser JSON.'}), 400

    if 'email' not in dados or 'senha' not in dados:
        return jsonify({'erro': 'Os campos "email" e "senha" são obrigatórios.'}), 400

    email = dados['email']
    senha = dados['senha']

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado.'}), 404

    if not check_password_hash(usuario.senha_hash, senha):
        return jsonify({'erro': 'Senha incorreta.'}), 401

    return jsonify({
        'mensagem': 'Login realizado com sucesso!',
        'usuario': {
            'nome_completo': usuario.nome_completo,
            'email': usuario.email,
            'codigo_urso': usuario.codigo_urso
        }
    }), 200

# --- Rota para Carregar Músicas do Usuário ---
@app.route('/musics/<email>', methods=['GET'])
def get_user_musics(email):
    # Encontra o usuário pelo email
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado.'}), 404
    
    # Busca todas as músicas associadas a este usuário
    musicas = Musica.query.filter_by(user_id=usuario.id).all()
    
    # Converte os objetos de música para um formato JSON
    musicas_json = []
    for musica in musicas:
        musicas_json.append({
            'id': musica.id,
            'title': musica.title,
            'time': musica.time,
            'audioUrl': musica.audio_url,
            'isSelected': False,
            'isDeletable': musica.is_deletable
        })
    
    return jsonify({'musics': musicas_json}), 200

# --- Rota para Adicionar Músicas ---
@app.route('/add_music', methods=['POST'])
def add_music():
    try:
        dados = request.get_json()
    except Exception:
        return jsonify({'erro': 'Formato de requisição inválido. O corpo da requisição deve ser JSON.'}), 400

    required_fields = ['email', 'title', 'audio_url', 'time']
    if not all(field in dados for field in required_fields):
        return jsonify({'erro': f'Os campos {", ".join(required_fields)} são obrigatórios.'}), 400

    email = dados['email']
    title = dados['title']
    audio_url = dados['audio_url']
    time = dados['time']

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado.'}), 404

    try:
        nova_musica = Musica(
            title=title,
            time=time,
            audio_url=audio_url,
            is_deletable=True, # A partir do front-end, a música é deletável
            user_id=usuario.id
        )
        db.session.add(nova_musica)
        db.session.commit()
        return jsonify({'mensagem': 'Música adicionada com sucesso!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao adicionar música.', 'detalhes': str(e)}), 500

# --- Rota para Deletar Músicas ---
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

# --- Rota para Relatórios de Humor ---
@app.route('/report/<email>', methods=['GET'])
def get_humor_report(email):
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado.'}), 404

    humor_events = HumorEvent.query.filter_by(user_id=usuario.id).order_by(HumorEvent.data_hora.desc()).all()

    if not humor_events:
        return jsonify({'mensagem': 'Nenhum evento de humor encontrado para este usuário.'}), 200

    events_json = []
    for event in humor_events:
        events_json.append({
            'dataHora': event.data_hora.isoformat(),
            'musica': event.musica,
            'duracao': event.duracao,
            'humor': event.humor,
            'mudancaHumor': event.mudanca_humor
        })

    return jsonify(events_json), 200

# --- Executa o aplicativo ---
if __name__ == '__main__':
    app.run(port=5000, debug=True)
