# async-http-server
A very simple and fast http server focused on embedded devices

![Tests](https://github.com/remote-artifacts/async-http-server/workflows/test/badge.svg)

# WHY
I wanted a really fast and light web server. Something that can runs on
things like `esp32`. There was other solutions out there but all are very slow.
I need something that responds in less than 1 second.

# Features
* Fully async: It uses asyncio so it can handles a lot of requests concurrently but consuming a few resources
* Simple: It just does one thing. No fancy or cool features, just handling http connections as much raw as possible
* Easy to use: You only need your routes and your functions that generate your content
* Non blocking: You can do your stuff in your microcontroller while the server is running
* Static files: Static files like HTML or CSS can be served just by putting them in the `www` directory

# Example
```
import async_http_server


def set_led_status(led_name, status):
    # here my logic to handle the led status
    print("Setting led {led_name} status to {status}".format(led_name=led_name, status=status))


def index(params, body):
    with open("www/index.html", "r") as f:
        return f.read(), 200


def handle_leds(params, body):
    if "status" in body and "led" in body:
        set_led_status(body["led"], body["status"])
        return {
            "status": "ok",
            "params": params

        }, 200
    else:
        return {
            "Error": "Please provide the led and the status"
        }, 400


async_http_server.router.update({
    "": index,
    "/": index,
    "/led": handle_leds
})

# By using the `asyncio` from async_http_server you will load the proper asyncio library (uasyncio for the case of embedded device)
loop = async_http_server.asyncio.get_event_loop()
loop.create_task(async_http_server.asyncio.start_server(async_http_server.handle_client, '0.0.0.0', 8080))
print("Listening port: 8080")
loop.run_forever()
```

# TODO
* Url variables support (like http://host/:led/status)