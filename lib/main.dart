
import 'dart:convert';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher.dart';

void main() => runApp(const EduReachApp());

enum UserRole { student, teacher }

// EduReach light pastel palette
const skyBlue = Color(0xFF64B5F6);
const softBlue = Color(0xFFBBDEFB);
const mint = Color(0xFFA5D6A7);
const lavender = Color(0xFFCE93D8);
const peach = Color(0xFFFFCCBC);
const yellow = Color(0xFFFFF59D);
const pink = Color(0xFFF8BBD0);
const teal = Color(0xFF80CBC4);
const background = Color(0xFFF5FAFF);
const navy = Color(0xFF29465B);

class StudyNote {
  final int id;
  final int standard;
  final String subject;
  final String title;
  final String content;
  final String teacher;
  final String date;
  final String? pdfUrl;

  StudyNote({
    this.id = 0,
    required this.standard,
    required this.subject,
    required this.title,
    required this.content,
    required this.teacher,
    required this.date,
    this.pdfUrl,
  });

  factory StudyNote.fromJson(Map<String, dynamic> json) {
    return StudyNote(
      id: json['id'] is int ? json['id'] : int.tryParse('${json['id'] ?? 0}') ?? 0,
      standard: json['standard'] is int ? json['standard'] : int.parse('${json['standard']}'),
      subject: '${json['subject'] ?? ''}',
      title: '${json['title'] ?? ''}',
      content: '${json['content'] ?? ''}',
      teacher: '${json['teacher'] ?? 'Class Teacher'}',
      date: '${json['date'] ?? 'Today'}',
      pdfUrl: json['pdf_url']?.toString(),
    );
  }
}


class AuthUser {
  final int id;
  final String name;
  final String email;
  final UserRole role;
  final int? standard;

  AuthUser({required this.id, required this.name, required this.email, required this.role, this.standard});

  factory AuthUser.fromJson(Map<String, dynamic> json) {
    return AuthUser(
      id: json['id'] is int ? json['id'] : int.tryParse('${json['id']}') ?? 0,
      name: '${json['name'] ?? 'Student'}',
      email: '${json['email'] ?? ''}',
      role: '${json['role']}' == 'teacher' ? UserRole.teacher : UserRole.student,
      standard: json['standard'] == null ? null : (json['standard'] is int ? json['standard'] : int.tryParse('${json['standard']}')),
    );
  }
}

class QuizQuestion {
  final int id;
  final String question;
  final List<String> options;

  QuizQuestion({required this.id, required this.question, required this.options});

  factory QuizQuestion.fromJson(Map<String, dynamic> json) => QuizQuestion(
        id: json['id'] is int ? json['id'] : int.tryParse('${json['id']}') ?? 0,
        question: '${json['question_text'] ?? ''}',
        options: (json['options'] as List<dynamic>? ?? const []).map((e) => '$e').toList(),
      );
}

class QuizData {
  final int id;
  final String title;
  final String subject;
  final String description;
  final List<QuizQuestion> questions;

  QuizData({required this.id, required this.title, required this.subject, required this.description, required this.questions});

  factory QuizData.fromJson(Map<String, dynamic> json) => QuizData(
        id: json['id'] is int ? json['id'] : int.tryParse('${json['id']}') ?? 0,
        title: '${json['title'] ?? 'Practice Quiz'}',
        subject: '${json['subject'] ?? ''}',
        description: '${json['description'] ?? ''}',
        questions: (json['questions'] as List<dynamic>? ?? const [])
            .map((e) => QuizQuestion.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
}

class AttendanceStudent {
  final int id;
  final String name;
  bool present;
  AttendanceStudent({required this.id, required this.name, required this.present});

  factory AttendanceStudent.fromJson(Map<String, dynamic> json) => AttendanceStudent(
        id: json['student_id'] ?? json['id'] ?? 0,
        name: '${json['student_name'] ?? json['name'] ?? 'Student'}',
        present: json['is_present'] ?? true,
      );
}

class ProgressItem {
  final String subject;
  final double value;
  final String percentage;
  ProgressItem({required this.subject, required this.value, required this.percentage});

  factory ProgressItem.fromJson(Map<String, dynamic> json) => ProgressItem(
        subject: '${json['subject'] ?? ''}',
        value: (json['value'] as num?)?.toDouble() ?? 0,
        percentage: '${json['percentage_str'] ?? '${(((json['value'] as num?)?.toDouble() ?? 0) * 100).round()}% completed'}',
      );
}

class PerformanceItem {
  final String name;
  final String progress;
  PerformanceItem({required this.name, required this.progress});

  factory PerformanceItem.fromJson(Map<String, dynamic> json) => PerformanceItem(
        name: '${json['name'] ?? 'Student'}',
        progress: '${json['progress'] ?? '0%'}',
      );
}

class ApiService {
  static String? token;

  static String get baseUrl {
    if (kIsWeb) return 'http://localhost:8000/api/v1';
    if (defaultTargetPlatform == TargetPlatform.android) return 'http://10.0.2.2:8000/api/v1';
    return 'http://127.0.0.1:8000/api/v1';
  }

  static Map<String, String> get headers => {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      };

  static Future<AuthUser> login({
    required String email,
    required String password,
    required UserRole role,
    required String name,
    required int standard,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email.trim(),
        'password': password,
        'role': role == UserRole.teacher ? 'teacher' : 'student',
        'name': name.trim(),
        'standard': standard,
      }),
    );
    if (response.statusCode != 200) {
      String detail = 'Login failed (${response.statusCode})';
      try { detail = '${(jsonDecode(response.body) as Map<String, dynamic>)['detail'] ?? detail}'; } catch (_) {}
      throw Exception(detail);
    }
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    token = '${data['access_token']}';
    return AuthUser.fromJson(data['user'] as Map<String, dynamic>);
  }

