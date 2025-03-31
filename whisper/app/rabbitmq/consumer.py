from aio_pika import connect_robust, Message, Queue, Channel, IncomingMessage
from app.toml_helper import load_data_from_toml
from app.minio_client import MinioClient, TMP_PATH
from app.transcription import AsyncWhisper
import os
import asyncio
import logging
from uuid import uuid4
from .models import MsgQueued, MsgProccess, MsgComplete

__minio_client: MinioClient
__async_whisper_model: AsyncWhisper
__queues_names = ["queued", "process", "complete"]
__encoding_to = "utf-8"


async def on_message_proccess(incoming_message: IncomingMessage):
    async with incoming_message.process():
        logging.debug(
            f"Получено сообщение в process: {incoming_message.body.decode(__encoding_to)}")
        try:
            msg_data = MsgProccess.from_json(
                incoming_message.body.decode(__encoding_to))

            result = await __async_whisper_model.transcribe_async(msg_data.file_path)

            new_msg_data = MsgComplete(call_id=msg_data.call_id, result=result)

            complete_queue = await channel.declare_queue("complete", durable=True)
            complete_message = Message(
                body=new_msg_data.to_json().encode(__encoding_to),
                content_type="application/json",
                headers={"status": "ok"}
            )
            await channel.default_exchange.publish(
                complete_message, routing_key=complete_queue.name
            )
            logging.debug("Сообщение перемещено в очередь complete")

            os.remove(msg_data.file_path)
            await incoming_message.ack()
        except Exception as e:
            logging.error("Ошибка обработки сообщения", exc_info=True)
            await incoming_message.nack()


async def on_message_queued(incoming_message: IncomingMessage):
    async with incoming_message.process():
        logging.debug(
            f"Получено сообщение в queued: {incoming_message.body.decode(__encoding_to)}")
        try:
            msg_data = MsgQueued.from_json(
                incoming_message.body.decode(__encoding_to))

            file_path = await __minio_client.download_file_to_temp(
                msg_data.bucket_name, msg_data.object_name, msg_data.file_path
            )

            new_msg_data = MsgProccess(
                call_id=msg_data.call_id, file_path=file_path)

            process_queue = await channel.declare_queue("process", durable=True)
            new_message_proccess = Message(
                body=new_msg_data.to_json().encode(__encoding_to),
                content_type="application/json"
            )
            await channel.default_exchange.publish(
                new_message_proccess, routing_key=process_queue.name
            )
            logging.debug("Сообщение перемещено в очередь process")

            await incoming_message.ack()
        except Exception as e:
            logging.error("Ошибка обработки сообщения", exc_info=True)
            await incoming_message.nack()


async def listen(minio_client: MinioClient, async_whisper_model: AsyncWhisper):
    global __minio_client, __async_whisper_model, channel
    __minio_client = minio_client
    __async_whisper_model = async_whisper_model

    rabbitmq_data = load_data_from_toml()

    connection = await connect_robust(
        host=rabbitmq_data["services"]["rabbitmq_host"],
        port=int(rabbitmq_data["services"]["rabbitmq_port"]),
        login=rabbitmq_data["services"]["rabbitmq_user"],
        password=rabbitmq_data["services"]["rabbitmq_password"]
    )

    async with connection:
        channel = await connection.channel()

        queues: dict[str, Queue] = {}
        for queue_name in __queues_names:
            queues[queue_name] = await channel.declare_queue(queue_name, durable=True)

        await queues["queued"].consume(on_message_queued)
        await queues["process"].consume(on_message_proccess)
        logging.debug("Ожидание сообщений...")

        await asyncio.Future()
