import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:google_fonts/google_fonts.dart';
import 'dart:convert';

class RegistrationScreen extends StatefulWidget {
  final String token;

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
          'Authorization': 'Bearer ${widget.token}',
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
      'avail_slots': capacity,
      'total_slots': capacity,
      'owner_id': 1,
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
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('登録が成功しました', style: GoogleFonts.notoSansJp())),
        );
        _fetchOwnedParkings();
        Navigator.pop(context);
      } else {
        final errorData = json.decode(response.body);
        _showError("登録に失敗しました: ${errorData['detail']}");
      }
    } catch (e) {
      _showError("通信エラー: $e");
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message, style: GoogleFonts.notoSansJp())),
    );
  }

  void _showRegistrationForm() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) {
        final _formKey = GlobalKey<FormState>();
        final _nameController = TextEditingController();
        final _addressController = TextEditingController();
        final _latitudeController = TextEditingController();
        final _longitudeController = TextEditingController();
        final _capacityController = TextEditingController();

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
                _buildTextField('名前', _nameController),
                _buildTextField('住所', _addressController),
                _buildTextField('緯度', _latitudeController, isNumber: true),
                _buildTextField('経度', _longitudeController, isNumber: true),
                _buildTextField('駐輪可能台数', _capacityController, isNumber: true),
                SizedBox(height: 20),
                ElevatedButton(
                  onPressed: () {
                    if (_formKey.currentState!.validate()) {
                      _submitForm(
                        _nameController.text,
                        _addressController.text,
                        double.parse(_latitudeController.text),
                        double.parse(_longitudeController.text),
                        int.parse(_capacityController.text),
                      );
                    }
                  },
                  child: Text('登録', style: GoogleFonts.notoSansJp()),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildTextField(String label, TextEditingController controller, {bool isNumber = false}) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(labelText: label),
      keyboardType: isNumber ? TextInputType.number : TextInputType.text,
      style: GoogleFonts.notoSansJp(),
      validator: (value) {
        if (value == null || value.isEmpty) {
          return '$label を入力してください';
        }
        return null;
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('駐輪場リスト', style: GoogleFonts.notoSansJp()),
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator())
          : _parkingList.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text('まだ駐輪場が登録されていません。', style: GoogleFonts.notoSansJp(fontSize: 18)),
                      SizedBox(height: 20),
                      ElevatedButton(
                        onPressed: _showRegistrationForm,
                        child: Text('新規登録はこちら', style: GoogleFonts.notoSansJp()),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  itemCount: _parkingList.length,
                  itemBuilder: (context, index) {
                    final parking = _parkingList[index];
                    return ListTile(
                      title: Text(parking['name'], style: GoogleFonts.notoSansJp()),
                      subtitle: Text(parking['address'], style: GoogleFonts.notoSansJp()),
                    );
                  },
                ),
      floatingActionButton: _parkingList.isNotEmpty
          ? FloatingActionButton(
              onPressed: _showRegistrationForm,
              child: Icon(Icons.add),
            )
          : null,
    );
  }
}