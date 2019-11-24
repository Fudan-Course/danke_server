# 旦课

复旦课程论坛

## 部署

### 安装

```shell
pip install -e .
```

### 配置

应该在`danke_server/instance/config.py`文件中填写相关配置。必须填写的如下

```py
FLASK_SECRET_KEY = '' # 加密使用的随机串
MAIL_USERNAME = '' # 发送邮件使用的邮箱账号
MAIL_PASSWORD = '' # 发送邮件使用的邮箱密码
MAIL_DEFAULT_SENDER = '' # 发送邮件使用的邮箱账号
```

### 设置环境变量

在当前命令行下执行以下语句以确保flask执行当前app。

linux

```shell
export FLASK_APP=danke
export FLASK_ENV=development
```

cmd

```shell
set FLASK_APP=danke
set FLASK_ENV=development
```

powershell

```powershell
$env:FLASK_APP="danke"
$env:FLASK_ENV="development"
```

## 运行

根据环境选择以下一个语句执行

```shell
python run.py
./run.bat
./run.sh
```

## 测试

```shell
pytest
```

## 工具

### 初始化数据库

linux

```shell
flask reset_db
```

将会删除所有数据并初始化一个admin账号。

其他环境应该对应更改`export`命令，参考run脚本。

### 生成依赖

```shell
pipreqs . --encoding=utf8 --force
```
