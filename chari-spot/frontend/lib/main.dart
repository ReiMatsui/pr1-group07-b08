import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  Future<String> fetchMessage() async {
    // ↓ 開発環境に応じて localhost を変更（注意）
    final url = Uri.parse('http://localhost:8000/api/hello');
    final response = await http.get(url);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['message'] ?? 'No message';
    } else {
      return 'Failed to load';
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter + FastAPI',
      home: Scaffold(
        appBar: AppBar(title: const Text('API Test')),
        body: Center(
          child: FutureBuilder<String>(
            future: fetchMessage(),
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const CircularProgressIndicator();
              } else if (snapshot.hasError) {
                return Text('Error: ${snapshot.error}');
              } else {
                return Text(snapshot.data ?? 'No data');
              }
            },
          ),
        ),
      ),
    );
  }
}
