// lib/screens/home_screen.dart
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:dorotea_app/screens/profile_screen.dart';
import 'package:dorotea_app/screens/about_screen.dart';
import 'package:dorotea_app/screens/music_selection_screen.dart';
import 'package:dorotea_app/screens/report_screen.dart';
import 'package:dorotea_app/screens/initial_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  late final List<Map<String, dynamic>> _featureCards;

  @override
  void initState() {
    super.initState();
    _featureCards = [
      {
        'icon': Icons.camera_alt,
        'title': 'Visualizar Agora',
        'description': 'Acompanhe em tempo real como está seu pequeno',
        'onTap': () {
          debugPrint('Visualizar Agora clicado!');
        },
      },
      {
        'icon': Icons.music_note,
        'title': 'Escolher Música',
        'description': 'Escolha a música que o ursinho Dorotea vai tocar',
        'onTap': () {
          Navigator.push(
            context,
            MaterialPageRoute(
                builder: (context) => const MusicSelectionScreen()),
          );
        },
      },
      {
        'icon': Icons.bar_chart,
        'title': 'Relatórios de Humor',
        'description': 'Veja gráficos do comportamento do seu pequeno',
        'onTap': () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const ReportScreen()),
          );
        },
      },
      {
        'icon': Icons.person,
        'title': 'Meu Perfil',
        'description': 'Gerencie as suas informações e do seu ursinho',
        'onTap': () async {
          final prefs = await SharedPreferences.getInstance();
          final userEmail = prefs.getString('userEmail');

          if (userEmail != null) {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => ProfileScreen(userEmail: userEmail),
              ),
            );
          } else {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Por favor, faça login novamente.')),
            );
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (context) => const InitialScreen()),
            );
          }
        },
      },
      {
        'icon': Icons.info,
        'title': 'Sobre',
        'description': 'Conheça mais sobre o projeto Dorotea',
        'onTap': () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const AboutScreen()),
          );
        },
      },
    ];
  }

  @override
  Widget build(BuildContext context) {
    // ... (restante do código, sem mudanças)
    final Color primaryPurple = Theme.of(context).primaryColor;
    return Scaffold(
      backgroundColor: primaryPurple,
      appBar: AppBar(
        title: const Text('Home'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 30.0),
        child: Column(
          children: _featureCards
              .map((card) => Padding(
                    padding: const EdgeInsets.only(bottom: 20.0),
                    child: _buildFeatureCard(
                      context,
                      icon: card['icon'],
                      title: card['title'],
                      description: card['description'],
                      onTap: card['onTap'],
                    ),
                  ))
              .toList(),
        ),
      ),
    );
  }

  Widget _buildFeatureCard(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String description,
    required VoidCallback onTap,
  }) {
    final Color primaryPurple = Theme.of(context).primaryColor;
    final Color lightPurpleText = Theme.of(context).colorScheme.secondary;
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(24.0),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20.0),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(12.0),
              decoration: BoxDecoration(
                color: primaryPurple.withOpacity(0.2),
                borderRadius: BorderRadius.circular(15.0),
              ),
              child: Icon(
                icon,
                size: 40.0,
                color: primaryPurple,
              ),
            ),
            const SizedBox(width: 20.0),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      color: lightPurpleText,
                      fontSize: 18.0,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4.0),
                  Text(
                    description,
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 14.0,
                    ),
                  ),
                ],
              ),
            ),
            IconButton(
              icon: Icon(Icons.arrow_forward, color: lightPurpleText),
              onPressed: onTap,
            ),
          ],
        ),
      ),
    );
  }
}