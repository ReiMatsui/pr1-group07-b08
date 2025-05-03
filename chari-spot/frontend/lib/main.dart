import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '駐車場マップUI',
      theme: ThemeData.dark(),
      home: ParkingMapScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class ParkingMapScreen extends StatefulWidget {
  @override
  _ParkingMapScreenState createState() => _ParkingMapScreenState();
}

class _ParkingMapScreenState extends State<ParkingMapScreen> {
  final LatLng _initialPosition = LatLng(35.030, 135.780);
  final MapController _mapController = MapController();
  final TextEditingController _searchController = TextEditingController();
  LatLng? _currentLocationMarker;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          FlutterMap(
            mapController: _mapController,
            options: MapOptions(
              initialCenter: _initialPosition,
              initialZoom: 15.0,
            ),
            children: [
              TileLayer(
                urlTemplate:
                    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                subdomains: ['a', 'b', 'c'],
              ),
              MarkerLayer(
                markers: _createMarkers(),
              ),
            ],
          ),

          // 検索バー
          Positioned(
            top: 40,
            left: 15,
            right: 15,
            child: _buildSearchBar(),
          ),

          // 「このエリアで検索」ボタン
          Positioned(
            bottom: 100,
            left: 40,
            right: 40,
            child: ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.teal,
                shape: StadiumBorder(),
              ),
              icon: Icon(Icons.refresh),
              label: Text("このエリアで検索"),
              onPressed: () {},
            ),
          ),

          // 現在地ボタン
          Positioned(
            bottom: 30,
            right: 20,
            child: FloatingActionButton(
              onPressed: _goToCurrentLocation,
              child: Icon(Icons.navigation),
            ),
          ),
        ],
      ),

      // 下部ナビゲーションバー
      bottomNavigationBar: BottomNavigationBar(
        selectedItemColor: Colors.teal,
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.local_parking),
            label: '駐車場を探す',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.favorite_border),
            label: 'お気に入り',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.book),
            label: '予約情報',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.menu),
            label: 'メニュー',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person_outline),
            label: 'オーナー',
          ),
        ],
      ),
    );
  }

  // 検索バー
  Widget _buildSearchBar() {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 10),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.8),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _searchController,
              style: TextStyle(color: Colors.white),
              decoration: InputDecoration(
                icon: Icon(Icons.search, color: Colors.white),
                hintText: '地名やスポット名で検索',
                hintStyle: TextStyle(color: Colors.white60),
                border: InputBorder.none,
              ),
            ),
          ),
          IconButton(
            icon: Icon(Icons.send, color: Colors.teal),
            onPressed: _searchLocation,
          ),
        ],
      ),
    );
  }

  // マーカー作成
  List<Marker> _createMarkers() {
    List<Marker> markers = [
      Marker(
        width: 80.0,
        height: 80.0,
        point: LatLng(35.031, 135.78),
        rotate: true,
        child: _buildPriceMarker("¥30〜"),
      ),
      Marker(
        width: 80.0,
        height: 80.0,
        point: LatLng(35.0305, 135.781),
        rotate: true,
        child: _buildPriceMarker("¥770"),
      ),
    ];

    if (_currentLocationMarker != null) {
      markers.add(
        Marker(
          width: 50.0,
          height: 50.0,
          point: _currentLocationMarker!,
          child: Icon(
            Icons.my_location,
            color: Colors.blue,
            size: 40,
          ),
        ),
      );
    }

    return markers;
  }

  Widget _buildPriceMarker(String price) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: Colors.green,
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        price,
        style: TextStyle(
          color: Colors.white,
          fontWeight: FontWeight.bold,
          fontSize: 12,
        ),
      ),
    );
  }

  // 現在地取得
  Future<void> _goToCurrentLocation() async {
    bool serviceEnabled;
    LocationPermission permission;

    serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      _showError('位置情報サービスが無効です');
      return;
    }

    permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        _showError('位置情報のパーミッションが拒否されました');
        return;
      }
    }

    if (permission == LocationPermission.deniedForever) {
      _showError('位置情報のパーミッションが永続的に拒否されています');
      return;
    }

    final Position position = await Geolocator.getCurrentPosition();
    final LatLng currentLocation = LatLng(position.latitude, position.longitude);

    setState(() {
      _currentLocationMarker = currentLocation;
    });

    _mapController.move(currentLocation, 15.0);
  }

  // 地名検索
  Future<void> _searchLocation() async {
    final query = _searchController.text.trim();
    if (query.isEmpty) return;

    final url = Uri.parse(
      'https://nominatim.openstreetmap.org/search?q=$query&format=json&limit=1',
    );

    try {
      final response = await http.get(url, headers: {
        'User-Agent': 'flutter-map-app-example', // 任意のアプリ名を記述
      });

      if (response.statusCode == 200) {
        final results = json.decode(response.body);
        if (results.isNotEmpty) {
          final lat = double.parse(results[0]['lat']);
          final lon = double.parse(results[0]['lon']);
          final target = LatLng(lat, lon);
          _mapController.move(target, 15.0);
        } else {
          _showError("地名が見つかりませんでした");
        }
      } else {
        _showError("検索に失敗しました（HTTP ${response.statusCode}）");
      }
    } catch (e) {
      _showError("検索エラー: $e");
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }
}