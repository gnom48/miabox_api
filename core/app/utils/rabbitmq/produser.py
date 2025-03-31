from aio_pika import connect_robust, Message, Queue, Channel, IncomingMessage
from app.toml_helper import load_data_from_toml
import os
import asyncio
import logging
from .models import MsgQueued, MsgProccess, MsgComplete
from app.database.repositories import CallsRepository

__queues_names = ["queued", "process", "complete"]
__encoding_to = "utf-8"


async def send_message_to_queue(
    call_id: str,
    object_name: str,
    bucket_name: str
) -> bool:
    try:
        rabbitmq_data = load_data_from_toml()
        connection = await connect_robust(
            host=rabbitmq_data["services"]["rabbitmq_host"],
            port=int(rabbitmq_data["services"]["rabbitmq_port"]),
            login=rabbitmq_data["services"]["rabbitmq_user"],
            password=rabbitmq_data["services"]["rabbitmq_password"]
        )

        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue("queued", durable=True)
            new_msg_data = MsgQueued(
                call_id=call_id,
                file_path="",
                object_name=object_name,
                bucket_name=bucket_name
            )
            complete_message = Message(
                body=new_msg_data.to_json().encode(__encoding_to),
                content_type="application/json",
                headers={"status": "ok"}
            )
            await channel.default_exchange.publish(
                complete_message, routing_key="queued"
            )
            logging.debug("Сообщение отправлено в очередь queued")
            return True
    except Exception as e:
        logging.error("Ошибка отправки сообщения", exc_info=True)
        return False


async def on_message_complete(incoming_message: IncomingMessage):
    async with incoming_message.process():
        logging.debug(
            f"Получено сообщение в complete: {incoming_message.body.decode(__encoding_to)}")
        try:
            msg_data = MsgComplete.from_json(
                incoming_message.body.decode(__encoding_to))

            calls_repo = CallsRepository.repository_factory()
            async with calls_repo:
                calls_repo.update_transcription(
                    msg_data.call_id, msg_data.result)

            await incoming_message.ack()
        except Exception as e:
            logging.error("Ошибка обработки сообщения", exc_info=True)
            await incoming_message.nack()


async def listen():
    global channel

    rabbitmq_data = load_data_from_toml()
    connection = await connect_robust(
        host="rabbitmq",
        port=rabbitmq_data["services"]["rabbitmq_port"],
        login=rabbitmq_data["services"]["rabbitmq_user"],
        password=rabbitmq_data["services"]["rabbitmq_password"]
    )

    async with connection:
        channel = await connection.channel()

        queues: dict[str, Queue] = {}
        for queue_name in __queues_names:
            queues[queue_name] = await channel.declare_queue(queue_name, durable=True)

        await queues["complete"].consume(on_message_complete)
        logging.debug("Ожидание сообщений...")

        await asyncio.Future()
