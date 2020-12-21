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