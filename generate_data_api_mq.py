import sys
import publish_mq
import request_api
import configparser
import time
import json

###### Help Function explaining the usage of this script
def help():
    print("How-to use this script:")
    print("\tpython generate_data_api_mq.py [ini_file] [payload_file]\n")
    print("About parameters:")
    print("\t[ini_file] Should contain at least 6 variables plus a section header:")
    print("\t\t[SECTION_NAME] - As any .ini file, your file must have a section header. E.g. [Something] in the 1st line")
    print("\t\tENDPOINT={the name of the endpoint you're trying to reach}")
    print("\t\tMETHOD={GET or POST}")
    print("\t\tHOST={the machine where mqserver is installed}")
    print("\t\tQUEUE={the name of the queue you're looking for}")
    print("\t\tNUM_REQUESTS={Amount of requests to be done, if empty or method=POST default value will be 1}")
    print("\t\tTIME_INTERVAL_REQUESTS={Time in seconds to trigger the requests, default value 10 not applied for POST}")
    print("\t[payload_file] *OPTIONAL argument* file where your post data resides")
    exit(0)

###### Checker to compare the expected variables against the ini file, called inside the ini_reader()
def ini_checker(list_variable):
    list_template = [ 'ENDPOINT', 'METHOD', 'HOST', 'QUEUE', 'NUM_REQUESTS', 'TIME_INTERVAL_REQUESTS' ]
    if len(set(list_template).intersection(list_variable)) != len(list_template):
        raise Exception("Invalid variable set in your ini file")

###### Function to read the ini config file
def ini_reader(file):
    config = configparser.ConfigParser()
    config.read(file)
    
    if len(config.sections()) >= 2:
        raise Exception("More than 1 section not allowed")
    else:
        section = ''.join(config.sections())
        list_variable = [str(key).upper() for key in config[section]]
        ini_checker(list_variable=list_variable)
        return config[section]

###### Main Function receives data from some API endpoint and send it to a MQ     
def start():
    # Without arguments, display the help msg
    if len(sys.argv) == 1:
        help()

    # 1 argument = ini file
    elif len(sys.argv) == 2:
        #For Debug purposes
        """ print("Metodo utilizado: {}".format(variables.get("METHOD")))
            print("Endpoint utilizado: {}".format(variables.get("ENDPOINT")))
            print("Host do MQ: {}".format(variables.get("HOST")))
            print("Queue: {}".format(variables.get("QUEUE")))
            print("Numero de Requests: {}".format(variables.get("NUM_REQUESTS")))
            print("Intervalo em segs: {}".format(variables.get("TIME_INTERVAL_REQUESTS"))) """
        variables = ini_reader(file=sys.argv[1])
        num_requests = variables.get('NUM_REQUESTS') or 1
        time_interval_requests = variables.get('TIME_INTERVAL_REQUESTS') or 10

        for i in range(int(num_requests)):
            message = receive_data(variables=variables)
            send_data(variables=variables, message=message)
            print("Message Returned from API: {}".format(message))
            print("Request Round: {} \nSleeping for: {} seconds".format(i + 1, time_interval_requests))
            time.sleep(int(time_interval_requests))  

    # 2 argument = payload file for posting
    elif len(sys.argv) == 3:
        variables = ini_reader(file=sys.argv[1])
        payload_file = sys.argv[2]
        return_post = receive_data(variables=variables, payload=payload_file)
        print(return_post)        

    else:
        raise Exception("Number of arguments unknown\n")

###### Function to interact with API and relies on Request_API Class    
def receive_data(variables, payload = ''):
    endpoint = variables.get('ENDPOINT')
    method = variables.get('METHOD')
    call = request_api.Request_API(endpoint=endpoint, method=method, payload=payload)
    message = call.request_api()
    return message.json()

###### Function to retrieve some messsage and send to a MQ that depends on Publish_MQ Class
def send_data(variables, message):
    host = variables.get('HOST')
    queue = variables.get('QUEUE')
    produce = publish_mq.Publish_MQ(host=host, queue=queue, message=str(message))
    if produce.publish():
        print("Sent msg for mq: {} in the queue: {} at {}".format(host, queue, time.ctime()))
    else:
        raise Exception("Something went wrong")

if __name__ == "__main__":
    start()