from json import JSONEncoder

class TrustEncodable():
    def toJson(self) -> dict:
        pass

class TrustEnconder(JSONEncoder):
    def default(self, o: TrustEncodable):
        return o.toJson()