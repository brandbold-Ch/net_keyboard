# Implementación de Clases Abstractas para Listeners de Teclado

## Resumen Ejecutivo

Este documento describe en detalle cómo implementar las clases abstractas para la escucha de eventos de teclado en el proyecto NetKeyboard. La arquitectura utiliza un patrón de herencia abstracta (`ABC`) donde `KeyboardBackend` define la interfaz que todos los listeners de teclado deben implementar.

---

## 1. Arquitectura General

### 1.1 Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                      Aplicación (main.py / gui.py)          │
└────────────────┬────────────────────────────────────────────┘
                 │ crea e inicializa
                 ↓
┌─────────────────────────────────────────────────────────────┐
│                    EventListener (Concreto)                 │
│          Implementa: KeyboardBackend (Abstracto)             │
│  - on_press(codes)                                          │
│  - on_release(codes)                                        │
│  - add_subscriber(cb, kind)                                 │
│  - _emit_event(codes, kind)                                 │
│  - listen()                                                 │
└────────────────┬────────────────────────────────────────────┘
                 │ delega a
                 ↓
┌─────────────────────────────────────────────────────────────┐
│              IPCProcessLauncher (Gestor de IPC)              │
│  - Configura client/server (roles intercambiables)          │
│  - Maneja la comunicación entre procesos                    │
│  - Coordina KeyListener (IPCStreamReader)                   │
└────────────────┬────────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        ↓                 ↓
   ┌─────────┐       ┌──────────┐
   │KeyListener│      │IPCStream │
   │(Client/  │      │Reader    │
   │ Server)  │      │(abstracto)
   │Concreto  │      │          │
   └─────────┘      └──────────┘
        │
        ↓
   ┌──────────────────┐
   │Device Events     │
   │(/dev/input/...)  │
   └──────────────────┘
```

---

## 2. Clases Base Abstractas

### 2.1 `KeyboardBackend` (Clase Abstracta)

**Ubicación:** `src/backends/base.py`

```python
class KeyboardBackend(ABC):
    """Abstract base class for keyboard backend implementations."""

    @abstractmethod
    def on_press(self, codes: TUPLE_CODES) -> None:
        """Handle keyboard press events.
        Args:
            codes (Tuple[int, int, int]): (scancode, state, time)
        """
        pass

    @abstractmethod
    def on_release(self, codes: TUPLE_CODES) -> None:
        """Handle keyboard release events.
        Args:
            codes (Tuple[int, int, int]): (scancode, state, time)
        """
        pass

    @abstractmethod
    def press(self, codes: TUPLE_CODES) -> None:
        """Simulate pressing a key."""
        pass

    def add_subscriber(
        self, cb: Callable[[TUPLE_CODES], None], kind: KeyboardTypeEvent
    ) -> None:
        """Register a callback for keyboard events (opcional)."""
        pass

    @abstractmethod
    def listen(self) -> None:
        """Start listening for keyboard events (bloqueante)."""
        pass
```

**Métodos Abstractos Requeridos:**
- `on_press()` - Procesa eventos de presión de tecla
- `on_release()` - Procesa eventos de liberación de tecla
- `press()` - Simula presión de tecla (actualmente stub)
- `listen()` - Inicia el loop de escucha bloqueante

**Métodos Opcionales:**
- `add_subscriber()` - Registra callbacks para eventos

---

### 2.2 `KeyboardTypeEvent` (Enumeración)

**Ubicación:** `src/backends/base.py`

```python
class KeyboardTypeEvent(Enum):
    """Enumeration of keyboard event types."""
    PRESS = auto()
    RELEASE = auto()
```

**Uso:** Identifica qué tipo de evento de teclado ocurrió.

---

### 2.3 `KeyboardSubscribers` (Dataclass)

**Ubicación:** `src/backends/base.py`

```python
@dataclass
class KeyboardSubscribers:
    """Container for keyboard event callbacks."""
    press: EventList = field(default_factory=list)
    release: EventList = field(default_factory=list)
```

**Propósito:** Almacena las listas de callbacks para eventos de presión y liberación.

---

### 2.4 `IPCStreamReader` (Clase Abstracta)

**Ubicación:** `src/transport/ipc/tools.py`

```python
class IPCStreamReader(ABC):
    @property
    @abstractmethod
    def device(self) -> Optional[str]:
        """Return the device path this reader will read from."""
        pass

    @abstractmethod
    def open(self, raw: CALLBACK_READER) -> None:
        """Start reading from the provided raw callback reader."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Request the reader to stop and clean up resources."""
        pass
