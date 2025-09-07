import asyncio
import random
import socket
import sys
import os
from dotenv import load_dotenv

import asyncpraw

load_dotenv()


async def main():
    scope_input = input(
        "Enter a comma separated list of scopes, or '*' for all scopes: "
    )
    scopes = [scope.strip() for scope in scope_input.strip().split(",")]

    reddit = asyncpraw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
        redirect_uri="http://localhost:8080",
    )
    state = str(random.randint(0, 65000))
    url = reddit.auth.url(duration="permanent", scopes=scopes, state=state)
    print(f"Now open this url in your browser: {url}")
    # print(await reddit.user.me())

    client = receive_connection()
    data = client.recv(1024).decode("utf-8")
    param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
    params = dict([token.split("=") for token in param_tokens])

    if state != params["state"]:
        send_message(
            client,
            f"State mismatch. Expected: {state} Received: {params['state']}",
        )
        return 1
    elif "error" in params:
        send_message(client, params["error"])
        return 1

    refresh_token = await reddit.auth.authorize(params["code"])
    send_message(client, f"Refresh token: {refresh_token}")
    await reddit.close()
    return 0


def receive_connection():
    """Wait for and then return a connected socket..

    Opens a TCP connection on port 8080, and waits for a single client.

    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 8080))
    server.listen(1)
    client = server.accept()[0]
    server.close()
    return client


def send_message(client, message):
    """Send message to client and close the connection."""
    print(message)
    client.send(f"HTTP/1.1 200 OK\r\n\r\n{message}".encode())
    client.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    sys.exit(loop.run_until_complete(main()))
