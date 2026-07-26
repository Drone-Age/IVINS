# INDRA Visual-Inertial Navigation System

INDRA VINS — система візуально-інерціальної навігації, що складається з
обчислювальної платформи та програмного забезпечення.

## Компоненти

- [VINS-NEO](components/VINS-NEO) — ключовий програмний компонент на базі
  ROS 2 Jazzy для Ubuntu 24.04. Компонент підключено як Git submodule, тому
  головний репозиторій фіксує перевірену версію його вихідного коду.
- [IROS2_0](components/IROS2_0) — відтворювана збірка та пакування
  ROS 2 Jazzy для Raspberry Pi 5 з Debian 13 ARM64. Build host: Windows 11
  із Docker Desktop; кінцевий результат: нативний Debian-пакет без Docker
  dependency на цільовому обладнанні.
- [iMAVROS-release](components/iMAVROS-release) — інструменти нативної збірки,
  перевірки та випуску Debian-пакета iMAVROS для Debian 13 ARM64
  (Raspberry Pi 5).

## Поставка кінцевого продукту

iVINS постачається як продуктовий Debian meta-package із точними залежностями
від `iros2-0`, `imavros` і `vins-mono-ros2`. Для офлайн-встановлення один
release bundle містить усі component `.deb`, meta-package, manifest і
контрольні суми.

- [Процес випуску iVINS](docs/RELEASE_PROCESS_UK.md)
- [Передрелізний gate](docs/PRE_RELEASE_TESTING_UK.md)
- [Узгодження процесів компонентів](docs/COMPONENT_PROCESS_ALIGNMENT_UK.md)
- [Політика версіювання](docs/VERSIONING_UK.md)

Поточний draft manifest:
[`manifests/ivins-1.0.0.0.json`](manifests/ivins-1.0.0.0.json).

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