  static void logout() => token = null;

  static Future<List<StudyNote>> fetchNotes({required int standard}) async {
    final response = await http.get(Uri.parse('$baseUrl/notes?standard=$standard'), headers: headers);
    if (response.statusCode != 200) throw Exception('Could not load notes (${response.statusCode})');
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return (data['notes'] as List<dynamic>? ?? const [])
        .map((item) => StudyNote.fromJson(item as Map<String, dynamic>)).toList();
  }

  static Future<StudyNote> uploadNote({required int standard, required String subject, required String title, required String content, required PlatformFile pdfFile}) async {
    final request = http.MultipartRequest('POST', Uri.parse('$baseUrl/notes'));
    if (token != null) request.headers['Authorization'] = 'Bearer $token';
    request.fields.addAll({'standard': '$standard', 'subject': subject, 'title': title, 'content': content, 'teacher': 'Class Teacher'});
    if (pdfFile.bytes != null) {
      request.files.add(http.MultipartFile.fromBytes('pdf', pdfFile.bytes!, filename: pdfFile.name));
    } else if (pdfFile.path != null) {
      request.files.add(await http.MultipartFile.fromPath('pdf', pdfFile.path!, filename: pdfFile.name));
    } else {
      throw Exception('Could not read the selected PDF.');
    }
    final response = await request.send();
    final body = await response.stream.bytesToString();
    if (response.statusCode != 201) throw Exception('Upload failed (${response.statusCode}): $body');
    return StudyNote.fromJson(jsonDecode(body) as Map<String, dynamic>);
  }

  static Future<List<AttendanceStudent>> fetchAttendance({required int standard, required DateTime date}) async {
    final d = '${date.year.toString().padLeft(4, '0')}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
    final response = await http.get(Uri.parse('$baseUrl/attendance?standard=$standard&date=$d'), headers: headers);
    if (response.statusCode != 200) throw Exception('Could not load attendance (${response.statusCode})');
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return (data['records'] as List<dynamic>? ?? const []).map((e) => AttendanceStudent.fromJson(e)).toList();
  }

  static Future<void> saveAttendance({required int standard, required DateTime date, required List<AttendanceStudent> students}) async {
    final d = '${date.year.toString().padLeft(4, '0')}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
    final response = await http.post(
      Uri.parse('$baseUrl/attendance'),
      headers: headers,
      body: jsonEncode({
        'standard': standard,
        'session_date': d,
        'records': students.map((s) => {'student_id': s.id, 'student_name': s.name, 'is_present': s.present}).toList(),
      }),
    );
    if (response.statusCode != 200) throw Exception('Could not save attendance (${response.statusCode})');
  }

  static Future<List<ProgressItem>> fetchProgress({required int standard}) async {
    final response = await http.get(Uri.parse('$baseUrl/progress/my-progress?standard=$standard'), headers: headers);
    if (response.statusCode != 200) throw Exception('Could not load progress (${response.statusCode})');
    final data = jsonDecode(response.body) as List<dynamic>;
    return data.map((e) => ProgressItem.fromJson(e)).toList();
  }

  static Future<List<QuizData>> fetchQuizzes({required int standard}) async {
    final response = await http.get(Uri.parse('$baseUrl/quizzes?standard=$standard'), headers: headers);
    if (response.statusCode != 200) throw Exception('Could not load quizzes (${response.statusCode})');
    final data = jsonDecode(response.body) as List<dynamic>;
    return data.map((e) => QuizData.fromJson(e)).toList();
  }

  static Future<Map<String, dynamic>> submitQuiz({required int quizId, required List<int> answers}) async {
    final response = await http.post(Uri.parse('$baseUrl/quizzes/$quizId/submit'), headers: headers, body: jsonEncode({'answers': answers}));
    if (response.statusCode != 200) throw Exception('Could not submit quiz (${response.statusCode})');
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  static Future<List<PerformanceItem>> fetchPerformance({required int standard}) async {
    final response = await http.get(Uri.parse('$baseUrl/analytics/performance?standard=$standard'), headers: headers);
    if (response.statusCode != 200) throw Exception('Could not load performance (${response.statusCode})');
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return (data['students'] as List<dynamic>? ?? const []).map((e) => PerformanceItem.fromJson(e)).toList();
  }
}

class EduReachApp extends StatelessWidget {
  const EduReachApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'EduReach',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: skyBlue,
          brightness: Brightness.light,
        ),
        scaffoldBackgroundColor: background,
        fontFamily: 'Arial',
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.white,
          foregroundColor: navy,
          elevation: 0,
        ),
        cardTheme: CardThemeData(
          color: Colors.white,
          elevation: 0,
          margin: EdgeInsets.zero,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(18)),
          ),
        ),
        inputDecorationTheme: const InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.all(Radius.circular(14)),
            borderSide: BorderSide.none,
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.all(Radius.circular(14)),
            borderSide: BorderSide(color: softBlue),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.all(Radius.circular(14)),
            borderSide: BorderSide(color: skyBlue, width: 2),
          ),
        ),
      ),
      home: const LoginPage(),
    );
  }
}

