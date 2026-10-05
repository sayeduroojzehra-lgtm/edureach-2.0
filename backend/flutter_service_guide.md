# EduReach Flutter Integration Guide

This guide explains how to connect the existing EduReach Flutter frontend to the newly created backend API. As requested, **no changes were made to `lib/main.dart` or the existing Flutter directory**.

When you are ready to connect `main.dart` to live data, you can use the code snippets below.

---

## 1. Network Configuration

When calling the backend from Flutter:

| Platform | Base URL |
| :--- | :--- |
| **Android Emulator** | `http://10.0.2.2:8000/api/v1` |
| **iOS Simulator** | `http://127.0.0.1:8000/api/v1` |
| **Flutter Web** | `http://localhost:8000/api/v1` |
| **Real Device (LAN)** | `http://<YOUR_COMPUTER_IP>:8000/api/v1` |

---

## 2. Dependencies

Add to your `pubspec.yaml` when ready:
```yaml
dependencies:
  http: ^1.2.0
```

---

## 3. Plug-and-Play ApiService (`lib/services/api_service.dart`)

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // Change to 10.0.2.2 for Android emulator or localhost for Web/Desktop
  static const String baseUrl = 'http://127.0.0.1:8000/api/v1';
  static String? authToken;

  // 1. Authentication
  static Future<Map<String, dynamic>> login({
    required String name,
    required String email,
    required String password,
    required String role,
    int? standard,
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'name': name,
        'email': email,
        'password': password,
        'role': role,
        'standard': standard,
      }),
    );
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      authToken = data['access_token'];
      return data;
    } else {
      throw Exception('Login failed: ${res.body}');
    }
  }

  // 2. Fetch Study Notes
  static Future<List<Map<String, dynamic>>> fetchNotes({required int standard, String? subject}) async {
    String url = '$baseUrl/notes?standard=$standard';
    if (subject != null && subject.isNotEmpty) {
      url += '&subject=${Uri.encodeComponent(subject)}';
    }
    final res = await http.get(Uri.parse(url));
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      return List<Map<String, dynamic>>.from(data['notes']);
    }
    return [];
  }

  // 3. Upload Study Note
  static Future<Map<String, dynamic>> uploadNote({
    required int standard,
    required String subject,
    required String title,
    required String content,
    String teacher = 'Class Teacher',
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl/notes'),
      headers: {
        'Content-Type': 'application/json',
        if (authToken != null) 'Authorization': 'Bearer $authToken',
      },
      body: jsonEncode({
        'standard': standard,
        'subject': subject,
        'title': title,
        'content': content,
        'teacher': teacher,
        'date': 'Today',
      }),
    );
    return jsonDecode(res.body);
  }

  // 4. Quizzes & Submissions
  static Future<List<Map<String, dynamic>>> fetchQuizzes({required int standard}) async {
    final res = await http.get(Uri.parse('$baseUrl/quizzes?standard=$standard'));
    if (res.statusCode == 200) {
      return List<Map<String, dynamic>>.from(jsonDecode(res.body));
    }
    return [];
  }

  static Future<Map<String, dynamic>> submitQuiz({required int quizId, required List<int> answers}) async {
    final res = await http.post(
      Uri.parse('$baseUrl/quizzes/$quizId/submit'),
      headers: {
        'Content-Type': 'application/json',
        if (authToken != null) 'Authorization': 'Bearer $authToken',
      },
      body: jsonEncode({'answers': answers}),
    );
    return jsonDecode(res.body);
  }

  // 5. Daily Attendance
  static Future<Map<String, dynamic>> fetchAttendance({required int standard, String? date}) async {
    String url = '$baseUrl/attendance?standard=$standard';
    if (date != null) url += '&date=$date';
    final res = await http.get(Uri.parse(url));
    return jsonDecode(res.body);
  }

  static Future<void> saveAttendance({
    required int standard,
    required String date,
    required List<Map<String, dynamic>> records,
  }) async {
    await http.post(
      Uri.parse('$baseUrl/attendance'),
      headers: {
        'Content-Type': 'application/json',
        if (authToken != null) 'Authorization': 'Bearer $authToken',
      },
      body: jsonEncode({
        'standard': standard,
        'date': date,
        'records': records,
      }),
    );
  }

  // 6. Learn Offline Bundle
  static Future<Map<String, dynamic>> downloadOfflineBundle({required int standard}) async {
    final res = await http.get(Uri.parse('$baseUrl/sync/offline-bundle?standard=$standard'));
    return jsonDecode(res.body);
  }
}
```
