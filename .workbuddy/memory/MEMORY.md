# 项目长期记忆

## 项目：Flask 论坛（d:\claw\forum）

- **本地 Python 路径**：`D:\Python\python\python.exe`（Python 3.11.4，系统安装）
- **服务器部署**：阿里云 ECS（Linux, root@iZbp1bydso5n73ijvqbttnZ），代码目录 `~/dining-hall/`，Python 命令 `python3`
- **运行端口**：5001（服务器上 nginx 反向代理接管 5001，Flask 需换端口或停 nginx 后启动）
- **启动脚本**：`d:\claw\forum\start.bat`（Windows 本地）；`nohup python3 app.py &`（Linux 服务器）
- **管理员默认账号**：admin / admin888
- **GitHub 仓库**：https://github.com/chicken-123-oss/dining-hall
- **GitHub 用户名**：chicken-123-oss
- **代理端口**：HTTP 127.0.0.1:10809（用于 git push）

## 项目功能

- 首页、登录/注册、话题页、用户个人主页、管理后台
- 管理员默认账号：admin / admin888
- CORS 已设置为 origins='*'
- 封禁/解封用户 + 功能限制（can_post / can_reply）
- 申诉系统：支持封禁申诉和功能限制申诉，用户可查看申诉结果
- `/api/my_appeals`：用户查看自己的申诉记录和审核结果

## 技术栈

- 后端：Flask + SQLite
- 前端：原生 HTML/CSS/JS（无框架）
- 认证：Flask Session + SHA-256

## 数据库结构

- users 表：id, username, password, role, created_at, banned, can_post, can_reply
- appeals 表：id, user_id, username, reason, contact, status, admin_reply, appeal_type, created_at, processed_at, processed_by
  - appeal_type: 'ban'（封禁申诉）或 'restrict'（功能限制申诉）

## 已完成的主要工作

1. 完善后端 API（发言数统计、修改密码、用户主页、管理员重置密码）
2. 新增用户个人主页 profile.html
3. 完善管理后台（发言数列修复、重置密码弹窗、管理员改密码）
4. 优化话题页体验（工具栏、头像颜色、自动伸缩输入框、字数计数、toast）
5. 上传至 GitHub，附带 README 建立手册
6. 防御性重构：所有 can_post/can_reply 查询均带 try/except，兼容旧数据库
7. 申诉系统扩展：支持功能限制申诉（appeal_type='restrict'），审批通过自动恢复权限
8. 前端限制提醒：首页横幅 + 申诉页面结果展示 + 管理后台类型列