/* ---------------- LOGIN ---------------- */

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  UserRole role = UserRole.student;
  final name = TextEditingController();
  final email = TextEditingController();
  final password = TextEditingController();
  int standard = 8;
  bool obscure = true;

  bool loggingIn = false;

  Future<void> login() async {
    if (name.text.trim().isEmpty || email.text.trim().isEmpty || password.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please fill in all fields.')));
      return;
    }
    setState(() => loggingIn = true);
    try {
      final user = await ApiService.login(
        email: email.text.trim(),
        password: password.text,
        role: role,
        name: name.text.trim(),
        standard: standard,
      );
      if (!mounted) return;
      Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => AppShell(
        role: user.role,
        userName: user.name,
        standard: user.standard ?? standard,
      )));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Login failed: $e')));
    } finally {
      if (mounted) setState(() => loggingIn = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 480),
              child: Card(
                elevation: 0,
                child: Padding(
                  padding: const EdgeInsets.all(28),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(Icons.school_rounded,
                          size: 52, color: skyBlue),
                      const SizedBox(height: 14),
                      const Text('Welcome to EduReach',
                          style: TextStyle(
                              fontSize: 28, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 6),
                      const Text(
                        'Technology-enabled education for every learner.',
                        style: TextStyle(color: Colors.grey),
                      ),
                      const SizedBox(height: 26),
                      SegmentedButton<UserRole>(
                        segments: const [
                          ButtonSegment(
                            value: UserRole.student,
                            label: Text('Student'),
                            icon: Icon(Icons.person),
                          ),
                          ButtonSegment(
                            value: UserRole.teacher,
                            label: Text('Teacher'),
                            icon: Icon(Icons.co_present),
                          ),
                        ],
                        selected: {role},
                        onSelectionChanged: (v) =>
                            setState(() => role = v.first),
                      ),
                      const SizedBox(height: 22),
                      TextField(
                        controller: name,
                        decoration: const InputDecoration(
                          labelText: 'Name',
                          prefixIcon: Icon(Icons.person_outline),
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 14),
                      TextField(
                        controller: email,
                        keyboardType: TextInputType.emailAddress,
                        decoration: const InputDecoration(
                          labelText: 'Email',
                          prefixIcon: Icon(Icons.email_outlined),
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 14),
                      TextField(
                        controller: password,
                        obscureText: obscure,
                        decoration: InputDecoration(
                          labelText: 'Password',
                          prefixIcon: const Icon(Icons.lock_outline),
                          border: const OutlineInputBorder(),
                          suffixIcon: IconButton(
                            icon: Icon(obscure
                                ? Icons.visibility
                                : Icons.visibility_off),
                            onPressed: () =>
                                setState(() => obscure = !obscure),
                          ),
                        ),
                      ),
                      if (role == UserRole.student) ...[
                        const SizedBox(height: 14),
                        DropdownButtonFormField<int>(
                          value: standard,
                          decoration: const InputDecoration(
                            labelText: 'Standard',
                            prefixIcon: Icon(Icons.class_outlined),
                            border: OutlineInputBorder(),
                          ),
                          items: List.generate(
                            10,
                            (i) => DropdownMenuItem(
                              value: i + 1,
                              child: Text('Standard ${i + 1}'),
                            ),
                          ),
                          onChanged: (v) =>
                              setState(() => standard = v ?? 8),
                        ),
                      ],
                      const SizedBox(height: 22),
                      SizedBox(
                        width: double.infinity,
                        height: 52,
                        child: FilledButton.icon(
                          onPressed: loggingIn ? null : login,
                          icon: loggingIn ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.login),
                          label: Text(
                            role == UserRole.student
                                ? 'Login as Student'
                                : 'Login as Teacher',
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      const Center(
                        child: Text(
                          'Secure login connected to the EduReach backend.',
                          style: TextStyle(fontSize: 12, color: Colors.grey),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/* ---------------- APP SHELL ---------------- */

class AppShell extends StatefulWidget {
  final UserRole role;
  final String userName;
  final int standard;

  const AppShell({
    super.key,
    required this.role,
    required this.userName,
    required this.standard,
  });

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int index = 0;
  bool loadingNotes = true;

  @override
  void initState() {
    super.initState();
    _loadNotes();
  }

  Future<void> _loadNotes() async {
    try {
      final remoteNotes = await ApiService.fetchNotes(standard: widget.standard);
      if (!mounted) return;
      setState(() {
        notes
          ..clear()
          ..addAll(remoteNotes);
        loadingNotes = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() => loadingNotes = false);
    }
  }

  final List<StudyNote> notes = [
    StudyNote(
      standard: 8,
      subject: 'Mathematics',
      title: 'Algebra Basics',
      content: 'Learn variables, expressions and simple equations.',
      teacher: 'Class Teacher',
      date: 'Today',
    ),
    StudyNote(
      standard: 8,
      subject: 'Science',
      title: 'Force and Pressure',
      content: 'Important concepts and examples for revision.',
      teacher: 'Class Teacher',
      date: 'Yesterday',
    ),
  ];

  void logout() {
    ApiService.logout();
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (_) => const LoginPage()),
      (_) => false,
    );
  }

  List<Widget> get studentPages => [
        StudentHome(
          name: widget.userName,
          standard: widget.standard,
          notes: notes,
        ),
        LearnPage(
          standard: widget.standard,
          notes: notes,
          onAddNote: addNote,
          teacher: false,
          loadingNotes: loadingNotes,
        ),
        PracticePage(standard: widget.standard),
        StudentProgressPage(standard: widget.standard),
        ProfilePage(
          name: widget.userName,
          role: widget.role,
          standard: widget.standard,
          onLogout: logout,
        ),
      ];

  List<Widget> get teacherPages => [
        TeacherHome(
          name: widget.userName,
          onAttendance: () => openPage(
            AttendancePage(standard: widget.standard),
          ),
          onNotes: () => openPage(
            LearnPage(
              standard: widget.standard,
              notes: notes,
              onAddNote: addNote,
              teacher: true,
              loadingNotes: loadingNotes,
            ),
          ),
        ),
        TeacherToolsPage(
          standard: widget.standard,
          notes: notes,
          onAddNote: addNote,
        ),
        AttendancePage(standard: widget.standard),
        TeacherPerformancePage(standard: widget.standard),
        ProfilePage(
          name: widget.userName,
          role: widget.role,
          standard: widget.standard,
          onLogout: logout,
        ),
      ];

  List<String> get studentLabels =>
      ['Home', 'Learn', 'Practice', 'Progress', 'Profile'];

  List<String> get teacherLabels =>
      ['Home', 'Notes', 'Attendance', 'Performance', 'Profile'];

  void openPage(Widget page) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => page),
    );
  }

  void addNote(StudyNote note) {
    setState(() => notes.insert(0, note));
  }

  @override
  Widget build(BuildContext context) {
    final pages = widget.role == UserRole.student ? studentPages : teacherPages;
    final labels =
        widget.role == UserRole.student ? studentLabels : teacherLabels;
    final icons = widget.role == UserRole.student
        ? [
            Icons.home_rounded,
            Icons.menu_book_rounded,
            Icons.quiz_rounded,
            Icons.insights_rounded,
            Icons.person_rounded
          ]
        : [
            Icons.home_rounded,
            Icons.notes_rounded,
            Icons.event_available_rounded,
            Icons.analytics_rounded,
            Icons.person_rounded
          ];

    return Scaffold(
      body: pages[index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: index,
        onDestinationSelected: (v) => setState(() => index = v),
        destinations: List.generate(
          labels.length,
          (i) => NavigationDestination(
            icon: Icon(icons[i]),
            label: labels[i],
          ),
        ),
      ),
    );
  }
}

/* ---------------- STUDENT ---------------- */

class StudentHome extends StatelessWidget {
  final String name;
  final int standard;
  final List<StudyNote> notes;

  const StudentHome({
    super.key,
    required this.name,
    required this.standard,
    required this.notes,
  });

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          _top('Hello, $name 👋', 'Standard $standard • Student'),
          const SizedBox(height: 20),
          _hero(
            'Continue Learning',
            'Mathematics • Algebra',
            '80% completed',
            Icons.auto_stories_rounded,
          ),
          const SizedBox(height: 18),
          const Text('Your Overview',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          Row(
            children: const [
              Expanded(child: _Stat(title: 'Attendance', value: '92%', icon: Icons.event_available)),
              SizedBox(width: 10),
              Expanded(child: _Stat(title: 'Notes', value: '12', icon: Icons.notes)),
              SizedBox(width: 10),
              Expanded(child: _Stat(title: 'Progress', value: '78%', icon: Icons.trending_up)),
            ],
          ),
          const SizedBox(height: 22),
          const Text('Today’s Learning',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 10),
          const _Lesson(subject: 'Mathematics', topic: 'Algebra', icon: Icons.calculate),
          const _Lesson(subject: 'Science', topic: 'Force and Pressure', icon: Icons.science),
          const _Lesson(subject: 'English', topic: 'Grammar Practice', icon: Icons.menu_book),
          const SizedBox(height: 22),
          const Text('Recent Notes',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 10),
          ...notes.take(2).map((n) => _NoteCard(note: n)),
          const SizedBox(height: 18),
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(20),
              color: softBlue.withOpacity(.45),
            ),
            child: const Row(
              children: [
                Icon(Icons.wifi_off_rounded, size: 32),
                SizedBox(width: 14),
                Expanded(
                  child: Text(
                    'Learn Offline\nSaved lessons can be accessed even with limited internet.',
                    style: TextStyle(fontWeight: FontWeight.w600),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/* ---------------- TEACHER ---------------- */

class TeacherHome extends StatelessWidget {
  final String name;
  final VoidCallback onAttendance;
  final VoidCallback onNotes;

  const TeacherHome({
    super.key,
    required this.name,
    required this.onAttendance,
    required this.onNotes,
  });

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          _top('Hello, $name 👋', 'Teacher Dashboard'),
          const SizedBox(height: 20),
          _hero(
            'Class Overview',
            'Keep your students connected and learning.',
            '8 students • Standard 8',
            Icons.co_present_rounded,
          ),
          const SizedBox(height: 20),
          const Text('Teacher Tools',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _ToolCard(
                  title: 'Attendance',
                  icon: Icons.event_available_rounded,
                  onTap: onAttendance,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _ToolCard(
                  title: 'Upload Notes',
                  icon: Icons.upload_file_rounded,
                  onTap: onNotes,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Row(
            children: [
              Expanded(child: _ToolCard(title: 'Assignments', icon: Icons.assignment_rounded)),
              SizedBox(width: 12),
              Expanded(child: _ToolCard(title: 'Announcements', icon: Icons.campaign_rounded)),
            ],
          ),
          const SizedBox(height: 22),
          const Text('Today',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 10),
          Card(
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: mint.withOpacity(.55),
                child: const Icon(Icons.groups, color: navy),
              ),
              title: Text('Attendance not yet marked'),
              subtitle: Text('Open Attendance to mark today’s class.'),
            ),
          ),
          Card(
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: softBlue.withOpacity(.55),
                child: const Icon(Icons.notes, color: navy),
              ),
              title: Text('Keep notes updated'),
              subtitle: Text('Students can see notes uploaded by their teacher.'),
            ),
          ),
        ],
      ),
    );
  }
}

class TeacherToolsPage extends StatelessWidget {
  final int standard;
  final List<StudyNote> notes;
  final void Function(StudyNote) onAddNote;

  const TeacherToolsPage({
    super.key,
    required this.standard,
    required this.notes,
    required this.onAddNote,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Teacher Notes'),
        leading: Navigator.canPop(context) ? const BackButton() : null,
      ),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          FilledButton.icon(
            onPressed: () => _uploadDialog(context),
            icon: const Icon(Icons.upload_file),
            label: const Text('Upload New Note'),
          ),
          const SizedBox(height: 20),
          const Text('Uploaded Notes',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 10),
          ...notes.map((n) => _NoteCard(note: n)),
        ],
      ),
    );
  }

  Future<void> _uploadDialog(BuildContext context) async {
    final title = TextEditingController();
    final content = TextEditingController();
    String subject = 'Mathematics';
    PlatformFile? selectedPdf;

    await showDialog(
      context: context,
      builder: (_) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Upload PDF Note'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                DropdownButtonFormField<String>(
                  value: subject,
                  items: const ['Mathematics', 'Science', 'English', 'Social Science', 'Hindi', 'Marathi']
                      .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                      .toList(),
                  onChanged: (v) => setDialogState(() => subject = v ?? 'Mathematics'),
                  decoration: const InputDecoration(labelText: 'Subject'),
                ),
                TextField(
                  controller: title,
                  decoration: const InputDecoration(labelText: 'Note title'),
                ),
                TextField(
                  controller: content,
                  maxLines: 3,
                  decoration: const InputDecoration(labelText: 'Description (optional)'),
                ),
                const SizedBox(height: 12),
                OutlinedButton.icon(
                  icon: const Icon(Icons.picture_as_pdf_rounded),
                  label: Text(selectedPdf == null ? 'Select PDF' : selectedPdf!.name),
                  onPressed: () async {
                    final result = await FilePicker.platform.pickFiles(
                      type: FileType.custom,
                      allowedExtensions: ['pdf'],
                      withData: kIsWeb,
                    );
                    if (result != null && result.files.isNotEmpty) {
                      setDialogState(() => selectedPdf = result.files.single);
                    }
                  },
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
            FilledButton(
              onPressed: () async {
                if (title.text.trim().isEmpty || selectedPdf == null) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Please enter a title and select a PDF.')),
                  );
                  return;
                }
                try {
                  final note = await ApiService.uploadNote(
                    standard: standard,
                    subject: subject,
                    title: title.text.trim(),
                    content: content.text.trim(),
                    pdfFile: selectedPdf!,
                  );
                  onAddNote(note);
                  if (!context.mounted) return;
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('PDF note uploaded successfully.')),
                  );
                } catch (e) {
                  if (!context.mounted) return;
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Upload failed: $e')),
                  );
                }
              },
              child: const Text('Upload'),
            ),
          ],
        ),
      ),
    );
  }

}

