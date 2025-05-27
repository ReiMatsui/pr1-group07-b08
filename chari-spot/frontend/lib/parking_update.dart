import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ParkingUpdateScreen extends StatefulWidget {
  final int parkingId;
  final String token;

  ParkingUpdateScreen({required this.parkingId, required this.token});

  @override
  _ParkingUpdateScreenState createState() => _ParkingUpdateScreenState();
}

class _ParkingUpdateScreenState extends State<ParkingUpdateScreen> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _addressController = TextEditingController();
  final TextEditingController _capacityController = TextEditingController();
  LatLng? _location;
  int _availSlots = 0;

  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchParkingDetails();
  }

  Future<void> _fetchParkingDetails() async {
    final url = Uri.parse('http://localhost:8000/parking/${widget.parkingId}');
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
          _nameController.text = data['name'];
          _addressController.text = data['address'];
          _capacityController.text = data['total_slots'].toString();
          _availSlots = data['avail_slots'];
          _location = LatLng(data['latitude'], data['longitude']);
          _isLoading = false;
        });
      } else {
        _showError("詳細情報の取得に失敗しました");
      }
    } catch (e) {
      _showError("通信エラー: $e");
    }
  }

  Future<void> _updateParking() async {
    final url = Uri.parse('http://localhost:8000/parking/update');
    final requestBody = {
      'id': widget.parkingId,
      'name': _nameController.text,
      'address': _addressController.text,
      'latitude': _location!.latitude,
      'longitude': _location!.longitude,
      'avail_slots': _availSlots,
      'total_slots': int.parse(_capacityController.text),
    };

    try {
      final response = await http.put(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${widget.token}',
        },
        body: json.encode(requestBody),
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('更新が成功しました')),
        );
        Navigator.pop(context, true); // 更新後に戻る
      } else {
        _showError("更新に失敗しました");
      }
    } catch (e) {
      _showError("通信エラー: $e");
    }
  }

  Future<void> _deleteParking() async {
    final url = Uri.parse('http://localhost:8000/parking/delete/${widget.parkingId}');
    try {
      final response = await http.delete(
        url,
        headers: {
          'Authorization': 'Bearer ${widget.token}',
        },
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('削除が成功しました')),
        );
        Navigator.pop(context, true); // 削除後に戻る
      } else {
        _showError("削除に失敗しました");
      }
    } catch (e) {
      _showError("通信エラー: $e");
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('駐輪場詳細'),
        actions: [
          IconButton(
            icon: Icon(Icons.delete),
            onPressed: _deleteParking,
          ),
        ],
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(16.0),
              child: Form(
                key: _formKey,
                child: ListView(
                  children: [
                    TextFormField(
                      controller: _nameController,
                      decoration: InputDecoration(labelText: '名前'),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return '名前を入力してください';
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
                    _location != null
                        ? Container(
                            height: 200,
                            child: FlutterMap(
                              options: MapOptions(
                                initialCenter: _location!,
                                initialZoom: 15.0,
                              ),
                              children: [
                                TileLayer(
                                  urlTemplate: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                                  subdomains: ['a', 'b', 'c'],
                                ),
                                MarkerLayer(
                                  markers: [
                                    Marker(
                                      point: _location!,
                                      width: 40,
                                      height: 40,
                                      child: Icon(
                                        Icons.location_pin,
                                        color: Colors.red,
                                        size: 40,
                                      ),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          )
                        : SizedBox.shrink(),
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
                        if (_formKey.currentState!.validate()) {
                          _updateParking();
                        }
                      },
                      child: Text('更新'),
                    ),
                  ],
                ),
              ),
            ),
    );
  }
}