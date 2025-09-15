// lib/main.dart
import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart'; // Importe para inicializar o Firebase
import 'firebase_options.dart'; // Importe as opções geradas pelo FlutterFire CLI
import 'screens/initial_screen.dart'; // Importe a tela inicial
import 'screens/music_selection_screen.dart'; // Importe a tela de seleção de música

void main() async {
  WidgetsFlutterBinding.ensureInitialized(); // Garante que os bindings do Flutter estejam inicializados


 
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    // Cores definidas para o tema
    // Cor 1: Fundo da tela (um roxo mais claro)
    const Color primaryPurple = Color.fromARGB(255, 181, 154, 230);

    // Cor 2: Cor dos botões Elevated (um roxo mais escuro para contraste)
    const Color buttonPurple = Color(0xFF673AB7); // O roxo principal que usávamos antes

    // Cor 3: Cor dos textos/botões TextButton (um roxo mais claro para textos de link)
    const Color lightPurpleText = Color(0xFF7E57C2);

    // Cor para o fundo dos campos de entrada
    const Color whiteBackgroundFields = Colors.white;

    return MaterialApp(
      title: 'Doroteia Login App',
      debugShowCheckedModeBanner: false, // Remove a faixa "DEBUG" no canto superior direito
      theme: ThemeData(
        // Define a cor primária para ser usada em todo o aplicativo (fundo da tela, AppBar)
        primaryColor: primaryPurple,

        colorScheme: ColorScheme.fromSwatch(
          primarySwatch: Colors.deepPurple, // Começamos com um swatch similar para gerar tons
        ).copyWith(
          primary: primaryPurple,       // A cor primária do tema será o roxo de fundo
          secondary: lightPurpleText,   // A cor secundária será o roxo para textos de destaque
          background: primaryPurple,    // Usado como cor de fundo padrão para Scaffolds se não for especificado
        ),

        // Define a cor de fundo padrão para todos os Scaffolds (o fundo da tela)
        scaffoldBackgroundColor: primaryPurple,

        // Estilo global para todos os campos de entrada de texto (TextFormField)
        inputDecorationTheme: InputDecorationTheme(
          filled: true, // Indica que o campo terá uma cor de preenchimento
          fillColor: whiteBackgroundFields, // A cor de fundo branco para os campos
          labelStyle: TextStyle(color: Colors.grey[700]), // Cor do label do campo
          hintStyle: TextStyle(color: Colors.grey[500]),   // Cor do texto de dica
          contentPadding: const EdgeInsets.symmetric(vertical: 16.0, horizontal: 16.0), // Padding interno do campo
          border: OutlineInputBorder( // Define o estilo da borda padrão
            borderRadius: BorderRadius.circular(10.0), // Borda arredondada
            borderSide: BorderSide.none, // Sem borda visível por padrão (pois tem fill)
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10.0),
            borderSide: BorderSide(color: Colors.grey[300]!, width: 1.0), // Borda cinza suave
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10.0),
            borderSide: BorderSide(color: primaryPurple, width: 2.0), // Borda com a cor de fundo focada
          ),
          errorBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10.0),
            borderSide: const BorderSide(color: Colors.red, width: 2.0),
          ),
          focusedErrorBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10.0),
            borderSide: const BorderSide(color: Colors.red, width: 2.0),
          ),
          errorStyle: const TextStyle(color: Colors.red, fontSize: 14.0),
        ),

        // Estilo global para todos os botões ElevatedButton (VAMOS LÁ!, ENTRAR, CADASTRAR)
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: buttonPurple, // NOVA COR PARA O FUNDO DO BOTÃO!
            foregroundColor: Colors.white, // Cor do texto do botão (branco)
            padding: const EdgeInsets.symmetric(vertical: 16.0),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10.0), // Borda arredondada do botão
            ),
            textStyle: const TextStyle(
              fontSize: 18.0,
              fontWeight: FontWeight.bold, // Texto em negrito
            ),
          ),
        ),

        // Estilo global para todos os botões TextButton (CADASTRAR na tela de login, Já tem uma conta?)
        textButtonTheme: TextButtonThemeData(
          style: TextButton.styleFrom(
            foregroundColor: lightPurpleText, // Cor do texto do botão (o roxo mais claro)
            textStyle: const TextStyle(
              fontSize: 16.0,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),

        // Estilo da barra de aplicativos (AppBar)
        appBarTheme: const AppBarTheme(
          backgroundColor: primaryPurple, // Cor do fundo da AppBar será a cor da tela
          foregroundColor: Colors.white,   // Cor do texto e ícones da AppBar
          centerTitle: true,
          elevation: 0,
        ),
      ),
      home: const InitialScreen(),
    );
  }
}