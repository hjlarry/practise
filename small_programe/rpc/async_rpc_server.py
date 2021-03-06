import asyncore
from io import StringIO
import json
import struct
import socket
import os


class RPCHandler(asyncore.dispatcher_with_send):  # 客户套接字处理器必须继承 dispatcher_with_send
    def __init__(self, sock, addr):
        super().__init__(sock)
        self.addr = addr
        self.handlers = {"ping": self.ping}
        self.rbuf = StringIO()  # 读缓冲区由用户代码维护，写缓冲区由 asyncore 内部提供

    def handle_connect(self):  # 新的连接被 accept 后回调方法
        print(self.addr, "comes")

    def handle_close(self):  # 连接关闭之前回调方法
        print(self.addr, "bye")
        self.close()

    def handle_read(self):  # 有读事件到来时回调方法
        while True:
            content = self.recv(1024).decode()
            if content:
                self.rbuf.write(content)
            if len(content) < 1024:
                break
        self.handle_rpc()

    def handle_rpc(self):  # 将读到的消息解包并处理
        while True:  # 可能一次性收到了多个请求消息，所以需要循环处理
            self.rbuf.seek(0)
            length_prefix = self.rbuf.read(4).encode()
            if len(length_prefix) < 4:  # 不足一个消息
                break
            (length,) = struct.unpack("I", length_prefix)
            body = self.rbuf.read(length)
            if len(body) < length:  # 不足一个消息
                break
            request = json.loads(body)
            in_ = request["in"]
            params = request["params"]
            print(in_, params)
            handler = self.handlers[in_]
            handler(params)  # 处理消息
            left = self.rbuf.getvalue()[length + 4 :]  # 消息处理完了，缓冲区要截断
            self.rbuf = StringIO()
            self.rbuf.write(left)
        self.rbuf.seek(0, 2)  # 将游标挪到文件结尾，以便后续读到的内容直接追加...

    def ping(self, params):
        self.send_result("pong", params)

    def send_result(self, out, result):
        response = {"out": out, "result": result}
        body = json.dumps(response)
        length_prefix = struct.pack("I", len(body))
        self.send(length_prefix)  # 写入缓冲区
        self.send(body.encode())  # 写入缓冲区...


class RPCServer(asyncore.dispatcher):  # 服务器套接字处理器必须继承 dispatcher
    def __init__(self, host, port):
        super().__init__()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(1)
        self.prefork(10)

    def prefork(self, n):
        for i in range(n):
            pid = os.fork()
            if pid < 0:  # fork error
                return
            if pid > 0:  # parent process
                continue
            if pid == 0:
                break  # child process...

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            RPCHandler(sock, addr)


if __name__ == "__main__":
    RPCServer("localhost", 8083)
    asyncore.loop()
