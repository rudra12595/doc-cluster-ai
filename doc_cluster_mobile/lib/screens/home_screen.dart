import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'upload_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<dynamic> _clusters = [];
  bool _isLoading = true;
  String _errorMessage = '';

  @override
  void initState() {
    super.initState();
    _loadClusters();
  }

  Future<void> _loadClusters() async {
    setState(() {
      _isLoading = true;
      _errorMessage = '';
    });
    try {
      final data = await ApiService.fetchClusters();
      setState(() {
        _clusters = data['clusters'] ?? [];
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Could not connect to the backend.\nPlease make sure your Flask app is running.\n\nDetails: $e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('DocCluster App'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadClusters,
            tooltip: 'Refresh Clusters',
          )
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _errorMessage.isNotEmpty
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.error_outline, size: 64, color: Colors.red),
                        const SizedBox(height: 16),
                        Text(
                          _errorMessage,
                          textAlign: TextAlign.center,
                          style: const TextStyle(fontSize: 16, color: Colors.red),
                        ),
                        const SizedBox(height: 24),
                        ElevatedButton(
                          onPressed: _loadClusters,
                          child: const Text('Try Again'),
                        )
                      ],
                    ),
                  ),
                )
              : _clusters.isEmpty
                  ? const Center(
                      child: Text(
                        'No clusters found. Upload some documents!',
                        style: TextStyle(fontSize: 18),
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _clusters.length,
                      itemBuilder: (context, index) {
                        final cluster = _clusters[index];
                        final files = cluster['files'] as List<dynamic>? ?? [];
                        
                        return Card(
                          margin: const EdgeInsets.only(bottom: 16),
                          elevation: 4,
                          child: Padding(
                            padding: const EdgeInsets.all(16.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    const Icon(Icons.folder_shared, color: Colors.blueAccent),
                                    const SizedBox(width: 8),
                                    Text(
                                      'Cluster ${cluster['cluster_id'] ?? index}',
                                      style: const TextStyle(
                                        fontSize: 20,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ],
                                ),
                                const Divider(),
                                ...files.map((file) => Padding(
                                      padding: const EdgeInsets.symmetric(vertical: 4.0),
                                      child: Row(
                                        children: [
                                          const Icon(Icons.insert_drive_file, size: 16, color: Colors.grey),
                                          const SizedBox(width: 8),
                                          Expanded(child: Text(file.toString())),
                                        ],
                                      ),
                                    )),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const UploadScreen()),
          ).then((_) => _loadClusters());
        },
        icon: const Icon(Icons.add),
        label: const Text('Upload'),
      ),
    );
  }
}