/* ---------------- LEARNING ---------------- */

class LearnPage extends StatefulWidget {
  final int standard;
  final List<StudyNote> notes;
  final void Function(StudyNote) onAddNote;
  final bool teacher;
  final bool loadingNotes;

  const LearnPage({
    super.key,
    required this.standard,
    required this.notes,
    required this.onAddNote,
    required this.teacher,
    this.loadingNotes = false,
  });

  @override
  State<LearnPage> createState() => _LearnPageState();
}

class _LearnPageState extends State<LearnPage> {
  late int standard;

  @override
  void initState() {
    super.initState();
    standard = widget.standard;
  }

  @override
  Widget build(BuildContext context) {
    final subjects = standard <= 5
        ? ['English', 'Mathematics', 'Environmental Studies', 'Hindi', 'Marathi']
        : ['English', 'Mathematics', 'Science', 'Social Science', 'Hindi', 'Marathi'];

    final visibleNotes =
        widget.notes.where((n) => n.standard == standard).toList();

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.teacher ? 'Teacher Notes' : 'Learn'),
        leading: Navigator.canPop(context)
            ? const BackButton()
            : null,
        actions: [
          if (widget.teacher)
            IconButton(
              tooltip: 'Upload note',
              icon: const Icon(Icons.upload_file),
              onPressed: () => _upload(context),
            ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          DropdownButtonFormField<int>(
            value: standard,
            decoration: const InputDecoration(
              labelText: 'Standard',
              border: OutlineInputBorder(),
            ),
            items: List.generate(
              10,
              (i) => DropdownMenuItem(
                value: i + 1,
                child: Text('Standard ${i + 1}'),
              ),
            ),
            onChanged: (v) => setState(() => standard = v!),
          ),
          const SizedBox(height: 20),
          const Text('Subjects',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: subjects
                .map((s) => ActionChip(
                      label: Text(s),
                      avatar: const Icon(Icons.book_outlined, size: 18),
                      onPressed: () => _subject(context, s),
                    ))
                .toList(),
          ),
          const SizedBox(height: 22),
          Text(
            widget.teacher ? 'Uploaded Notes' : 'Notes from Teacher',
            style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 10),
          if (widget.loadingNotes && visibleNotes.isEmpty)
            const Padding(
              padding: EdgeInsets.all(20),
              child: Center(child: CircularProgressIndicator()),
            ),
          if (!widget.loadingNotes && visibleNotes.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(20),
                child: Text('No notes available for this standard yet.'),
              ),
            ),
          ...visibleNotes.map((n) => _NoteCard(note: n)),
        ],
      ),
    );
  }

  void _subject(BuildContext context, String subject) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => SubjectPage(
          standard: standard,
          subject: subject,
        ),
      ),
    );
  }

  Future<void> _upload(BuildContext context) async {
    final title = TextEditingController();
    final content = TextEditingController();
    String subject = 'General';
    PlatformFile? selectedPdf;

    await showDialog(
      context: context,
      builder: (_) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Upload PDF Note'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: title,
                  decoration: const InputDecoration(labelText: 'Title'),
                ),
                const SizedBox(height: 10),
                DropdownButtonFormField<String>(
                  value: subject,
                  decoration: const InputDecoration(labelText: 'Subject'),
                  items: const [
                    'English', 'Mathematics', 'Science', 'Social Science',
                    'Hindi', 'Marathi', 'General',
                  ].map((s) => DropdownMenuItem(value: s, child: Text(s))).toList(),
                  onChanged: (value) => setDialogState(() => subject = value ?? 'General'),
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: content,
                  maxLines: 3,
                  decoration: const InputDecoration(labelText: 'Description (optional)'),
                ),
                const SizedBox(height: 12),
                OutlinedButton.icon(
                  icon: const Icon(Icons.picture_as_pdf_rounded),
                  label: Text(selectedPdf == null ? 'Select PDF' : selectedPdf!.name),
                  onPressed: () async {
                    final result = await FilePicker.platform.pickFiles(
                      type: FileType.custom,
                      allowedExtensions: ['pdf'],
                      withData: kIsWeb,
                    );
                    if (result != null && result.files.isNotEmpty) {
                      setDialogState(() => selectedPdf = result.files.single);
                    }
                  },
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
            FilledButton(
              onPressed: () async {
                if (title.text.trim().isEmpty || selectedPdf == null) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Please enter a title and select a PDF.')),
                  );
                  return;
                }
                try {
                  final note = await ApiService.uploadNote(
                    standard: standard,
                    subject: subject,
                    title: title.text.trim(),
                    content: content.text.trim(),
                    pdfFile: selectedPdf!,
                  );
                  if (!mounted) return;
                  widget.onAddNote(note);
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('PDF note uploaded successfully.')),
                  );
                } catch (e) {
                  if (!mounted) return;
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Upload failed: $e')),
                  );
                }
              },
              child: const Text('Upload'),
            ),
          ],
        ),
      ),
    );
  }

}

