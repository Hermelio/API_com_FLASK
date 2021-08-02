from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

# ConfiguraÃ§Ãµes inicias
app.config['SECRET_KEY'] = 'segredo2030'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

db = SQLAlchemy(app)
db: SQLAlchemy


class Postagem(db.Model):
    __tablename__ = 'postagem'
    id_postagem = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String)
    id_autor = db.Column(db.Integer, db.ForeignKey('autor.id_autor'))


class Autor(db.Model):
    __tablename__ = 'autor'
    id_autor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    email = db.Column(db.String)
    senha = db.Column(db.String)
    admin = db.Column(db.Boolean)
    postagens = db.relationship('Postagem')


def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Verificar se foi incluÃ­do um token na requisiÃ§Ã£o
        if 'x-acess-token' in request.headers:
            token = request.headers['x-acess-token']
        # Se nÃ£o houver um token, retornar a requesiÃ§Ã£o, solicitando um token
        if not token:
            return jsonify({'mensagem': 'Token de autenticaÃ§Ã£o precisa ser incluÃ­do nessa requisiÃ§Ã£o!'})
        try:
            dados = jwt.decode(token, app.config['SECRET_KEY'])
            autor_atual = Autor.query.filter_by(
                id_autor=dados['id_autor']).first()
        except:
            return jsonify({'mensagem': 'Token Ã© invÃ¡lido!'}, 401)

        return f(autor_atual, *args, **kwargs)
    # retornando o decorador
    return decorated


@app.route('/postagens', methods=['GET'])
@token_obrigatorio
def obter_todas_postagens(autor_atual):
    postagens = Postagem.query.all()

    lista_postagens = []
    for postagem in postagens:
        dados_postagem = {}
        dados_postagem['titulo'] = postagem.titulo
        dados_postagem['id_autor'] = postagem.id_autor
        lista_postagens.append(dados_postagem)

    return jsonify({'postagens': lista_postagens})


@app.route('/postagens/<int:id_postagem>', methods=['GET'])
@token_obrigatorio
def obter_postagem_por_id(autor_atual, id_postagem):
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()

    dados_postagem = {}
    dados_postagem['titulo'] = postagem.titulo
    dados_postagem['id_autor'] = postagem.id_autor

    return jsonify({'postagens': dados_postagem})


@app.route('/postagens', methods=['POST'])
@token_obrigatorio
def nova_postagem(autor_atual):
    postagem = request.get_json()

    nova_postagem = Postagem(
        titulo=postagem['titulo'], id_autor=postagem['id_autor'])

    db.session.add(nova_postagem)
    db.session.commit()

    return jsonify({'nova postagem': 'postagem criado com sucesso!'})


@app.route('/postagens/<int:id_postagem>', methods=['PUT'])
@token_obrigatorio
def atualizar_postagem(autor_atual, id_postagem):
    dados = request.get_json()
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()

    postagem.titulo = dados['titulo']
    postagem.id_autor = dados['id_autor']

    db.session.commit()

    return jsonify({'mensagem': 'Postagem alterada com sucesso!'})


@app.route('/postagens/<int:id_postagem>', methods=['DELETE'])
@token_obrigatorio
def excluir_postagem(autor_atual, id_postagem):
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()

    if not postagem:
        return jsonify({'mensagem': 'Postagem nÃ£o encontrada'})

    db.session.delete(postagem)
    db.session.commit()

    return jsonify({'mensagem': 'A postagem foi excluÃ­da!'})

# * Criar uma api para criar novos autores


@app.route('/autores', methods=['GET'])
@token_obrigatorio
def obter_todos_autores(autor_atual):
    autores = Autor.query.all()
    lista_de_autores = []
    for autor in autores:
        dados_autores = {}
        dados_autores['id_autor'] = autor.id_autor
        dados_autores['nome'] = autor.nome
        dados_autores['email'] = autor.email
        lista_de_autores.append(dados_autores)

    return jsonify({'autores': lista_de_autores})


@app.route('/autores/<int:id_autor>', methods=['GET'])
@token_obrigatorio
def obter_autor_por_id(autor_atual, id_autor):
    autor = Autor.query.filter_by(id_autor=id_autor).first()

    if not autor:
        return jsonify({'mensagem': 'Autor nÃ£o encontrado'})

    dados_autor = {}
    dados_autor['id_autor'] = autor.id_autor
    dados_autor['nome'] = autor.nome
    dados_autor['email'] = autor.email

    return jsonify({'autor': dados_autor})


@app.route('/autores', methods=['POST'])
@token_obrigatorio
def novo_autor(autor_atual):
    dados = request.get_json()

    novo_usuario = Autor(nome=dados['nome'],
                         senha=dados['senha'], email=dados['email'])

    db.session.add(novo_usuario)
    db.session.commit()

    return jsonify({'mensagem': 'Novo usuÃ¡rio criado com sucesso!'}, 200)


@app.route('/autores/<int:id_autor>', methods=['PUT'])
@token_obrigatorio
def atualizar_ator(autor_atual, id_autor):
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    dados_autor = request.get_json()

    autor.nome = dados_autor['nome']
    autor.email = dados_autor['email']

    db.session.commit()

    return jsonify({'mensagem': 'autor foi alterado com sucesso!'})


@app.route('/autores/<int:id_autor>', methods=['DELETE'])
@token_obrigatorio
def excluir_autor(autor_atual, id_autor):
    autor = Autor.query.filter_by(id_autor=id_autor).first()

    if not autor:
        return jsonify({'mensagem': 'Autor nÃ£o encontrado'})

    db.session.delete(autor)
    db.session.commit()

    return jsonify({'mensagem': ' Autor excluÃ­do com sucesso!'})


@app.route('/login')
def login():
    dados_autenticacao = request.authorization

    if not dados_autenticacao or not dados_autenticacao.username or not dados_autenticacao.password:
        return make_response('Login invÃ¡lido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatÃ³rio!"'})

    user = Autor.query.filter_by(nome=dados_autenticacao.username).first()
    if user.senha == dados_autenticacao.password:
        token = jwt.encode({'id_autor': user.id_autor, 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Login invÃ¡lido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatÃ³rio!"'})


if __name__ == '__main__':
    app.run(port=5000, host='localhost', debug=True)
