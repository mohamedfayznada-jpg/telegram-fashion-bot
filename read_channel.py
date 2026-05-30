async def main():
    await client.start()

    channel = await client.get_entity("yasminstoriii")

    messages = await client.get_messages(
        channel,
        limit=5
    )

    for i, msg in enumerate(messages):
        print("=" * 50)
        print("MESSAGE", i + 1)
        print("ID:", msg.id)
        print("TEXT:", repr(msg.message))
        print("MEDIA:", msg.media is not None)
