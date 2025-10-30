# 🎧🐻 doroTEA — Assistente Emocional Infantil

Aplicativo desenvolvido com **Flutter/Dart** (frontend) e **Python + Flask** (API) para auxiliar no **acompanhamento emocional de crianças com TEA** (Transtorno do Espectro Autista).  
O sistema monitora expressões faciais via câmera IP, detecta emoções usando IA e adapta músicas e respostas de acordo com o humor da criança.

---

## 🎯 Objetivo do Projeto
Criar uma interface simples e amigável que permita:
✅ Identificar emoções em tempo real utilizando visão computacional  
✅ Registrar mudanças emocionais ao longo do tempo  
✅ Reagir de forma sensorial com músicas adequadas  
✅ Gerenciar perfis e interação com o sistema  

Esse projeto foi desenvolvido no contexto acadêmico na ETE FMC e avaliado em sala.

---

## 🧠 Tecnologias & Conceitos Aplicados

### 📱 Frontend (Flutter/Dart)
- Gerenciamento de estado
- Navegação estruturada por páginas
- Requisições HTTP com autenticação
- Reprodução de áudio
- Upload de arquivos
- Design intuitivo para crianças

### 🐍 Backend (Python + Flask)
- APIs RESTful com CORS habilitado
- Banco de dados com SQLite + SQLAlchemy (ORM)
- Migrações com Flask-Migrate
- Hash seguro de senhas utilizando Werkzeug
- CRUD completo:
  - Usuários
  - Seleção de músicas
  - Eventos de humor detectados
- Upload e serving de arquivos
- Streaming de imagem da câmera em tempo real

### 🤖 Inteligência Artificial
- Biblioteca **FER (Facial Emotion Recognition)** pré-treinada
- Detector com **MTCNN** para maior precisão
- Algoritmo de lógica emocional:
  - Identifica microexpressões faciais
  - Garante persistência da emoção antes de registrar
  - Armazena duração e mudança de humor no banco

Emoções detectadas incluem:  
😄 Feliz | 😢 Triste | 😡 Raiva | 😮 Surpreso | 😐 Neutro 

### 🎥 Processamento de Vídeo
- Captura de câmera IP via **RTSP**
- Buffer otimizado para evitar latência
- Thread dedicada para detecção contínua
- Snapshot do vídeo disponível via API

---

## 🗄 Banco de Dados
Estruturas principais:

| Tabela | Função |
|--------|--------|
| `Usuario` | Autenticação e dados do usuário |
| `HumorEvent` | Histórico de emoções e duração |
| `Musica` | Biblioteca de músicas personalizadas |
| `SelecaoMusica` | Música selecionada conforme humor |
| `CodigoUrso` | Sistema de liberação com código exclusivo |

---

## 🔌 Principais Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/login` | Login seguro |
| POST | `/cadastro` | Cadastro com chave exclusiva |
| GET | `/ultima_emocao` | Último humor detectado + música |
| POST | `/select_music` | Selecionar música padrão ou customizada |
| GET | `/snapshot` | Snapshot da câmera em tempo real |
| POST | `/add_music` | Upload de músicas |
| GET | `/eventos` | Histórico de humor registrado |

> ✅ Toda API foi projetada para integração fluida com Flutter

---

## 🧩 Arquitetura Geral

Flutter (App) <--> Flask API <--> SQLite
↳ Câmera IP (RTSP)
↳ IA FER (Visão Computacional)

---

## 🚀 Futuras Melhorias
- Notificações inteligentes para responsáveis
- Geração de relatórios de comportamento
- Dashboard com gráficos de evolução emocional
- Suporte a múltiplas câmeras
- Personagens e animações mais lúdicas

---

## 👨‍💻 Autor
**Murilo Soares Guislande**  
Estudante de programação e sistemas embarcados — ETE FMC  
Apaixonado por tecnologia assistiva e IA aplicada ao bem-estar infantil 💙

---

## 📌 Observação
Projeto em desenvolvimento acadêmico. Não substitui acompanhamento profissional.

---
