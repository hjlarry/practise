import socket
from urllib.parse import urlparse
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

# 使用多线程可以在协程中集成阻塞IO
def get_url(url):
    url = urlparse(url)
    host = url.netloc
    path = url.path
    if path == "":
        path = "/"

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, 80))

    client.send(
        "GET {} HTTP/1.1\r\nHost:{}\r\nConnection:close\r\n\r\n".format(
            path, host
        ).encode("utf8")
    )

    data = b""
    while True:
        d = client.recv(1024)
        if d:
            data += d
        else:
            break

    data = data.decode("utf8")
    html_data = data.split("\r\n\r\n")[1]
    client.close()


start = time.time()
loop = asyncio.get_event_loop()
executor = ThreadPoolExecutor(max_workers=3)
tasks = []
try:
    for i in range(20):
        url = f"http://shop.projectsedu.com/goods/{i}/"
        task = loop.run_in_executor(executor, get_url, url)
        tasks.append(task)
    loop.run_until_complete(asyncio.wait(tasks))
finally:
    loop.close()
    print(time.time() - start)
