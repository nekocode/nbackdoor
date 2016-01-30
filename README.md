# nbackdoor
> **nbackdoor** 是一个使用命令行进行远程控制的系统  
> （Dev 分支正在尝试进行重构）

## feature
- 使用 Python 编写
- 使用 Job Pool 进行任务调度
- 绕过 Windows 的 UAC 机制获得管理员权限
- 自动感染系统加入自启动项


### todo
- [x] 添加 from 字段
- [x] 安全密码输入
- [x] 命令行帮助信息：https://github.com/docopt/docopt
- [x] 下载文件
- [x] ShowDialog 执行完毕返回 result 消息
- [x] 缓冲传输回显字符
- [x] 参数分割
- [x] 获取动态服务器 ip
- [x] esc 终止运行中的命令
- [ ] send_data 和 send_char 融合

## tofix
- [x] 执行 ShowDialog 命令，参数使用中文字符串失败
- [x] connect to client success 处理
- [ ] cat 测试


## note
- [pyinstaller](https://github.com/pyinstaller/pyinstaller)
- [cmd shell -> ftp upload](http://home.51.com/xiaobai521100/diary/item/10008446.html)


## screenshots
![](art/1.png "")
