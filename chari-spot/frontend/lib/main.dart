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
      theme: ThemeData(
        brightness: Brightness.dark,
        fontFamily: 'NotoSansJP', // ✅ カスタムフォントを明示指定
      ),
      home: ParkingMapScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class ParkingSpot {
  final int id;
  final String name;
  final String address;
  final double latitude;
  final double longitude;
  final int totalSlots;
  final int availSlots;

  ParkingSpot({
    required this.id,
    required this.name,
    required this.address,
    required this.latitude,
    required this.longitude,
    required this.totalSlots,
    required this.availSlots,
  });
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
  List<ParkingSpot> _parkingSpots = [];

  @override
  void initState() {
    super.initState();
    _loadParkingSpots();
  }

  Future<void> _loadParkingSpots() async {
    try {
      final url = Uri.parse('http://localhost:8000/parkings');
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        setState(() {
          _parkingSpots = data.map((item) {
            return ParkingSpot(
              id: item['id'],
              name: item['name'],
              address: item['address'],
              latitude: item['latitude'],
              longitude: item['longitude'],
              totalSlots: item['total_slots'],
              availSlots: item['avail_slots'],
            );
          }).toList();
        });
      } else {
        _showError("駐車場データの取得に失敗しました");
      }
    } catch (e) {
      _showError("通信エラー: $e");
    }
  }

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
                urlTemplate: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                subdomains: ['a', 'b', 'c'],
              ),
              MarkerLayer(
                markers: _createMarkers(context),
              ),
            ],
          ),
          Positioned(
            top: 40,
            left: 15,
            right: 15,
            child: _buildSearchBar(),
          ),
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
              onPressed: _loadParkingSpots,
            ),
          ),
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
      bottomNavigationBar: BottomNavigationBar(
        selectedItemColor: Colors.teal,
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.local_parking), label: '駐車場を探す'),
          BottomNavigationBarItem(icon: Icon(Icons.favorite_border), label: 'お気に入り'),
          BottomNavigationBarItem(icon: Icon(Icons.book), label: '予約情報'),
          BottomNavigationBarItem(icon: Icon(Icons.menu), label: 'メニュー'),
          BottomNavigationBarItem(icon: Icon(Icons.person_outline), label: 'オーナー'),
        ],
      ),
    );
  }

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

  List<Marker> _createMarkers(BuildContext context) {
    List<Marker> markers = _parkingSpots.map((spot) {
      return Marker(
        width: 60.0,
        height: 60.0,
        point: LatLng(spot.latitude, spot.longitude),
        rotate: true,
        child: GestureDetector(
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => ParkingDetailScreen(spot: spot),
              ),
            );
          },
          child: Icon(Icons.location_pin, color: Colors.red, size: 60),
        ),
      );
    }).toList();

    if (_currentLocationMarker != null) {
      markers.add(
        Marker(
          width: 50.0,
          height: 50.0,
          point: _currentLocationMarker!,
          child: Icon(Icons.my_location, color: Colors.blue, size: 40),
        ),
      );
    }

    return markers;
  }

  Future<void> _goToCurrentLocation() async {
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) return _showError('位置情報サービスが無効です');

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) return _showError('パーミッションが拒否されました');
    }
    if (permission == LocationPermission.deniedForever) return _showError('パーミッションが永続的に拒否されています');

    final position = await Geolocator.getCurrentPosition();
    final currentLocation = LatLng(position.latitude, position.longitude);

    setState(() {
      _currentLocationMarker = currentLocation;
    });
    _mapController.move(currentLocation, 15.0);
  }

  Future<void> _searchLocation() async {
    final query = _searchController.text.trim();
    if (query.isEmpty) return;

    final url = Uri.parse('https://nominatim.openstreetmap.org/search?q=$query&format=json&limit=1');
    try {
      final response = await http.get(url, headers: {'User-Agent': 'flutter-map-app-example'});
      if (response.statusCode == 200) {
        final results = json.decode(response.body);
        if (results.isNotEmpty) {
          final lat = double.parse(results[0]['lat']);
          final lon = double.parse(results[0]['lon']);
          _mapController.move(LatLng(lat, lon), 15.0);
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

class ParkingDetailScreen extends StatelessWidget {
  final ParkingSpot spot;

  const ParkingDetailScreen({Key? key, required this.spot}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(spot.name), backgroundColor: Colors.teal),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: DefaultTextStyle(
          style: TextStyle(fontSize: 16, color: Colors.white),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text("🅿️ 駐輪場名: ${spot.name}", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              SizedBox(height: 12),
              Text("📍 住所: ${spot.address}"),
              SizedBox(height: 12),
              Text("🚲 空き台数: ${spot.availSlots} / ${spot.totalSlots}"),
            ],
          ),
        ),
      ),
    );
  }
}