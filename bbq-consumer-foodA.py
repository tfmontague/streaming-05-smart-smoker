""" 
BBQ Consumer A
Name: Topaz Montague
Date: 5/29/24

File Description & Approach:
This Python script monitors "Food A" temperature by reading messages from a RabbitMQ 
queue and tracking recent readings with a deque. If the temperature change is minimal 
over 10 minutes, it sends an email alert using SMTP based on configurations from a TOML file. 
The script establishes a RabbitMQ connection, manages the queue, and processes messages 
with a callback function, ensuring robust error handling and graceful shutdown. 
It requires Python 3.11 for TOML support and includes a main function for 
direct execution and proper module importation.

"""

from collections import deque
from email.message import EmailMessage
import pika
import pprint
import smtplib
import sys
import tomllib  # requires Python 3.11

# declare variables
foodA_temp_queue = "02-food-A"
foodA_deque = deque(maxlen=20)  # limited to 20 items (the 20 most recent readings)
subject_str = "FOOD A STALL"
content_str = "FOOD A STALL: Food A temp has changed by 1 degree or less in the last 10 minutes."

# define a function to send email alerts
def CreateAndSendEmailAlert(email_subject: str, email_body: str):
  
    """Read outgoing email info from a TOML config file"""

    with open(".env.toml", "rb") as file_object:
        secret_dict = tomllib.load(file_object)
    pprint.pprint(secret_dict)

    # basic information

    host = secret_dict["outgoing_email_host"]
    port = secret_dict["outgoing_email_port"]
    outemail = secret_dict["outgoing_email_address"]
    outpwd = secret_dict["outgoing_email_password"]

    # Create an instance of an EmailMessage

    msg = EmailMessage()
    msg["From"] = secret_dict["outgoing_email_address"]
    msg["To"] = secret_dict["outgoing_email_address"]
    msg["Reply-to"] = secret_dict["outgoing_email_address"]
    msg["Subject"] = email_subject
    msg.set_content(email_body)

    print("========================================")
    print(f"Prepared Email Message: ")
    print("========================================")
    print()
    print(f"{str(msg)}")
    print("========================================")
    print()

    try:
        if port == 465:
            # Use SMTP_SSL for port 465
            server = smtplib.SMTP_SSL(host, port)
        else:
            # Use SMTP for port 587
            server = smtplib.SMTP(host, port)
            server.starttls()
        
        server.set_debuglevel(2)

        print("========================================")
        print(f"SMTP server created: {str(server)}")
        print("========================================")
        print()

        server.login(outemail, outpwd)
        print("========================================")
        print(f"Successfully logged in as {outemail}.")
        print("========================================")
        print()

        server.send_message(msg)
        print("========================================")
        print(f"Message sent.")
        print("========================================")
        print()
    except Exception as e:
        print(f"Failed to connect or send email: {e}")
    finally:
        server.quit()
        print("========================================")
        print(f"Session terminated.")
        print("========================================")

# define a callback function to be called when a message is received
def foodA_callback(ch, method, properties, body):
    """ Define behavior on getting a message about the temperature of food A"""
    #define a list to place food A temps initializing with 0
    foodAtemp = ['0']
    # split timestamp and temp
    message = body.decode().split(",")
    # assign the temp to a variable and convert to float
    foodAtemp[0] = float(message[-1])
    # add the temp to the deque
    foodA_deque.append(foodAtemp[0])
    # check to see that the deque has 20 items before analyzing
    if len(foodA_deque) == 20:
        # assign difference in most recent temp and oldest temp in deque to a variable as a float
        foodA_temp_check = round(float(foodA_deque[-1]-foodA_deque[0]), 1)
        # if the temp has changed by 1 degree or less in 10 minutes, then an alert is sent
        if foodA_temp_check <= 1:
            print("FOOD STALL: Current food A temp is:", foodAtemp[0],";", "Food A temp change in last 10 minutes is:", foodA_temp_check, "degrees")
            # send user an email alert
            CreateAndSendEmailAlert(subject_str, content_str)
        
        # let user know current temp
        else:
            print("Current food A temp is:", foodAtemp[0])
    else:
        #if the deque has less than 20 items the current temp is printed
        print("Current food A temp is:", foodAtemp[0])
    # acknowledge the message was received and processed 
    # (now it can be deleted from the queue)
    ch.basic_ack(delivery_tag=method.delivery_tag)


# define a main function to run the program
def main(hn: str = "localhost", qn: str = "task_queue"):
    """ Continuously listen for task messages on a named queue.
    
    Parameters:
        host (str): the host name or IP address of the RabbitMQ server
        foodA_temp_queue (str): food A queue
        """

    # when a statement can go wrong, use a try-except block
    try:
        # try this code, if it works, keep going
        # create a blocking connection to the RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hn))

    # except, if there's an error, do this
    except Exception as e:
        print()
        print("ERROR: connection to RabbitMQ server failed.")
        print(f"Verify the server is running on host={hn}.")
        print(f"The error says: {e}")
        print()
        sys.exit(1)

    try:
        # use the connection to create a communication channel
        channel = connection.channel()

        # use the channel to clear the queue
        channel.queue_delete(foodA_temp_queue)
        
        # use the channel to declare a durable queue
        # a durable queue will survive a RabbitMQ server restart
        # and help ensure messages are processed in order
        # messages will not be deleted until the consumer acknowledges
        channel.queue_declare(foodA_temp_queue, durable=True)

        # The QoS level controls the # of messages
        # that can be in-flight (unacknowledged by the consumer)
        # at any given time.
        # Set the prefetch count to one to limit the number of messages
        # being consumed and processed concurrently.
        # This helps prevent a worker from becoming overwhelmed
        # and improve the overall system performance. 
        # prefetch_count = Per consumer limit of unaknowledged messages      
        channel.basic_qos(prefetch_count=1) 

        # configure the channel to listen on a specific queue,  
        # use the callback function named foodA_callback,
        # and do not auto-acknowledge the message (let the callback handle it)
        channel.basic_consume(foodA_temp_queue, auto_ack = False, on_message_callback=foodA_callback)

        # print a message to the console for the user
        print(" [*] Ready for work. To exit press CTRL+C")

        # start consuming messages via the communication channel
        channel.start_consuming()

    # except, in the event of an error OR user stops the process, do this
    except Exception as e:
        print()
        print("ERROR: something went wrong.")
        print(f"The error says: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print()
        print(" User interrupted continuous listening process.")
        sys.exit(0)
    finally:
        print("\nClosing connection. Goodbye.\n")
        connection.close()

# Standard Python idiom to indicate main program entry point
# This allows us to import this module and use its functions
# without executing the code below.
# If this is the program being run, then execute the code below
if __name__ == "__main__":
    # call the main function with the information needed
    main("localhost", "foodA_temp_queue")
