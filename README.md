# INDRA Visual-Inertial Navigation System

INDRA VINS — система візуально-інерціальної навігації, що складається з
обчислювальної платформи та програмного забезпечення.

## Набори даних / Datasets

- [DataSetsManager/client](https://github.com/DataSetsManager/client) — CLI,
  конфігурації та каталог наборів даних / CLI, configurations, and dataset catalog.
- [DataSetsManager/server](https://github.com/DataSetsManager/server) — публічний
  Web-каталог, API та авторизовані локальні artifacts / public Web catalog, API,
  and authenticated local artifacts.
- [Документація й ITSM / Documentation and ITSM](https://github.com/DataSetsManager/DataSetsManager).

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
- [Draft release notes iVINS 2.0.0.0](docs/RELEASE_NOTES_2.0.0.0.uk.md)

Історичний manifest випуску 1.0.0.0:
[`manifests/ivins-1.0.0.0.json`](manifests/ivins-1.0.0.0.json).

Поточний draft manifest випуску 2.0.0.0:
[`manifests/ivins-2.0.0.0.json`](manifests/ivins-2.0.0.0.json).

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
