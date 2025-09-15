import 'package:flutter/material.dart';
import 'package:dorotea_app/screens/music_selection_screen.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class AddMusicScreen extends StatefulWidget {
  const AddMusicScreen({super.key});

  @override
  State<AddMusicScreen> createState() => _AddMusicScreenState();
}

class _AddMusicScreenState extends State<AddMusicScreen> {
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _artistController = TextEditingController();
  final _audioUrlController = TextEditingController();

  Future<void> _addMusic() async {
    if (_formKey.currentState!.validate()) {
      final String title = _titleController.text.trim();
      final String artist = _artistController.text.trim();
      final String audioUrl = _audioUrlController.text.trim();

      // A URL da sua API.
      const String apiUrl = 'http://127.0.0.1:5000';
      final url = Uri.parse('$apiUrl/add-music');

      try {
        final response = await http.post(
          url,
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({
            'title': title,
            'artist': artist,
            'audioUrl': audioUrl,
          }),
        );

        if (response.statusCode == 201) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Música adicionada com sucesso!')),
          );
          // Redireciona de volta para a tela de seleção de música
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => const MusicSelectionScreen()),
          );
        } else {
          final erro = jsonDecode(response.body)['erro'];
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Erro ao adicionar música: $erro')),
          );
        }
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Erro de conexão. Verifique o servidor.')),
        );
      }
    }
  }

  @override
  void dispose() {
    _titleController.dispose();
    _artistController.dispose();
    _audioUrlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final Color primaryPurple = Theme.of(context).primaryColor;
    final Color lightPurpleText = Theme.of(context).colorScheme.secondary;

    return Scaffold(
      backgroundColor: primaryPurple,
      appBar: AppBar(
        title: const Text('Adicionar Música'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: <Widget>[
              // Imagem ou ícone
              Icon(
                Icons.music_note,
                size: 80.0,
                color: Colors.white,
              ),
              const SizedBox(height: 30.0),

              // Formulário
              Container(
                padding: const EdgeInsets.all(24.0),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20.0),
                ),
                child: Column(
                  children: [
                    TextFormField(
                      controller: _titleController,
                      decoration: const InputDecoration(labelText: 'Título da Música'),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Por favor, insira o título.';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _artistController,
                      decoration: const InputDecoration(labelText: 'Artista'),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Por favor, insira o artista.';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _audioUrlController,
                      decoration: const InputDecoration(labelText: 'URL do Arquivo de Áudio'),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Por favor, insira um URL de áudio válido.';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 32),
                    ElevatedButton(
                      onPressed: _addMusic,
                      child: const Text('Adicionar Música'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.white,
                        foregroundColor: primaryPurple,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}