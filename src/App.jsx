import { useEffect, useMemo, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
    ArrowUpRight,
    BarChart3,
    BookOpenCheck,
    Calculator,
    CalendarCheck,
    CalendarPlus,
    Check,
    CheckCircle2,
    Clipboard,
    Circle,
    FilePenLine,
    GraduationCap,
    Home,
    ImagePlus,
    Landmark,
    LayoutDashboard,
    Leaf,
    ListChecks,
    ListTodo,
    LogIn,
    LogOut,
    MessageCircle,
    Plus,
    Send,
    ShieldCheck,
    Sparkles,
    Trash2,
    X,
} from 'lucide-react';
import './styles.css';

const navItems = [
            { id: 'dashboard', label: 'Dashboard', icon: 'layout-dashboard' },
            { id: 'ai-tutor', label: 'AI Tutor', icon: 'sparkles' },
            { id: 'tasks', label: 'Tasks', icon: 'list-checks' },
            { id: 'assignments', label: 'Assignments', icon: 'calendar-check' },
        ];

        const statusClass = {
            Pending: 'badge-pending',
            'In Progress': 'badge-progress',
            Completed: 'badge-completed',
            Overdue: 'badge-overdue',
        };

const icons = {
    'arrow-up-right': ArrowUpRight,
    'bar-chart-3': BarChart3,
    'book-open-check': BookOpenCheck,
    calculator: Calculator,
    'calendar-check': CalendarCheck,
    'calendar-plus': CalendarPlus,
    check: Check,
    'check-circle-2': CheckCircle2,
    clipboard: Clipboard,
    'file-pen-line': FilePenLine,
    'graduation-cap': GraduationCap,
    home: Home,
    'image-plus': ImagePlus,
    landmark: Landmark,
    'layout-dashboard': LayoutDashboard,
    leaf: Leaf,
    'list-checks': ListChecks,
    'list-todo': ListTodo,
    'log-in': LogIn,
    'log-out': LogOut,
    'message-circle': MessageCircle,
    plus: Plus,
    send: Send,
    'shield-check': ShieldCheck,
    sparkles: Sparkles,
    'trash-2': Trash2,
    x: X,
};

function Icon({ name, size = 18 }) {
    const Component = icons[name] || Circle;
    return <Component size={size} strokeWidth={2} aria-hidden="true" />;
}

function useLucide() {}

function MessageContent({ text, sender }) {
    if (sender === 'user') {
        return <span className="message-text">{text}</span>;
    }

    return (
        <div className="message-content">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {text}
            </ReactMarkdown>
        </div>
    );
}

