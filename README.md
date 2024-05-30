# streaming-05-smart-smoker
Repository for Streaming Project 5: Creating a Producer

# Topaz Montague

# Project Repository: [Project  - Creating a Producer-Smart Smoker](https://github.com/tfmontague/streaming-05-smart-smoker)

## Project Overview

> This project is to design and implement a Smart Smoker program that monitors the temperature of a smoker and food.

The Smart Smoker program processes a CSV file to set up a producer with three task queues. It simulates continuous temperature readings from a smart smoker and two food items, capturing temperatures every 30 seconds.

The smoker-temp.csv file includes four columns: [0] Date-time stamp, [1] Smoker temperature, [2] Food A temperature, and [3] Food B temperature.

| Date-time stamp | Smoker temperature | Food A temperature | Food B temperature |
|-----------------|--------------------|--------------------|--------------------|

Three consumers are assigned to the producer, each one dedicated to a specific temperature queue.

## Project Approach

Python will be used to:

- Simulate a streaming series of temperature readings from our smart smoker and two foods.
- Create a producer to send these temperature readings to RabbitMQ.
- Create three consumer processes, each one monitoring one of the temperature streams. 
- Perform calculations to determine if a significant event has occurred.

## NOTE: The focus of this repository is Creating a Producer. Information provided below is limited to executing the producer file. Additional guidance on executing the full Smart Smoker app will be provided in future repositories.

## Prerequisites

- RabbitMQ server running
- Pika installed in the active Python environment

## Running the Program

- Open VS Code Terminal
- Run `python bbq-producer.py`

## Screenshot

- BBQ Producer Process
![alt text](<Screenshot 2024-05-29 210915.png>)


