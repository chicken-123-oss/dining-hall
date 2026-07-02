from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import sqlite3, hashlib, os, time
from datetime import timedelta

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'wwiii_forum_secret_2026_x9k'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
CORS(app, supports_credentials=True, origins='*')

DB = os.path.join(os.path.dirname(__file__), 'forum.db')

# ---------- DB ----------
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at INTEGER DEFAULT 0,
        banned INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        author_id INTEGER,
        created_at INTEGER DEFAULT 0,
        pinned INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER NOT NULL,
        author_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        reply_to INTEGER DEFAULT NULL,
        created_at INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS security_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS appeals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        reason TEXT NOT NULL,
        contact TEXT,
        status TEXT DEFAULT 'pending',
        admin_reply TEXT,
        created_at INTEGER DEFAULT 0,
        processed_at INTEGER DEFAULT 0,
        processed_by INTEGER DEFAULT NULL
    );
    ''')

    # 数据迁移：添加功能限制字段（兼容旧数据库）
    for migration_sql in [
        'ALTER TABLE users ADD COLUMN can_post INTEGER DEFAULT 1',
        'ALTER TABLE users ADD COLUMN can_reply INTEGER DEFAULT 1',
    ]:
        try:
            c.execute(migration_sql)
        except Exception:
            pass  # 列已存在，忽略
    # 迁移：申诉类型字段
    try:
        c.execute('ALTER TABLE appeals ADD COLUMN appeal_type TEXT DEFAULT "ban"')
    except Exception:
        pass
    conn.commit()

    c.execute('SELECT COUNT(*) FROM security_answers')
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO security_answers(question,answer) VALUES(?,?)",
                  ('世界上最伟大的动物是什么？', '猫'))

    c.execute('SELECT COUNT(*) FROM appeals')
    if c.fetchone()[0] == 0:
        # 示例申诉数据，实际运行时会被清空
        c.execute("INSERT INTO appeals(user_id,username,reason,contact,status,created_at) VALUES(?,?,?,?,?,?)",
                  (2, 'testuser', '误封账号', 'test@example.com', 'pending', int(time.time()) - 86400))

    c.execute('SELECT COUNT(*) FROM users WHERE role="admin"')
    if c.fetchone()[0] == 0:
        pwd = hashlib.sha256('admin888'.encode()).hexdigest()
        c.execute("INSERT INTO users(username,password,role,created_at) VALUES(?,?,?,?)",
                  ('admin', pwd, 'admin', int(time.time())))

    c.execute('SELECT COUNT(*) FROM topics')
    if c.fetchone()[0] == 0:
        now = int(time.time())
        default_topics = [
            ('豆腐脑吃甜的还是咸的？', '甜党 vs 咸党，千年论战，今日终结！'),
            ('腐乳就该是辣的', '不加辣椒的腐乳，是对腐乳的侮辱。'),
            ('粽子到底是甜的好吃还是咸的？', '肉粽党和甜粽党请各自发表意见！'),
            ('汤圆里应该有馅还是没馅？', '无馅汤圆是什么？一个球吗？'),
            ('火锅蘸料：芝麻酱还是油碟？', '两种蘸料，两种人生，你站哪队？'),
            ('方便面汤要不要喝？', '倒掉汤是一种罪过！'),
            ('榴莲：天堂还是地狱？', '榴莲爱好者和厌恶者的终极对决。'),
            ('螺蛳粉臭还是香？', '那股味道，是灵魂还是折磨？'),
            ('月饼蛋黄是异端吗？', '蛋黄月饼爱好者请进来辩论。'),
            ('早餐该吃咸还是甜？', '豆浆油条 vs 牛奶面包，中西之争。'),
        ]
        for title, desc in default_topics:
            c.execute('INSERT INTO topics(title,description,author_id,created_at,pinned) VALUES(?,?,?,?,?)',
                      (title, desc, 1, now, 0))

    conn.commit()
    conn.close()

def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'ok': False, 'msg': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            return jsonify({'ok': False, 'msg': '无权限'}), 403
        return f(*args, **kwargs)
    return decorated

# ---------- 静态页面 ----------
@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/1')
def page1():
    return send_from_directory('templates', '1.html')

@app.route('/1.txt')
def page1_txt():
    return send_from_directory('static', '1.txt')

@app.route('/login')
def login_page():
    return send_from_directory('templates', 'login.html')

@app.route('/register')
def register_page():
    return send_from_directory('templates', 'register.html')

@app.route('/appeal')
def appeal_page():
    return send_from_directory('templates', 'appeal.html')

@app.route('/topic/<int:tid>')
def topic_page(tid):
    return send_from_directory('templates', 'topic.html')

@app.route('/admin')
def admin_page():
    return send_from_directory('templates', 'admin.html')

@app.route('/user/<int:uid>')
def user_profile_page(uid):
    return send_from_directory('templates', 'profile.html')

# ---------- API 认证 ----------
@app.route('/api/security_question', methods=['GET'])
def get_security_question():
    conn = get_db()
    row = conn.execute('SELECT question FROM security_answers LIMIT 1').fetchone()
    conn.close()
    return jsonify({'question': row['question'] if row else ''})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    answer = data.get('answer', '').strip()
    if not username or not password or not answer:
        return jsonify({'ok': False, 'msg': '请填写所有字段'}), 400
    if len(username) < 2 or len(username) > 16:
        return jsonify({'ok': False, 'msg': '用户名需2-16个字符'}), 400
    if len(password) < 6:
        return jsonify({'ok': False, 'msg': '密码至少6个字符'}), 400
    conn = get_db()
    row = conn.execute('SELECT answer FROM security_answers LIMIT 1').fetchone()
    if not row or answer.lower() != row['answer'].lower():
        conn.close()
        return jsonify({'ok': False, 'msg': '安全问题回答错误'}), 400
    try:
        conn.execute('INSERT INTO users(username,password,created_at) VALUES(?,?,?)',
                     (username, hash_pwd(password), int(time.time())))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'ok': False, 'msg': '用户名已存在'}), 400
    conn.close()
    return jsonify({'ok': True, 'msg': '注册成功'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({'ok': False, 'msg': '请填写用户名和密码'}), 400
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username=? AND password=?',
                        (username, hash_pwd(password))).fetchone()
    conn.close()
    if not user:
        return jsonify({'ok': False, 'msg': '用户名或密码错误'}), 401
    if user['banned']:
        return jsonify({
            'ok': False, 
            'msg': '账号已被封禁',
            'banned': True,
            'appeal_url': f'/appeal?username={username}'
        }), 403
    session.permanent = True
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role'] = user['role']
    return jsonify({'ok': True, 'username': user['username'], 'role': user['role']})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'ok': True})

@app.route('/api/me', methods=['GET'])
def me():
    if 'user_id' not in session:
        return jsonify({'ok': False, 'msg': '未登录'}), 401
    conn = get_db()
    u = conn.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()
    conn.close()

    # 用户已被删除
    if not u:
        session.clear()
        return jsonify({'ok': False, 'msg': '账号不存在'}), 401

    # 用户已被封禁：服务端主动清除 session，强制下线
    banned = u['banned'] if 'banned' in u.keys() else 0
    if banned:
        session.clear()
        return jsonify({
            'ok': False,
            'msg': '账号已被封禁',
            'banned': True,
            'appeal_url': f'/appeal?username={u["username"]}'
        }), 403

    can_post = 1
    can_reply = 1
    try:
        can_post = u['can_post'] if u['can_post'] is not None else 1
    except Exception:
        pass
    try:
        can_reply = u['can_reply'] if u['can_reply'] is not None else 1
    except Exception:
        pass

    return jsonify({
        'ok': True,
        'id': session['user_id'],
        'username': session['username'],
        'role': session['role'],
        'can_post': can_post,
        'can_reply': can_reply,
    })

@app.route('/api/me/password', methods=['PUT'])
@login_required
def change_password():
    data = request.json or {}
    old_pwd = data.get('old_password', '').strip()
    new_pwd = data.get('new_password', '').strip()
    if not old_pwd or not new_pwd:
        return jsonify({'ok': False, 'msg': '请填写所有字段'}), 400
    if len(new_pwd) < 6:
        return jsonify({'ok': False, 'msg': '新密码至少6个字符'}), 400
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id=? AND password=?',
                        (session['user_id'], hash_pwd(old_pwd))).fetchone()
    if not user:
        conn.close()
        return jsonify({'ok': False, 'msg': '原密码错误'}), 400
    conn.execute('UPDATE users SET password=? WHERE id=?',
                 (hash_pwd(new_pwd), session['user_id']))
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'msg': '密码修改成功'})

# ---------- API 申诉 ----------
@app.route('/api/check_status', methods=['GET'])
def check_user_status():
    """检测用户当前封禁/限制状态，供申诉页面自动识别封禁类型"""
    username = request.args.get('username', '').strip()
    if not username:
        return jsonify({'ok': False, 'msg': '请提供用户名'}), 400
    conn = get_db()
    # 防御性查询：兼容旧数据库无 can_post/can_reply 列
    user = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
    conn.close()
    if not user:
        return jsonify({'ok': False, 'msg': '用户不存在'}), 404

    banned = user['banned'] if 'banned' in user.keys() else 0
    can_post = 1
    can_reply = 1
    try:
        can_post = user['can_post'] if user['can_post'] is not None else 1
    except Exception:
        pass
    try:
        can_reply = user['can_reply'] if user['can_reply'] is not None else 1
    except Exception:
        pass
    
    if banned:
        appeal_type = 'ban'
        type_label = '账号封禁'
    elif can_post == 0 or can_reply == 0:
        appeal_type = 'restrict'
        parts = []
        if can_post == 0:
            parts.append('禁止发帖')
        if can_reply == 0:
            parts.append('禁止回复')
        type_label = '功能限制（' + '、'.join(parts) + '）'
    else:
        appeal_type = 'none'
        type_label = '账号状态正常'
    
    return jsonify({
        'ok': True,
        'appeal_type': appeal_type,
        'type_label': type_label,
        'banned': banned,
        'can_post': can_post,
        'can_reply': can_reply
    })

@app.route('/api/appeal', methods=['POST'])
def submit_appeal():
    data = request.json or {}
    username = data.get('username', '').strip()
    reason = data.get('reason', '').strip()
    contact = data.get('contact', '').strip()
    
    if not username or not reason:
        return jsonify({'ok': False, 'msg': '请填写必要信息'}), 400
    
    if len(reason) > 1000:
        return jsonify({'ok': False, 'msg': '申诉理由不能超过1000字'}), 400
    
    if contact and len(contact) > 100:
        return jsonify({'ok': False, 'msg': '联系方式不能超过100字'}), 400
    
    conn = get_db()
    # 检查用户是否存在且被封禁或功能受限（防御性查询：兼容旧数据库）
    user = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
    if not user:
        conn.close()
        return jsonify({'ok': False, 'msg': '用户不存在'}), 404

    # 安全读取 can_post / can_reply（旧数据库可能无此列）
    _banned = user['banned'] if 'banned' in user.keys() else 0
    _can_post = 1
    _can_reply = 1
    try:
        _can_post = user['can_post'] if user['can_post'] is not None else 1
    except Exception:
        pass
    try:
        _can_reply = user['can_reply'] if user['can_reply'] is not None else 1
    except Exception:
        pass

    # 判断申诉类型
    appeal_type = 'ban'
    if _banned:
        appeal_type = 'ban'
    elif _can_post == 0 or _can_reply == 0:
        appeal_type = 'restrict'
    else:
        conn.close()
        return jsonify({'ok': False, 'msg': '账号状态正常，无需申诉'}), 400
    
    # 检查是否有同类型未处理的申诉
    existing = conn.execute(
        'SELECT id FROM appeals WHERE username=? AND status="pending" AND appeal_type=?', 
        (username, appeal_type)
    ).fetchone()
    
    if existing:
        conn.close()
        return jsonify({'ok': False, 'msg': f'已有待处理的{appeal_type == "ban" and "封禁" or "功能限制"}申诉，请耐心等待'}), 400
    
    # 提交申诉
    now = int(time.time())
    conn.execute(
        'INSERT INTO appeals(user_id, username, reason, contact, status, appeal_type, created_at) VALUES(?, ?, ?, ?, ?, ?, ?)',
        (user['id'], username, reason, contact, 'pending', appeal_type, now)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'ok': True, 'msg': '申诉提交成功，请耐心等待管理员处理'})

@app.route('/api/admin/appeals', methods=['GET'])
@admin_required
def admin_get_appeals():
    status_filter = request.args.get('status', 'all')
    conn = get_db()
    
    query = '''
        SELECT a.*, u.username as processed_by_name
        FROM appeals a
        LEFT JOIN users u ON a.processed_by = u.id
    '''
    params = []
    
    if status_filter != 'all':
        query += ' WHERE a.status = ?'
        params.append(status_filter)
    
    query += ' ORDER BY a.created_at DESC'
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    
    return jsonify([dict(r) for r in rows])

@app.route('/api/admin/appeals/<int:aid>/process', methods=['POST'])
@admin_required
def process_appeal(aid):
    data = request.json or {}
    action = data.get('action')  # 'approve' or 'reject'
    reply = data.get('reply', '').strip()
    # 功能限制申诉时，管理员可选择恢复哪些权限（1=恢复，0=不恢复）
    restore_can_post = data.get('can_post', 1)  # 默认恢复
    restore_can_reply = data.get('can_reply', 1)  # 默认恢复
    
    if action not in ['approve', 'reject']:
        return jsonify({'ok': False, 'msg': '无效的操作'}), 400
    
    conn = get_db()
    appeal = conn.execute('SELECT * FROM appeals WHERE id=?', (aid,)).fetchone()
    
    if not appeal:
        conn.close()
        return jsonify({'ok': False, 'msg': '申诉不存在'}), 404
    
    if appeal['status'] != 'pending':
        conn.close()
        return jsonify({'ok': False, 'msg': '申诉已处理'}), 400
    
    new_status = 'approved' if action == 'approve' else 'rejected'
    now = int(time.time())
    
    # 更新申诉状态
    conn.execute(
        'UPDATE appeals SET status=?, admin_reply=?, processed_at=?, processed_by=? WHERE id=?',
        (new_status, reply, now, session['user_id'], aid)
    )
    
    # 批准申诉时，根据申诉类型恢复权限
    if action == 'approve':
        appeal_type = appeal['appeal_type'] if 'appeal_type' in appeal.keys() else 'ban'
        if appeal_type == 'restrict':
            # 功能限制申诉：按管理员勾选的权限恢复
            conn.execute(
                'UPDATE users SET can_post=?, can_reply=? WHERE username=?',
                (restore_can_post, restore_can_reply, appeal['username'])
            )
        else:
            # 封禁申诉：解封账号
            conn.execute(
                'UPDATE users SET banned=0 WHERE username=?',
                (appeal['username'],)
            )
    
    conn.commit()
    conn.close()
    
    return jsonify({'ok': True, 'msg': f'申诉已{new_status == "approved" and "批准" or "拒绝"}'})

@app.route('/api/my_appeals', methods=['GET'])
@login_required
def my_appeals():
    """当前用户查看自己的申诉记录与结果"""
    conn = get_db()
    # 防御性查询：兼容旧数据库无 appeal_type 列的情况
    try:
        rows = conn.execute(
            'SELECT id, reason, contact, status, admin_reply, appeal_type, created_at, processed_at '
            'FROM appeals WHERE user_id=? ORDER BY created_at DESC LIMIT 5',
            (session['user_id'],)
        ).fetchall()
    except Exception:
        # 旧数据库缺少 appeal_type 列，回退查询
        rows = conn.execute(
            'SELECT id, reason, contact, status, admin_reply, created_at, processed_at '
            'FROM appeals WHERE user_id=? ORDER BY created_at DESC LIMIT 5',
            (session['user_id'],)
        ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        # 兼容旧数据：缺少 appeal_type 时补默认值
        if 'appeal_type' not in d or d.get('appeal_type') is None:
            d['appeal_type'] = 'ban'
        result.append(d)
    return jsonify(result)

@app.route('/api/stats', methods=['GET'])
def public_stats():
    """公开统计接口，不需要管理员权限"""
    conn = get_db()
    user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    topic_count = conn.execute('SELECT COUNT(*) FROM topics').fetchone()[0]
    post_count = conn.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    conn.close()
    return jsonify({'users': user_count, 'topics': topic_count, 'posts': post_count})

@app.route('/api/users/<int:uid>', methods=['GET'])
def get_user_profile(uid):
    conn = get_db()
    user = conn.execute('SELECT id, username, role, created_at, banned FROM users WHERE id=?', (uid,)).fetchone()
    if not user:
        conn.close()
        return jsonify({'ok': False, 'msg': '用户不存在'}), 404
    post_count = conn.execute('SELECT COUNT(*) FROM posts WHERE author_id=?', (uid,)).fetchone()[0]
    topic_count = conn.execute('SELECT COUNT(*) FROM topics WHERE author_id=?', (uid,)).fetchone()[0]
    recent_posts = conn.execute('''
        SELECT p.id, p.content, p.created_at, t.id as topic_id, t.title as topic_title
        FROM posts p JOIN topics t ON p.topic_id=t.id
        WHERE p.author_id=?
        ORDER BY p.created_at DESC LIMIT 10
    ''', (uid,)).fetchall()
    conn.close()
    return jsonify({
        'ok': True,
        'id': user['id'],
        'username': user['username'],
        'role': user['role'],
        'created_at': user['created_at'],
        'banned': user['banned'],
        'post_count': post_count,
        'topic_count': topic_count,
        'recent_posts': [dict(r) for r in recent_posts]
    })

# ---------- API 话题 ----------
@app.route('/api/topics', methods=['GET'])
def get_topics():
    conn = get_db()
    rows = conn.execute('''
        SELECT t.*, u.username as author_name,
               (SELECT COUNT(*) FROM posts p WHERE p.topic_id=t.id) as post_count
        FROM topics t LEFT JOIN users u ON t.author_id=u.id
        ORDER BY t.pinned DESC, t.created_at DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/topics', methods=['POST'])