function ChatMessage({ message, index }) {
    const [copied, setCopied] = useState(false);
    const isUser = message.sender === 'user';

    const copyMessage = async () => {
        try {
            await navigator.clipboard.writeText(message.text || '');
            setCopied(true);
            window.setTimeout(() => setCopied(false), 1400);
        } catch (error) {
            setCopied(false);
        }
    };

    return (
        <div key={`${message.timestamp || index}-${index}`} className={`message ${isUser ? 'message-user' : 'message-ai'}`}>
            <div className="message-topline">
                <span className="message-meta">{isUser ? 'You' : 'Tutorly'}</span>
                {!isUser && (
                    <button className="message-copy" onClick={copyMessage} title="Copy response" aria-label="Copy response">
                        <Icon name="clipboard" size={14} />
                        {copied ? 'Copied' : 'Copy'}
                    </button>
                )}
            </div>
            <MessageContent text={message.text} sender={message.sender} />
            {message.imagePreview && <img src={message.imagePreview} alt="Uploaded preview" className="image-preview" />}
        </div>
    );
}

        function formatDate(value) {
            if (!value) return 'No date';
            const date = new Date(`${value}T00:00:00`);
            if (Number.isNaN(date.getTime())) return value;
            return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
        }

        function getDueValue(assignment) {
            return assignment.due || assignment.due_date || assignment.dueDate || '';
        }

        function getInitials(name) {
            return (name || 'Student')
                .split(' ')
                .filter(Boolean)
                .slice(0, 2)
                .map((part) => part[0])
                .join('')
                .toUpperCase() || 'ST';
        }

        class APIService {
            constructor(baseUrl) {
                this.baseUrl = baseUrl || '/api';
            }

            async request(endpoint, options = {}) {
                const response = await fetch(`${this.baseUrl}${endpoint}`, {
                    headers: {
                        'Content-Type': 'application/json',
                        ...options.headers,
                    },
                    ...options,
                });

                if (!response.ok) {
                    throw new Error(`API Error: ${response.status}`);
                }

                return response.status === 204 ? null : response.json();
            }

            login(credentials) {
                return this.request('/auth/login', {
                    method: 'POST',
                    body: JSON.stringify(credentials),
                });
            }

            getAssignments(userId) {
                return this.request(`/assignments/${userId}`);
            }

            createAssignment(userId, assignment) {
                return this.request(`/assignments/${userId}`, {
                    method: 'POST',
                    body: JSON.stringify(assignment),
                });
            }

            deleteAssignment(assignmentId) {
                return this.request(`/assignments/${assignmentId}`, { method: 'DELETE' });
            }

            getProgress(userId) {
                return this.request(`/progress/${userId}`);
            }

            getChatHistory(userId) {
                return this.request(`/chat/${userId}`);
            }

            async sendImageMessage(userId, formData) {
                const response = await fetch(`${this.baseUrl}/chat/${userId}/ai/image`, {
                    method: 'POST',
                    body: formData,
                });

                if (!response.ok) {
                    throw new Error(`API Error: ${response.status}`);
                }

                return response.json();
            }
        }

        function Auth({ onLogin }) {
            const [name, setName] = useState('');
            const [id, setId] = useState('');
            const [message, setMessage] = useState('');
            const [isLoading, setIsLoading] = useState(false);
            const apiService = useMemo(() => new APIService(), []);
            useLucide([isLoading, message]);

            const login = async () => {
                if (!name.trim() || !id.trim()) {
                    setMessage('Enter both your name and student ID.');
                    return;
                }

                setIsLoading(true);
                setMessage('');

                try {
                    const response = await apiService.login({ name: name.trim(), studentId: id.trim() });
                    onLogin(response.name || name.trim(), response.studentId || id.trim());
                } catch (error) {
                    onLogin(name.trim(), id.trim());
                } finally {
                    setIsLoading(false);
                }
            };

            return (
                <div className="auth-page">
                    <section className="auth-visual">
                        <div className="auth-brand brand-mark">
                            <img className="brand-logo" src="/static/logo.png" alt="Tutorly logo" />
                            <span>Tutorly</span>
                        </div>
                        <div className="auth-copy">
                            <h1>A focused study command center.</h1>
                            <p>Plan assignments, track progress, manage your study queue, and get AI tutoring support in one calm workspace.</p>
                            <div className="auth-snapshot" aria-hidden="true">
                                <div className="snapshot-item">
                                    <span className="snapshot-value">AI</span>
                                    <span className="snapshot-label">Homework explanations and image help</span>
                                </div>
                                <div className="snapshot-item">
                                    <span className="snapshot-value">4</span>
                                    <span className="snapshot-label">Core study tools in one dashboard</span>
                                </div>
                                <div className="snapshot-item">
                                    <span className="snapshot-value">24/7</span>
                                    <span className="snapshot-label">A study flow that stays ready</span>
                                </div>
                            </div>
                        </div>
                    </section>

                    <main className="auth-panel-wrap">
                        <div className="auth-panel">
                            <div className="eyebrow"><Icon name="graduation-cap" /> Student workspace</div>
                            <h2>Start your session</h2>
                            <p>Use any student name and ID. Tutorly will connect to the local backend when it is available.</p>
                            <div className="field">
                                <label htmlFor="student-name">Student name</label>
                                <input
                                    id="student-name"
                                    type="text"
                                    placeholder="Ava Chen"
                                    value={name}
                                    onChange={(event) => setName(event.target.value)}
                                    onKeyDown={(event) => event.key === 'Enter' && login()}
                                />
                            </div>
                            <div className="field">
                                <label htmlFor="student-id">Student ID</label>
                                <input
                                    id="student-id"
                                    type="text"
                                    placeholder="STU-1024"
                                    value={id}
                                    onChange={(event) => setId(event.target.value)}
                                    onKeyDown={(event) => event.key === 'Enter' && login()}
                                />
                            </div>
                            <button className="btn btn-primary btn-wide" onClick={login} disabled={isLoading}>
                                <Icon name="log-in" />
                                {isLoading ? 'Starting...' : 'Enter Tutorly'}
                            </button>
                            {message && <p className="error-message" role="alert">{message}</p>}
                        </div>
                    </main>
                </div>
            );
        }

        function AppShell({ children, currentPage, setCurrentPage, studentName, studentId, onLogout }) {
            useLucide([currentPage, studentName]);
            const current = navItems.find((item) => item.id === currentPage) || navItems[0];

            return (
                <div className="app-shell">
                    <aside className="sidebar">
                        <div className="brand-mark">
                            <img className="brand-logo" src="/static/logo.png" alt="Tutorly logo" />
                            <span>Tutorly</span>
                        </div>
                        <nav className="nav-stack" aria-label="Main navigation">
                            {navItems.map((item) => (
                                <button
                                    key={item.id}
                                    className={`nav-item ${currentPage === item.id ? 'active' : ''}`}
                                    onClick={() => setCurrentPage(item.id)}
                                >
                                    <Icon name={item.icon} />
                                    {item.label}
                                </button>
                            ))}
                        </nav>
                        <div className="student-card">
                            <div className="student-meta">
                                <div className="avatar">{getInitials(studentName)}</div>
                                <div>
                                    <div className="student-name">{studentName}</div>
                                    <div className="student-id">{studentId}</div>
                                </div>
                            </div>
                            <button className="btn btn-ghost btn-wide" onClick={onLogout}>
                                <Icon name="log-out" />
                                Sign out
                            </button>
                        </div>
                    </aside>

                    <main className="workspace">
                        <header className="topbar">
                            <div className="page-title">
                                <h1>{current.label}</h1>
                                <p>{currentPage === 'dashboard' ? `Welcome back, ${studentName}.` : 'Everything is organized for a smoother study session.'}</p>
                            </div>
                            <div className="topbar-actions">
                                <button className="btn btn-ghost mobile-menu" onClick={() => setCurrentPage('dashboard')}>
                                    <Icon name="home" />
                                    Home
                                </button>
                                <button className="btn btn-primary" onClick={() => setCurrentPage('ai-tutor')}>
                                    <Icon name="sparkles" />
                                    Ask Tutorly
                                </button>
                            </div>
                        </header>

                        <div className="content">{children}</div>
                    </main>

                    <nav className="mobile-nav" aria-label="Mobile navigation">
                        {navItems.map((item) => (
                            <button
                                key={item.id}
                                className={currentPage === item.id ? 'active' : ''}
                                onClick={() => setCurrentPage(item.id)}
                                title={item.label}
                                aria-label={item.label}
                            >
                                <Icon name={item.icon} />
                            </button>
                        ))}
                    </nav>
                </div>
            );
        }

        function Dashboard({ studentName, studentId, setCurrentPage, assignments, tasks }) {
            const [progress, setProgress] = useState(null);
            const apiService = useMemo(() => new APIService(), []);
            useLucide([progress, assignments.length, tasks.length]);

            useEffect(() => {
                if (!studentId) return;
                apiService.getProgress(studentId)
                    .then(setProgress)
                    .catch(() => setProgress(null));
            }, [studentId]);

            const completedAssignments = assignments.filter((item) => item.status === 'Completed').length;
            const pendingTasks = tasks.filter((task) => !task.done).length;
            const overdueAssignments = assignments.filter((item) => item.status === 'Overdue').length;
            const avgScore = Math.round(
                assignments
                    .map((item) => Number(item.score))
                    .filter((score) => Number.isFinite(score))
                    .reduce((sum, score, _, list) => sum + score / list.length, 0)
            ) || 0;
            const subjects = progress?.subjectPerformance?.length
                ? progress.subjectPerformance
                : summarizeSubjects(assignments);
            const upcoming = [...assignments]
                .sort((a, b) => new Date(getDueValue(a)) - new Date(getDueValue(b)))
                .slice(0, 4);

            return (
                <div className="dashboard-grid">
                    <section>
                        <div className="hero-panel">
                            <div className="hero-copy">
                                <div className="eyebrow"><Icon name="book-open-check" /> Today in Tutorly</div>
                                <h2>Turn scattered schoolwork into a clear next step.</h2>
                                <p>Your assignments, study tasks, progress signals, and AI tutor live together so you can move through the day without hunting for context.</p>
                                <div className="hero-actions">
                                    <button className="btn btn-primary" onClick={() => setCurrentPage('ai-tutor')}>
                                        <Icon name="message-circle" />
                                        Open AI tutor
                                    </button>
                                    <button className="btn btn-ghost" onClick={() => setCurrentPage('assignments')}>
                                        <Icon name="calendar-plus" />
                                        Add assignment
                                    </button>
                                </div>
                            </div>
                            <div className="hero-art" aria-hidden="true"></div>
                        </div>

                        <div className="stats-row">
                            <StatCard icon="calendar-check" value={assignments.length} label="Assignments" />
                            <StatCard icon="check-circle-2" value={completedAssignments} label="Completed" tone="green" />
                            <StatCard icon="list-todo" value={pendingTasks} label="Open tasks" tone="amber" />
                            <StatCard icon="bar-chart-3" value={avgScore ? `${avgScore}%` : 'New'} label="Average score" tone="indigo" />
                        </div>

                        <div className="work-panel" style={{ marginTop: 20 }}>
                            <div className="panel-header">
                                <div className="panel-title">
                                    <h2>Subject momentum</h2>
                                    <p>Scores and workload grouped by subject.</p>
                                </div>
                                <span className={`badge ${overdueAssignments ? 'badge-overdue' : 'badge-completed'}`}>
                                    {overdueAssignments ? `${overdueAssignments} overdue` : 'On track'}
                                </span>
                            </div>
                            <div className="panel-body">
                                {subjects.length ? (
                                    <div className="subject-list">
                                        {subjects.slice(0, 5).map((subject) => (
                                            <SubjectRow key={subject.subject} subject={subject} />
                                        ))}
                                    </div>
                                ) : (
                                    <div className="empty-state">Add assignments with scores to see subject momentum.</div>
                                )}
                            </div>
                        </div>
                    </section>

                    <aside className="insight-panel">
                        <div className="panel-header">
                            <div className="panel-title">
                                <h2>Upcoming work</h2>
                                <p>The next items needing attention.</p>
                            </div>
                            <button className="btn btn-ghost btn-icon" onClick={() => setCurrentPage('assignments')} title="Open assignments" aria-label="Open assignments">
                                <Icon name="arrow-up-right" />
                            </button>
                        </div>
                        <div className="panel-body">
                            {upcoming.length ? (
                                <div className="assignment-list">
                                    {upcoming.map((assignment) => (
                                        <AssignmentCard key={assignment.id || `${assignment.title}-${getDueValue(assignment)}`} assignment={assignment} />
                                    ))}
                                </div>
                            ) : (
                                <div className="empty-state">No assignments yet. Add one to start shaping the week.</div>
                            )}
                        </div>
                    </aside>
                </div>
            );
        }

        function StatCard({ icon, value, label, tone }) {
            const toneClass = tone === 'amber' ? 'icon-amber' : tone === 'indigo' ? 'icon-indigo' : tone === 'green' ? 'icon-green' : '';
            return (
                <div className="stat-card">
                    <span className={`icon-chip ${toneClass}`}><Icon name={icon} /></span>
                    <span className="stat-value">{value}</span>
                    <span className="stat-label">{label}</span>
                </div>
            );
        }

        function SubjectRow({ subject }) {
            const score = Math.max(0, Math.min(100, Math.round(subject.avg_score || subject.score || 0)));
            return (
                <div className="subject-item">
                    <div className="subject-row">
                        <div>
                            <div className="subject-name">{subject.subject}</div>
                            <div className="subject-meta">{subject.total_assignments || subject.count || 1} assignments tracked</div>
                        </div>
                        <strong>{score}%</strong>
                    </div>
                    <div className="progress-track" aria-hidden="true">
                        <div className="progress-bar" style={{ width: `${score}%` }}></div>
                    </div>
                </div>
            );
        }

        function AssignmentCard({ assignment }) {
            const due = getDueValue(assignment);
            return (
                <div className="assignment-card">
                    <div>
                        <div className="assignment-title">{assignment.title}</div>
                        <div className="assignment-meta">{assignment.subject} · Due {formatDate(due)}</div>
                    </div>
                    <span className={`badge ${statusClass[assignment.status] || 'badge-pending'}`}>{assignment.status || 'Pending'}</span>
                </div>
            );
        }

        function summarizeSubjects(assignments) {
            const map = new Map();
            assignments.forEach((assignment) => {
                const score = Number(assignment.score);
                const entry = map.get(assignment.subject) || { subject: assignment.subject || 'General', total: 0, count: 0, total_assignments: 0 };
                entry.total_assignments += 1;
                if (Number.isFinite(score)) {
                    entry.total += score;
                    entry.count += 1;
                }
                map.set(entry.subject, entry);
            });

            return [...map.values()].map((entry) => ({
                subject: entry.subject,
                total_assignments: entry.total_assignments,
                avg_score: entry.count ? entry.total / entry.count : 0,
            }));
        }

        function ChatbotPage({ studentId }) {
            const quickActions = [
                { icon: 'calculator', text: 'Help me solve this math problem' },
                { icon: 'leaf', text: 'Explain photosynthesis' },
                { icon: 'file-pen-line', text: 'Review my essay for grammar' },
                { icon: 'landmark', text: 'Teach me about the Civil War' },
            ];
            const [chatMessages, setChatMessages] = useState([]);
            const [input, setInput] = useState('');
            const [isLoading, setIsLoading] = useState(false);
            const [error, setError] = useState('');
            const [selectedImage, setSelectedImage] = useState(null);
            const [imagePreview, setImagePreview] = useState('');
            const messagesRef = useRef(null);
            const apiService = useMemo(() => new APIService(), []);
            useLucide([chatMessages.length, isLoading, imagePreview, error]);

            useEffect(() => {
                if (!studentId) return;
                apiService.getChatHistory(studentId)
                    .then((history) => {
                        setChatMessages((history || []).map((item) => ({
                            sender: item.sender,
                            text: item.text || item.message || '',
                            timestamp: item.timestamp,
                        })));
                    })
                    .catch(() => setChatMessages([]));
            }, [studentId]);

            useEffect(() => {
                if (messagesRef.current) {
                    messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
                }
            }, [chatMessages, isLoading]);

            const handleImageChange = (event) => {
                const file = event.target.files && event.target.files[0];
                if (!file) return;
                setSelectedImage(file);
                const reader = new FileReader();
                reader.onload = () => setImagePreview(reader.result);
                reader.readAsDataURL(file);
            };

            const clearImage = () => {
                setSelectedImage(null);
                setImagePreview('');
            };

            const sendMessage = async () => {
                if ((!input.trim() && !selectedImage) || isLoading) return;
                if (selectedImage) {
                    await sendImage();
                    return;
                }

                const messageText = input.trim();
                const userMessage = { sender: 'user', text: messageText, timestamp: new Date().toISOString() };
                setChatMessages((messages) => [...messages, userMessage]);
                setInput('');
                setIsLoading(true);
                setError('');

                try {
                    const result = await apiService.request(`/chat/${studentId}/ai`, {
                        method: 'POST',
                        body: JSON.stringify({ message: messageText }),
                    });
                    setChatMessages((messages) => [...messages, {
                        sender: 'ai',
                        text: result.response,
                        timestamp: result.timestamp || new Date().toISOString(),
                    }]);
                } catch (err) {
                    setError('Tutorly could not reach the AI service. Check your Gemini API key in .env.');
                } finally {
                    setIsLoading(false);
                }
            };

            const sendImage = async () => {
                if (!selectedImage || isLoading) return;
                const messageText = input.trim() || 'Please help me understand this image.';
                setChatMessages((messages) => [...messages, {
                    sender: 'user',
                    text: messageText,
                    timestamp: new Date().toISOString(),
                    imagePreview,
                }]);
                setInput('');
                setIsLoading(true);
                setError('');

                try {
                    const formData = new FormData();
                    formData.append('image', selectedImage);
                    formData.append('message', messageText);
                    const result = await apiService.sendImageMessage(studentId, formData);
                    setChatMessages((messages) => [...messages, {
                        sender: 'ai',
                        text: result.response || 'I reviewed the image. Tell me which part you want to focus on.',
                        timestamp: new Date().toISOString(),
                    }]);
                    clearImage();
                } catch (err) {
                    setError('Tutorly could not process the image. Check your Gemini API key and try again.');
                } finally {
                    setIsLoading(false);
                }
            };

            return (
                <div className="tutor-layout">
                    <aside className="quick-panel">
                        <div className="panel-header">
                            <div className="panel-title">
                                <h2>Study prompts</h2>
                                <p>Tap one, then tune it to your question.</p>
                            </div>
                        </div>
                        <div className="panel-body">
                            <div className="quick-grid">
                                {quickActions.map((action) => (
                                    <button className="quick-action-btn" key={action.text} onClick={() => setInput(action.text)}>
                                        <span className="icon-chip"><Icon name={action.icon} /></span>
                                        <span>{action.text}</span>
                                    </button>
                                ))}
                            </div>
                        </div>
                    </aside>

                    <section className="chat-panel">
                        <div className="panel-header">
                            <div className="panel-title">
                                <h2>AI tutor</h2>
                                <p>Ask for explanations, examples, feedback, or image-based help.</p>
                            </div>
                            <span className="badge badge-completed"><Icon name="shield-check" size={14} /> Study mode</span>
                        </div>

                        {error && <div className="error-message" style={{ margin: 16 }}>{error}</div>}

                        <div className="chat-messages" ref={messagesRef}>
                            {chatMessages.length === 0 ? (
                                <div className="empty-state">
                                    <div>
                                        <strong>Start with a question.</strong>
                                        <p style={{ margin: '8px 0 0' }}>Tutorly can explain concepts, check reasoning, or help interpret an uploaded image.</p>
                                    </div>
                                </div>
                            ) : (
                                chatMessages.map((message, index) => (
                                    <ChatMessage key={`${message.timestamp || index}-${index}`} message={message} index={index} />
                                ))
                            )}
                            {isLoading && (
                                <div className="message message-ai">
                                    <span className="message-meta">Tutorly</span>
                                    <span>Thinking through it...</span>
                                </div>
                            )}
                        </div>

                        <div className="composer">
                            {imagePreview && (
                                <div className="composer-preview">
                                    <img src={imagePreview} alt="Selected upload preview" className="image-preview" />
                                    <button className="btn btn-danger btn-icon" onClick={clearImage} title="Remove image" aria-label="Remove image">
                                        <Icon name="x" />
                                    </button>
                                </div>
                            )}
                            <div className="composer-row">
                                <div className="image-upload-container">
                                    <button className="btn btn-ghost btn-icon" disabled={isLoading} title="Upload image" aria-label="Upload image">
                                        <Icon name="image-plus" />
                                    </button>
                                    <input className="image-upload-input" type="file" accept="image/*" onChange={handleImageChange} disabled={isLoading} />
                                </div>
                                <textarea
                                    value={input}
                                    onChange={(event) => setInput(event.target.value)}
                                    placeholder="Ask a study question..."
                                    rows="1"
                                    onKeyDown={(event) => {
                                        if (event.key === 'Enter' && !event.shiftKey) {
                                            event.preventDefault();
                                            sendMessage();
                                        }
                                    }}
                                    disabled={isLoading}
                                />
                                <button className="btn btn-primary" onClick={sendMessage} disabled={isLoading || (!input.trim() && !selectedImage)}>
                                    <Icon name="send" />
                                    Send
                                </button>
                            </div>
                        </div>
                    </section>
                </div>
            );
        }

        function TasksPage({ studentId, tasks, setTasks }) {
            const [input, setInput] = useState('');
            const [searchQuery, setSearchQuery] = useState('');
            const [filter, setFilter] = useState('all');
            useLucide([tasks.length, filter]);

            useEffect(() => {
                localStorage.setItem(`todos_${studentId}`, JSON.stringify(tasks));
            }, [tasks, studentId]);

            const addTask = () => {
                if (!input.trim()) return;
                setTasks((current) => [...current, {
                    id: Date.now(),
                    text: input.trim(),
                    done: false,
                    createdAt: new Date().toISOString(),
                }]);
                setInput('');
            };

            const toggleDone = (taskId) => {
                setTasks((current) => current.map((task) => task.id === taskId ? { ...task, done: !task.done } : task));
            };

            const deleteTask = (taskId) => {
                setTasks((current) => current.filter((task) => task.id !== taskId));
            };

            const filteredTasks = tasks.filter((task) => {
                const matchesSearch = task.text.toLowerCase().includes(searchQuery.toLowerCase());
                if (filter === 'pending') return matchesSearch && !task.done;
                if (filter === 'done') return matchesSearch && task.done;
                return matchesSearch;
            });

            return (
                <div className="board-layout">
                    <section className="form-panel">
                        <div className="panel-header">
                            <div className="panel-title">
                                <h2>Task queue</h2>
                                <p>Capture small study actions before they turn into clutter.</p>
                            </div>
                        </div>
                        <div className="panel-body">
                            <div className="task-controls">
                                <input
                                    type="text"
                                    placeholder="Add a study task..."
                                    value={input}
                                    onChange={(event) => setInput(event.target.value)}
                                    onKeyDown={(event) => event.key === 'Enter' && addTask()}
                                />
                                <button className="btn btn-primary" onClick={addTask}>
                                    <Icon name="plus" />
                                    Add task
                                </button>
                            </div>
                        </div>
                    </section>

                    <section className="list-panel">
                        <div className="panel-header">
                            <div className="panel-title">
                                <h2>Tasks</h2>
                                <p>{filteredTasks.length} shown from {tasks.length} total.</p>
                            </div>
                            <div className="task-filter" aria-label="Task filters">
                                {[
                                    ['all', 'All'],
                                    ['pending', 'Open'],
                                    ['done', 'Done'],
                                ].map(([value, label]) => (
                                    <button key={value} className={filter === value ? 'active' : ''} onClick={() => setFilter(value)}>
                                        {label}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div className="panel-body">
                            <div style={{ marginBottom: 14 }}>
                                <input
                                    type="text"
                                    placeholder="Search tasks..."
                                    value={searchQuery}
                                    onChange={(event) => setSearchQuery(event.target.value)}
                                />
                            </div>
                            {filteredTasks.length ? (
                                <div className="task-list">
                                    {filteredTasks.map((task) => (
                                        <div key={task.id} className={`task-item ${task.done ? 'done' : ''}`}>
                                            <button className={`task-check ${task.done ? 'done' : ''}`} onClick={() => toggleDone(task.id)} title="Toggle complete" aria-label="Toggle complete">
                                                <Icon name="check" size={14} />
                                            </button>
                                            <span className="task-text">{task.text}</span>
                                            <button className="btn btn-danger btn-icon" onClick={() => deleteTask(task.id)} title="Delete task" aria-label="Delete task">
                                                <Icon name="trash-2" />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="empty-state">No tasks match this view.</div>
                            )}
                        </div>
                    </section>
                </div>
            );
        }

        function AssignmentsPage({ studentId, assignments, setAssignments }) {
            const [title, setTitle] = useState('');
            const [subject, setSubject] = useState('');
            const [due, setDue] = useState('');
            const [status, setStatus] = useState('Pending');
            const [difficulty, setDifficulty] = useState('Medium');
            const [score, setScore] = useState('');
            const [search, setSearch] = useState('');
            const [filterStatus, setFilterStatus] = useState('');
            const [isLoading, setIsLoading] = useState(false);
            const [error, setError] = useState('');
            const apiService = useMemo(() => new APIService(), []);
            useLucide([assignments.length, filterStatus, isLoading, error]);

            const addAssignment = async () => {
                if (!title.trim() || !subject.trim() || !due) {
                    setError('Title, subject, and due date are required.');
                    return;
                }

                const newAssignment = {
                    id: Date.now(),
                    title: title.trim(),
                    subject: subject.trim(),
                    due,
                    status,
                    difficulty,
                    score,
                    createdAt: new Date().toISOString(),
                };

                setIsLoading(true);
                setError('');

                try {
                    const saved = studentId ? await apiService.createAssignment(studentId, newAssignment) : newAssignment;
                    setAssignments((current) => [...current, saved]);
                    setTitle('');
                    setSubject('');
                    setDue('');
                    setStatus('Pending');
                    setDifficulty('Medium');
                    setScore('');
                } catch (err) {
                    setAssignments((current) => [...current, newAssignment]);
                    setError('Saved locally because the assignment API was not available.');
                    setTitle('');
                    setSubject('');
                    setDue('');
                    setStatus('Pending');
                    setDifficulty('Medium');
                    setScore('');
                } finally {
                    setIsLoading(false);
                }
            };

            const removeAssignment = async (assignment) => {
                setAssignments((current) => current.filter((item) => item !== assignment));
                if (!assignment.id) return;

                try {
                    await apiService.deleteAssignment(assignment.id);
                } catch (err) {
                    localStorage.setItem(`assignments_${studentId}`, JSON.stringify(assignments.filter((item) => item !== assignment)));
                }
            };

            const filteredAssignments = assignments.filter((assignment) => {
                const titleMatch = (assignment.title || '').toLowerCase().includes(search.toLowerCase());
                const subjectMatch = (assignment.subject || '').toLowerCase().includes(search.toLowerCase());
                const statusMatch = !filterStatus || assignment.status === filterStatus;
                return (titleMatch || subjectMatch) && statusMatch;
            });

            return (
                <div className="board-layout">
                    <section className="form-panel">
                        <div className="panel-header">
                            <div className="panel-title">
                                <h2>New assignment</h2>
                                <p>Keep every due date visible before it becomes urgent.</p>
                            </div>
                        </div>
                        <div className="panel-body">
                            {error && <div className="error-message" style={{ marginBottom: 14 }}>{error}</div>}
                            <div className="form-grid">
                                <div className="field" style={{ margin: 0 }}>
                                    <label htmlFor="assignment-title">Title</label>
                                    <input id="assignment-title" type="text" placeholder="Research outline" value={title} onChange={(event) => setTitle(event.target.value)} />
                                </div>
                                <div className="field" style={{ margin: 0 }}>
                                    <label htmlFor="assignment-subject">Subject</label>
                                    <input id="assignment-subject" type="text" placeholder="Biology" value={subject} onChange={(event) => setSubject(event.target.value)} />
                                </div>
                                <div className="field" style={{ margin: 0 }}>
                                    <label htmlFor="assignment-due">Due date</label>
                                    <input id="assignment-due" type="date" value={due} onChange={(event) => setDue(event.target.value)} />
                                </div>
                                <div className="field" style={{ margin: 0 }}>
                                    <label htmlFor="assignment-status">Status</label>
                                    <select id="assignment-status" value={status} onChange={(event) => setStatus(event.target.value)}>
                                        <option>Pending</option>
                                        <option>In Progress</option>
                                        <option>Completed</option>
                                        <option>Overdue</option>
                                    </select>
                                </div>
                                <div className="field" style={{ margin: 0 }}>
                                    <label htmlFor="assignment-difficulty">Difficulty</label>
                                    <select id="assignment-difficulty" value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>
                                        <option>Easy</option>
                                        <option>Medium</option>
                                        <option>Hard</option>
                                    </select>
                                </div>
                                <div className="field" style={{ margin: 0 }}>
                                    <label htmlFor="assignment-score">Score</label>
                                    <input id="assignment-score" type="number" min="0" max="100" placeholder="92" value={score} onChange={(event) => setScore(event.target.value)} />
                                </div>
                                <button className="btn btn-primary" onClick={addAssignment} disabled={isLoading}>
                                    <Icon name="plus" />
                                    Add
                                </button>
                            </div>
                        </div>
                    </section>

                    <section className="table-panel">
                        <div className="panel-header">
                            <div className="panel-title">
                                <h2>Assignment board</h2>
                                <p>{filteredAssignments.length} shown from {assignments.length} total.</p>
                            </div>
                            <div className="filter-row" style={{ width: 'min(520px, 100%)' }}>
                                <input type="text" placeholder="Search title or subject..." value={search} onChange={(event) => setSearch(event.target.value)} />
                                <select value={filterStatus} onChange={(event) => setFilterStatus(event.target.value)}>
                                    <option value="">All statuses</option>
                                    <option value="Pending">Pending</option>
                                    <option value="In Progress">In Progress</option>
                                    <option value="Completed">Completed</option>
                                    <option value="Overdue">Overdue</option>
                                </select>
                            </div>
                        </div>
                        <div className="panel-body">
                            {filteredAssignments.length ? (
                                <div className="assignments-table-wrap">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>Assignment</th>
                                                <th>Subject</th>
                                                <th>Due</th>
                                                <th>Status</th>
                                                <th>Difficulty</th>
                                                <th>Score</th>
                                                <th></th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {filteredAssignments.map((assignment) => (
                                                <tr key={assignment.id || `${assignment.title}-${getDueValue(assignment)}`}>
                                                    <td><strong>{assignment.title}</strong></td>
                                                    <td>{assignment.subject}</td>
                                                    <td>{formatDate(getDueValue(assignment))}</td>
                                                    <td><span className={`badge ${statusClass[assignment.status] || 'badge-pending'}`}>{assignment.status || 'Pending'}</span></td>
                                                    <td>{assignment.difficulty || 'Medium'}</td>
                                                    <td>{assignment.score ? `${assignment.score}%` : '—'}</td>
                                                    <td>
                                                        <div className="table-actions">
                                                            <button className="btn btn-danger btn-icon" onClick={() => removeAssignment(assignment)} title="Delete assignment" aria-label="Delete assignment">
                                                                <Icon name="trash-2" />
                                                            </button>
                                                        </div>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            ) : (
                                <div className="empty-state">No assignments match this view.</div>
                            )}
                        </div>
                    </section>
                </div>
            );
        }

        function App() {
            const [studentName, setStudentName] = useState(() => localStorage.getItem('tutorly_student_name') || '');
            const [studentId, setStudentId] = useState(() => localStorage.getItem('tutorly_student_id') || '');
            const [loggedIn, setLoggedIn] = useState(() => Boolean(localStorage.getItem('tutorly_student_id')));
            const [currentPage, setCurrentPage] = useState(() => window.location.hash.replace('#', '') || 'dashboard');
            const [assignments, setAssignments] = useState([]);
            const [tasks, setTasks] = useState([]);
            const apiService = useMemo(() => new APIService(), []);
            useLucide([loggedIn, currentPage, assignments.length, tasks.length]);

            useEffect(() => {
                const page = window.location.hash.replace('#', '');
                if (page && navItems.some((item) => item.id === page)) {
                    setCurrentPage(page);
                }

                const handleHash = () => {
                    const nextPage = window.location.hash.replace('#', '') || 'dashboard';
                    if (navItems.some((item) => item.id === nextPage)) {
                        setCurrentPage(nextPage);
                    }
                };
                window.addEventListener('hashchange', handleHash);
                return () => window.removeEventListener('hashchange', handleHash);
            }, []);

            useEffect(() => {
                if (loggedIn && currentPage) {
                    window.location.hash = currentPage === 'dashboard' ? '' : currentPage;
                }
            }, [currentPage, loggedIn]);

            useEffect(() => {
                if (!studentId) return;

                const savedTasks = localStorage.getItem(`todos_${studentId}`);
                setTasks(savedTasks ? JSON.parse(savedTasks) : [
                    { id: 1, text: 'Review today’s assignment list', done: false },
                    { id: 2, text: 'Ask Tutorly for one concept explanation', done: false },
                ]);

                const savedAssignments = localStorage.getItem(`assignments_${studentId}`);
                if (savedAssignments) {
                    setAssignments(JSON.parse(savedAssignments));
                }

                apiService.getAssignments(studentId)
                    .then((data) => {
                        setAssignments(data || []);
                        localStorage.setItem(`assignments_${studentId}`, JSON.stringify(data || []));
                    })
                    .catch(() => {
                        if (!savedAssignments) {
                            setAssignments([]);
                        }
                    });
            }, [studentId]);

            useEffect(() => {
                if (studentId) {
                    localStorage.setItem(`assignments_${studentId}`, JSON.stringify(assignments));
                }
            }, [assignments, studentId]);

            const handleLogin = (name, id) => {
                localStorage.setItem('tutorly_student_name', name);
                localStorage.setItem('tutorly_student_id', id);
                setStudentName(name);
                setStudentId(id);
                setLoggedIn(true);
                setCurrentPage('dashboard');
            };

            const handleLogout = () => {
                localStorage.removeItem('tutorly_student_name');
                localStorage.removeItem('tutorly_student_id');
                setLoggedIn(false);
                setStudentName('');
                setStudentId('');
                setCurrentPage('dashboard');
                window.location.hash = '';
            };

            if (!loggedIn) {
                return <Auth onLogin={handleLogin} />;
            }

            const pages = {
                dashboard: (
                    <Dashboard
                        studentName={studentName}
                        studentId={studentId}
                        setCurrentPage={setCurrentPage}
                        assignments={assignments}
                        tasks={tasks}
                    />
                ),
                'ai-tutor': <ChatbotPage studentId={studentId} />,
                tasks: <TasksPage studentId={studentId} tasks={tasks} setTasks={setTasks} />,
                assignments: <AssignmentsPage studentId={studentId} assignments={assignments} setAssignments={setAssignments} />,
            };

            return (
                <div className="app">
                    <AppShell
                        currentPage={currentPage}
                        setCurrentPage={setCurrentPage}
                        studentName={studentName}
                        studentId={studentId}
                        onLogout={handleLogout}
                    >
                        {pages[currentPage] || pages.dashboard}
                    </AppShell>
                </div>
            );
        }
export default App;
