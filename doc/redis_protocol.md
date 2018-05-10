###  REDIS协议定义
redis客户端使用一种叫做RESP(REdis Serialization Protocol)的协议与REDIS服务器通信。RESP协议虽然是为redis设计的，但是也适用于其他C/S模型的软件

RESP设计时考虑了以下几件事情
* 实现起来简单
* 解析起来快速
* 开发人员易阅读

RESP可以序列化不同类型的数据，像数字、字符串、数组以及一种专门表示错误的类型。客户端发往服务器的命令以及参数被处理成字符串数组，redis服务器通过特定类型的数据格式响应客户端。

RESP是二进制安全的且不需要将数据从一个进程传输到另一个进程因为它使用了一个表示长度的前缀来传输数据

注: 这里只讨论客户端-服务器之间的通信， redis集群使用了一种不同的二进制协议来实现节点间的数据交换。

####  网络层
客户端通过6379端口创建一条TCP连接，连接到redis服务器。RESP协议本身不是必须要使用TCP协议，但是在redis中，这个协议只用TCP的连接。

#### 请求-响应模型
redis服务器接收不同参数组装成的命令， 一旦接收到一个命令，服务器将进行处理并向客户端发送一个回复。

这几乎是一个最简单的模型，但是有下面两个例外
* redis 支持pipelining，因此客户端一次可以发送多条命令
* 当redis客户端订阅了一个channel，协议会变成一个推送协议，这意味着客户端不再需要发送命令，因为一旦服务器收到client订阅的channel上的新消息就会自动发送给客户端。

除了以上两个例外，redis协议是一个简单的请求-响应模型。

#### RESP协议描述
RESP协议在redis 1.2版本引入，但是直到redis 2.0版本才成为和redis 服务器通信的标准。

RESP协议实际上是一种序列化协议支持以下几种数据类型：简单字符串，错误信息，整形数字，多行字符串，数组。

redis中RESP协议的使用方式如下：
* 客户端发送至服务器的命令为 多行字符串数组。
* 服务器根据命令的实现回复RESP数据类型中的一种。

RESP协议中，数据的类型依赖第一个字节：
* 简单字符串：第一个字节是+
* 错误信息：第一个字节是-
* 整形数字：第一个字节是:
* 多行字符串：第一个字节是$
* 数组：第一个字节是*

RESP可以通过多行字符串或者数组的变体来表示一个NULL值
RESP协议每个部分以固定的'\r\n'(CRLF)结尾

#### 参考
[Redis Serialization Protocol](https://redis.io/topics/protocol)