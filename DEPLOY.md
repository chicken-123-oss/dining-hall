# 论坛部署指南

## 🚀 快速部署（开发环境）

### Windows 服务器部署

1. **上传文件**
   - 将整个项目文件夹上传到服务器
   - 建议使用 `d:\claw\forum` 路径

2. **运行启动脚本**
   ```cmd
   # 双击运行或在命令行执行
   start.bat
   ```

3. **访问论坛**
   - 本地访问：`http://127.0.0.1:5001`
   - 公网访问：查看 cpolar 窗口显示的地址

---

## 🏭 生产环境部署

### 使用生产级服务器

1. **安装依赖**
   ```cmd
   D:\Python\python\python.exe -m pip install -r requirements.txt
   ```

2. **启动生产服务器**
   ```cmd
   start_production.bat
   ```

   或使用命令行：
   ```cmd
   D:\Python\python\python.exe -m waitress --host=0.0.0.0 --port=5001 --threads=4 app:app
   ```

### 后台运行（推荐）

创建 `run_service.bat`：
```batch
@echo off
cd /d d:\claw\forum
start /B D:\Python\python\python.exe -m waitress --host=0.0.0.0 --port=5001 app:app > forum.log 2>&1
echo 论坛已在后台启动，日志文件：forum.log
```

---

## ⚙️ 配置说明

### 修改端口
编辑 `app.py` 第 488 行：
```python
app.run(debug=False, port=5001, use_reloader=False)  # 修改 port 参数
```

### 关闭调试模式
确保 `app.py` 中：
```python
app.run(debug=False, ...)  # debug 必须为 False
```

### 修改密钥（重要！）
编辑 `app.py` 第 7 行：
```python
app.secret_key = 'your-secret-key-here'  # 改为随机字符串
```

---

## 🌐 域名和 SSL

### 使用反向代理（推荐）

使用 Nginx 或 Apache 作为反向代理：

**Nginx 配置示例：**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 申请 SSL 证书
推荐使用 Let's Encrypt 免费证书。

---

## 🔒 安全建议

1. **防火墙设置**
   - 只开放必要端口（80、443、5001）
   - 使用防火墙限制访问 IP

2. **定期备份**
   ```cmd
   # 备份数据库
   copy forum.db forum_backup_%date%.db
   ```

3. **更新维护**
   - 定期检查依赖包更新
   - 监控系统资源使用情况

---

## 📊 监控和维护

### 查看运行状态
```cmd
# 检查进程
netstat -ano | findstr 5001

# 查看日志
type forum.log
```

### 重启服务
```cmd
# 结束进程
 taskkill /f /im python.exe

# 重新启动
start_production.bat
```

---

## 🆘 故障排除

### 常见问题

1. **端口被占用**
   ```cmd
   netstat -ano | findstr 5001
   taskkill /f /pid <进程ID>
   ```

2. **依赖安装失败**
   ```cmd
   D:\Python\python\python.exe -m pip install --upgrade pip
   D:\Python\python\python.exe -m pip install -r requirements.txt
   ```

3. **数据库锁定**
   - 确保没有多个实例同时运行
   - 重启服务器释放锁定

---

## 📞 技术支持

如遇问题，请检查：
1. Python 环境是否正确安装
2. 依赖包是否完整
3. 端口是否被占用
4. 防火墙设置

详细日志请查看 `forum.log` 文件。