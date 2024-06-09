from aiocoap import *
import asyncio
import json


async def request(ip, code, payload):
    context = await Context.create_client_context()
    request = Message(
        code=code, uri=f"coap://{ip}/", payload=json.dumps(payload).encode("utf-8")
    )

    try:
        response = await context.request(request).response
        if not response.payload:
            return None
        return json.loads(response.payload.decode("utf-8"))
    except Exception as e:
        return None


def request_info(ip):
    return asyncio.run(request(ip, GET, ["device"]))


def request_locate(ip):
    asyncio.run(request(ip, PUT, {"locate": 1}))


def request_get_brightness(ip):
    return asyncio.run(request(ip, GET, ["brightness"]))


def request_set_brightness(ip, max, min, magrin):
    asyncio.run(
        request(ip, PUT, {"brightness": {"max": max, "min": min, "margin": magrin}})
    )


def request_reset(ip):
    asyncio.run(request(ip, PUT, {"reset": 1, "restart": 1}))


def request_restart(ip):
    asyncio.run(request(ip, PUT, {"restart": 1}))


def request_update(ip, url, signature):
    asyncio.run(request(ip, PUT, {"update": {"url": url, "signature": signature}}))
