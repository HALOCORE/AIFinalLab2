import asyncio
import websockets
import json
import sys

async def echo(websocket, path):
    print("# input_server: ECHO started.", file=sys.stderr)
    async for message in websocket:
        try:
            msg_get = json.loads(message)
        except json.JSONDecodeError:
            await websocket.send("#RE: unknown message: " + message)
            continue
        if msg_get['type'] == 'STEP':
            stepx = msg_get['x']
            stepy = msg_get['y']
            # 标准输出
            try:
                # >>>>>>>>>>>>>>>>>> 当网页下棋的信息发来，使用如下语句产生C程序输入 <<<<<<<<<<<<<<<<<<<<
                print("%d %d" % (int(stepx), int(stepy)), file=sys.stdout)
            except:
                print("# input_server: pipe closed. END.", file=sys.stderr) # 结束代码
                exit()
            
            print("# input_server: recieved(%s, %s) " % (stepx, stepy), file=sys.stderr)
            await websocket.send("#RE: PATH Recieved: " + str((stepx, stepy)))
        if msg_get['type'] == 'CMD':
            if msg_get['command'] == 'SHUTDOWN':
                try:
                    # >>>>>>>>>>>>>>>>>> 关闭功能没什么用。不如ctrl+C关闭再运行 <<<<<<<<<<<<<<<<<<<<
                    print("-4 -4", file=sys.stdout) # 结束代码
                except:
                    pass
                print("# input_server: command END.", file=sys.stderr) # 结束代码
                exit()


asyncio.get_event_loop().run_until_complete(
    websockets.serve(echo, 'localhost', 8765))
asyncio.get_event_loop().run_forever()