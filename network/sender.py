from service.service import get_connection


async def send_msgs(host, port, token, sending_queue, watchdog_queue, logger):
    async with get_connection(host, port) as (reader, writer):
        await reader.readline()
        writer.write(token.encode() + b"\n")
        await writer.drain()

        while True:
            message = await sending_queue.get()
            message_edited = "".join(message).replace("\n", "")
            logger.debug(f"Соообщение: {message_edited}")
            writer.write(message_edited.encode() + b"\n\n")
            await watchdog_queue.put("Message sent")
            await writer.drain()