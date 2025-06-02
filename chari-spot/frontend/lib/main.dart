import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'registration.dart';
import 'profile_screen.dart';
import 'login_screen.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '駐車場マップUI',
      theme: ThemeData(
        brightness: Brightness.dark,
        fontFamily: 'NotoSansJP', // ✅ カスタムフォントを明示指定
      ),
      home: LoginScreen(), // 初期画面をログインページに設定
      debugShowCheckedModeBanner: false,
    );
  }
}