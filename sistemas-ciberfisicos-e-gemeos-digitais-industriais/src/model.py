from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Dict, Optional

# Tópicos e payloads (pydantic) conforme enunciado

class ElectricalPayload(BaseModel):
    timestamp: str
    voltage: Dict[str, float]
    current: Dict[str, float]
    power: Dict[str, float]
    energy: Dict[str, float]
    powerFactor: float
    frequency: float

class EnvironmentPayload(BaseModel):
    timestamp: str
    temperature: float
    humidity: float
    caseTemperature: float

class VibrationPayload(BaseModel):
    timestamp: str
    axial: float
    radial: float

# Severidades conforme tabela do enunciado
SEVERITY = {
    "INFO": 100,
    "LOW": 250,
    "MED": 500,
    "HIGH": 700,
    "CRIT": 900,
}

# Valores nominais (ajuste conforme seu caso)
NOMINAL_VOLTAGE = 220.0  # V
NOMINAL_CURRENT = 10.0   # A (estimativa para regras)

# Limites para alarmes
OVER_UNDER_TOL = 0.10  # ±10%
CASE_TEMP_CRIT = 60.0  # °C

# Nomes de tópicos
TOPIC_ELEC = "scgdi/motor/electrical"
TOPIC_ENV = "scgdi/motor/environment"
TOPIC_VIB = "scgdi/motor/vibration"

# Estrutura dos nós/variáveis do servidor
MOTOR_NODE_NAME = "Motor50CV"