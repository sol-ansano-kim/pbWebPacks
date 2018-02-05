# How to use it
# 1. Install google map python api
#    $ pip install googlemaps --user
# 2. Get the API key
#    https://developers.google.com/maps/documentation/geocoding/get-api-key  
# 3. Ensure google API is activated in the Google Developers Console:
#    https://console.developers.google.com/apis/api/geocoding_backend?project=_
#    https://console.developers.google.com/apis/api/places_backend?project=_
#    ...


import googlemaps
from petitBloc import block


class Client(object):
    def __init__(self, key):
        self.__key = key
        self.__client = googlemaps.Client(self.__key)

    def key(self):
        return self.__key

    def client(self):
        return self.__client


class GeoCode(object):
    def __init__(self, geoDict):
        self.__geo = geoDict

    def location(self):
        loc = self.__geo.get("geometry", {}).get("location", {})
        if loc:
            return "{},{}".format(loc.get("lat"), loc.get("lng"))

        return ""

    def formattedAddress(self):
        return self.__geo.get("formatted_address", "")



class GoogleMapClient(block.Block):
    def __init__(self):
        super(GoogleMapClient, self).__init__()

    def initialize(self):
        self.addParam(str, "key")
        self.addOutput(Client, "client")

    def run(self):
        key = self.param("key").get()
        self.output("client").send(Client(key))


class GoogleMapFind(block.Block):
    def __init__(self):
        super(GoogleMapFind, self).__init__()

    def initialize(self):
        self.addInput(Client, "client")
        self.addInput(str, "address")
        self.addOutput(GeoCode, "geocode")

    def run(self):
        client = self.input("client").receive()
        if client.isEOP():
            return

        self.__client = client.value().client()
        client.drop()

        super(GoogleMapFind, self).run()

    def process(self):
        if self.__client is None:
            return False

        ad_p = self.input("address").receive()
        if ad_p.isEOP():
            return False

        address = ad_p.value()
        ad_p.drop()

        geo = self.__client.geocode(address)
        for g in geo:
            self.output("geocode").send(GeoCode(g))

        return True


class GoogleMapPlaces(block.Block):
    def __init__(self):
        super(GoogleMapPlaces, self).__init__()

    def initialize(self):
        self.addInput(Client, "client")
        self.addInput(str, "keyword")
        self.addInput(GeoCode, "center")
        self.addOutput(GeoCode, "place")

    def run(self):
        client = self.input("client").receive()
        if client.isEOP():
            return

        self.__client = client.value().client()
        client.drop()

        self.__center_eop = False
        self.__center_dmp = None

        super(GoogleMapPlaces, self).run()

    def process(self):
        if self.__client is None:
            return False

        if not self.__center_eop:
            cen_p = self.input("center").receive()
            if cen_p.isEOP():
                self.__center_eop = True
            else:
                self.__center_dmp = cen_p.value()

        if self.__center_dmp is None:
            return False

        key_p = self.input("keyword").receive()
        if key_p.isEOP():
            return False

        keyword = key_p.value()
        key_p.drop()

        for p in self.__client.places(keyword, self.__center_dmp.location()).get("results"):
            self.output("place").send(GeoCode(p))

        return True


class GoogleMapURL(block.Block):
    UrlBase = "https://maps.googleapis.com/maps/api/staticmap?"

    def __init__(self):
        super(GoogleMapURL, self).__init__()

    def initialize(self):
        self.addParam(int, "width", value=640)
        self.addParam(int, "height", value=480)
        self.addParam(int, "zoom", value=15)
        self.addEnumParam("mapType", ["roadmap", "satellite", "terrain", "hybrid"])
        self.addEnumParam("format", ["png", "png32", "gif", "jpg"])
        self.addInput(Client, "client")
        self.addInput(GeoCode, "center")
        self.addInput(GeoCode, "place")
        self.addOutput(str, "url")

    def run(self):
        client_p = self.input("client").receive()
        if client_p.isEOP():
            return

        markers = ""
        center = ""
        key = ""

        client = client_p.value()
        client_p.drop()

        mt = self.param("mapType")
        width = self.param("width").get()
        width = 400 if width < 0 else width
        height = self.param("height").get()
        height = 400 if height < 0 else height
        zoom = self.param("zoom").get()
        zoom = 1 if zoom < 0 else zoom
        map_type = self.param("mapType").getLabel()
        format_name = self.param("format").getLabel()

        center_p = self.input("center").receive()
        if not center_p.isEOP():
            center_geo = center_p.value()
            center = "center={}".format(center_geo.location())
            markers += "&markers=color:red%7Clabel:C%7C{}".format(center_geo.location())

        place_in = self.input("place")
        while (True):
            place_p = place_in.receive()
            if place_p.isEOP():
                break

            place = place_p.value()
            place_p.drop()

            markers += "&markers=color:blue%7Clabel:P%7C{}".format(place.location())

        url = "{}{}{}&zoom={}&size={}x{}&maptype={}&format={}&key={}".format(GoogleMapURL.UrlBase, center, markers, zoom, width, height, map_type, format_name, client.key())
        self.output("url").send(url)
