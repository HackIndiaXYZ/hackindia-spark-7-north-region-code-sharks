import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_typeahead/flutter_typeahead.dart';
import 'package:dio/dio.dart';
import '../main.dart';
import 'results_screen.dart';
import 'passport_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final List<String> _supportedDrugs = [
    "Codeine", "Warfarin", "Clopidogrel", "Simvastatin", "Atorvastatin", 
    "Ibuprofen", "Aspirin", "Metformin", "Tamoxifen", "Oxycodone"
  ];
  
  final TextEditingController _drugSearchController = TextEditingController();
  List<String> _selectedDrugs = [];
  bool _isLoading = false;

  void _runDiagnostic() async {
    if (_selectedDrugs.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select at least one drug')),
      );
      return;
    }

    setState(() => _isLoading = true);
    final state = Provider.of<AppState>(context, listen: false);

    try {
      final response = await state.dio.post('/check-prescription', data: {
        'drug_names': _selectedDrugs,
      });
      
      if (!mounted) return;
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => ResultsScreen(results: response.data),
        ),
      );
    } on DioException catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Diagnostic Failed: ${e.response?.data?['detail'] ?? e.message}')),
      );
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = Provider.of<AppState>(context);
    final user = state.user;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Command Center'),
        actions: [
          IconButton(
            icon: const Icon(Icons.qr_code_2),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const PassportScreen()),
              );
            },
          ),
        ],
      ),
      drawer: Drawer(
        backgroundColor: const Color(0xFF020617),
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            UserAccountsDrawerHeader(
              decoration: const BoxDecoration(color: Color(0xFF0f172a)),
              accountName: Text(user?.name ?? 'User', style: const TextStyle(fontFamily: 'monospace')),
              accountEmail: Text(user?.email ?? '', style: const TextStyle(fontFamily: 'monospace', color: Colors.white60)),
              currentAccountPicture: user?.profilePic != null
                  ? CircleAvatar(backgroundImage: NetworkImage(user!.profilePic!))
                  : const CircleAvatar(backgroundColor: Color(0xFF3b82f6), child: Icon(Icons.person, color: Colors.white)),
            ),
            const ListTile(
              title: Text('Patient Genome History', style: TextStyle(color: Colors.white54, fontSize: 12, letterSpacing: 1.5)),
            ),
            // Mock list of files
            ListTile(
              leading: const Icon(Icons.source, color: Color(0xFF3b82f6)),
              title: const Text('clinical_master.vcf'),
              subtitle: const Text('ACTIVE', style: TextStyle(color: Colors.green, fontSize: 10)),
              onTap: () {},
            ),
            const Divider(color: Color(0xFF1e293b)),
            ListTile(
              leading: const Icon(Icons.logout, color: Colors.redAccent),
              title: const Text('Terminate Session', style: TextStyle(color: Colors.redAccent)),
              onTap: () {
                state.logout();
              },
            ),
          ],
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Active Genome Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF1e293b),
                border: Border.all(color: const Color(0xFF334155)),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Row(
                children: [
                  const Icon(Icons.science, color: Color(0xFF3b82f6), size: 32),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: const [
                        Text('Active Genome File', style: TextStyle(fontSize: 12, color: Colors.white54)),
                        SizedBox(height: 4),
                        Text('clinical_master.vcf', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                      ],
                    ),
                  ),
                  const Icon(Icons.check_circle, color: Colors.green),
                ],
              ),
            ),
            
            const SizedBox(height: 32),
            const Text('Multi-Drug Search', style: TextStyle(fontSize: 14, color: Colors.white70)),
            const SizedBox(height: 8),
            
            // Search Input
            TypeAheadField<String>(
              controller: _drugSearchController,
              builder: (context, controller, focusNode) {
                return TextField(
                  controller: controller,
                  focusNode: focusNode,
                  decoration: InputDecoration(
                    hintText: 'Enter drug name (e.g. Codeine)',
                    hintStyle: const TextStyle(color: Colors.white30),
                    filled: true,
                    fillColor: const Color(0xFF0f172a),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(4),
                      borderSide: const BorderSide(color: Color(0xFF334155)),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(4),
                      borderSide: const BorderSide(color: Color(0xFF334155)),
                    ),
                    suffixIcon: IconButton(
                      icon: const Icon(Icons.add, color: Color(0xFF3b82f6)),
                      onPressed: () {
                        if (_drugSearchController.text.isNotEmpty) {
                          setState(() {
                            if (!_selectedDrugs.contains(_drugSearchController.text)) {
                              _selectedDrugs.add(_drugSearchController.text);
                            }
                            _drugSearchController.clear();
                          });
                        }
                      },
                    ),
                  ),
                );
              },
              itemBuilder: (context, suggestion) {
                return ListTile(
                  tileColor: const Color(0xFF1e293b),
                  title: Text(suggestion, style: const TextStyle(color: Colors.white)),
                );
              },
              onSelected: (suggestion) {
                setState(() {
                  if (!_selectedDrugs.contains(suggestion)) {
                    _selectedDrugs.add(suggestion);
                  }
                  _drugSearchController.clear();
                });
              },
              suggestionsCallback: (pattern) {
                return _supportedDrugs.where((drug) => drug.toLowerCase().contains(pattern.toLowerCase())).toList();
              },
            ),
            
            const SizedBox(height: 16),
            // Selected Drugs Chips
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _selectedDrugs.map((drug) {
                return Chip(
                  label: Text(drug),
                  backgroundColor: const Color(0xFF334155),
                  labelStyle: const TextStyle(color: Colors.white),
                  deleteIconColor: Colors.redAccent,
                  onDeleted: () {
                    setState(() {
                      _selectedDrugs.remove(drug);
                    });
                  },
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                  side: BorderSide.none,
                );
              }).toList(),
            ),
            
            const Spacer(),
            
            // Run Button
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _runDiagnostic,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF3b82f6),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                ),
                child: _isLoading 
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text(
                        'RUN MULTI-DRUG DIAGNOSTIC',
                        style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: 1),
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
