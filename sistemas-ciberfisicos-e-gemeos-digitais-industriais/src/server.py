from __future__ import annotations
import asyncio
import json
import os
from datetime import datetime
from typing import Dict

from asyncua import ua, Server
from gmqtt import Client as MQTTClient
from loguru import logger
from dotenv import load_dotenv

from .model import (
    ElectricalPayload,
    EnvironmentPayload,
    VibrationPayload,
    SEVERITY,
    NOMINAL_VOLTAGE,
    NOMINAL_CURRENT,
    OVER_UNDER_TOL,
    CASE_TEMP_CRIT,
    TOPIC_ELEC,
    TOPIC_ENV,
    TOPIC_VIB,
    MOTOR_NODE_NAME,
)
from .storage import Storage
from .lds import try_register_with_lds

# ──────────────────────────────────────────────────────────────────────────────
# Utilidades
# ──────────────────────────────────────────────────────────────────────────────

def pct_over(value: float, nominal: float) -> float:
    return (value - nominal) / nominal

# ──────────────────────────────────────────────────────────────────────────────
# Servidor OPC UA + Árvore de Nós
# ──────────────────────────────────────────────────────────────────────────────

class MotorOPCUAServer:
    def __init__(self):
        load_dotenv()
        self.endpoint = os.getenv("OPCUA_ENDPOINT", "opc.tcp://0.0.0.0:4840/scgdi/motor50cv")
        self.server_name = os.getenv("OPCUA_SERVER_NAME", "SCGDI Motor50CV Server")
        self.ns_uri = os.getenv("OPCUA_NAMESPACE_URI", "http://scgdi.local/motor50cv")
        self.db_path = os.getenv("DB_PATH", "./scgdi_history.sqlite")
        self.lds_endpoint = os.getenv("LDS_ENDPOINT", "")

        self.mqtt_host = os.getenv("MQTT_HOST", "localhost")
        self.mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
        self.mqtt_username = os.getenv("MQTT_USERNAME", "")
        self.mqtt_password = os.getenv("MQTT_PASSWORD", "")
        self.mqtt_client_id = os.getenv("MQTT_CLIENT_ID", "scgdi-motor50cv")

        self.storage = Storage(self.db_path)
        self.server = Server()
        self.idx = None  # namespace index

        # Variáveis OPC UA (guardaremos refs p/ atualização)
        self.vars: Dict[str, any] = {}

        # MQTT client
        self.mqtt: MQTTClient | None = None

    async def init(self):
        await self.storage.init()
        await self.server.init()
        self.server.set_endpoint(self.endpoint)
        self.server.set_server_name(self.server_name)
        self.idx = await self.server.register_namespace(self.ns_uri)

        # Address space root
        objects = self.server.nodes.objects

        # Nó raiz do motor
        motor = await objects.add_object(self.idx, MOTOR_NODE_NAME)

        # Subnós conforme enunciado
        # Electrical
        n_elec = await motor.add_object(self.idx, "Electrical")
        self.vars["VoltageA"] = await n_elec.add_variable(self.idx, "VoltageA", 0.0)
        self.vars["VoltageB"] = await n_elec.add_variable(self.idx, "VoltageB", 0.0)
        self.vars["VoltageC"] = await n_elec.add_variable(self.idx, "VoltageC", 0.0)
        self.vars["CurrentA"] = await n_elec.add_variable(self.idx, "CurrentA", 0.0)
        self.vars["CurrentB"] = await n_elec.add_variable(self.idx, "CurrentB", 0.0)
        self.vars["CurrentC"] = await n_elec.add_variable(self.idx, "CurrentC", 0.0)
        self.vars["PowerActive"] = await n_elec.add_variable(self.idx, "PowerActive", 0.0)
        self.vars["PowerReactive"] = await n_elec.add_variable(self.idx, "PowerReactive", 0.0)
        self.vars["PowerApparent"] = await n_elec.add_variable(self.idx, "PowerApparent", 0.0)
        self.vars["EnergyActive"] = await n_elec.add_variable(self.idx, "EnergyActive", 0.0)
        self.vars["EnergyReactive"] = await n_elec.add_variable(self.idx, "EnergyReactive", 0.0)
        self.vars["EnergyApparent"] = await n_elec.add_variable(self.idx, "EnergyApparent", 0.0)
        self.vars["PowerFactor"] = await n_elec.add_variable(self.idx, "PowerFactor", 0.0)
        self.vars["Frequency"] = await n_elec.add_variable(self.idx, "Frequency", 0.0)

        # Environment
        n_env = await motor.add_object(self.idx, "Environment")
        self.vars["Temperature"] = await n_env.add_variable(self.idx, "Temperature", 0.0)
        self.vars["Humidity"] = await n_env.add_variable(self.idx, "Humidity", 0.0)
        self.vars["CaseTemperature"] = await n_env.add_variable(self.idx, "CaseTemperature", 0.0)

        # Vibration
        n_vib = await motor.add_object(self.idx, "Vibration")
        self.vars["Axial"] = await n_vib.add_variable(self.idx, "Axial", 0.0)
        self.vars["Radial"] = await n_vib.add_variable(self.idx, "Radial", 0.0)

        # Tornar variáveis graváveis por servidor
        for v in self.vars.values():
            await v.set_writable()

        # Preparar tipo de evento customizado (simples)
        await self._prepare_event_type()

        # Tentativa de registro em LDS (se configurado)
        await try_register_with_lds(self.server, self.lds_endpoint)

    async def _prepare_event_type(self):
        # Cria um tipo de evento customizado com campos adicionais
        self.evtype = await self.server.create_custom_event_type(
            self.idx,
            "SCGDIEventType",
            ua.ObjectIds.BaseEventType,
            [
                ("Category", ua.VariantType.String),
                ("Message", ua.VariantType.String),
            ],
        )

    async def fire_event(self, source_node, category: str, message: str, severity: int):
        event = await self.server.get_event_generator(self.evtype, source_node)
        event.event.Severity = severity
        event.event.Message = ua.LocalizedText(message)
        event.event.Category = category
        await event.trigger()
        # Persistir histórico de eventos
        await self.storage.add_event(
            ts=datetime.utcnow().isoformat(),
            source=str(source_node.nodeid),
            message=message,
            severity=severity,
            category=category,
        )

    async def start(self):
        async with self.server as srv:
            # MQTT loop como task concorrente
            await asyncio.gather(
                self._mqtt_loop(),
                self._heartbeat_task(srv.nodes.objects),
            )

    async def _heartbeat_task(self, source_node):
        # Emite evento informativo periódico para ver atividade
        while True:
            await self.fire_event(source_node, "status", "heartbeat", SEVERITY["INFO"])
            await asyncio.sleep(30)

    # ──────────────────────────────────────────────────────────────────────
    # MQTT
    # ──────────────────────────────────────────────────────────────────────

    async def _mqtt_loop(self):
        client = MQTTClient(self.mqtt_client_id)

        def on_connect(c, flags, rc, properties):  # noqa: ANN001
            logger.info("MQTT conectado: {}:{}, rc={} flags={}", self.mqtt_host, self.mqtt_port, rc, flags)
            c.subscribe(TOPIC_ELEC)
            c.subscribe(TOPIC_ENV)
            c.subscribe(TOPIC_VIB)

        async def on_message(c, topic, payload, qos, properties):  # noqa: ANN001
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                logger.warning("MQTT payload inválido em {}", topic)
                return

            if topic == TOPIC_ELEC:
                await self._handle_electrical(ElectricalPayload(**data))
            elif topic == TOPIC_ENV:
                await self._handle_environment(EnvironmentPayload(**data))
            elif topic == TOPIC_VIB:
                await self._handle_vibration(VibrationPayload(**data))

        client.on_connect = on_connect
        client.on_message = on_message

        self.mqtt = client
        await client.connect(host=self.mqtt_host, port=self.mqtt_port, keepalive=60, ssl=None,
                             username=(self.mqtt_username or None), password=(self.mqtt_password or None))

        try:
            await client.subscribe("$SYS/#")  # opcional, debug
            while True:
                await asyncio.sleep(1)
        finally:
            await client.disconnect()

    # ──────────────────────────────────────────────────────────────────────
    # Handlers de atualização de variáveis + regras de eventos/alarmes
    # ──────────────────────────────────────────────────────────────────────

    async def _set_and_store(self, name: str, ts: str, value: float, extra: Dict | None = None):
        node = self.vars[name]
        await node.write_value(value)
        path = f"{MOTOR_NODE_NAME}." + \
               ("Electrical." if name in {"VoltageA","VoltageB","VoltageC","CurrentA","CurrentB","CurrentC","PowerActive","PowerReactive","PowerApparent","EnergyActive","EnergyReactive","EnergyApparent","PowerFactor","Frequency"}
                else "Environment." if name in {"Temperature","Humidity","CaseTemperature"}
                else "Vibration.")
        path += name
        await self.storage.add_var(ts, path, value, extra)

    async def _handle_electrical(self, p: ElectricalPayload):
        ts = p.timestamp
        # Atualiza variáveis
        await self._set_and_store("VoltageA", ts, p.voltage.get("a", 0.0))
        await self._set_and_store("VoltageB", ts, p.voltage.get("b", 0.0))
        await self._set_and_store("VoltageC", ts, p.voltage.get("c", 0.0))
        await self._set_and_store("CurrentA", ts, p.current.get("a", 0.0))
        await self._set_and_store("CurrentB", ts, p.current.get("b", 0.0))
        await self._set_and_store("CurrentC", ts, p.current.get("c", 0.0))
        await self._set_and_store("PowerActive", ts, p.power.get("active", 0.0))
        await self._set_and_store("PowerReactive", ts, p.power.get("reactive", 0.0))
        await self._set_and_store("PowerApparent", ts, p.power.get("apparent", 0.0))
        await self._set_and_store("EnergyActive", ts, p.energy.get("active", 0.0))
        await self._set_and_store("EnergyReactive", ts, p.energy.get("reactive", 0.0))
        await self._set_and_store("EnergyApparent", ts, p.energy.get("apparent", 0.0))
        await self._set_and_store("PowerFactor", ts, p.powerFactor)
        await self._set_and_store("Frequency", ts, p.frequency)

        # Regras de alarme: tensão ±10%
        for phase_name, v in {
            "VoltageA": p.voltage.get("a", 0.0),
            "VoltageB": p.voltage.get("b", 0.0),
            "VoltageC": p.voltage.get("c", 0.0),
        }.items():
            dev = pct_over(v, NOMINAL_VOLTAGE)
            src = self.vars[phase_name]
            if dev > OVER_UNDER_TOL:
                await self.fire_event(src, "Electrical", "Overvoltage detected", SEVERITY["HIGH"])
            elif dev < -OVER_UNDER_TOL:
                await self.fire_event(src, "Electrical", "Undervoltage detected", SEVERITY["HIGH"])

        # Corrente > 10% acima nominal
        for phase_name, i in {
            "CurrentA": p.current.get("a", 0.0),
            "CurrentB": p.current.get("b", 0.0),
            "CurrentC": p.current.get("c", 0.0),
        }.items():
            src = self.vars[phase_name]
            if pct_over(i, NOMINAL_CURRENT) > OVER_UNDER_TOL:
                await self.fire_event(src, "Electrical", "Overcurrent detected", SEVERITY["HIGH"])

    async def _handle_environment(self, p: EnvironmentPayload):
        ts = p.timestamp
        await self._set_and_store("Temperature", ts, p.temperature)
        await self._set_and_store("Humidity", ts, p.humidity)
        await self._set_and_store("CaseTemperature", ts, p.caseTemperature)

        # Alarme crítico: caseTemperature > 60°C
        if p.caseTemperature > CASE_TEMP_CRIT:
            await self.fire_event(self.vars["CaseTemperature"], "Environment", "Case temperature critical", SEVERITY["CRIT"])

    async def _handle_vibration(self, p: VibrationPayload):
        ts = p.timestamp
        await self._set_and_store("Axial", ts, p.axial)
        await self._set_and_store("Radial", ts, p.radial)
        # Exemplo de evento 'baixo' (ajuste a regra se quiser)
        if max(p.axial, p.radial) > 0.2:
            await self.fire_event(self.vars["Axial"], "Vibration", "Slight vibration increase", SEVERITY["LOW"])


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

async def main():
    # uvloop (Linux) para melhor desempenho
    try:
        import uvloop  # type: ignore
        uvloop.install()
    except Exception:  # noqa: BLE001
        pass

    app = MotorOPCUAServer()
    await app.init()
    logger.info("OPC UA endpoint: {}", app.endpoint)
    logger.info("MQTT broker: {}:{}", app.mqtt_host, app.mqtt_port)
    await app.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print()
        logger.info("Encerrado pelo usuário.")
