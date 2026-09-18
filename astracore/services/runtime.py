from __future__ import annotations
import asyncio
class BackgroundSupervisor:
 def __init__(self):self.tasks=set()
 def spawn(self,coro,name):
  task=asyncio.create_task(coro,name=name);self.tasks.add(task);task.add_done_callback(self.tasks.discard);return task
 async def cancel_all(self):
  for task in list(self.tasks):task.cancel()
  if self.tasks:await asyncio.gather(*self.tasks,return_exceptions=True)
supervisor=BackgroundSupervisor()
