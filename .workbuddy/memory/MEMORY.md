# 项目长期记忆

## 项目：Flask 论坛（d:\claw\forum）

- **Python 路径**：`D:\Python\python\python.exe`
- **运行端口**：5001
- **启动脚本**：`d:\claw\forum\start.bat`（同时启动论坛和 cpolar 内网穿透）
- **cpolar 路径**：`D:\cpolar\cpolar.exe`
- **GitHub 仓库**：https://github.com/chicken-123-oss/dining-hall
- **GitHub 用户名**：chicken-123-oss
- **代理端口**：HTTP 127.0.0.1:10809（用于 git push）

## 项目功能

- 首页、登录/注册、话题页、用户个人主页、管理后台
- 管理员默认账号：admin / admin123
- CORS 已设置为 origins='*'

## 技术栈

- 后端：Flask + SQLite
- 前端：原生 HTML/CSS/JS（无框架）
- 认证：Flask Session + SHA-256

## 已完成的主要工作

1. 完善后端 API（发言数统计、修改密码、用户主页、管理员重置密码）
2. 新增用户个人主页 profile.html
3. 完善管理后台（发言数列修复、重置密码弹窗、管理员改密码）
4. 优化话题页体验（工具栏、头像颜色、自动伸缩输入框、字数计数、toast）
5. 上传至 GitHub，附带 README 建立手册
