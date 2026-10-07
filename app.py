#!/usr/bin/env python

import asyncio
import http
import json
import os
import signal
import random
import time

from websockets.asyncio.server import broadcast, serve
from flask import Flask, send_from_directory
import threading

from four_connect import Game

def key_gen(length):
    key = ""
    for _ in range(0, length):
        key += str(random.choice(range(0, 10)))
    return key

JOIN = {}

def find_game():
    for key in JOIN:
        game, _ = JOIN[key]
        if game.red == "" or game.blue == "":
            return key
    
    return None

def result(connected, game):
    event = {
        "type": "result",
        "winner": game.winner,
        "connected": game.connected
    }
    broadcast(connected, json.dumps(event))


async def error(websocket, message):
    event = {
        "type": "error",
        "message": message,
    }
    await websocket.send(json.dumps(event))


async def replay(websocket, game, join_key, secret):
    if game.red == secret:
        color = "red"
    elif game.blue == secret:
        color = "blue"
    event = {
        "type": "board",
        "board": game.board,
        "turn": "blue" if game.turn else "red",
        "game_id": join_key,
        "secret": secret,
        "color": color,
        "winner": game.winner,
        "connected": game.connected
    }
    await websocket.send(json.dumps(event))


async def play(websocket, game, secret, connected):
    async for message in websocket:
        event = json.loads(message)
        assert event["type"] == "play"
        col = int(event["col"])-1
        
        if game.red == secret:
            color = "red"
        elif game.blue == secret:
            color = "blue"
        else:
            await error(websocket, "invalid secret")
            continue

        if game.play(1 if color == "blue" else 0, col):
            pass
        else:
            await error(websocket, "invalid move")
            continue

        event = {
            "type": "play",
            "color": color,
            "col": col
        }
        broadcast(connected, json.dumps(event))

        if game.winner != "":
            time.sleep(1)
            result(connected, game)

async def start(websocket):
    game = Game()
    connected = {websocket}

    join_key = key_gen(4)
    JOIN[join_key] = game, connected
    color = random.choice(["blue", "red"])
    secret = key_gen(8)
    if color == "red":
        game.red = secret
    else:
        game.blue = secret
    try:
        event = {
            "type": "init",
            "game_id": join_key,
            "secret": secret,
            "color": color,
            "turn": "blue" if game.turn else "red",
        }
        await websocket.send(json.dumps(event))
        await play(websocket, game, secret, connected)
    finally:
        connected.remove(websocket)


async def continue_game(websocket, join_key, secret):
    try:
        game, connected = JOIN[join_key]
    except KeyError:
        await error(websocket, "Game not found.")
        return
    if game.red == secret or game.blue == secret:
        pass
    else:
        await error(websocket, "invalid secret.")
        return
    connected.add(websocket)
    try:
        await replay(websocket, game, join_key, secret)
        await play(websocket, game, secret, connected)
    finally:
        connected.remove(websocket)

async def join(websocket):
    join_key = find_game()
    try:
        game, connected = JOIN[join_key]
    except KeyError:
        await error(websocket, "Game not found.")
        return
    secret = key_gen(8)
    if game.red == "":
        game.red = secret
    elif game.blue == "":
        game.blue = secret
    else:
        await error(websocket, "invalid secret.")
        return
    connected.add(websocket)
    try:
        await replay(websocket, game, join_key, secret)
        await play(websocket, game, secret, connected)
    finally:
        connected.remove(websocket)

async def handler(websocket):
    message = await websocket.recv()
    event = json.loads(message)
    assert "type" in event;
    if event["type"] == "init":
        if "game_id" in event and event["game_id"] in JOIN:
            await continue_game(websocket, event["game_id"], event["secret"])
        elif find_game():
            await join(websocket)
        else:
            await start(websocket)

def requests(connection, request):
    if request.path == "/healthz":
        return connection.respond(http.HTTPStatus.OK, "OK\n")
    


async def main():
    port = int(os.environ.get("PORT", "8001"))
    async with serve(handler, "", port, process_request=requests) as server:
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGTERM, server.close)
        await server.wait_closed()


app = Flask(__name__, static_folder=".", static_url_path="")


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(".", filename)


def run_server():
    app.run(
        host="127.0.0.1",
        port=8000,
        debug=False,
        use_reloader=False,
    )

if __name__ == "__main__":
    httpd_thread = threading.Thread(
        target=run_server,
        name="httpd",
        daemon=True,
    )
    httpd_thread.start()
    asyncio.run(main())