```

**Responsabilidad:** Define cómo leer eventos desde un dispositivo o proceso externo.

---

## 3. Implementación Concreta: `EventListener`

### 3.1 Estructura y Flujo Real

**Ubicación:** `src/backends/keyboard/listener.py`

La clase `EventListener` implementa la interfaz `KeyboardBackend` y actúa como manejador de eventos de teclado respaldado por IPC. Utiliza un `IPCProcessLauncher` para lanzar un proceso auxiliar que lee eventos de teclado a bajo nivel y los reenvía a través de un canal IPC.

#### Características principales:
- **Suscripción:** Permite registrar callbacks para eventos de presionado (`PRESS`) y soltado (`RELEASE`) de teclas.
- **Recepción de eventos:** Los eventos llegan como tuplas `(code, state, time)` y se despachan a los suscriptores correspondientes.
- **Simulación de teclas:** El método `press` está preparado para simular la pulsación de teclas (puede requerir implementación adicional según plataforma).
- **Escucha:** El método `listen` inicia el proceso de escucha y es bloqueante hasta que se interrumpe el hilo.

#### Ejemplo de uso:
```python
listener = EventListener(launcher_factory)
listener.add_subscriber(on_press_callback, KeyboardTypeEvent.PRESS)
listener.listen()
```

#### Implementación relevante:
```python
class EventListener(KeyboardBackend):
    """IPC-backed keyboard event handler."""

    def __init__(self, launcher_factory: Callable[[], IPCProcessLauncher]) -> None:
        self._subscribers: KeyboardSubscribers = KeyboardSubscribers()
        self._launcher_factory = launcher_factory

    def on_press(self, event: TUPLE_CODES) -> None:
        self._emit_event(event, KeyboardTypeEvent.PRESS)

    def on_release(self, event: TUPLE_CODES) -> None:
        self._emit_event(event, KeyboardTypeEvent.RELEASE)

    def press(self, event: TUPLE_CODES) -> None:
        # Simulación de pulsación (stub)
        pass

    def add_subscriber(self, cb: Callable[[TUPLE_CODES], None], kind: KeyboardTypeEvent) -> None:
        match kind:
            case KeyboardTypeEvent.PRESS:
                self._subscribers.press.append(cb)
            case KeyboardTypeEvent.RELEASE:
                self._subscribers.release.append(cb)

    def _emit_event(self, event: TUPLE_CODES, kind: KeyboardTypeEvent) -> None:
        match kind:
            case KeyboardTypeEvent.PRESS:
                for cb in self._subscribers.press:
                    cb(event)
            case KeyboardTypeEvent.RELEASE:
                for cb in self._subscribers.release:
                    cb(event)

    def listen(self) -> None:
        launcher = self._launcher_factory()
        launcher.launch()
```

#### Detalles de flujo:
- El `EventListener` recibe eventos desde un proceso auxiliar lanzado por `IPCProcessLauncher`.
- Los eventos se decodifican y se notifican a los callbacks registrados.
- El patrón de diseño es Observer, permitiendo desacoplar la fuente de eventos de los consumidores.

---

## 4. Integración con IPC

### 4.1 `IPCProcessLauncher`

**Ubicación:** `src/transport/ipc/tools.py`

```python
class IPCProcessLauncher(ABC):
    def __init__(self, client: AGENT_SOURCE, server: AGENT_SOURCE, shared: str) -> None:
        self.client = client          # IPCStreamReader o str (ejecutable)
        self.server = server          # IPCStreamReader o str (ejecutable)
        self.shared = shared          # Dirección IPC (socket/pipe)
        self.base_path = Path(__file__).resolve().parents[2]

    def launch(self) -> None:
        """Launch both server and client agents."""
        if os.name == "posix":
            self._cleanup(self.shared)
        
        self._set_readables()
        self._launch_channel("server", self.server)
        self._launch_channel("client", self.client)
