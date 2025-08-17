from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import re
from werkzeug.security import generate_password_hash

app = Flask(__name__)
# Configurações do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urso.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Lista de códigos de urso válidos
codigos_urso_validos = ['URSO-ALPHA', 'URSO-BETA', 'URSO-GAMA', 'URSO-DELTA']

# --- Modelos do Banco de Dados ---
# Tabela para os usuários
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    codigo_urso = db.Column(db.String(50), nullable=False)

# Tabela para os códigos de urso
class CodigoUrso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    usado = db.Column(db.Boolean, default=False)

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

# --- NOVA ROTA para limpar códigos de urso ---
@app.route('/limpar_codigos_urso', methods=['POST'])
def limpar_codigos_urso():
    codigos_limpos_count = 0
    # Encontra todos os códigos marcados como usados
    codigos_usados = CodigoUrso.query.filter_by(usado=True).all()
    
    for codigo_db in codigos_usados:
        # Verifica se existe um usuário com este código
        usuario = Usuario.query.filter_by(codigo_urso=codigo_db.codigo).first()
        
        # Se não houver usuário, significa que o código pode ser liberado
        if not usuario:
            codigo_db.usado = False
            codigos_limpos_count += 1
            
    db.session.commit()
    return jsonify({'mensagem': f'{codigos_limpos_count} códigos de urso foram liberados com sucesso.'}), 200


if __name__ == '__main__':
    app.run(port=5000, debug=True)