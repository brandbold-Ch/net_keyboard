# Net Keyboard

Una aplicación para compartir eventos de teclado y ratón sobre TCP, permitiendo controlar un ordenador remoto desde otro a través de la red.

## Estado del Proyecto

⚠️ **ACTUALMENTE INSERVIBLE** - El proyecto se encuentra en una fase de refactorización arquitectónica.

Se está implementando una característica importante que permitirá escuchar los eventos de entrada desde **C** para obtener mayor precisión y mejor rendimiento. Por esta razón, la arquitectura se ha reorganizado significativamente y el proyecto no es funcional en este momento.

Una vez completada la integración con C, el proyecto recuperará su funcionalidad completa.

## Arquitectura Actual

El proyecto está estructurado en los siguientes módulos:

```
src/
├── tcp/              # Módulo base de comunicación TCP
│   ├── base.py       # Clase abstracta TCP
│   ├── client.py     # Cliente TCP
│   └── server.py     # Servidor TCP
├── backends/         # Implementaciones de captura de eventos
│   ├── base.py       # Clases abstractas de teclado y ratón
│   ├── pynput.py     # Implementación con Pynput
│   └── evdev.py      # Implementación con Evdev (Linux)
├── adapters/         # Adaptadores que combinan TCP con backends
│   └── keyboard/
│       └── pynput.py # Adaptador servidor/cliente con Pynput
├── utils/            # Utilidades
│   └── config.py     # Gestión de configuración
├── cli.py            # Interfaz de línea de comandos
└── gui.py            # Interfaz gráfica
```

## Uso Previsto

Una vez que el proyecto esté funcional, se utilizará de la siguiente manera:

### Como Servidor (Captura de eventos locales)

```python
from src.adapters.keyboard.pynput import PynputServer

# Crear servidor en localhost:5000
server = PynputServer(host="0.0.0.0", port=5000)

# Ejecutar servidor y capturar eventos
server.run()
```

### Como Cliente (Simular eventos remotos)

```python
from src.adapters.keyboard.pynput import PynputClient

# Conectar a servidor en localhost:5000
client = PynputClient(host="127.0.0.1", port=5000)

# Ejecutar cliente y recibir eventos
client.run()
```

## Configuración

La configuración se gestiona mediante el archivo `config.json` en la raíz del proyecto:

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 5000
  },
  "client": {
    "host": "127.0.0.1",
    "port": 5000
  },
  "connections": []
}
```

## Características Planificadas

- ✅ Arquitectura base TCP (Cliente/Servidor)
- ✅ Backends para captura de eventos (Pynput, Evdev)
- ✅ Adaptadores para integración de TCP + backends
- ✅ Sistema de configuración
- 🔄 **Integración con C para mayor precisión** (en progreso)
- ⏳ Interfaz gráfica funcional
- ⏳ Interfaz de línea de comandos funcional
- ⏳ Soporte multi-conexión
- ⏳ Encriptación de datos

## Próximas Etapas

1. Completar la integración con C para escuchar eventos desde el kernel
2. Actualizar la arquitectura para utilizar el nuevo sistema de escucha de eventos
3. Realizar pruebas de precisión y rendimiento
4. Restaurar funcionalidad completa del proyecto
5. Implementar interfaz gráfica y CLI

## Notas Técnicas

La decisión de integrar C se toma para:
- Mayor precisión en la captura de eventos
- Mejor rendimiento y menor latencia
- Acceso directo a eventos del kernel en lugar de abstracciones de librerías
- Mayor control sobre el timing y secuenciamiento de eventos

## Licencia

Este proyecto es de código abierto.

## Autor

Brandbold
