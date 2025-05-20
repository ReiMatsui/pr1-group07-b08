import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:latlong2/latlong.dart';
import 'map_screen.dart';

class RegistrationScreen extends StatefulWidget {
  final String token; // トークンを受け取る

  RegistrationScreen({required this.token});

  @override
  _RegistrationScreenState createState() => _RegistrationScreenState();
}

class _RegistrationScreenState extends State<RegistrationScreen> {
  List<dynamic> _parkingList = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _fetchOwnedParkings();
  }

  Future<void> _fetchOwnedParkings() async {
    setState(() {
      _isLoading = true;
    });

    final url = Uri.parse('http://localhost:8000/parking/owned');

    try {
      final response = await http.get(
        url,
        headers: {
          'Authorization': 'Bearer ${widget.token}', // トークンをヘッダーに追加
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _parkingList = data;
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

  Future<void> _submitForm(String name, String address, double latitude, double longitude, int capacity) async {
    final url = Uri.parse('http://localhost:8000/parking/register');
    final requestBody = {
      'name': name,
      'address': address,
      'latitude': latitude,
      'longitude': longitude,
      'avail_slots': capacity, // 初期値として全て空き
      'total_slots': capacity,
      'owner_id': 1, // ユーザーIDは固定
    };

    try {
      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${widget.token}', // トークンをヘッダーに追加
        },
        body: json.encode(requestBody),
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('登録が成功しました')),
        );
        _fetchOwnedParkings(); // リストを更新
        Navigator.pop(context); // モーダルを閉じる
      } else {
        final errorData = json.decode(response.body);
        _showError("登録に失敗しました: ${errorData['detail']}");
      }
    } catch (e) {
      _showError("通信エラー: $e");
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }

  void _showRegistrationForm() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) {
        final _formKey = GlobalKey<FormState>();
        final TextEditingController _nameController = TextEditingController();
        final TextEditingController _addressController = TextEditingController();
        final TextEditingController _capacityController = TextEditingController();
        LatLng? _selectedLocation;

        return Padding(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(context).viewInsets.bottom,
            left: 16.0,
            right: 16.0,
            top: 16.0,
          ),
          child: Form(
            key: _formKey,
            child: ListView(
              shrinkWrap: true,
              children: [
                TextFormField(
                  controller: _nameController,
                  decoration: InputDecoration(labelText: '名前'),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return '駐輪場の名前を入力してください';
                    }
                    return null;
                  },
                ),
                TextFormField(
                  controller: _addressController,
                  decoration: InputDecoration(labelText: '住所'),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return '住所を入力してください';
                    }
                    return null;
                  },
                ),
                SizedBox(height: 20),
                ElevatedButton(
                  onPressed: () async {
                    final result = await Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => MapScreen(
                          initialLocation: LatLng(35.6895, 139.6917), // 初期位置（例: 東京）
                        ),
                      ),
                    );
                    if (result != null) {
                      setState(() {
                        _selectedLocation = result;
                      });
                    }
                  },
                  child: Text(_selectedLocation == null
                      ? '地図で位置を選択'
                      : '選択済み: ${_selectedLocation!.latitude}, ${_selectedLocation!.longitude}'),
                ),
                TextFormField(
                  controller: _capacityController,
                  decoration: InputDecoration(labelText: '駐輪可能台数'),
                  keyboardType: TextInputType.number,
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return '駐輪可能台数を入力してください';
                    }
                    return null;
                  },
                ),
                SizedBox(height: 20),
                ElevatedButton(
                  onPressed: () {
                    if (_formKey.currentState!.validate() && _selectedLocation != null) {
                      _submitForm(
                        _nameController.text,
                        _addressController.text,
                        _selectedLocation!.latitude,
                        _selectedLocation!.longitude,
                        int.parse(_capacityController.text),
                      );
                    } else if (_selectedLocation == null) {
                      _showError('地図で位置を選択してください');
                    }
                  },
                  child: Text('登録'),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('駐輪場リスト'),
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator())
          : _parkingList.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        'まだ駐輪場が登録されていません。',
                        style: TextStyle(fontSize: 18),
                      ),
                      SizedBox(height: 20),
                      ElevatedButton(
                        onPressed: _showRegistrationForm,
                        child: Text('新規登録はこちら'),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  itemCount: _parkingList.length,
                  itemBuilder: (context, index) {
                    final parking = _parkingList[index];
                    return ListTile(
                      title: Text(parking['name']),
                      subtitle: Text(parking['address']),
                    );
                  },
                ),
      floatingActionButton: _parkingList.isNotEmpty
          ? FloatingActionButton(
              onPressed: _showRegistrationForm,
              child: Icon(Icons.add),
            )
          : null, // 駐輪場がない場合はFABを非表示
    );
  }
}