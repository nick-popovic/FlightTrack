import json
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from multiprocessing import Pool as ThreadPool
import re

import os


'''
get_flights(CARRIER_CDE) -> [str]
Gets the list of flight summary strings for a particular carrier code
'''
def get_flights(CARRIER_CDE, offset):

    ret = []
    links_found = 0

    print("======== Get Flight Listings ========")

    URL = "https://flightaware.com/live/fleet/"+CARRIER_CDE+"?;offset="+str(offset)
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')

    links = soup.findAll("a")

    # get all links but filter out the relevant ones that give info on flights
    for link in links:

        if "/live/flight/id/" + CARRIER_CDE in link['href']:
            flight_link = "https://flightaware.com" + link['href']

            print("\tFound link: {}".format(flight_link))
            links_found += 1
            ret.append(flight_link)

    print("Found {} links".format(links_found))
    
    return ret

def flight_data_load(FLIGHT_URL):

    session = HTMLSession()
    r = session.get(FLIGHT_URL)
    r.html.render(timeout=15, wait=5, retries=10)

    soup = BeautifulSoup(r.html.html, 'html.parser')

    '''
    Get STATION info:
    > orig_code: IATA airport code (departure station)
    > orig_delay_msg: message that indicates some sort of delay going on at departure airport - defaults to 'None'

    > dest_code: IATA airport code (arrival station)
    > dest_delay_msg: message that indicates some sort of delay going on at arrival airport - defaults to 'None'
    '''

    orig = soup.select("div.flightPageSummaryAirports div.flightPageSummaryOrigin")
    # for some reason, this seems to contain a list of 2 results (at least) ... just pick the first
    orig_code = BeautifulSoup(str(orig[0]), 'html.parser').select("span.displayFlexElementContainer")[0].text.strip()
    try:
        orig_delay_msg = BeautifulSoup(str(orig[0]), 'html.parser').select("span.flightPageSummaryAirportDelay")[0][
            'data-tip'].strip()
    except IndexError:
        orig_delay_msg = "None"


    # try to get the delay message ...

    delay_messages = soup.select("div.flightPageDelayMessage ul")
    #print(delay_messages)
    
    for delay_message in delay_messages:
        print("\t|---> " + delay_message.text.strip())


    dest = soup.select("div.flightPageSummaryAirports div.flightPageSummaryDestination")
    # for some reason, this seems to contain a list of 2 results (at least) ... just pick the first
    dest_code = BeautifulSoup(str(dest[0]), 'html.parser').select("span.displayFlexElementContainer")[0].text.strip()
    try:
        dest_delay_msg = BeautifulSoup(str(dest[0]), 'html.parser').select("span.flightPageSummaryAirportDelay")[0][
            'data-tip'].strip()
    except IndexError:
        dest_delay_msg = "None"

    print(orig_code, orig_delay_msg)
    print(dest_code, dest_delay_msg)

    # Find the JSON data string from the script code
    pattern = "<script>[\\n]?var[ ]*trackpollBootstrap[ ]*=[ ]*({\"version\":.*)[ ]*;[ ]*[\\n]?<\/script>"
    p = re.compile(pattern)
    JSON_DATA_STRING = p.search(r.html.html).group(1)

    try:
        JSON_DATA = json.loads(JSON_DATA_STRING)
        print(JSON_DATA)
        print(type(JSON_DATA))
        print("+++found-data+++")
    except ValueError as e:
        print("Error Parsing JSON string")


# Entry Point
if __name__ == '__main__':

    
    import time
    import os
    
    start_time = time.time()
    WORKERS = 5
    offset = 0
    keep_going = True

    
    while keep_going:

        #list of flight urls to parse
        flights = get_flights('ACA', offset)
        
        # exit condition for loop: the run produced no links
        if len(flights) == 0:
            break
        
        
        # Make the Pool of workers
        pool = ThreadPool(WORKERS)

        # Open the URLs in their own threads
        # and return the results
        results = pool.map(flight_data_load, flights)

        # Close the pool and wait for the work to finish
        pool.close()
        pool.join()
        


        offset += 20 # try next batch of flights

        print("batch# "+ str((offset/20)+1) +"complete - time to sleep ..")

        os.system("killall chrome")
        time.sleep(2)


    print("--- %s seconds ---" % (time.time() - start_time))