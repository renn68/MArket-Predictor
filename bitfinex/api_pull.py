import requests
import time
import datetime

# import util


def api_request(url, params, wait_time, start, end):

    data = []
    errors = 0
    count =1

    while end > start:

        print("\n Data Pull")

        r = requests.get(url, params=params)
        data.extend(r.json())

        if r.ok == False:
            errors += 1
            print("received error")
            print("trying again: " + str(errors))
            time.sleep(60)
            continue

        print(str(count) + ' data added at time')
        print(datetime.datetime.fromtimestamp(int(start / 1000)).strftime('%Y-%m-%d %H:%M:%S'))
        print("to")
        print(datetime.datetime.fromtimestamp(int(data[-1][0] / 1000)).strftime('%Y-%m-%d %H:%M:%S'))
        print("errors: " + str(errors))

        start = data[-1][0] + 300000
        params['start'] = start
        count += 1

        time.sleep(wait_time)

        pass

    return data