@login_required
def create_topic():
    data = request.json or {}
    title = data.get('title', '').strip()
    desc = data.get('description', '').strip()
    if not title:
        return jsonify({'ok': False, 'msg': '话题标题不能为空'}), 400
    if len(title) > 80:
        return jsonify({'ok': False, 'msg': '标题不超过80个字符'}), 400
    conn = get_db()
    # 检查发帖限制
    try:
        u = conn.execute('SELECT can_post FROM users WHERE id=?', (session['user_id'],)).fetchone()
        if u and u['can_post'] == 0:
            conn.close()
            return jsonify({'ok': False, 'msg': '您的账号已被限制发帖功能，可前往 /appeal 提交申诉'}), 403
    except Exception:
        pass  # 数据库缺少列，允许发帖
    cur = conn.execute('INSERT INTO topics(title,description,author_id,created_at) VALUES(?,?,?,?)',
                 (title, desc, session['user_id'], int(time.time())))
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'id': new_id})

@app.route('/api/topics/<int:tid>', methods=['GET'])
def get_topic(tid):
    conn = get_db()
    topic = conn.execute(
        'SELECT t.*, u.username as author_name FROM topics t LEFT JOIN users u ON t.author_id=u.id WHERE t.id=?',
        (tid,)).fetchone()
    conn.close()
    if not topic:
        return jsonify({'ok': False, 'msg': '话题不存在'}), 404
    return jsonify(dict(topic))

