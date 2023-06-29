import csv
import asyncio
import logging
import termux

# turned off by default
DISABLE_CONSOLE_LOGGING = False

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.disabled = DISABLE_CONSOLE_LOGGING


def validate_csv_file(csv_file):
    """
    This function validates a csv file for some needed requirements
    returns True on success, False otherwise
    """
    try:
        with open(csv_file, "r") as file:
            csv_reader = csv.reader(file)
            headers = next(csv_reader)  # Skip header row
            for row in csv_reader:
                if len(row) != 5:
                    logger.info(f"CSV file columns not equal to 5")
                    return False
                if not row[0].isdigit() or len(row[0]) != 11:
                    return False
                if not all(row[1:]):
                    return False
    except FileNotFoundError:
        logger.info(f"CSV file {csv_file} cannot be found.")
        return False
    except Exception as e:
        logger.info(f"Unknown exception : {e.message}")
        return False

    return True


def read_csv_file(csv_file):
    """
    returns a list containing the rows from the CSV File, converted into list of dict
    """
    if not validate_csv_file(csv_file):
        logger.info("Aborting program, validation had failed")
        return None

    data = []

    # Read the CSV file and convert into a list of dictionary
    with open(csv_file, "r") as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)  # Skip header row
        logger.info("Reading the csv list rows")
        for row in csv_reader:
            item = {
                "mobile": row[0],
                "firstName": row[1],
                "lastName": row[2],
                "id": row[3],
                "message": row[4],
            }
            data.append(item)
    return data


async def sms_send(sms):
    """
    async function that sends an SMS
    """
    # Simulating sending an SMS
    logger.info(f"Sending SMS to {sms['mobile']}...")
    number = sms["mobile"]
    recipient = f"sms['firstName] sms['lastName]"

    # this is the message that the recipient will receive
    # make sure to use correct variable name for firstName, lastName etc..
    message_to_send = f"""
    id: {sms['id']}
    firstname: {sms['firstName']}
    lastname: {sms['lastName']}!
    mobile number: {sms['mobile']}
    message: {sms['message']}
    """

    # the function that made me write this app
    termux.SMS.send(message_to_send, number)

    # provide result
    print(f"Message sent to the {number}, Recipient's name : {recipient}")
    logger.info(f"SMS sent to {sms['firstName']} {sms['lastName']}: {sms['message']}")


async def send_sms_async(sms):
    """
    Wrapper function for sms_send
    """
    await sms_send(sms)


async def main(sms_list):
    """
    schedules every sms_send as tasks, assigns to worker threads (i think!)
    and gather the results
    """
    tasks = [send_sms_async(sms) for sms in sms_list]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # replace sms_list.csv with your own CSV file, make sure to follow column formats
    message_list = read_csv_file("sms_list.csv")
    # send text asynchronously
    asyncio.run(main(message_list))
