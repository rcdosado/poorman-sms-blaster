import csv
import asyncio
import logging
import concurrent.futures
import termux

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


def convert_csv_to_json(csv_file):
    if not validate_csv_file(csv_file):
        logger.info("Aborting program, validation had failed")
        exit(-1)

    data = []

    # Read the CSV file and convert each row to a dictionary
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

    # __import__('pdb').set_trace()
    return data


async def sms_send(sms):
    # Simulating sending an SMS
    logger.info(f"Sending SMS to {sms['mobile']}...")
    number = sms['mobile']
    message_to_send = f"""
    id: {sms['id']}
    firstname: {sms['firstName']}
    lastname: {sms['lastName']}!
    mobile number: {sms['mobile']}
    message: {sms['message']}
    """
    
    termux.SMS.send(message_to_send,number)
    print(f"Message sent to {number}")
    logger.info(f"SMS sent to {sms['firstName']} {sms['lastName']}: {sms['message']}")


async def send_sms_async(sms):
    await sms_send(sms)


async def main(sms_list):
    tasks = [send_sms_async(sms) for sms in sms_list]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    message_list = convert_csv_to_json("sms_list.csv")
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main(message_list))
