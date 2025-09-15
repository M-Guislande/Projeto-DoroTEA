// lib/about_screen.dart
import 'package:flutter/material.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Cores do tema, puxadas de main.dart
    final Color primaryPurple = Theme.of(context).primaryColor;
    final Color lightPurpleText = Theme.of(context).colorScheme.secondary;
    final Color textColorOnPrimary = Theme.of(context).elevatedButtonTheme.style?.foregroundColor?.resolve({}) ?? Colors.white;

    return Scaffold(
      backgroundColor: primaryPurple, // Fundo roxo consistente
      appBar: AppBar(
        title: const Text('Sobre'), // Título da AppBar conforme a imagem
        centerTitle: true, // Centraliza o título
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 30.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: <Widget>[
              // Imagem do Urso
              Image.asset(
                'assets/bear_logo.png', // O mesmo ursinho usado nas telas de login
                height: 100.0, // Ajuste o tamanho conforme necessário
                fit: BoxFit.contain,
              ),
              const SizedBox(height: 30.0),

              // Container com o texto explicativo
              Container(
                padding: const EdgeInsets.all(24.0),
                decoration: BoxDecoration(
                  color: Colors.white, // Fundo branco
                  borderRadius: BorderRadius.circular(20.0), // Borda arredondada
                ),
                child: Column(
                  children: [
                    Text(
                      'O DoroTEA é uma babá eletrônica pensada para crianças com TEA. Com câmeras inteligentes, monitora o comportamento da criança e avisa os pais em caso de sinais de crise ou desconforto. Pelo app, dá pra acompanhar tudo em tempo real e escolher músicas terapêuticas que o ursinho toca, ajudando a acalmar e trazer bem-estar mesmo quando você não está por perto.',
                      textAlign: TextAlign.justify, // Justifica o texto
                      style: TextStyle(
                        color: Colors.grey[800], // Cor do texto
                        fontSize: 16.0,
                        height: 1.5, // Espaçamento entre linhas
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20.0),
            ],
          ),
        ),
      ),
    );
  }
}