@app.route('/api/topics/<int:tid>', methods=['DELETE'])
@admin_required
def delete_topic(tid):
    conn = get_db()
    conn.execute('DELETE FROM topics WHERE id=?', (tid,))
    conn.execute('DELETE FROM posts WHERE topic_id=?', (tid,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/api/topics/<int:tid>/pin', methods=['POST'])
@admin_required
def pin_topic(tid):
    conn = get_db()
    topic = conn.execute('SELECT pinned FROM topics WHERE id=?', (tid,)).fetchone()
    if not topic:
        conn.close()
        return jsonify({'ok': False, 'msg': '话题不存在'}), 404
    new_pin = 0 if topic['pinned'] else 1
    conn.execute('UPDATE topics SET pinned=? WHERE id=?', (new_pin, tid))
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'pinned': new_pin})

# ---------- API 发言 ----------
@app.route('/api/topics/<int:tid>/posts', methods=['GET'])
def get_posts(tid):
    conn = get_db()
    rows = conn.execute('''
        SELECT p.*, u.username as author_name
        FROM posts p LEFT JOIN users u ON p.author_id=u.id
        WHERE p.topic_id=?
        ORDER BY p.created_at ASC
    ''', (tid,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/topics/<int:tid>/posts', methods=['POST'])
@login_required
def create_post(tid):
    data = request.json or {}
    content = data.get('content', '').strip()
    reply_to = data.get('reply_to', None)
    if not content:
        return jsonify({'ok': False, 'msg': '内容不能为空'}), 400
    if len(content) > 2000:
        return jsonify({'ok': False, 'msg': '内容不能超过2000字'}), 400
    conn = get_db()
    # 检查回复限制
    try:
        u = conn.execute('SELECT can_reply FROM users WHERE id=?', (session['user_id'],)).fetchone()
        if u and u['can_reply'] == 0:
            conn.close()
            return jsonify({'ok': False, 'msg': '您的账号已被限制回复功能，可前往 /appeal 提交申诉'}), 403
    except Exception:
        pass  # 数据库缺少列，允许回复
    topic = conn.execute('SELECT id FROM topics WHERE id=?', (tid,)).fetchone()
    if not topic:
        conn.close()
        return jsonify({'ok': False, 'msg': '话题不存在'}), 404
    if reply_to:
        ref = conn.execute('SELECT id FROM posts WHERE id=? AND topic_id=?', (reply_to, tid)).fetchone()
        if not ref:
            reply_to = None
    cur = conn.execute('INSERT INTO posts(topic_id,author_id,content,reply_to,created_at) VALUES(?,?,?,?,?)',
                 (tid, session['user_id'], content, reply_to, int(time.time())))
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'id': cur.lastrowid})

