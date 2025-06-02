import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'main.dart'; // ParkingSpot が定義されているファイル

class ParkingDetailScreen extends StatelessWidget {
  final ParkingSpot spot;

  const ParkingDetailScreen({Key? key, required this.spot}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          spot.name,
          style: GoogleFonts.notoSansJp(fontSize: 20),
        ),
        backgroundColor: Colors.orange,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "住所: ${spot.address}",
              style: GoogleFonts.notoSansJp(fontSize: 18),
            ),
            SizedBox(height: 8),
            Text(
              "緯度: ${spot.latitude}",
              style: GoogleFonts.notoSansJp(fontSize: 16),
            ),
            Text(
              "経度: ${spot.longitude}",
              style: GoogleFonts.notoSansJp(fontSize: 16),
            ),
            SizedBox(height: 8),
            Text(
              "駐車可能台数: ${spot.totalSlots}",
              style: GoogleFonts.notoSansJp(fontSize: 16),
            ),
            Text(
              "空き台数: ${spot.availSlots}",
              style: GoogleFonts.notoSansJp(fontSize: 16),
            ),
          ],
        ),
      ),
    );
  }
}