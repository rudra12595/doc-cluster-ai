import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

class ApiService {
  // If running on Android emulator, use 10.0.2.2.
  // If running on a physical device, use your PC's IP address (e.g., 192.168.1.x)
  // For Windows desktop app or web app, localhost/127.0.0.1 is fine.
  static const String baseUrl = 'http://127.0.0.1:5000/api';

  static Future<Map<String, dynamic>> fetchClusters() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/clusters'));
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load clusters: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching clusters: $e');
    }
  }

  static Future<Map<String, dynamic>> uploadDocument(String filePath, String fileName) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/upload'));
      
      request.files.add(
        await http.MultipartFile.fromPath(
          'file',
          filePath,
          filename: fileName,
        ),
      );

      var response = await request.send();
      var responseData = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        return json.decode(responseData);
      } else {
        throw Exception('Failed to upload document: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error uploading document: $e');
    }
  }
}
