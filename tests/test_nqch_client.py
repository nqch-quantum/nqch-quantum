from nqch_quantum.nqch_client import Client as NQCHClient


class TestNQCHClient:
    def test_init(self):
        client = NQCHClient(token="test")
        assert client.token == "test"
        assert client.base_url == "https://nqch.qibo.science"
