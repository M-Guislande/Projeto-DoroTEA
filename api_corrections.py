# Correções necessárias na API para compatibilidade com o Flutter

# 1. Alterar a rota de /select_music para /set_selected_music
@app.route('/set_selected_music', methods=['POST'])
def set_selected_music():
    dados = request.get_json()
    music_id = dados.get('music_id')
    is_user_music = dados.get('is_user_music', False)
    
    # Para este exemplo, usar user_id fixo = 1 (pode ser melhorado com autenticação)
    user_id = 1
    
    if is_user_music:
        # Música personalizada do usuário
        if not music_id:
            return jsonify({'erro': 'music_id é obrigatório para músicas personalizadas.'}), 400
            
        # Verificar se é um arquivo no diretório uploads
        if music_id.endswith('.mp3') or music_id.endswith('.wav'):
            music_url = f"{request.url_root}uploads/{music_id}"
            selected_type = 'custom'
        else:
            return jsonify({'erro': 'Formato de música inválido.'}), 400
    else:
        # Música padrão do app
        music_url = 'default'
        selected_type = 'default'
        music_id = None

    # Busca ou cria a entrada de seleção
    selecao = SelecaoMusica.query.filter_by(user_id=user_id).first()
    if not selecao:
        selecao = SelecaoMusica(user_id=user_id)
        db.session.add(selecao)

    selecao.selected_type = selected_type
    selecao.selected_music_id = music_id
    selecao.selected_music_url = music_url
    
    db.session.commit()

    return jsonify({
        'mensagem': 'Música selecionada com sucesso!',
        'selected_url': music_url,
        'selected_type': selected_type
    }), 200

# 2. Remover a rota antiga /select_music e substituir pela nova