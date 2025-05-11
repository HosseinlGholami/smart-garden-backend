FROM rabbitmq:3.12

RUN rabbitmq-plugins enable rabbitmq_management
RUN rabbitmq-plugins enable rabbitmq_mqtt 
RUN rabbitmq-plugins enable rabbitmq_prometheus

EXPOSE 1883
EXPOSE 5672
EXPOSE 15672
EXPOSE 15692
