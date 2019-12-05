import asyncio
import sys
import threading
import time
from collections import deque
from datetime import datetime
from typing import List

import psutil
from starlette.websockets import WebSocket


class NetIOSocket:
    def __init__(self):
        self.connections: List[WebSocket] = []
        self.generator = self.get_notification_generator()
        self.net_record = deque(maxlen=2)
        self.update_time = 0  # must be numeric type
        self.version_info = (
            str(sys.version_info.major) + "." + str(sys.version_info.minor)
        )
        self.platform = str(sys.platform)

    async def get_notification_generator(self):
        while True:
            message = yield
            await self._notify(message)

    def update_net_io(self):
        net = psutil.net_io_counters()
        now = datetime.now().timestamp()

        recv = net.bytes_recv / 1024  # kb
        send = net.bytes_sent / 1024
        self.net_record.append([recv, send])
        self.msg = {
            "recv": {
                "x": now,
                "y": round(
                    (self.net_record[-1][0] - self.net_record[0][0])
                    / (now - self.update_time),
                    3,
                ),
            },
            "send": {
                "x": now,
                "y": round(
                    (self.net_record[-1][1] - self.net_record[0][1])
                    / (now - self.update_time),
                    3,
                ),
            },
        }
        self.update_time = now

    async def broadcast(self):
        self.update_net_io()
        if len(self.connections) > 0:
            await self.generator.asend(self.msg)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        await websocket.send_json(
            {
                **self.msg,
                **{
                    "server_info": {
                        "boot_time": datetime.now().timestamp() - psutil.boot_time(),
                        "version": self.version_info,
                        "plat_form": self.platform,
                    }
                },
            }
        )
        self.connections.append(websocket)

    def remove(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def _notify(self, message: str):
        living_connections = []
        while len(self.connections) > 0:
            # Looping like this is necessary in case a disconnection is handled
            # during await websocket.send_text(message)
            websocket = self.connections.pop()
            await websocket.send_json(message)
            living_connections.append(websocket)
        self.connections = living_connections


class NetIOMessagePusher(threading.Thread):
    def __init__(self, notifier):
        threading.Thread.__init__(self)
        self.n = notifier

    def run(self):
        while True:
            try:
                broadcast_task = self.n.broadcast()
                asyncio.run(broadcast_task)
            except Exception as e:
                print(e)
            finally:
                time.sleep(10)


socket_manager = NetIOSocket()
