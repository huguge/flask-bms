# flask-bms
Books management system based on python flask library.基于flask的图书管理系统支持电子书下载及纸质书的管理（借阅流转）

#### 配置服务器

将以下设置加入到环境变量
```
export FLASK_BMS_SECRET=隐私字段用于加密数据使用
export FLASK_BMS_EMAIL_SERVER=邮件服务器地址
export FLASK_BMS_EMAIL_USERNAME=邮件服务器的用户名
export FLASK_BMS_EMAIL_PASSWORD=邮件服务器的登入密码
export FLASK_BMS_DATABASE_URI='mysql://root:123456@localhost/'(实例)
```

第一次部署需要安装数据库

```
mysql -u*** -p < install/install.sql
```


生产环境下启动服务器
```
gunicorn --bind 0.0.0.0:8000 wsgi
```