@app.route('/api/posts/<int:pid>', methods=['DELETE'])
@login_required
def delete_post(pid):
    conn = get_db()
    post = conn.execute('SELECT * FROM posts WHERE id=?', (pid,)).fetchone()
    if not post:
        conn.close()
        return jsonify({'ok': False, 'msg': '发言不存在'}), 404
    if post['author_id'] != session['user_id'] and session.get('role') != 'admin':
        conn.close()
        return jsonify({'ok': False, 'msg': '无权限删除'}), 403
    conn.execute('DELETE FROM posts WHERE id=?', (pid,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

# ---------- API 管理员 ----------
@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_users():
    conn = get_db()
    try:
        rows = conn.execute('''
            SELECT u.id, u.username, u.role, u.created_at, u.banned,
                   COALESCE(u.can_post, 1) as can_post,
                   COALESCE(u.can_reply, 1) as can_reply,
                   (SELECT COUNT(*) FROM posts p WHERE p.author_id=u.id) as post_count
            FROM users u ORDER BY u.id
        ''').fetchall()
    except Exception:
        # 数据库缺少 can_post/can_reply 列，回退查询
        rows = conn.execute('''
            SELECT u.id, u.username, u.role, u.created_at, u.banned,
                   1 as can_post, 1 as can_reply,
                   (SELECT COUNT(*) FROM posts p WHERE p.author_id=u.id) as post_count
            FROM users u ORDER BY u.id
        ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def admin_stats():
    conn = get_db()
    user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    topic_count = conn.execute('SELECT COUNT(*) FROM topics').fetchone()[0]
    post_count = conn.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    banned_count = conn.execute('SELECT COUNT(*) FROM users WHERE banned=1').fetchone()[0]
    conn.close()
    return jsonify({'users': user_count, 'topics': topic_count,
                    'posts': post_count, 'banned': banned_count})

@app.route('/api/admin/users/<int:uid>/ban', methods=['POST'])
@admin_required
def ban_user(uid):
    if uid == session['user_id']:
        return jsonify({'ok': False, 'msg': '不能封禁自己'}), 400
    conn = get_db()
    user = conn.execute('SELECT banned,role FROM users WHERE id=?', (uid,)).fetchone()
    if not user:
        conn.close()
        return jsonify({'ok': False, 'msg': '用户不存在'}), 404
    if user['role'] == 'admin':
        conn.close()
        return jsonify({'ok': False, 'msg': '不能封禁管理员'}), 400
    new_ban = 0 if user['banned'] else 1
    conn.execute('UPDATE users SET banned=? WHERE id=?', (new_ban, uid))
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'banned': new_ban})

@app.route('/api/admin/users/<int:uid>/restrict', methods=['POST'])
@admin_required
def restrict_user(uid):
    if uid == session['user_id']:
        return jsonify({'ok': False, 'msg': '不能限制自己'}), 400
    data = request.json or {}
    can_post = 1 if data.get('can_post', 1) else 0
    can_reply = 1 if data.get('can_reply', 1) else 0
    conn = get_db()
    user = conn.execute('SELECT role FROM users WHERE id=?', (uid,)).fetchone()
    if not user:
        conn.close()
        return jsonify({'ok': False, 'msg': '用户不存在'}), 404
    if user['role'] == 'admin':
        conn.close()
        return jsonify({'ok': False, 'msg': '不能限制管理员'}), 400
    try:
        conn.execute('UPDATE users SET can_post=?, can_reply=? WHERE id=?', (can_post, can_reply, uid))
    except Exception:
        conn.close()
        return jsonify({'ok': False, 'msg': '数据库不支持功能限制，请升级数据库结构'}), 500
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'can_post': can_post, 'can_reply': can_reply})

@app.route('/api/admin/users/<int:uid>', methods=['DELETE'])
@admin_required
def delete_user(uid):
    if uid == session['user_id']:
        return jsonify({'ok': False, 'msg': '不能删除自己'}), 400
    conn = get_db()
    conn.execute('DELETE FROM users WHERE id=?', (uid,))
    conn.execute('DELETE FROM posts WHERE author_id=?', (uid,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/api/admin/users/<int:uid>/password', methods=['PUT'])
@admin_required
def admin_reset_password(uid):
    data = request.json or {}
    new_pwd = data.get('new_password', '').strip()
    if not new_pwd or len(new_pwd) < 6:
        return jsonify({'ok': False, 'msg': '新密码至少6个字符'}), 400
    conn = get_db()
    user = conn.execute('SELECT id FROM users WHERE id=?', (uid,)).fetchone()
    if not user:
        conn.close()
        return jsonify({'ok': False, 'msg': '用户不存在'}), 404
    conn.execute('UPDATE users SET password=? WHERE id=?', (hash_pwd(new_pwd), uid))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/api/admin/security_question', methods=['GET'])
@admin_required
def admin_get_security_question():
    conn = get_db()
    row = conn.execute('SELECT question, answer FROM security_answers LIMIT 1').fetchone()
    conn.close()
    return jsonify(dict(row) if row else {})

@app.route('/api/admin/security_question', methods=['PUT'])
@admin_required
def update_security_question():
    data = request.json or {}
    q = data.get('question', '').strip()
    a = data.get('answer', '').strip()
    if not q or not a:
        return jsonify({'ok': False, 'msg': '问题和答案不能为空'}), 400
    conn = get_db()
    conn.execute('UPDATE security_answers SET question=?,answer=? WHERE id=1', (q, a))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

if __name__ == '__main__':
    init_db()
    app.run(debug=False, port=5001, use_reloader=False)
