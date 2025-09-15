// lib/initial_screen.dart
import 'package:flutter/material.dart';
import 'package:dorotea_app/screens/login_screen.dart'; // Importe a tela de login

class InitialScreen extends StatelessWidget {
  const InitialScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Cores do tema, puxadas de main.dart
    final Color primaryPurple = Theme.of(context).primaryColor;
    final Color buttonPurple = Theme.of(context).elevatedButtonTheme.style?.backgroundColor?.resolve({}) ?? Colors.deepPurple;
    final Color textColorOnPrimary = Theme.of(context).elevatedButtonTheme.style?.foregroundColor?.resolve({}) ?? Colors.white;


    return Scaffold(
      backgroundColor: primaryPurple, // Fundo da tela roxo
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              // Imagem do urso
              Image.asset(
                'assets/bear_logo.png', // Verifique o caminho no pubspec.yaml
                height: MediaQuery.of(context).size.height * 0.3, // 30% da altura da tela
                fit: BoxFit.contain,
              ),
              const SizedBox(height: 20.0),
              // Texto "DOROTEA" (se for uma imagem, use Image.asset)
              Image.asset(
                'assets/dorotea_text.png', // Verifique o caminho no pubspec.yaml
                height: 80.0, // Ajuste o tamanho conforme necessário
                fit: BoxFit.contain,
              ),
              const SizedBox(height: 50.0), // Espaço antes do botão

              // Botão "VAMOS LÁ!"
              ElevatedButton(
                onPressed: () {
                  // Navegar para a tela de login
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const LoginScreen()),
                  );
                },
                child: const Text('VAMOS LÁ!'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}