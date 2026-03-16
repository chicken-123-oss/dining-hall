# 🗣️ Forum —— 轻量级论坛系统

基于 Python Flask + SQLite 构建的全栈论坛网站，包含首页、用户界面、管理员后台，开箱即用。

---

## ✨ 功能特性

| 模块 | 功能 |
|------|------|
| **首页** | 话题列表、置顶话题、实时统计（用户数/话题数/发言数）、搜索 |
| **用户系统** | 注册 / 登录 / 退出、修改密码、个人主页 |
| **话题** | 发起话题、发言回复、引用楼层、删除发言、楼层跳转 |
| **管理后台** | 用户管理（封禁/解封/删除/重置密码）、话题管理（置顶/删除）、安全问题设置 |
| **权限控制** | 普通用户 / 管理员 两级权限，接口级鉴权 |

---

## 🗂️ 项目结构

```
forum/
├── app.py              # Flask 后端，全部 API 路由
├── forum.db            # SQLite 数据库（运行后自动生成）
├── requirements.txt    # Python 依赖
├── start.bat           # Windows 一键启动脚本
├── static/             # 静态资源（CSS / JS / 图片）
└── templates/          # 前端页面
    ├── index.html      # 首页
    ├── login.html      # 登录页
    ├── register.html   # 注册页
    ├── topic.html      # 话题详情页
    ├── profile.html    # 用户个人主页
    └── admin.html      # 管理员后台
```

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip

### 1. 克隆项目

```bash
git clone https://github.com/chicken-123-oss/forum.git
cd forum
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动服务

**Windows：**
```bash
# 方式一：双击 start.bat
# 方式二：命令行
python app.py
```

**macOS / Linux：**
```bash
python3 app.py
```

### 4. 访问网站

打开浏览器访问：[http://127.0.0.1:5001](http://127.0.0.1:5001)

---

## 👤 默认管理员账号

首次启动后，使用以下账号登录管理后台：

| 字段 | 值 |
|------|-----|
| 用户名 | `admin` |
| 密码 | `admin123` |

> ⚠️ **请登录后立即在管理后台修改默认密码！**

管理后台地址：[http://127.0.0.1:5001/admin](http://127.0.0.1:5001/admin)

---

## 🌐 部署到公网

### 方式一：内网穿透（快速临时，推荐测试用）

使用 [cpolar](https://www.cpolar.com) 或 [ngrok](https://ngrok.com)：

```bash
# 先启动论坛
python app.py

# 新开一个终端，运行穿透
cpolar http 5001
# 或
ngrok http 5001
```

运行后会得到一个公网地址，例如 `https://xxxx.cpolar.cn`，分享给任何人即可访问。

### 方式二：云服务器（长期稳定）

```bash
# 服务器上安装依赖
pip install -r requirements.txt gunicorn

# 用 Gunicorn 生产级启动
gunicorn -w 2 -b 0.0.0.0:5001 app:app --daemon
```

配合 Nginx 反向代理绑定域名：

```nginx
server {
    listen 80;
    server_name 你的域名;
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔌 API 接口一览

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/register` | 注册 |
| POST | `/api/login` | 登录 |
| POST | `/api/logout` | 退出 |
| GET  | `/api/me` | 获取当前用户信息 |
| PUT  | `/api/me/password` | 修改自己密码 |

### 话题
| 方法 | 路径 | 说明 |
|------|------|------|
| GET  | `/api/topics` | 话题列表 |
| POST | `/api/topics` | 创建话题 |
| GET  | `/api/topics/<id>` | 话题详情 |
| DELETE | `/api/topics/<id>` | 删除话题（管理员）|

### 发言
| 方法 | 路径 | 说明 |
|------|------|------|
| GET  | `/api/topics/<id>/posts` | 获取发言列表 |
| POST | `/api/topics/<id>/posts` | 发言 |
| DELETE | `/api/posts/<id>` | 删除发言 |

### 用户
| 方法 | 路径 | 说明 |
|------|------|------|
| GET  | `/api/users/<id>` | 用户个人主页信息 |
| GET  | `/api/stats` | 公开统计数据 |

### 管理员
| 方法 | 路径 | 说明 |
|------|------|------|
| GET  | `/api/admin/users` | 用户列表（含发言数）|
| PUT  | `/api/admin/users/<id>/ban` | 封禁/解封用户 |
| DELETE | `/api/admin/users/<id>` | 删除用户 |
| PUT  | `/api/admin/users/<id>/password` | 重置用户密码 |
| GET/PUT | `/api/admin/topics` | 话题管理 |

---

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3 · Flask · SQLite |
| 前端 | 原生 HTML / CSS / JavaScript（无框架）|
| 认证 | Flask Session · SHA-256 密码哈希 |
| 跨域 | Flask-CORS |

---

## 📄 License

MIT License — 自由使用、修改、分发。