class SubjectPage extends StatelessWidget {
  final int standard;
  final String subject;

  const SubjectPage({
    super.key,
    required this.standard,
    required this.subject,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(subject),
        leading: const BackButton(),
      ),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          Text(
            'Standard $standard • $subject',
            style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 18),
          const _Chapter(title: 'Chapter 1', subtitle: 'Introduction and basics'),
          const _Chapter(title: 'Chapter 2', subtitle: 'Important concepts'),
          const _Chapter(title: 'Chapter 3', subtitle: 'Examples and practice'),
        ],
      ),
    );
  }
}

/* ---------------- PRACTICE ---------------- */

class PracticePage extends StatefulWidget {
  final int standard;
  const PracticePage({super.key, required this.standard});
  @override
  State<PracticePage> createState() => _PracticePageState();
}

class _PracticePageState extends State<PracticePage> {
  bool loading = true;
  String? error;
  List<QuizData> quizzes = [];
  int selectedQuiz = 0;
  int question = 0;
  final List<int> answers = [];
  bool submitting = false;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try {
      final data = await ApiService.fetchQuizzes(standard: widget.standard);
      if (!mounted) return;
      setState(() { quizzes = data; loading = false; });
    } catch (e) {
      if (!mounted) return;
      setState(() { error = '$e'; loading = false; });
    }
  }

  Future<void> choose(int answer) async {
    final quiz = quizzes[selectedQuiz];
    answers.add(answer);
    if (question < quiz.questions.length - 1) {
      setState(() => question++);
      return;
    }
    setState(() => submitting = true);
    try {
      final result = await ApiService.submitQuiz(quizId: quiz.id, answers: answers);
      if (!mounted) return;
      await showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title: const Text('Quiz Complete!'),
          content: Text('You scored ${result['score']} / ${result['total_questions']} (${result['percentage']}%).\n\n${result['feedback']}'),
          actions: [FilledButton(onPressed: () => Navigator.pop(context), child: const Text('Done'))],
        ),
      );
      if (mounted) setState(() { question = 0; answers.clear(); submitting = false; });
    } catch (e) {
      if (!mounted) return;
      setState(() => submitting = false);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Quiz submission failed: $e')));
    }
  }

  @override
  Widget build(BuildContext context) {
    if (loading) return const Scaffold(body: Center(child: CircularProgressIndicator()));
    if (error != null) return Scaffold(appBar: AppBar(title: const Text('Practice & Quizzes'), leading: const BackButton()), body: Center(child: Padding(padding: const EdgeInsets.all(20), child: Text(error!))));
    if (quizzes.isEmpty) return Scaffold(appBar: AppBar(title: const Text('Practice & Quizzes'), leading: const BackButton()), body: const Center(child: Text('No quizzes are available for this standard yet.')));
    final quiz = quizzes[selectedQuiz];
    if (quiz.questions.isEmpty) return Scaffold(appBar: AppBar(title: Text(quiz.title), leading: const BackButton()), body: const Center(child: Text('This quiz has no questions yet.')));
    final q = quiz.questions[question];
    return Scaffold(
      appBar: AppBar(title: Text(quiz.title), leading: const BackButton()),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('${quiz.subject} • Question ${question + 1} of ${quiz.questions.length}', style: const TextStyle(color: Colors.grey)),
          const SizedBox(height: 18),
          Text(q.question, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 25),
          ...List.generate(q.options.length, (i) => Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: SizedBox(width: double.infinity, child: OutlinedButton(onPressed: submitting ? null : () => choose(i), child: Padding(padding: const EdgeInsets.all(14), child: Text(q.options[i])))),
          )),
          if (submitting) const Center(child: Padding(padding: EdgeInsets.all(12), child: CircularProgressIndicator())),
        ]),
      ),
    );
  }
}

