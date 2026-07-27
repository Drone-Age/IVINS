# INDRA Visual-Inertial Navigation System

INDRA VINS — система візуально-інерціальної навігації, що складається з
обчислювальної платформи та програмного забезпечення.

## Компоненти

- [VINS-NEO](https://github.com/Drone-Age/VINS-NEO) — ключовий програмний
  компонент на базі ROS 2 Jazzy.
- [iROS2j](https://github.com/Drone-Age/iros2_0) — нативно зібраний signed
  APT snapshot ROS 2 Jazzy зі split-пакетами `iros2j-*` для Raspberry Pi 5
  з Debian 13 ARM64 та prefix `/opt/iros2j`.
- [iMAVROS-release](https://github.com/Drone-Age/iMAVROS-release) — інструменти нативної збірки,
  перевірки та випуску Debian-пакета iMAVROS для Debian 13 ARM64
  (Raspberry Pi 5).

## Поставка кінцевого продукту

iVINS постачається як продуктовий Debian meta-package із точними залежностями
від потрібних `iros2j-*` пакетів, `imavros` і `vins-mono-ros2`. Офлайн bundle
містить signed iROS2j APT snapshot, component `.deb`, meta-package, manifest,
installer, SBOM, evidence і контрольні суми.

- [Нормативна документація](docs/README.md)
- [Процес випуску iVINS](docs/RELEASE_PROCESS.uk.md)
- [Передрелізний gate](docs/PRE_RELEASE_TESTING.uk.md)
- [Контракт сумісності компонентів](docs/COMPONENT_PROCESS_ALIGNMENT.uk.md)
- [Політика версіонування](docs/VERSIONING.uk.md)

Історичний manifest випуску 1.0.0.0:
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
