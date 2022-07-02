"""
Example scripts that performs XBL authentication
"""
import argparse
import asyncio
import os
import webbrowser

from pprint import pprint
from aiohttp import ClientSession, web

from xbox.webapi.api.client import XboxLiveClient
from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.webapi.authentication.models import OAuth2TokenResponse
from xbox.webapi.scripts import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, TOKENS_FILE

queue = asyncio.Queue(1)


async def auth_callback(request):
    error = request.query.get("error")
    if error:
        description = request.query.get("error_description")
        print(f"Error in auth_callback: {description}")
        return
    # Run in task to not make unsuccessful parsing the HTTP response fail
    asyncio.create_task(queue.put(request.query["code"]))
    return web.Response(
        headers={"content-type": "text/html"},
        text="<script>window.close()</script>",
    )


async def async_main(
    client_id: str, client_secret: str, redirect_uri: str, token_filepath: str
):

    async with ClientSession() as session:
        auth_mgr = AuthenticationManager(
            session, client_id, client_secret, redirect_uri
        )

        # Refresh tokens if we have them
        if os.path.exists(token_filepath):
            with open(token_filepath, mode="r") as f:
                tokens = f.read()
            auth_mgr.oauth = OAuth2TokenResponse.parse_raw(tokens)
            await auth_mgr.refresh_tokens()

        # Request new ones if they are not valid
        if not (auth_mgr.xsts_token and auth_mgr.xsts_token.is_valid()):
            auth_url = auth_mgr.generate_authorization_url()
            webbrowser.open(auth_url)
            code = await queue.get()
            await auth_mgr.request_tokens(code)

        with open(token_filepath, mode="w") as f:
            xbl_client = XboxLiveClient(auth_mgr)
            print(f"XUID: {xbl_client.xuid}")
            f.write(auth_mgr.oauth.json())


def main():
    parser = argparse.ArgumentParser(description="Authenticate with XBL")

    app = web.Application()
    app.add_routes([web.get("/auth/callback", auth_callback)])
    runner = web.AppRunner(app)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, "localhost", 8080)
    loop.run_until_complete(site.start())
    loop.run_until_complete(
        async_main("a02c5504-0ba9-4f59-8ba7-27410ab055cd", "gwI8Q~D6c5IBamwHB9xKJVderNr_lr.1C9dnAbTu", "http://localhost:8080/auth/callback", "tokens.json")
    )


if __name__ == "__main__":
    main()