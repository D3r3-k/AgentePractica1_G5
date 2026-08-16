<div align="center">

# Práctica 1 — Análisis de Ventas Online 2021 - Grupo 5

**Sistemas Organizacionales y Gerenciales 2**

Facultad de Ingeniería · Ingeniería en Ciencias y Sistemas

Universidad de San Carlos de Guatemala · Segundo Semestre 2026

Entregable: `SOG2-2S26_grupo5.pdf`

</div>

---
	
## Integrantes

|   #   | Nombre                          |   Carné   | Bloque asignado                           |
| :---: | ------------------------------- | :-------: | ----------------------------------------- |
|   1   | Derek Francisco Orellana Ibáñez | 202001151 | Datos y Base de Datos                     |
|   2   | Juan Esteban Chacón Trampe      | 202300431 | MCPServer                                 |
|   3   | Daniel Andree Hernandez Flores  | 202300512 | Agente conversacional (Google ADK)        |
|   4   | Fátima Florisel Cerezo Paredes  | 202300434 | Análisis exploratorio y de tendencias     |
|   5   | Valery Pamela Alarcon Ramos     | 202300794 | Segmentación, correlación e informe final |


El detalle de tareas por integrante está en [`docs/01-planificacion.md`](docs/01-planificacion.md).

---

## Índice

- [Planificacion](docs/01-planificacion.md)
- [Proceso de Análisis](docs/02-proceso-analisis.md)
- [Metodología](docs/03-metodologia.md)
- [Conclusiones](docs/04-conclusiones.md)
- [Recomendaciones](docs/05-recomendaciones.md)
- [Respuestas](docs/06-respuestas.md)
- [Diagrama de BD](docs/07-diagrama-bd.md)

---


## Configuración

> [!NOTE] Windows

```bash
git clone https://github.com/D3r3-k/AgentePractica1_G5.git
cd AgentePractica1_G5
```

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

```bash
copy .env.example .env
# Llenar .env con las credenciales
python db/conexion.py
```

> [!NOTE] Linux

```bash
git clone https://github.com/D3r3-k/AgentePractica1_G5.git
cd AgentePractica1_G5
```

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```bash
cp .env.example .env
# Llenar .env con las credenciales
python3 db/conexion.py
```

> [!NOTE] Mac

```bash
git clone https://github.com/D3r3-k/AgentePractica1_G5.git
cd AgentePractica1_G5
```

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```bash
cp .env.example .env
# Llenar .env con las credenciales
python3 db/conexion.py
```

