# INDRA Visual-Inertial Navigation System

INDRA VINS — система візуально-інерціальної навігації, що складається з
обчислювальної платформи та програмного забезпечення.

## Компоненти

- [VINS-NEO](https://github.com/Drone-Age/VINS-NEO) — ключовий програмний
  компонент на базі ROS 2 Jazzy.
- [IROS2_0](https://github.com/Drone-Age/iros2_0) — відтворювана збірка та пакування
  ROS 2 Jazzy для Raspberry Pi 5 з Debian 13 ARM64. Build host: Windows 11
  із Docker Desktop; кінцевий результат: нативний Debian-пакет без Docker
  dependency на цільовому обладнанні.
- [iMAVROS-release](https://github.com/Drone-Age/iMAVROS-release) — інструменти нативної збірки,
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

Клонуйте кореневий репозиторій звичайним способом:

```bash
git clone <URL-РЕПОЗИТОРІЮ-INDRA>
```

Компоненти не зберігаються як Git submodules. Їхні точні repository, commit,
tag, Debian version, artifact URL і SHA-256 зафіксовані в release manifest.

## Розгортання VINS-NEO

Інструкції зі встановлення, конфігурації, запуску та діагностики містяться у
[документації VINS-NEO](https://github.com/Drone-Age/VINS-NEO).
