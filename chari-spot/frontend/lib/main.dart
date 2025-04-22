import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // 地図表示
          FlutterMap(
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
            child: Column(
              children: [
                _buildSearchBar(),
                const SizedBox(height: 10),
                _buildFilterButton(),
              ],
            ),
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

          // 現在地ボタン（※機能は未実装）
          Positioned(
            bottom: 30,
            right: 20,
            child: FloatingActionButton(
              onPressed: () {
                // 現在地取得など
              },
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

  Widget _buildSearchBar() {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 10),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.8),
        borderRadius: BorderRadius.circular(8),
      ),
      child: TextField(
        style: TextStyle(color: Colors.white),
        decoration: InputDecoration(
          icon: Icon(Icons.search, color: Colors.white),
          hintText: '地名やスポット名で検索',
          hintStyle: TextStyle(color: Colors.white60),
          border: InputBorder.none,
        ),
      ),
    );
  }

  Widget _buildFilterButton() {
    return Align(
      alignment: Alignment.centerLeft,
      child: TextButton(
        onPressed: () {},
        child: Text(
          '日時や車種で絞り込む',
          style: TextStyle(color: Colors.teal),
        ),
      ),
    );
  }

  List<Marker> _createMarkers() {
    return [
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
}