```

**Flujo de Lanzamiento:**
1. Limpia socket anterior (POSIX)
2. Escribe archivos de configuración (`shared.txt`, `device.txt`)
3. Lanza canal servidor con `_launch_channel()`
4. Lanza canal cliente con `_launch_channel()`

### 4.2 `KeyListener` (Implementación Concreta de `IPCStreamReader`)

**Ubicación:** `src/transport/ipc/tools.py`

```python
class KeyListener(IPCStreamReader):
    def __init__(
        self,
        on_press: Optional[CB_EVENT] = None,
        on_release: Optional[CB_EVENT] = None,
        device: Optional[str] = None,
    ) -> None:
        self.on_press = on_press           # Callback → EventListener.on_press
        self.on_release = on_release       # Callback → EventListener.on_release
        self._device = device
        self._running: bool = True

    @property
    def device(self) -> Optional[str]:
        return self._device

    def open(self, raw: CALLBACK_READER) -> None:
        """Read events from raw callback and dispatch to on_press/on_release."""
        spec = GLOBAL_FORMAT  # "<H B Q" = unsigned short, byte, uint64
        
        try:
            while self._running:
                # Lee 11 bytes (2+1+8)
                data: bytes = safe_read(raw, spec.size)
                code, state, time = unpack(spec.fmt, data)
                
                # state: 1 = presión, 0 = liberación
                if state == 1 and self.on_press:
                    self.on_press((code, state, time))
                elif state == 0 and self.on_release:
                    self.on_release((code, state, time))
        except Exception as e:
            print(f"KeyListener error: {e}")
        finally:
            self.close()

    def close(self) -> None:
        self._running = False
```

**Flujo de Eventos:**
```
┌─────────────────────────────────┐
│ Dispositivo físico               │
│ (/dev/input/event*)             │
└────────────┬────────────────────┘
             │ bytes: (code, state, time)
             ↓
┌─────────────────────────────────┐
│ Proceso cliente (bin/...)        │
│ Lee dispositivo, envía bytes     │
└────────────┬────────────────────┘
             │ raw CALLBACK_READER
             ↓
┌─────────────────────────────────┐
│ KeyListener.open()              │
│ Recibe bytes del cliente        │
│ Decodifica: unpack()            │
└────────────┬────────────────────┘
             │ if state == 1: on_press()
             │ if state == 0: on_release()
             ↓
┌─────────────────────────────────┐
│ EventListener.on_press()        │
│ EventListener.on_release()      │
│ Emite eventos a subscribers     │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│ Callbacks registrados            │
│ (MKVServer, GUI, etc.)          │
└─────────────────────────────────┘
```

---

## 5. Formato de Eventos

### 5.1 GLOBAL_FORMAT

**Ubicación:** `src/transport/ipc/tools.py`

```python
FMT: str = "<H B Q"          # Little-endian format
SIZE: int = calcsize(FMT)    # 11 bytes (2 + 1 + 8)

# Desglose:
# H = unsigned short (2 bytes)  → scancode de la tecla
# B = unsigned char (1 byte)    → estado (0=liberado, 1=presionado)
# Q = unsigned long long (8 bytes) → timestamp en microsegundos
```

**Ejemplo de Evento:**
```
bytes: b'\x1e\x00\x01\x00\x00\x00\x00\x00\x00\xab\xcd'
↓
unpack("<H B Q", data)
↓
(30, 1, 0x00000000000000cdab)
→ (scancode=30 (tecla 'A'), estado=1 (presionada), tiempo=52651)
```

---

## 6. Casos de Uso - ¿Cuándo Funciona Temporalmente?

### 6.1 ✅ Funciona Correctamente

#### **Caso 1: Uso en Aplicación Principal (main.py)**

```python
# Inicialización
listener = EventListener(launcher_factory)
listener.add_subscriber(on_press, KeyboardTypeEvent.PRESS)
listener.add_subscriber(on_release, KeyboardTypeEvent.RELEASE)
listener.listen()  # Bloqueante - inicia loop de eventos
```

**Requisitos:**
- ✅ El dispositivo de teclado existe (`/dev/input/event*` en Linux)
- ✅ El ejecutable cliente existe (`bin/socket_unix/keyboard/out`)
- ✅ El socket/pipe puede crearse en la ruta especificada
- ✅ Se tienen permisos para leer el dispositivo

**Limitaciones Conocidas:**
- ⚠️ En Linux, `listener.listen()` es bloqueante
- ⚠️ Si el cliente no se lanza, el socket queda esperando indefinidamente

#### **Caso 2: Uso como Servidor de Red (MKVServer)**

```python
listener = EventListener(launcher_factory)

