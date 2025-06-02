import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:google_fonts/google_fonts.dart';
import 'dart:convert';

class ProfileScreen extends StatefulWidget {
  final String token;

  ProfileScreen({required this.token});

  @override
  _ProfileScreenState createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final int userId = 1;
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  bool _isLoading = false;
  bool _isEditing = false;

  @override
  void initState() {
    super.initState();
    _fetchUserProfile();
  }

  Future<void> _fetchUserProfile() async {
    setState(() {
      _isLoading = true;
    });

    final url = Uri.parse('http://localhost:8000/user/get');

    try {
      final response = await http.get(
        url,
        headers: {
          'Authorization': 'Bearer ${widget.token}',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _usernameController.text = data['username'];
          _emailController.text = data['email'];
        });
      } else {
        final errorData = json.decode(response.body);
        _showError("取得に失敗しました: ${errorData['detail']}");
      }
    } catch (e) {
      _showError("通信エラー: $e");
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _updateUserProfile() async {
    if (_formKey.currentState!.validate()) {
      final url = Uri.parse('http://localhost:8000/user/update');
      final requestBody = {
        'id': userId,
        'username': _usernameController.text,
        'email': _emailController.text,
        'password': _passwordController.text,
      };

      try {
        final response = await http.post(
          url,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ${widget.token}',
          },
          body: json.encode(requestBody),
        );

        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('更新が成功しました: ${data['username']}', style: GoogleFonts.notoSansJp())),
          );
          setState(() {
            _isEditing = false;
          });
        } else {
          final errorData = json.decode(response.body);
          _showError("更新に失敗しました: ${errorData['detail']}");
        }
      } catch (e) {
        _showError("通信エラー: $e");
      }
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message, style: GoogleFonts.notoSansJp())),
    );
  }

  Future<bool> _verifyPassword(String password) async {
    final url = Uri.parse('http://localhost:8000/user/verify?pwd=$password');

    try {
      final response = await http.get(
        url,
        headers: {
          'Authorization': 'Bearer ${widget.token}',
        },
      );

      if (response.statusCode == 200) {
        return true; // パスワードが正しい
      } else {
        final errorData = json.decode(response.body);
        _showError("パスワードの確認に失敗しました: ${errorData['detail']}");
        return false;
      }
    } catch (e) {
      _showError("通信エラー: $e");
      return false;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.orange,
        title: Text(
          'プロフィール',
          style: GoogleFonts.notoSansJp(
            color: Colors.white,          // 真っ白に
            fontWeight: FontWeight.bold, // 太字に
            fontSize: 20,                // 読みやすく少し大きめに（任意）
          ),
        ),
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(16.0),
              child: _isEditing
                  ? Form(
                      key: _formKey,
                      child: ListView(
                        children: [
                          TextFormField(
                            controller: _usernameController,
                            decoration: InputDecoration(
                              labelText: 'ユーザー名',
                              labelStyle: GoogleFonts.notoSansJp(),
                            ),
                            style: GoogleFonts.notoSansJp(),
                            validator: (value) {
                              if (value == null || value.isEmpty) {
                                return 'ユーザー名を入力してください';
                              }
                              return null;
                            },
                          ),
                          TextFormField(
                            controller: _emailController,
                            decoration: InputDecoration(
                              labelText: 'メールアドレス',
                              labelStyle: GoogleFonts.notoSansJp(),
                            ),
                            style: GoogleFonts.notoSansJp(),
                            validator: (value) {
                              if (value == null || value.isEmpty) {
                                return 'メールアドレスを入力してください';
                              }
                              if (!RegExp(r'^[^@]+@[^@]+\.[^@]+').hasMatch(value)) {
                                return '有効なメールアドレスを入力してください';
                              }
                              return null;
                            },
                          ),
                          TextFormField(
                            controller: _passwordController,
                            decoration: InputDecoration(
                              labelText: '新しいパスワード',
                              labelStyle: GoogleFonts.notoSansJp(),
                            ),
                            style: GoogleFonts.notoSansJp(),
                            obscureText: true,
                            validator: (value) {
                              if (value == null || value.isEmpty) {
                                return 'パスワードを入力してください';
                              }
                              return null;
                            },
                          ),
                          SizedBox(height: 20),
                          ElevatedButton(
                            onPressed: _updateUserProfile,
                            child: Text('更新', style: GoogleFonts.notoSansJp()),
                          ),
                        ],
                      ),
                    )
                  : Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text("ユーザー名: ${_usernameController.text}",
                            style: GoogleFonts.notoSansJp(fontSize: 18)),
                        SizedBox(height: 10),
                        Text("メールアドレス: ${_emailController.text}",
                            style: GoogleFonts.notoSansJp(fontSize: 18)),
                        SizedBox(height: 20),
                        ElevatedButton(
                          onPressed: () async {
                            final passwordController = TextEditingController();

                            // パスワード入力ダイアログを表示
                            final result = await showDialog<bool>(
                              context: context,
                              builder: (context) {
                                return AlertDialog(
                                  title: Text('パスワード確認', style: GoogleFonts.notoSansJp()),
                                  content: Column(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Text('現在のパスワードを入力してください', style: GoogleFonts.notoSansJp()),
                                      SizedBox(height: 10),
                                      TextField(
                                        controller: passwordController,
                                        obscureText: true,
                                        decoration: InputDecoration(
                                          labelText: 'パスワード',
                                          labelStyle: GoogleFonts.notoSansJp(),
                                        ),
                                      ),
                                    ],
                                  ),
                                  actions: [
                                    TextButton(
                                      onPressed: () => Navigator.pop(context, false), // キャンセル
                                      child: Text('キャンセル', style: GoogleFonts.notoSansJp()),
                                    ),
                                    TextButton(
                                      onPressed: () async {
                                        final isValid = await _verifyPassword(passwordController.text);
                                        Navigator.pop(context, isValid); // 検証結果を返す
                                      },
                                      child: Text('確認', style: GoogleFonts.notoSansJp()),
                                    ),
                                  ],
                                );
                              },
                            );

                            // パスワードが正しい場合のみ修正画面に遷移
                            if (result == true) {
                              setState(() {
                                _isEditing = true;
                              });
                            }
                          },
                          child: Text('修正', style: GoogleFonts.notoSansJp()),
                        ),
                      ],
                    ),
            ),
    );
  }
}