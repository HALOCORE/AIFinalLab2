import asyncio
import websockets
import json
import re
import sys

# >>>>>>>> 棋盘状态数据字典 <<<<<<<<<
# type,tick,last_x,last_y, status，user都可以保持默认值，都不关键.
# status就用'NOT DONE'表示还在下即可。
# chessmap是一个二维数组。数组中的'.'表示空格，'O'表示AI，'X'表示用户棋子。 <<<<<<<<
status = {
    'type':'STATUS',
    'tick': 0,
    'status': 'NOT DONE',
    'turn': 'USER',
    'chess_map': None,   # 必须修改的项：棋盘状态的二维数组。[['.', 'O', 'X' ..], ..]
    'last_x':-1,
    'last_y':-1,
}


async def data_sender(websocket, path):
    print("# output_server: DATA_SENDER started.", file=sys.stderr)
    for line in sys.stdin:
        line = str(line)
        # >>>>>>>> 根据C程序的某一行特殊输出，来开始解析后续的棋盘状态信息输出 <<<<<<<<
        if line.startswith("#STATUS OUTPUT"):
            print("# output_server: find STATUS.", file=sys.stderr)
            
            # >>>>>>>> 以下代码自行修改 <<<<<<<<<<<<<<<<<<<<<
            line1 = input()
            line2 = input()
            line3 = input()
            line4 = input()
            line_chs = list()
            for i in range(15):
                line_chs.append(input())
            # 处理第1行
            tick = line1.split(':')[1]
            status['tick'] = int(tick)
            # 处理第2行
            stat = line2.split(':')[1].split('.')[0]
            status['status'] = stat.strip()
            # 处理第3行
            turn = line3.split(':')[1]
            status['turn'] = turn.strip()
            # TODO 处理第四行

            # 处理棋盘
            status['chess_map'] = list()
            for i in range(15):
                status['chess_map'].append(list())
                row = line_chs[i]
                ps = row.strip().split(' ')
                for j in range(15):
                    status['chess_map'][i].append(ps[j])
            # >>>>>>>> 以上代码自行修改 <<<<<<<<<<<<<<<<<<<<<

            # 发送数据
            await websocket.send(json.dumps(status))
        elif line.startswith("#END"):
            print("# output_server: input msg END.", file=sys.stderr)
            exit()
        else:
            pass
            # print("# output_server: unknown line: " + line)


asyncio.get_event_loop().run_until_complete(
    websockets.serve(data_sender, 'localhost', 8788))
asyncio.get_event_loop().run_forever()
    