# MKVServer se suscribe automáticamente
server = MKVServer(host, port, listener)
server.start()  # Inicia servidor TCP en thread separado
```

**Funciona cuando:**
- ✅ El listener captura eventos del teclado local
- ✅ Se serializa correctamente el formato GLOBAL_FORMAT
- ✅ Los clientes TCP reciben los bytes sin corrupción

#### **Caso 3: Uso en GUI (PySide6)**

```python
# En gui.py - inicialización
listener = EventListener(launcher_factory)
listener.listen()

# Callbacks pueden actualizar la interfaz gráfica
def on_key_press(codes):
    update_gui_with_event(codes)
```

**Funciona cuando:**
- ✅ El listener se inicia antes de mostrar la ventana
- ✅ Los callbacks no bloquean el event loop de Qt (ejecutar en threads)

---

### 6.2 ⚠️ Funciona Temporalmente (Parcial)

#### **Caso: on_press / on_release sin Inicialización**

```python
listener = EventListener(launcher_factory)
# ❌ NO se agregaron subscribers
listener.on_press((30, 1, 12345))  # Se llama pero no hace nada
listener.on_release((30, 0, 12346))
```

**Por qué funciona "temporalmente":**
- No hay excepciones
- `_emit_event()` itera sobre lista vacía
- **Problema:** Los callbacks nunca se ejecutan

**Solución:**
```python
listener.add_subscriber(on_press, KeyboardTypeEvent.PRESS)
```

---

### 6.3 ❌ No Funciona

#### **Caso 1: Método `press()` no Implementado**

```python
listener.press((30,))  # ❌ No hace nada
```

**Razón:** El método es un stub:
```python
def press(self, codes: TUPLE_CODES) -> None:
    pass  # Sin implementación
```

**Estado:** Está reservado para simular presiones de tecla (ej: inyectar eventos).

#### **Caso 2: Dispositivo no Disponible**

```python
kbds = scan_device("kbd")
# kbds == {} si no hay dispositivos con sufijo "-kbd"

# En launcher_factory()
device=str(kbds["usb-BY_Tech_Gaming_Keyboard-event-kbd"])
# ❌ KeyError: dispositivo no encontrado
```

**Causa:**
- El dispositivo del teclado no existe en `/dev/input/by-id/`
- O no tiene el sufijo `-event-kbd`

**Solución:**
```bash
ls /dev/input/by-id/
# Buscar el dispositivo adecuado
```

#### **Caso 3: Binario Cliente no Existe**

```python
IPCProcessLauncher(
    client="bin/socket_unix/keyboard/out",  # ❌ No existe
    ...
)
launcher.launch()
```

**Resultado:** El socket espera indefinidamente sin eventos.

#### **Caso 4: Permisos Insuficientes**

```bash
$ python main.py
# ❌ PermissionError: [Errno 13] Permission denied: '/dev/input/event1'
```

**Solución:**
```bash
sudo python main.py
# O agregar usuario al grupo input
sudo usermod -aG input $USER
```

---

## 7. Análisis de Uso en el Proyecto

### 7.1 Uso en `main.py`

```python
def launcher_factory() -> IPCProcessLauncher:
    kbds = scan_device("kbd")  # Escanea dispositivos de teclado
    
    return IPCProcessLauncher(
        client="bin/socket_unix/keyboard/out",     # Ejecutable de lectura
        server=KeyListener(                         # Servidor IPC (receptor)
            on_press=listener.on_press,
            on_release=listener.on_release,
            device=str(kbds["usb-BY_Tech_Gaming_Keyboard-event-kbd"]),
        ),
        shared="/tmp/jazmin_bean.sock",            # Socket IPC
    )

