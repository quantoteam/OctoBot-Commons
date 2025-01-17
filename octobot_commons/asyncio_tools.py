#  Drakkar-Software OctoBot-Commons
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
import asyncio
import traceback

import octobot_commons.constants as constants
import octobot_commons.logging as logging_util

LOGGER = logging_util.get_logger("asyncio_tools")


def run_coroutine_in_asyncio_loop(coroutine, async_loop):
    """
    Run a coroutine in the specified asyncio loop
    :param coroutine: the coroutine to run
    :param async_loop: the asyncio loop
    :return: the execution result
    """
    current_task_before_start = asyncio.current_task(async_loop)
    future = asyncio.run_coroutine_threadsafe(coroutine, async_loop)
    try:
        return future.result(constants.DEFAULT_FUTURE_TIMEOUT)
    except asyncio.TimeoutError as timeout_error:
        LOGGER.error(
            f"{coroutine} coroutine took too long to execute, cancelling the task. "
            f"(current task before starting this one: {current_task_before_start}, actual current "
            f"task before cancel: {asyncio.current_task(async_loop)})"
        )
        future.cancel()
        raise timeout_error
    except Exception as global_exception:
        LOGGER.exception(
            global_exception,
            True,
            f"{coroutine} coroutine raised an exception: {global_exception}",
        )
        raise global_exception


class ErrorContainer:
    """
    ErrorContainer is used to catch exceptions in as asyncio loop context
    """

    def __init__(self):
        self.errors = []
        # set to True when investigating post loop closing exceptions (ex: on task __del__)
        self.print_received_exceptions = True

    def exception_handler(self, _, context) -> None:
        """
        To be set in the watched asyncio loop via loop.set_exception_handler()
        :param _: the loop argument, not used
        :param context: the context dict of the exception
        :return: None
        """
        self.errors.append(context)
        if self.print_received_exceptions:
            print(context)
            error = context.get("exception")
            if error:
                traceback.print_exception(
                    etype=type(error), value=error, tb=error.__traceback__
                )

    async def check(self) -> None:
        """
        Will raise AssertionError if an exception has been raised in the registered loop(s)
        :return: None
        """
        if self.errors:
            raise AssertionError("\n".join(f"{e}" for e in self.errors))


async def wait_asyncio_next_cycle():
    """
    Wait for next asyncio next loop cycle
    """

    async def do_nothing():
        pass

    await asyncio.create_task(do_nothing())


class RLock(asyncio.Lock):
    """
    Async Lock implementing reentrancy
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._task = None
        self._depth = 0

    async def acquire(self):
        if self._task is None or self._task is not asyncio.current_task():
            await super().acquire()
            self._task = asyncio.current_task()
            if self._depth != 0:
                raise RuntimeError(
                    f"Async RLock acquired when depth !=0 (depth = {self._depth})."
                )
        self._depth += 1
        return True

    def release(self):
        if self._depth > 0:
            self._depth -= 1
        if self._depth == 0:
            super().release()
            self._task = None
