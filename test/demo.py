import asyncio


async def main():
    loop = asyncio.get_event_loop()
    print("running event loop", loop)

    print("hello ...")
    await asyncio.sleep(1)
    print("world")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    print("running event loop", loop)
    co = main()
    print(co)
    asyncio.run(co, debug=True)
    asyncio.run(main())

