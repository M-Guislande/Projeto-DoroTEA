import 'dart:math';
import '../models/humor_event.dart';

List<HumorEvent> generateSimulatedData() {
  final random = Random();
  final List<HumorEvent> data = [];
  final DateTime now = DateTime.now();

  final List<String> musicas = [
    'Música Relaxante',
    'Sons da Natureza',
    'Canção de Ninar',
    'Melodia Feliz'
  ];

  for (int i = 0; i < 20; i++) {
    final DateTime eventTime = now.subtract(Duration(days: i, hours: random.nextInt(24)));
    final int humorValue = random.nextInt(5) + 1; // De 1 a 5

    data.add(HumorEvent(
      dataHora: eventTime,
      humor: humorValue,
      musica: musicas[random.nextInt(musicas.length)],
      duracao: '${random.nextInt(5) + 1} min',
      mudancaHumor: _getHumorChange(humorValue),
    ));
  }

  // Ordenar por dataHora para que o gráfico seja linear
  data.sort((a, b) => a.dataHora.compareTo(b.dataHora));

  return data;
}

String _getHumorChange(int humor) {
  if (humor <= 2) return 'Pouco satisfeito para insatisfeito';
  if (humor <= 4) return 'Neutro para satisfeito';
  return 'Satisfeito para muito satisfeito';
}