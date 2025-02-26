
import requests
import json
import os

FLOWER_CHECK_TASK_URL = "http://celery:6666/flower/api/tasks"


# TODO: GET /api/task/info/(.*) inside "https://flower.readthedocs.io/en/latest/api.html" doesnt work instead I get it form web page!
def get_url_flower_check_task(_id):
    return f"http://celery:6666/flower/task/{_id}"


def request_flower_check_task(task_id):
    response = requests.get(get_url_flower_check_task(task_id))
    response = str(response.content)
    start_pattern = "<td>State</td>"
    start_index = response.find(start_pattern)+len(start_pattern)

    end_pattern = "</span>"
    end_index = response.find(end_pattern, start_index)

    excat_start_pattern = "\">"
    excat_start_point = response.find(
        excat_start_pattern, start_index, end_index) + len(excat_start_pattern)
    output = response[excat_start_point:end_index]
    if len(output) > 10:
        output = "NOTEXIST"
    return output


def check_beat_is_activate():
    response = requests.get(FLOWER_CHECK_TASK_URL)
    response = str(response.content)
    if ("reset_worker_task_for_problem_case" in response):
        return True
    return False


def purge_rabbitmq_queue(username, password, rabbitmq_address, virtual_host, queue_name, port=15672):
    print("purge_rabbitmq_queue")
    print("==========")

    # RabbitMQ management API endpoint to purge a queue
    management_api_url = f'http://{rabbitmq_address}:{port}/rabbit/api/queues/{virtual_host}/{queue_name}/contents'

    # Sending a DELETE request to purge the queue
    response = requests.delete(
        management_api_url,
        auth=(username, password),
    )

    if response.status_code == 204:
        print(
            f"The '{queue_name}' queue in the '{virtual_host}' virtual host has been purged.")
    else:
        print(
            f"Failed to purge the '{queue_name}' queue. Status code: {response.status_code}")
        print(response.text)


def request_from_supernova_get_active_basket_dict():
    url = "https://fc.digikala.com/api/automation/presort/ready-holders"
    payload = {}
    headers = {
        'api-key': 'A1DBACA8B217675FA7F6D8B27F70B580E7BDF38343B30B83B2971C3063969E7A13E2329129393301F86A53D993923D7AADDD0973606D0F78CA40117AF026E3C5',
        'Cookie': 'tracker_glob_new=fQZCZVo; tracker_session=cIDsov4'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    barcode_data = json.loads(response.text)

    barcode_dict = {data["holder_code"]: data["pigeon_id"]
                    for data in barcode_data['holders']}

    return barcode_dict


def supernova_inquiry_url(_id):
    return f"https://fc.digikala.com/api/presort/holder/{_id}/pigeon?Authorization=d3947cf7f9deaf82cabcde97c7ca2c5fdd377692"


def request_from_supernova_without_timeout(barcode):
    response = requests.get(supernova_inquiry_url(barcode))
    code = str(response)[-5:-2]
    erorr = str(response.content)[:200]
    if int(code) == 200:
        try:
            data = json.loads(response.content)
            try:
                return (1, data['result']['pigeon'])
            except:
                return (0, str(data))
        except:
            return (0, f"{code}->{erorr}")
    else:
        return (0, f"{code}->{erorr}")
