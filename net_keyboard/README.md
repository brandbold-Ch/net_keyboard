# Net Keyboard

Una aplicación para compartir eventos de teclado y ratón sobre TCP, permitiendo controlar un ordenador remoto desde otro a través de la red.

## Arquitectura Actual (resumen)

El código ha sido reorganizado para separar claramente las responsabilidades:

```
src/
├── core/             # Adaptadores de alto nivel (servidor/cliente) y lógica central
│   ├── mkv_server.py  # TCP server adapter: serialize/forward events
│   └── mkv_client.py  # TCP client adapter: receive/deserializar eventos
├── backends/         # Abstracción de backends y listeners
│   ├── base.py       # Clases abstractas de teclado y ratón
│   ├── keyboard/     # Listener que integra con el IPC/launcher (native agent)
│   └── mouse/        # Placeholder para backends de ratón
├── transport/        # Canales de transporte (TCP, Unix sockets, pipes, IPC helpers)
├── utils/            # Utilidades (configuración, etc.)
└── bin/              # Binaries nativos/auxiliares (C agents) y artefactos
```

Notas:
- La integración con procesos nativos en C se realiza mediante un `IPCProcessLauncher` que lanza agentes nativos y expone los eventos por canales (Unix socket / pipe según la plataforma).
- Las referencias previas a `pynput` han sido retiradas: la captura de eventos se realizará desde el agente nativo o, en sistemas Linux, por adaptadores que leen directamente desde dispositivos de entrada (evdev) cuando aplique.
- **Actualmente ya es posible escuchar eventos de teclado en Linux:** el sistema selecciona automáticamente el dispositivo de entrada adecuado usando el módulo `core/devices/linux.py`, que detecta y resuelve los dispositivos disponibles en `/dev/input`. Esto permite que la aplicación funcione de forma plug-and-play en sistemas Linux sin configuración manual del dispositivo.

## Uso Previsto (ejemplo actualizado)

Ejemplos mínimos para utilizar los adaptadores actuales que se encuentran en `src/core`:

### Como Servidor (captura y reenvío de eventos)

```python
from src.core.mkv_server import MKVServer
from src.backends.keyboard import EventListener

# Crear servidor en localhost:5000
listener_factory = lambda: ...  # factory que devuelve IPCProcessLauncher configurado
keyboard_listener = EventListener(listener_factory)
server = MKVServer(host="0.0.0.0", port=5000, keyboard_listener=keyboard_listener)

# Iniciar servidor (arranque del listener IPC se hace dentro de server.start)
server.start()
```

### Como Cliente (recibir eventos y simularlos localmente)

```python
from src.core.mkv_client import MKVClient

# Conectar a servidor en localhost:5000
client = MKVClient(host="127.0.0.1", port=5000)

# Ejecutar cliente (recibe paquetes y los procesa)
client.start()
```

## Configuración

La configuración se gestiona mediante el archivo `config.json` en la raíz del proyecto (ejemplo):

```json
{
    "first_run": false,
    "os": "Windows",
    "client": {
        "host": "192.168.100.10",
        "port": 3500,
        "save_connection": true,
        "auto_reconnect": true
    },
    "server": {
        "host": "0.0.0.0",
        "port": 8000,
        "clients": [
            {
                "host": "192.168.100.1",
                "port": 8000,
                "save_connection": true,
                "auto_reconnect": true
            }
        ],
        "pool": 2,
        "keyboard": "\\\\?\\ACPI#MSFT0001#4&2d8d93fa&0#{884b96c3-56ef-11d1-bc8c-00a0c91405dd}",
        "mouse": "\\\\?\\HID#VID_258A&PID_0049&MI_01&Col07#7&17e8f3e&0&0006#{378de44c-56ef-11d1-bc8c-00a0c91405dd}",
        "save_connection": false,
        "auto_reconnect": false
    }
}
```

## Características Planificadas

- ✅ Arquitectura base TCP (Cliente/Servidor)
- ✅ Abstracciones de backend para teclado/ratón
- 🔄 Integración con C / agentes nativos para lectura de eventos (en progreso)
- ⏳ Interfaz gráfica funcional
- ⏳ Interfaz de línea de comandos funcional
- ⏳ Soporte multi-conexión
- ⏳ Encriptación de datos

## Próximas Etapas

1. Completar la integración con los agentes nativos en C para escuchar eventos de forma fiable
2. Ajustar los launchers IPC y los agentes para cada plataforma (Linux/Windows)
3. Probar y validar la latencia/precisión de los eventos
4. Restaurar y validar las interfaces (CLI/GUI)

## Notas Técnicas

La migración a agentes nativos busca:
- Mayor precisión en la captura de eventos
- Mejor rendimiento y menor latencia
- Acceso directo a eventos del kernel (cuando aplique)
- Mayor control sobre el timing y secuenciamiento de eventos

## Licencia

Este proyecto es de código abierto.

## Autor

Brandbold
