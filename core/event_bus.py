import asyncio
from typing import Callable, Coroutine, Dict, List, Any, Optional

# Alias de tipo para las callbacks de eventos
EventHandler = Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[EventHandler]] = {}
        self._queue = asyncio.Queue()
        self._running = False
        self._worker_task: Optional[asyncio.Task] = None

    def subscribe(self, event_type: str, handler: EventHandler):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        print(f"[EventBus] Subscrito a evento: {event_type}")

    async def publish(self, event_type: str, payload: Optional[Dict[str, Any]] = None):
        if payload is None:
            payload = {}
        event = {"type": event_type, "payload": payload}
        await self._queue.put(event)
        # print(f"[EventBus] Evento publicado: {event_type}") # Opcional para debug

    async def _worker(self):
        while self._running:
            event = await self._queue.get()
            # Validar que event sea diccionario dict[str, Any]
            if not isinstance(event, dict):
                continue
            event_type = event.get("type")
            
            if event_type in self._subscribers and isinstance(event_type, str):
                for handler in self._subscribers[event_type]:
                    try:
                        # Ejecutar los handlers de forma asíncrona pero sin bloquear todo
                        asyncio.create_task(handler(event.get("payload", {})))
                    except Exception as e:
                        print(f"[EventBus] Error procesando evento {event_type}: {e}")
            self._queue.task_done()

    async def start(self):
        self._running = True
        self._worker_task = asyncio.create_task(self._worker())
        print("[EventBus] Evento loop iniciado.")

    async def stop(self):
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
        print("[EventBus] Evento loop detenido.")