/* ---------------- ATTENDANCE ---------------- */

class AttendancePage extends StatefulWidget {
  final int standard;
  const AttendancePage({super.key, required this.standard});
  @override
  State<AttendancePage> createState() => _AttendancePageState();
}

class _AttendancePageState extends State<AttendancePage> {
  DateTime date = DateTime.now();
  List<AttendanceStudent> students = [];
  bool loading = true;
  bool saving = false;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() => loading = true);
    try {
      final data = await ApiService.fetchAttendance(standard: widget.standard, date: date);
      if (!mounted) return;
      setState(() { students = data; loading = false; });
    } catch (e) {
      if (!mounted) return;
      setState(() => loading = false);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Could not load attendance: $e')));
    }
  }

  Future<void> _pickDate() async {
    final d = await showDatePicker(context: context, initialDate: date, firstDate: DateTime(2025), lastDate: DateTime(2030));
    if (d != null) { setState(() => date = d); await _load(); }
  }

  Future<void> _save() async {
    setState(() => saving = true);
    try {
      await ApiService.saveAttendance(standard: widget.standard, date: date, students: students);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Attendance saved to the backend.')));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Attendance save failed: $e')));
    } finally { if (mounted) setState(() => saving = false); }
  }

  @override
  Widget build(BuildContext context) {
    final count = students.where((s) => s.present).length;
    return Scaffold(
      appBar: AppBar(title: const Text('Daily Attendance'), leading: const BackButton()),
      body: loading ? const Center(child: CircularProgressIndicator()) : ListView(padding: const EdgeInsets.all(18), children: [
        Card(child: ListTile(leading: const Icon(Icons.calendar_month), title: Text('${date.day}/${date.month}/${date.year}', style: const TextStyle(fontWeight: FontWeight.bold)), subtitle: const Text('Select attendance date'), trailing: IconButton(icon: const Icon(Icons.edit_calendar), onPressed: _pickDate))),
        const SizedBox(height: 10),
        Text('$count / ${students.length} present', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 10),
        ...students.map((s) => Card(child: SwitchListTile(title: Text(s.name), subtitle: Text(s.present ? 'Present' : 'Absent'), value: s.present, onChanged: (v) => setState(() => s.present = v)))),
        const SizedBox(height: 12),
        FilledButton.icon(onPressed: saving ? null : _save, icon: saving ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.save), label: Text(saving ? 'Saving...' : 'Save Attendance')),
      ]),
    );
  }
}

