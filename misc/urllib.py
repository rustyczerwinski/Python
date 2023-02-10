# using urllib to request data

# TODO: import the urllib request class
# import urllib3
import requests

def main():
    # the URL to retrieve our sample data from
    url = "http://httpbin.org/xml"

    # TODO: open the URL and retrieve some data
    # http = urllib3.PoolManager()
    result = requests.get(url)

    # TODO: Print the result code from the request, should be 200 OK
    print("Result code: {0}".format(result.status))

    # TODO: print the returned data headers
    print("Headers: ----------------------")

    # TODO: print the returned data itself
    print("Returned data: ----------------------")


if __name__ == "__main__":
    main()
