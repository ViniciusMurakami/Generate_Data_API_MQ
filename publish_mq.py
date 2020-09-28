import pika

class Publish_MQ:
    def __init__(self, host, queue, message):
        self.host = host
        self.queue = queue
        self.message = message

    def publish(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        channel = connection.channel()
        channel.queue_declare(queue=self.queue, durable=True)
        channel.basic_publish(exchange='',
                            routing_key=self.queue,
                            body=self.message,
                            properties=pika.BasicProperties(delivery_mode=2)
        )
        return True