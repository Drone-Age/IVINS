# INDRA Visual-Inertial Navigation System

INDRA VINS — система візуально-інерціальної навігації, що складається з
обчислювальної платформи та програмного забезпечення.

## Компоненти

- [VINS-NEO](components/VINS-NEO) — ключовий програмний компонент на базі
  ROS 2 Jazzy для Ubuntu 24.04. Компонент підключено як Git submodule, тому
  головний репозиторій фіксує перевірену версію його вихідного коду.
- [IROS2-Jazzy](components/IROS2-Jazzy) — відтворювана збірка та пакування
  ROS 2 Jazzy для Raspberry Pi 5 з Debian 13 ARM64. Build host: Windows 11
  із Docker Desktop; кінцевий результат: нативний Debian-пакет без Docker
  dependency на цільовому обладнанні.

## Отримання проєкту

Клонуйте репозиторій разом із підмодулями:

```bash
git clone --recurse-submodules <URL-РЕПОЗИТОРІЮ-INDRA>
```

Якщо головний репозиторій уже клоновано:

```bash
git submodule update --init --recursive
```

## Розгортання VINS-NEO

Інструкції зі встановлення, конфігурації, запуску та діагностики містяться у
[документації VINS-NEO](components/VINS-NEO/docs/README_UK.md). Відтворюване
розгортання через Docker описано в
[Docker-посібнику](components/VINS-NEO/docs/DOCKER_UK.md).
