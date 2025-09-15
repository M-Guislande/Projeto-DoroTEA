// lib/screens/profile_screen.dart
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:dorotea_app/screens/initial_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ProfileScreen extends StatefulWidget {
  final String userEmail;

  const ProfileScreen({super.key, required this.userEmail});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  String _fullName = 'Carregando...';
  String _email = 'Carregando...';
  String _bearCode = 'Carregando...';
  
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadUserProfile();
  }

  Future<void> _loadUserProfile() async {
    const String apiUrl = 'http://127.0.0.1:5000';
    final url = Uri.parse('$apiUrl/usuario/${widget.userEmail}');

    try {
      final response = await http.get(url);
      
      if (response.statusCode == 200) {
        final userData = jsonDecode(response.body);
        setState(() {
          _fullName = userData['nome_completo'] ?? 'Não informado';
          _email = userData['email'] ?? 'Não informado';
          _bearCode = userData['codigo_urso'] ?? 'Não informado';
          _isLoading = false;
        });
      } else {
        setState(() {
          _fullName = 'Erro ao carregar';
          _email = 'Erro ao carregar';
          _bearCode = 'Erro ao carregar';
          _isLoading = false;
        });
        debugPrint('Erro ao carregar perfil: ${response.body}');
      }
    } catch (e) {
      setState(() {
        _fullName = 'Erro de conexão';
        _email = 'Erro de conexão';
        _bearCode = 'Erro de conexão';
        _isLoading = false;
      });
      debugPrint('Erro de conexão ao carregar perfil: $e');
    }
  }

  void _handleLogout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('userEmail');
    
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (context) => const InitialScreen()),
      (Route<dynamic> route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    final Color primaryPurple = Theme.of(context).primaryColor;
    final Color lightPurpleText = Theme.of(context).colorScheme.secondary;
    
    return Scaffold(
      backgroundColor: primaryPurple,
      appBar: AppBar(
        title: const Text('Meu Perfil'),
        centerTitle: true,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Colors.white))
          : SingleChildScrollView(
              child: Column(
                children: [
                  const SizedBox(height: 20),
                  const CircleAvatar(
                    radius: 50,
                    backgroundColor: Colors.white,
                    child: Icon(Icons.person, size: 60, color: Colors.deepPurple),
                  ),
                  const SizedBox(height: 20),
                  Text(
                    _fullName,
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 30),
                  Container(
                    margin: const EdgeInsets.symmetric(horizontal: 24.0),
                    padding: const EdgeInsets.all(16.0),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20.0),
                    ),
                    child: Column(
                      children: [
                        _buildProfileInfoRow(
                          context,
                          icon: Icons.email,
                          label: 'Email',
                          value: _email,
                          labelColor: lightPurpleText,
                          valueColor: Colors.black54,
                        ),
                        _buildDivider(),
                        _buildProfileInfoRow(
                          context,
                          icon: Icons.pets,
                          label: 'Código do Urso',
                          value: _bearCode,
                          labelColor: lightPurpleText,
                          valueColor: Colors.black54,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 30),
                  ElevatedButton(
                    onPressed: _handleLogout,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: primaryPurple,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(30.0),
                      ),
                      padding: const EdgeInsets.symmetric(
                          horizontal: 40.0, vertical: 15.0),
                    ),
                    child: const Text('SAIR'),
                  ),
                ],
              ),
            ),
    );
  }
  
  Widget _buildProfileInfoRow(
      BuildContext context, {
        required IconData icon,
        required String label,
        required String value,
        required Color labelColor,
        required Color valueColor,
      }) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 15.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: labelColor),
          const SizedBox(width: 15.0),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: TextStyle(
                    color: labelColor,
                    fontSize: 14.0,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  value,
                  style: TextStyle(
                    color: valueColor,
                    fontSize: 16.0,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDivider() {
    return Container(
      height: 1.0,
      color: Colors.grey[200],
      margin: const EdgeInsets.symmetric(horizontal: 20.0),
    );
  }
}