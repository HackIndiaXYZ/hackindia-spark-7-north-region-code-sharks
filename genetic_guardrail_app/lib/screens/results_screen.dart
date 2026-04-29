import 'package:flutter/material.dart';
import 'package:syncfusion_flutter_gauges/gauges.dart';
import 'package:fl_chart/fl_chart.dart';

class ResultsScreen extends StatelessWidget {
  final Map<String, dynamic> results;

  const ResultsScreen({super.key, required this.results});

  @override
  Widget build(BuildContext context) {
    final List<dynamic> drugResults = results['results'] ?? [];

    return Scaffold(
      appBar: AppBar(
        title: const Text('Analysis Report'),
        backgroundColor: const Color(0xFF020617),
      ),
      body: drugResults.isEmpty
          ? const Center(child: Text('No results found.', style: TextStyle(color: Colors.white70)))
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: drugResults.length,
              itemBuilder: (context, index) {
                final result = drugResults[index];
                return DiagnosticCard(data: result);
              },
            ),
    );
  }
}

class DiagnosticCard extends StatelessWidget {
  final Map<String, dynamic> data;

  const DiagnosticCard({super.key, required this.data});

  Color _getRiskColor(String riskLevel) {
    switch (riskLevel.toUpperCase()) {
      case 'HIGH': return Colors.redAccent;
      case 'MODERATE': return Colors.orangeAccent;
      case 'LOW': return Colors.greenAccent;
      default: return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    final String drugName = data['drug'] ?? 'Unknown';
    final String riskLevel = data['risk_level'] ?? 'UNKNOWN';
    final double score = (data['toxicity_score'] ?? 0.0).toDouble();
    final String clinicalNote = data['clinical_note'] ?? 'No clinical note available.';
    final String alternative = data['alternative'] ?? 'None recommended.';
    
    final riskColor = _getRiskColor(riskLevel);

    return Container(
      margin: const EdgeInsets.only(bottom: 24),
      decoration: BoxDecoration(
        color: const Color(0xFF1e293b),
        border: Border.all(color: const Color(0xFF334155)),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: const BoxDecoration(
              border: Border(bottom: BorderSide(color: Color(0xFF334155))),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  drugName.toUpperCase(),
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1.5,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: riskColor.withOpacity(0.1),
                    border: Border.all(color: riskColor.withOpacity(0.5)),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    riskLevel,
                    style: TextStyle(
                      color: riskColor,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          // Visuals
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Gauge
                Expanded(
                  child: SizedBox(
                    height: 150,
                    child: SfRadialGauge(
                      axes: <RadialAxis>[
                        RadialAxis(
                          minimum: 0,
                          maximum: 100,
                          ranges: <GaugeRange>[
                            GaugeRange(startValue: 0, endValue: 33, color: Colors.greenAccent),
                            GaugeRange(startValue: 33, endValue: 66, color: Colors.orangeAccent),
                            GaugeRange(startValue: 66, endValue: 100, color: Colors.redAccent),
                          ],
                          pointers: <GaugePointer>[
                            NeedlePointer(value: score, needleColor: Colors.white, knobStyle: const KnobStyle(color: Colors.white)),
                          ],
                          annotations: <GaugeAnnotation>[
                            GaugeAnnotation(
                              widget: Text(
                                score.toStringAsFixed(1),
                                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                              ),
                              angle: 90,
                              positionFactor: 0.8,
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
                // Radar Chart
                Expanded(
                  child: SizedBox(
                    height: 150,
                    child: RadarChart(
                      RadarChartData(
                        radarBackgroundColor: Colors.transparent,
                        borderData: FlBorderData(show: false),
                        radarBorderData: const BorderSide(color: Color(0xFF334155)),
                        tickBorderData: const BorderSide(color: Color(0xFF334155), width: 0.5),
                        gridBorderData: const BorderSide(color: Color(0xFF334155), width: 0.5),
                        titlePositionPercentageOffset: 0.2,
                        titleTextStyle: const TextStyle(color: Colors.white54, fontSize: 8),
                        getTitle: (index, angle) {
                          switch (index) {
                            case 0: return const RadarChartTitle(text: 'Metabolism');
                            case 1: return const RadarChartTitle(text: 'Binding');
                            case 2: return const RadarChartTitle(text: 'Toxicity');
                            case 3: return const RadarChartTitle(text: 'Confidence');
                            default: return const RadarChartTitle(text: '');
                          }
                        },
                        dataSets: [
                          RadarDataSet(
                            fillColor: riskColor.withOpacity(0.2),
                            borderColor: riskColor,
                            entryRadius: 2,
                            dataEntries: [
                              RadarEntry(value: score * 0.8), // Mock values
                              RadarEntry(value: score * 0.9),
                              RadarEntry(value: score),
                              RadarEntry(value: 80),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          // Clinical Notes
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Container(
              padding: const EdgeInsets.all(12),
              width: double.infinity,
              decoration: BoxDecoration(
                color: const Color(0xFF0f172a),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('CLINICAL NOTE', style: TextStyle(color: Color(0xFF3b82f6), fontSize: 10, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  Text(clinicalNote, style: const TextStyle(height: 1.5, fontSize: 12)),
                  const SizedBox(height: 12),
                  const Text('ALTERNATIVE RECOMMENDATION', style: TextStyle(color: Colors.greenAccent, fontSize: 10, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  Text(alternative, style: const TextStyle(height: 1.5, fontSize: 12)),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }
}
