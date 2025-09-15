import 'package:cloud_firestore/cloud_firestore.dart';

class HumorEvent {
  final DateTime dataHora;
  final int humor; // Por exemplo, 1-5
  final String musica;
  final String duracao;
  final String mudancaHumor;

  HumorEvent({
    required this.dataHora,
    required this.humor,
    required this.musica,
    required this.duracao,
    required this.mudancaHumor,
  });

  // Construtor que cria um objeto a partir de um mapa de dados (vindo do Firestore)
  factory HumorEvent.fromMap(Map<String, dynamic> data) {
    return HumorEvent(
      dataHora: (data['dataHora'] as Timestamp).toDate(),
      humor: data['humor'] as int,
      musica: data['musica'] as String,
      duracao: data['duracao'] as String,
      mudancaHumor: data['mudancaHumor'] as String,
    );
  }
}