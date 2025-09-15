import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import 'package:dorotea_app/models/humor_event.dart';
import 'package:dorotea_app/humor_data_generator.dart';

class ReportScreen extends StatefulWidget {
  const ReportScreen({Key? key}) : super(key: key);

  @override
  State<ReportScreen> createState() => _ReportScreenState();
}

class _ReportScreenState extends State<ReportScreen> {
  late List<HumorEvent> _humorData;
  late List<HumorEvent> _filteredData;
  String _selectedTimeframe = 'Semana';

  @override
  void initState() {
    super.initState();
    _humorData = generateSimulatedData();
    _filterData(_selectedTimeframe);
  }

  void _filterData(String timeframe) {
    setState(() {
      _selectedTimeframe = timeframe;
      final now = DateTime.now();
      _filteredData = _humorData.where((event) {
        if (timeframe == 'Dia') {
          return now.difference(event.dataHora).inHours <= 24;
        } else if (timeframe == 'Semana') {
          return now.difference(event.dataHora).inDays <= 7;
        } else { // Mês
          return now.difference(event.dataHora).inDays <= 30;
        }
      }).toList();
    });
  }

  // Mapeia o valor do humor para um ícone
  IconData _getHumorIcon(int humorValue) {
    switch (humorValue) {
      case 1:
        return Icons.sentiment_very_dissatisfied;
      case 2:
        return Icons.sentiment_dissatisfied;
      case 3:
        return Icons.sentiment_neutral;
      case 4:
        return Icons.sentiment_satisfied;
      case 5:
        return Icons.sentiment_very_satisfied;
      default:
        return Icons.sentiment_neutral;
    }
  }

  @override
  Widget build(BuildContext context) {
    final Color primaryPurple = Theme.of(context).primaryColor;

    return Scaffold(
      backgroundColor: primaryPurple,
      appBar: AppBar(
        title: const Text('Relatórios de Humor', style: TextStyle(color: Colors.white)),
        backgroundColor: primaryPurple,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Contêiner para o Gráfico e Botões de Filtro
            Card(
              elevation: 4,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20.0)),
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Gráfiiiiiico de Humor',
                      style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 10),

                    // Botões de Filtro de Período
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: ['Dia', 'Semana', 'Mês'].map((timeframe) {
                        return Expanded(
                          child: Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 4.0),
                            child: ElevatedButton(
                              onPressed: () => _filterData(timeframe),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: _selectedTimeframe == timeframe ? primaryPurple.withOpacity(0.8) : Colors.grey[200],
                                foregroundColor: _selectedTimeframe == timeframe ? Colors.white : Colors.black,
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                              ),
                              child: Text(timeframe),
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                    const SizedBox(height: 20),
                    
                    // Gráfico de Linha
                    SizedBox(
                      height: 200,
                      child: LineChart(
                        LineChartData(
                          minX: 0,
                          maxX: (_filteredData.length - 1).toDouble(),
                          minY: 1, // Minimo 1
                          maxY: 5, // Máximo 5
                          gridData: FlGridData(
                            show: true,
                            drawVerticalLine: true,
                            horizontalInterval: 1,
                            verticalInterval: 1,
                            getDrawingHorizontalLine: (value) {
                              return const FlLine(color: Color(0xffececec), strokeWidth: 1);
                            },
                            getDrawingVerticalLine: (value) {
                              return const FlLine(color: Color(0xffececec), strokeWidth: 1);
                            },
                          ),
                          titlesData: FlTitlesData(
                            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                            bottomTitles: AxisTitles(
                              sideTitles: SideTitles(
                                showTitles: true,
                                getTitlesWidget: (value, meta) {
                                  final index = value.toInt();
                                  if (index < 0 || index >= _filteredData.length) {
                                    return const SizedBox.shrink();
                                  }
                                  final event = _filteredData[index];
                                  String format;
                                  if (_selectedTimeframe == 'Dia') {
                                    format = 'HH:mm';
                                  } else {
                                    format = 'dd/MM';
                                  }
                                  return SideTitleWidget(
                                    axisSide: meta.axisSide,
                                    child: Text(
                                      DateFormat(format).format(event.dataHora),
                                      style: const TextStyle(fontSize: 10),
                                    ),
                                  );
                                },
                                interval: _filteredData.length > 10 ? (_filteredData.length / 5).floorToDouble() : 1, // Ajusta o intervalo dinamicamente
                              ),
                            ),
                            leftTitles: AxisTitles(
                              sideTitles: SideTitles(
                                showTitles: true,
                                interval: 1,
                                reservedSize: 40,
                                getTitlesWidget: (value, meta) {
                                  return Row(
                                    mainAxisAlignment: MainAxisAlignment.end,
                                    children: [
                                      Text(value.toInt().toString(), style: const TextStyle(fontSize: 12)),
                                      const SizedBox(width: 4),
                                      Icon(_getHumorIcon(value.toInt()), size: 16),
                                    ],
                                  );
                                },
                              ),
                            ),
                          ),
                          lineBarsData: [
                            LineChartBarData(
                              spots: _filteredData.asMap().entries.map((entry) {
                                return FlSpot(entry.key.toDouble(), entry.value.humor.toDouble());
                              }).toList(),
                              isCurved: true,
                              color: primaryPurple.withOpacity(0.8),
                              barWidth: 3,
                              isStrokeCapRound: true,
                              dotData: FlDotData(
                                getDotPainter: (spot, percent, barData, index) {
                                  return FlDotCirclePainter(
                                    radius: 4,
                                    color: primaryPurple,
                                    strokeColor: Colors.white,
                                    strokeWidth: 2,
                                  );
                                },
                              ),
                              belowBarData: BarAreaData(
                                show: true,
                                color: primaryPurple.withOpacity(0.3),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 40),
            
            // Lista de Eventos (Cards de Relatório)
            const Text(
              'Relatórios Detalhados',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white),
            ),
            const SizedBox(height: 20),
            
            // Lista de Eventos
            _filteredData.isEmpty
                ? const Center(child: Text('Nenhum dado encontrado para o período.', style: TextStyle(color: Colors.white)))
                : ListView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: _filteredData.length,
                    itemBuilder: (context, index) {
                      final event = _filteredData[index];
                      return Card(
                        margin: const EdgeInsets.symmetric(vertical: 8),
                        child: ListTile(
                          title: Text('Data: ${DateFormat('dd/MM/yyyy HH:mm').format(event.dataHora)}'),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Música: ${event.musica}'),
                              Text('Duração: ${event.duracao}'),
                              Text('Mudança de Humor: ${event.mudancaHumor}'),
                              Row(
                                children: [
                                  const Text('Humor: '),
                                  Icon(_getHumorIcon(event.humor), color: primaryPurple),
                                  Text(' (${event.humor})'),
                                ],
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
          ],
        ),
      ),
    );
  }
}