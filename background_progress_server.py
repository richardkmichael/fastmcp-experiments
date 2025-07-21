import asyncio
import logging

from fastmcp import Context, FastMCP

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="tmp/progress-notifications.log",
    filemode="a",
)

background_tasks: set[asyncio.Task] = set()

server = FastMCP("Progress", version="1.2.3")


async def background_work(count: int, ctx: Context) -> None:
    for message_number in range(1, count + 1):
        message = f"Background {message_number}"
        logging.info(message)
        await ctx.report_progress(progress=message_number, message=message)
        await asyncio.sleep(2)


@server.tool
async def send_progress(ctx: Context, count: int = 20) -> str:
    task = asyncio.create_task(background_work(count, ctx))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

    await asyncio.sleep(10)

    return "Done"


def main():
    server.run()


if __name__ == "__main__":
    main()