/* ---------------- PROGRESS / PERFORMANCE ---------------- */

class StudentProgressPage extends StatefulWidget {
  final int standard;
  const StudentProgressPage({super.key, required this.standard});
  @override
  State<StudentProgressPage> createState() => _StudentProgressPageState();
}

class _StudentProgressPageState extends State<StudentProgressPage> {
  bool loading = true;
  List<ProgressItem> items = [];
  @override
  void initState() { super.initState(); _load(); }
  Future<void> _load() async {
    try {
      final data = await ApiService.fetchProgress(standard: widget.standard);
      if (!mounted) return;
      setState(() { items = data; loading = false; });
    } catch (e) {
      if (!mounted) return;
      setState(() => loading = false);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Could not load progress: $e')));
    }
  }
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('My Progress'), leading: Navigator.canPop(context) ? const BackButton() : null),
    body: loading ? const Center(child: CircularProgressIndicator()) : RefreshIndicator(
      onRefresh: _load,
      child: ListView(padding: const EdgeInsets.all(18), children: items.map((p) => _Progress(subject: p.subject, value: p.value)).toList()),
    ),
  );
}

class TeacherPerformancePage extends StatefulWidget {
  final int standard;
  const TeacherPerformancePage({super.key, required this.standard});
  @override
  State<TeacherPerformancePage> createState() => _TeacherPerformancePageState();
}

class _TeacherPerformancePageState extends State<TeacherPerformancePage> {
  bool loading = true;
  List<PerformanceItem> students = [];
  @override
  void initState() { super.initState(); _load(); }
  Future<void> _load() async {
    try {
      final data = await ApiService.fetchPerformance(standard: widget.standard);
      if (!mounted) return;
      setState(() { students = data; loading = false; });
    } catch (e) {
      if (!mounted) return;
      setState(() => loading = false);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Could not load performance: $e')));
    }
  }
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Student Performance'), leading: Navigator.canPop(context) ? const BackButton() : null),
    body: loading ? const Center(child: CircularProgressIndicator()) : RefreshIndicator(
      onRefresh: _load,
      child: ListView(padding: const EdgeInsets.all(18), children: students.map((s) => _Performance(name: s.name, progress: s.progress)).toList()),
    ),
  );
}

/* ---------------- PROFILE ---------------- */

class ProfilePage extends StatelessWidget {
  final String name;
  final UserRole role;
  final int standard;
  final VoidCallback onLogout;

  const ProfilePage({
    super.key,
    required this.name,
    required this.role,
    required this.standard,
    required this.onLogout,
  });

  @override
  Widget build(BuildContext context) {
    final teacher = role == UserRole.teacher;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
        leading: Navigator.canPop(context) ? const BackButton() : null,
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          CircleAvatar(
            radius: 42,
            child: Icon(teacher ? Icons.co_present : Icons.person, size: 42),
          ),
          const SizedBox(height: 12),
          Center(
            child: Text(name,
                style: const TextStyle(fontSize: 23, fontWeight: FontWeight.bold)),
          ),
          Center(
            child: Text(teacher ? 'Teacher' : 'Student • Standard $standard',
                style: const TextStyle(color: Colors.grey)),
          ),
          const SizedBox(height: 25),
          const Card(
            child: ListTile(
              leading: Icon(Icons.school_outlined),
              title: Text('EduReach'),
              subtitle: Text('Technology-enabled education'),
            ),
          ),
          const SizedBox(height: 10),
          Card(
            child: ListTile(
              leading: const Icon(Icons.logout),
              title: const Text('Logout'),
              onTap: onLogout,
            ),
          ),
        ],
      ),
    );
  }
}

/* ---------------- SMALL WIDGETS ---------------- */

