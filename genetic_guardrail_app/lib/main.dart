import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'screens/login_screen.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AppState()),
      ],
      child: const GeneticGuardrailApp(),
    ),
  );
}

class AppState extends ChangeNotifier {
  User? user;
  final Dio dio = Dio(BaseOptions(
    baseUrl: 'http://10.113.23.97:8000',
  ));

  AppState() {
    // Add interceptor to handle cookies if needed, though dio can use dio_cookie_manager
    // For simplicity, we just assume token is saved in shared prefs
    _loadUser();
  }

  Future<void> _loadUser() async {
    final prefs = await SharedPreferences.getInstance();
    final name = prefs.getString('name');
    final email = prefs.getString('email');
    final pic = prefs.getString('pic');
    
    if (name != null && email != null) {
      user = User(name: name, email: email, profilePic: pic);
      notifyListeners();
    }
  }

  void setUser(User newUser) async {
    user = newUser;
    notifyListeners();
    final prefs = await SharedPreferences.getInstance();
    prefs.setString('name', newUser.name);
    prefs.setString('email', newUser.email);
    if (newUser.profilePic != null) {
      prefs.setString('pic', newUser.profilePic!);
    }
  }

  void logout() async {
    user = null;
    notifyListeners();
    final prefs = await SharedPreferences.getInstance();
    prefs.clear();
  }
}

class User {
  final String name;
  final String email;
  final String? profilePic;

  User({required this.name, required this.email, this.profilePic});
}

class GeneticGuardrailApp extends StatelessWidget {
  const GeneticGuardrailApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Genetic Guardrail',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF020617), // slate-950
        cardColor: const Color(0xFF1e293b), // slate-800
        primaryColor: const Color(0xFF3b82f6), // medical-blue
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF3b82f6),
          surface: Color(0xFF1e293b),
          background: Color(0xFF020617),
        ),
        fontFamily: 'monospace', // Use monospaced font for clinical look
        textTheme: const TextTheme(
          bodyLarge: TextStyle(color: Colors.white70),
          bodyMedium: TextStyle(color: Colors.white60),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF020617),
          elevation: 0,
          centerTitle: false,
          iconTheme: IconThemeData(color: Colors.white),
          titleTextStyle: TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.bold,
            fontFamily: 'monospace',
          ),
        ),
      ),
      home: Consumer<AppState>(
        builder: (context, state, _) {
          if (state.user == null) {
            return const LoginScreen();
          }
          return const HomeScreen();
        },
      ),
    );
  }
}
