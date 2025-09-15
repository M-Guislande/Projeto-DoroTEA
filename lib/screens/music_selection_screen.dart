// lib/screens/music_selection_screen.dart
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/material.dart';
import 'package:just_audio/just_audio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:dorotea_app/screens/add_music_screen.dart';
import 'package:dorotea_app/screens/home_screen.dart';
import 'package:dorotea_app/screens/about_screen.dart';
import 'package:dorotea_app/screens/profile_screen.dart';
import 'package:dorotea_app/screens/initial_screen.dart';

class MusicSelectionScreen extends StatefulWidget {
  const MusicSelectionScreen({super.key});

  @override
  State<MusicSelectionScreen> createState() => _MusicSelectionScreenState();
}

class _MusicSelectionScreenState extends State<MusicSelectionScreen> {
  final List<Map<String, dynamic>> _defaultMusicList = [
    {
      'id': 'bmp',
      'title': '60 BPM',
      'time': '2:40 (min)',
      'isSelected': false,
      'isDeletable': false,
      'audioUrl': 'assets/audios/bmp.mp3'
    },
    {
      'id': 'brilha_estrelinha',
      'title': 'Brilha Estrelinha',
      'time': '1:17 (min)',
      'isSelected': false,
      'isDeletable': false,
      'audioUrl': 'assets/audios/brilha_brilha_estrelinha.mp3'
    },
    {
      'id': 'clair_de_lune',
      'title': 'Clair de Lune',
      'time': '4:57 (min)',
      'isSelected': false,
      'isDeletable': false,
      'audioUrl': 'assets/audios/clair_de_lune.mp3'
    },
    {
      'id': 'lullaby',
      'title': 'Lullaby',
      'time': '3:10 (min)',
      'isSelected': false,
      'isDeletable': false,
      'audioUrl': 'assets/audios/lullaby.mp3'
    },
    {
      'id': 'primavera',
      'title': 'Primavera',
      'time': '3:11 (min)',
      'isSelected': false,
      'isDeletable': false,
      'audioUrl': 'assets/audios/primavera.mp3'
    },
  ];

  late List<Map<String, dynamic>> _musicList;
  final _player = AudioPlayer();
  int? _playingIndex;
  int _selectedIndex = 0;

  @override
  void initState() {
    super.initState();
    _musicList = List.from(_defaultMusicList);
  }

  @override
  void dispose() {
    _player.dispose();
    super.dispose();
  }

  void _loadAllMusic() async {
    // Primeiro, verifique se o usuário está logado e obtenha o email
    final prefs = await SharedPreferences.getInstance();
    final userEmail = prefs.getString('userEmail');

    if (userEmail == null) {
      debugPrint('Usuário não logado.');
      return;
    }

    // URL da sua API. Lembre-se de ajustá-la para a sua máquina.
    const String apiUrl = 'http://127.0.0.1:5000';
    final url = Uri.parse('$apiUrl/musics/$userEmail');

    try {
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        final List<dynamic> fetchedMusics = data['musics'];

        // Converta a lista dinâmica para a lista de mapas
        final List<Map<String, dynamic>> userMusics =
            List<Map<String, dynamic>>.from(fetchedMusics);
        
        // Junte a lista padrão de músicas com as músicas do usuário
        setState(() {
          _musicList = List.from(_defaultMusicList)..addAll(userMusics);
        });

        debugPrint('Músicas do usuário carregadas com sucesso.');
      } else {
        debugPrint('Erro ao carregar músicas: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Erro de conexão ao carregar músicas: $e');
    }
  }

  Future<void> _playMusic(String audioUrl, int index) async {
    try {
      await _player.setAsset(audioUrl);
      await _player.play();
      setState(() {
        _playingIndex = index;
      });
      _player.playerStateStream.listen((playerState) {
        if (playerState.processingState == ProcessingState.completed) {
          setState(() {
            _playingIndex = null;
          });
        }
      });
    } catch (e) {
      debugPrint('Erro ao tocar música: $e');
    }
  }

  void _pauseMusic() {
    _player.pause();
    setState(() {
      _playingIndex = null;
    });
  }

  Widget _buildMusicItem(
      BuildContext context, Map<String, dynamic> music, int index) {
    final Color primaryPurple = Theme.of(context).primaryColor;
    final bool isPlaying = _playingIndex == index;

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 16.0),
      color: music['isSelected'] ? primaryPurple : Colors.white,
      child: ListTile(
        leading: Icon(
          isPlaying ? Icons.pause_circle_filled : Icons.play_circle_fill,
          color: music['isSelected'] ? Colors.white : primaryPurple,
          size: 40,
        ),
        title: Text(
          music['title'],
          style: TextStyle(
            color: music['isSelected'] ? Colors.white : Colors.black,
            fontWeight: FontWeight.bold,
          ),
        ),
        subtitle: Text(
          music['time'],
          style: TextStyle(
            color: music['isSelected'] ? Colors.white70 : Colors.grey[600],
          ),
        ),
        trailing: music['isDeletable']
            ? IconButton(
                icon: Icon(Icons.delete,
                    color: music['isSelected'] ? Colors.white : Colors.red),
                onPressed: () {
                  setState(() {
                    _musicList.removeAt(index);
                  });
                },
              )
            : null,
        onTap: () async {
          setState(() {
            _musicList.forEach((m) => m['isSelected'] = false);
            music['isSelected'] = true;
          });
          if (isPlaying) {
            _pauseMusic();
          } else {
            _playMusic(music['audioUrl'], index);
          }
        },
      ),
    );
  }

  Widget _buildAddMusicCard() {
    final Color primaryPurple = Theme.of(context).primaryColor;
    final Color lightPurpleText = Theme.of(context).colorScheme.secondary;
    return Container(
      margin: const EdgeInsets.all(16.0),
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      color: Colors.white,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Adicione suas próprias músicas',
              style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: lightPurpleText),
            ),
            IconButton(
              icon: Icon(Icons.arrow_forward, color: lightPurpleText),
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const AddMusicScreen()),
                ).then((_) {
                  _loadAllMusic();
                });
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBottomNavigationBar(Color lightPurpleText) {
    return BottomNavigationBar(
      items: const <BottomNavigationBarItem>[
        BottomNavigationBarItem(
          icon: Icon(Icons.home),
          label: 'Home',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.pets),
          label: 'Ursinho',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.person),
          label: 'Perfil',
        ),
      ],
      currentIndex: _selectedIndex,
      selectedItemColor: lightPurpleText,
      unselectedItemColor: Colors.grey,
      onTap: (index) async {
        setState(() {
          _selectedIndex = index;
        });

        // Navega para as telas correspondentes
        if (index == 0) {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const HomeScreen()),
          );
        } else if (index == 2) {
          final prefs = await SharedPreferences.getInstance();
          final userEmail = prefs.getString('userEmail');
          
          if (userEmail != null) {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => ProfileScreen(userEmail: userEmail)),
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
        }
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    // ... (restante do código, sem mudanças)
    final Color primaryPurple = Theme.of(context).primaryColor;
    final Color lightPurpleText = Theme.of(context).colorScheme.secondary;

    return Scaffold(
      backgroundColor: primaryPurple,
      appBar: AppBar(
        title: const Text('Escolher Música'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            _buildAddMusicCard(),
            ..._musicList
                .asMap()
                .entries
                .map((entry) =>
                    _buildMusicItem(context, entry.value, entry.key))
                .toList(),
          ],
        ),
      ),
      bottomNavigationBar: _buildBottomNavigationBar(lightPurpleText),
    );
  }
}