listener = EventListener(launcher_factory)
listener.add_subscriber(on_press, KeyboardTypeEvent.PRESS)
listener.add_subscriber(on_release, KeyboardTypeEvent.RELEASE)
listener.listen()  # ⚠️ BLOQUEANTE - programa no continúa
```

**Análisis:**
- En POSIX: usa socket Unix (`/tmp/*.sock`)
- `on_press` / `on_release` son los callbacks de nivel de usuario
- `listener.listen()` es bloqueante (no retorna)

---

### 7.2 Uso en `gui.py`

```python
def launcher_factory() -> IPCProcessLauncher:
    return IPCProcessLauncher(
        client="bin/socket_unix/klevent",
        server=KeyListener(...),
        shared="/tmp/keyboard_ipc.sock",
    )

listener = EventListener(launcher_factory)
listener.listen()  # ⚠️ Bloqueante - la GUI se congela

def build_server() -> None:
    server = MKVServer(e.CLIENT_HOST, e.CLIENT_PORT, listener)
    server.start()
```

**Problema:** `listener.listen()` bloquea el hilo principal de Qt.

**Solución Necesaria:**
```python
import threading

# En lugar de:
listener.listen()

# Usar:
threading.Thread(target=listener.listen, daemon=True).start()
```

---

### 7.3 Integración con MKVServer

**Ubicación:** `src/core/mkv_server.py`

```python
class MKVServer(TcpServer):
    def __init__(self, host: str, port: int, keyboard_listener: K_LISTENER = None):
        super().__init__(host, port)
        self.keyboard_listener = keyboard_listener
        
        if self.keyboard_listener:
            # ✅ Se suscribe automáticamente
            self.keyboard_listener.add_subscriber(
                self.on_press, KeyboardTypeEvent.PRESS
            )
            self.keyboard_listener.add_subscriber(
                self.on_release, KeyboardTypeEvent.RELEASE
            )
    
    def on_press(self, codes: TUPLE_CODES) -> None:
        self.send(self.serialize(codes))
    
    def on_release(self, codes: TUPLE_CODES) -> None:
        self.send(self.serialize(codes))
    
    def start(self) -> None:
        if self.keyboard_listener:
            threading.Thread(target=self.keyboard_listener.listen).start()
```

**Flujo:**
1. EventListener captura eventos del teclado local
2. MKVServer se suscribe a esos eventos
3. Cuando ocurre un evento, MKVServer lo serializa y envía por TCP
4. Los clientes TCP reciben los eventos remotamente

---

## 8. Plantilla para Implementar Nuevos Listeners

Si necesitas crear un nuevo listener (ej: para mouse), sigue este patrón:

### 8.1 Paso 1: Definir la Clase Base Abstracta

```python
# src/backends/base.py
class MouseBackend(ABC):
    @abstractmethod
    def on_move(self, position: Tuple[int, int]) -> None:
        pass
    
    @abstractmethod
    def on_click(self, button: str) -> None:
        pass
    
    @abstractmethod
    def on_scroll(self, direction: str) -> None:
        pass
    
    @abstractmethod
    def listen(self) -> None:
        pass
```

### 8.2 Paso 2: Implementar la Clase Concreta

```python
# src/backends/mouse/listener.py
from src.backends.base import MouseBackend

class MouseEventListener(MouseBackend):
    def __init__(self, launcher_factory):
        self._launcher_factory = launcher_factory
        self._subscribers = MouseSubscribers()
    
    def on_move(self, position):
        for cb in self._subscribers.move:
            cb(position)
    
    def on_click(self, button):
        for cb in self._subscribers.click:
            cb(button)
    
    def on_scroll(self, direction):
        for cb in self._subscribers.scroll:
            cb(direction)
    
    def add_subscriber(self, cb, kind):
        # Similar a EventListener...
        pass
    
    def listen(self):
        launcher = self._launcher_factory()
        launcher.launch()
```

### 8.3 Paso 3: Integrar con IPC

```python
# Crear una clase derivada de IPCStreamReader
class MouseListener(IPCStreamReader):
    def __init__(self, on_move=None, on_click=None, on_scroll=None, device=None):
        self.on_move = on_move
        self.on_click = on_click
        self.on_scroll = on_scroll
        self._device = device
        self._running = True
    
    def open(self, raw):
        # Leer eventos del socket/pipe
        # Decodificar y llamar a callbacks
        pass
    
    def close(self):
        self._running = False
```

---

## 9. Diagrama de Flujo Completo

```
┌─────────────────────────────────────────────────────────────┐
│                    main.py / gui.py                         │
│            Define launcher_factory() y crea EventListener   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                  listener.listen()                          │
│             (BLOQUEANTE - inicia el flujo)                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│         launcher_factory() → IPCProcessLauncher             │
│                    launcher.launch()                        │
│  ┌──────────────┐         ┌──────────────────┐             │
│  │ server side  │         │ client side      │             │
│  │ KeyListener  │◄───────►│ bin/socket_unix/ │             │
│  │(IPCReader)   │ socket  │ keyboard/out     │             │
│  └──────┬───────┘   IPC   └──────┬───────────┘             │
│         │                        │                          │
│         └────────┬───────────────┘                          │
│                  ↓                                           │
│      Recibe: unpack(code, state, time)                     │
│      Llama: on_press() o on_release()                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│           EventListener._emit_event()                       │
│      Itera sobre subscribers[PRESS/RELEASE]               │
└──────────────────────┬──────────────────────────────────────┘
                       │
    ┌──────────────────┼──────────────────┐
    ↓                  ↓                  ↓
┌──────────┐  ┌────────────────┐  ┌─────────────┐
│ on_press │  │ MKVServer      │  │ GUI update  │
│ callback │  │ send over TCP  │  │ callback    │
└──────────┘  └────────────────┘  └─────────────┘
```

---

## 10. Checklist de Implementación

Para implementar un nuevo listener sigue estos pasos:

- [ ] **Paso 1:** Crear clase abstracta base heredando de `ABC`
  - [ ] Definir todos los métodos abstractos (@abstractmethod)
  - [ ] Documentar cada método con docstring

- [ ] **Paso 2:** Crear enumeración para tipos de eventos
  - [ ] Usar `Enum` y `auto()`
  - [ ] Crear una por cada tipo de evento (PRESS, RELEASE, etc.)

- [ ] **Paso 3:** Crear dataclass para almacenar subscribers
  - [ ] Un campo `EventList` por tipo de evento
  - [ ] Usar `field(default_factory=list)`

- [ ] **Paso 4:** Implementar clase concreta
  - [ ] Heredar de la clase abstracta
  - [ ] Implementar todos los métodos abstractos
  - [ ] Implementar `__init__()` con `launcher_factory`
  - [ ] Implementar `add_subscriber()` con pattern matching
  - [ ] Implementar `_emit_event()` privado

- [ ] **Paso 5:** Implementar clase IPCStreamReader concreta
  - [ ] Heredar de `IPCStreamReader`
  - [ ] Implementar `open()` para leer eventos
  - [ ] Llamar callbacks desde `open()`
  - [ ] Implementar `close()`

- [ ] **Paso 6:** Integrar con IPCProcessLauncher
  - [ ] Crear launcher factory
  - [ ] Pasar la clase concreta del reader

- [ ] **Paso 7:** Testear
  - [ ] Verificar que los eventos se capturan
  - [ ] Verificar que los callbacks se ejecutan
  - [ ] Verificar permisos y dispositivos

---

## 11. Resumen: ¿Qué Funciona y Qué No?

| Componente | Estado | Notas |
|-----------|--------|-------|
| `KeyboardBackend` (abstracto) | ✅ Correcto | Define la interfaz |
| `EventListener` (concreto) | ✅ Funcional | Implementa completamente |
| `on_press()` / `on_release()` | ✅ Funciona | Si hay subscribers registrados |
| `add_subscriber()` | ✅ Funciona | Pattern matching correcto |
| `listen()` | ✅ Funciona (bloqueante) | Inicia el loop de eventos |
| `press()` (simular) | ❌ No implementado | Es un stub vacío |
| `IPCProcessLauncher` | ✅ Funcional | Gestiona procesos client/server |
| `KeyListener` (reader) | ✅ Funcional | Lee eventos del IPC |
| `GLOBAL_FORMAT` | ✅ Correcto | Serialización de eventos |
| Integración con MKVServer | ✅ Funcional | Envía eventos por TCP |
| Integración con GUI | ⚠️ Problemática | `listen()` bloquea el hilo |

---

## 12. Referencias Cruzadas

**Archivos Clave:**
- `src/backends/base.py` - Clases abstractas base
- `src/backends/keyboard/listener.py` - Implementación de EventListener
- `src/transport/ipc/tools.py` - IPCProcessLauncher y KeyListener
- `src/core/mkv_server.py` - Integración con servidor TCP
- `main.py` / `gui.py` - Uso final

**Patrón de Diseño:**
- **Abstract Base Class (ABC)** - Define contrato
- **Factory Pattern** - `launcher_factory()`
- **Observer Pattern** - Sistema de subscribers
- **IPC Pattern** - Comunicación entre procesos

---

**Documento Generado:** 20 de febrero de 2026  
**Versión:** 1.0  
**Alcance:** Solo listeners de teclado
