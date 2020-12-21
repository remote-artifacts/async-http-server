import unittest
import requests
import time
import multiprocessing
import async_http_server


def server():
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
                       "params": body

                   }, 200
        else:
            return {
                       "Error": "Please provide the led and the status"
                   }, 400

    def handle_params(params, body):
        return params, 200

    async_http_server.router.update({
        "": index,
        "/": index,
        "/led": handle_leds,
        "/params": handle_params
    })

    # By using the `asyncio` from async_http_server you will load the proper asyncio library (uasyncio for the case of embedded device)
    loop = async_http_server.asyncio.get_event_loop()
    loop.create_task(async_http_server.asyncio.start_server(async_http_server.handle_client, '0.0.0.0', 8080))
    print("Listening port: 8080")
    loop.run_forever()



class TestApiMethods(unittest.TestCase):

    def setUp(self):
        self.s = multiprocessing.Process(target=server)
        self.s.start()

    def tearDown(self):
        self.s.terminate()
        self.s.join()

    def test_index(self):
        with open("www/index.html") as f:
            real_content = f.read()

        res = requests.get("http://localhost:8080")
        code = res.status_code
        content = res.text
        self.assertEqual(content, real_content)
        self.assertEqual(code, 200)

        with open("www/index.html") as f:
            real_content = f.read()

        res = requests.get("http://localhost:8080/")
        code = res.status_code
        content = res.text
        self.assertEqual(content, real_content)
        self.assertEqual(code, 200)

    def test_path_attack(self):
        res = requests.get("http://localhost:8080/../LICENSE")
        code = res.status_code
        self.assertEqual(code, 404)

    def test_body(self):
        res = requests.post("http://localhost:8080/led", json={"key": "value", "test": "yep"})
        code = res.status_code

        self.assertEqual(code, 400)


        payload = {"status": "aa", "led": "bb", "key": "value", "test": "yep"}
        res = requests.post("http://localhost:8080/led", json=payload)
        code = res.status_code
        content = res.json()

        self.assertEqual(content["params"], payload)
        self.assertEqual(code, 200)

    def test_method_error(self):
        res = requests.get("http://localhost:8080/led")
        code = res.status_code
        self.assertEqual(code, 500)


    def test_params(self):
        res = requests.get("http://localhost:8080/params?foo=bar")
        code = res.status_code
        self.assertEqual(code, 200)
        self.assertEqual(res.json(), {"foo": "bar"})
