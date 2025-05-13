import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ProfileScreen extends StatefulWidget {
  @override
  _ProfileScreenState createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final int userId = 1; // 仮のユーザーID
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final TextEditingController _currentPasswordController = TextEditingController();

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

    final url = Uri.parse('http://localhost:8000/user/get/$userId');

    try {
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _usernameController.text = data['username'];
          _emailController.text = data['email'];
        });
      } else {
        final errorData = json.decode(response.body);
        _showError("取得に失敗しました: ${errorData['detail'][0]['msg']}");
      }
    } catch (e) {
      _showError("通信エラー: $e");
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _verifyPasswordAndEnableEditing() async {
    final currentPassword = _currentPasswordController.text;

    // 仮のパスワード検証（APIがある場合はここでリクエストを送信）
    if (currentPassword == "correct_password") { // 仮の正しいパスワード
      setState(() {
        _isEditing = true;
      });
      Navigator.pop(context); // ダイアログを閉じる
    } else {
      _showError("パスワードが正しくありません");
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
        final response = await http.put(
          url,
          headers: {'Content-Type': 'application/json'},
          body: json.encode(requestBody),
        );

        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('更新が成功しました: ${data['username']}')),
          );
          setState(() {
            _isEditing = false;
          });
        } else {
          final errorData = json.decode(response.body);
          _showError("更新に失敗しました: ${errorData['detail'][0]['msg']}");
        }
      } catch (e) {
        _showError("通信エラー: $e");
      }
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }

  void _showPasswordDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text("現在のパスワードを入力"),
          content: TextField(
            controller: _currentPasswordController,
            obscureText: true,
            decoration: InputDecoration(labelText: "パスワード"),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text("キャンセル"),
            ),
            TextButton(
              onPressed: _verifyPasswordAndEnableEditing,
              child: Text("確認"),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('プロフィール'),
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
                            decoration: InputDecoration(labelText: 'ユーザー名'),
                            validator: (value) {
                              if (value == null || value.isEmpty) {
                                return 'ユーザー名を入力してください';
                              }
                              return null;
                            },
                          ),
                          TextFormField(
                            controller: _emailController,
                            decoration: InputDecoration(labelText: 'メールアドレス'),
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
                            decoration: InputDecoration(labelText: '新しいパスワード'),
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
                            child: Text('更新'),
                          ),
                        ],
                      ),
                    )
                  : Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text("ユーザー名: ${_usernameController.text}", style: TextStyle(fontSize: 18)),
                        SizedBox(height: 10),
                        Text("メールアドレス: ${_emailController.text}", style: TextStyle(fontSize: 18)),
                        SizedBox(height: 20),
                        ElevatedButton(
                          onPressed: _showPasswordDialog,
                          child: Text('修正'),
                        ),
                      ],
                    ),
            ),
    );
  }
}