Color _pastelFor(String label) {
  switch (label.toLowerCase()) {
    case 'attendance':
      return mint;
    case 'notes':
    case 'upload notes':
      return softBlue;
    case 'progress':
    case 'student performance':
      return lavender;
    case 'assignments':
      return peach;
    case 'announcements':
      return yellow;
    case 'practice':
    case 'practice & quizzes':
      return pink;
    case 'english':
      return softBlue;
    case 'mathematics':
      return lavender;
    case 'science':
      return mint;
    case 'social science':
      return peach;
    case 'hindi':
      return pink;
    case 'marathi':
      return teal;
    default:
      return softBlue;
  }
}

Widget _top(String title, String subtitle) => Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title,
            style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
        const SizedBox(height: 4),
        Text(subtitle, style: const TextStyle(color: Colors.grey)),
      ],
    );

Widget _hero(String title, String subtitle, String trailing, IconData icon) =>
    Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        gradient: const LinearGradient(
          colors: [softBlue, lavender],
        ),
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 28,
            backgroundColor: Colors.white70,
            child: Icon(icon, color: navy, size: 30),
          ),
          const SizedBox(width: 15),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: const TextStyle(
                        color: navy,
                        fontSize: 19,
                        fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Text(subtitle,
                    style: const TextStyle(color: navy)),
                const SizedBox(height: 8),
                Text(trailing,
                    style: const TextStyle(
                        color: navy, fontWeight: FontWeight.w600)),
              ],
            ),
          ),
        ],
      ),
    );

class _Stat extends StatelessWidget {
  final String title, value;
  final IconData icon;
  const _Stat({required this.title, required this.value, required this.icon});

  @override
  Widget build(BuildContext context) => Card(
        child: Padding(
          padding: const EdgeInsets.all(13),
          child: Column(
            children: [
              CircleAvatar(
                radius: 20,
                backgroundColor: _pastelFor(title).withOpacity(.55),
                child: Icon(icon, size: 25, color: navy),
              ),
              const SizedBox(height: 8),
              Text(value,
                  style: const TextStyle(
                      fontSize: 19, fontWeight: FontWeight.bold)),
              Text(title,
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 12, color: Colors.grey)),
            ],
          ),
        ),
      );
}

class _Lesson extends StatelessWidget {
  final String subject, topic;
  final IconData icon;
  const _Lesson({required this.subject, required this.topic, required this.icon});

  @override
  Widget build(BuildContext context) => Card(
        child: ListTile(
          leading: CircleAvatar(
            backgroundColor: _pastelFor(subject).withOpacity(.55),
            child: Icon(icon, color: navy),
          ),
          title: Text(subject),
          subtitle: Text(topic),
          trailing: const Icon(Icons.chevron_right),
        ),
      );
}

class _NoteCard extends StatelessWidget {
  final StudyNote note;
  const _NoteCard({required this.note});

  Future<void> _openPdf(BuildContext context) async {
    final url = note.pdfUrl;
    if (url == null || url.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('This note does not have a PDF yet.')),
      );
      return;
    }
    final uri = Uri.tryParse(url);
    if (uri == null || !await launchUrl(uri, mode: LaunchMode.platformDefault)) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Could not open the PDF.')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) => Card(
        child: ListTile(
          onTap: note.pdfUrl == null ? null : () => _openPdf(context),
          leading: CircleAvatar(
            backgroundColor: softBlue.withOpacity(.55),
            child: const Icon(Icons.picture_as_pdf_rounded, color: navy),
          ),
          title: Text(note.title),
          subtitle: Text('${note.subject} • ${note.teacher}\n${note.content}'),
          isThreeLine: true,
          trailing: note.pdfUrl == null
              ? null
              : IconButton(
                  tooltip: 'View PDF',
                  icon: const Icon(Icons.open_in_new_rounded, color: skyBlue),
                  onPressed: () => _openPdf(context),
                ),
        ),
      );
}

class _ToolCard extends StatelessWidget {
  final String title;
  final IconData icon;
  final VoidCallback? onTap;

  const _ToolCard({required this.title, required this.icon, this.onTap});

  @override
  Widget build(BuildContext context) => Card(
        child: InkWell(
          borderRadius: BorderRadius.circular(12),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              children: [
                CircleAvatar(
                  radius: 25,
                  backgroundColor: _pastelFor(title).withOpacity(.65),
                  child: Icon(icon, size: 30, color: navy),
                ),
                const SizedBox(height: 8),
                Text(title, textAlign: TextAlign.center,
                    style: const TextStyle(fontWeight: FontWeight.w600)),
              ],
            ),
          ),
        ),
      );
}

class _Chapter extends StatelessWidget {
  final String title, subtitle;
  const _Chapter({required this.title, required this.subtitle});

  @override
  Widget build(BuildContext context) => Card(
        child: ListTile(
          leading: CircleAvatar(
            backgroundColor: lavender.withOpacity(.55),
            child: const Icon(Icons.play_arrow, color: navy),
          ),
          title: Text(title),
          subtitle: Text(subtitle),
          trailing: const Icon(Icons.chevron_right),
        ),
      );
}

class _Progress extends StatelessWidget {
  final String subject;
  final double value;
  const _Progress({required this.subject, required this.value});

  @override
  Widget build(BuildContext context) => Card(
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(subject, style: const TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 10),
              LinearProgressIndicator(value: value),
              const SizedBox(height: 6),
              Text('${(value * 100).round()}% completed'),
            ],
          ),
        ),
      );
}

class _Performance extends StatelessWidget {
  final String name, progress;
  const _Performance({required this.name, required this.progress});

  @override
  Widget build(BuildContext context) => Card(
        child: ListTile(
          leading: CircleAvatar(
            backgroundColor: mint.withOpacity(.55),
            child: const Icon(Icons.person, color: navy),
          ),
          title: Text(name),
          subtitle: const Text('Overall learning progress'),
          trailing: Text(progress,
              style: const TextStyle(fontWeight: FontWeight.bold)),
        ),
      );
}
