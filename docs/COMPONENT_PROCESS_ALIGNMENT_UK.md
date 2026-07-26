# Узгодження процесів компонентів

Цей документ визначає спільний контракт між iVINS, IROS2_0, iMAVROS та
VINS-NEO. Локальні правила компонентів можуть бути суворішими, але не можуть
послаблювати цей контракт для кінцевої поставки.

| Сфера | Єдине правило iVINS | Джерело практики |
|---|---|---|
| Платформа | Debian 13 Trixie, native ARM64/aarch64, Raspberry Pi 5 | усі компоненти |
| Вхід release | committed manifest із точними commit, tags, package versions, URL і SHA-256 | iMAVROS, VINS-NEO |
| Версії | окремі продуктова і процесна послідовності | iMAVROS |
| Metadata gate | перевірка staged/committed стану до тегу | iMAVROS, VINS-NEO |
| Native build | без Docker, емуляції та cross-compilation | iMAVROS, VINS-NEO |
| Пакування | окремі `.deb`, точні Debian Depends, окремі `/opt` prefixes | усі компоненти |
| Portability | відсутні build-host paths, broken symlinks, RPATH/RUNPATH і ELF `not found` | IROS2_0, iMAVROS |
| Install gate | чисте APT-встановлення з опублікованих артефактів | IROS2_0 |
| Runtime gate | clean-shell ROS smoke-test у порядку IROS2_0 → iMAVROS → VINS | IROS2_0, iMAVROS |
| Product gate | контрольований dataset test VINS із зафіксованими входами | VINS-NEO |
| Evidence | JSON/log із commit, manifest hash, artifact hash, host і timestamps | iMAVROS |
| Публікація | незмінний tag лише після всіх pre-release gate | iMAVROS, VINS-NEO |
| Post-release | повторне завантаження, checksum, clean install і smoke-test | усі компоненти |

## Імена й prefixes

| Компонент | Debian package | Install prefix |
|---|---|---|
| IROS2_0 | `iros2-0` | `/opt/iros2_0/jazzy` |
| iMAVROS | `imavros` | `/opt/imavros` |
| VINS-NEO | `vins-mono-ros2` | `/opt/vins` |
| iVINS | `ivins` | payload відсутній; це meta-package |

Компонент не копіює payload іншого компонента. `ivins` містить committed
release manifest та точні Debian dependencies. Офлайн-поставка є одним
архівом із чотирма `.deb`, checksums, manifest і installer, але пакети
залишаються незалежними одиницями обліку APT.

## Порядок середовищ

Runtime завжди активується в такому порядку:

```bash
source /opt/iros2_0/jazzy/setup.bash
source /opt/imavros/setup.bash
source /opt/vins/setup.bash
```

Зміна цього порядку є зміною процесного контракту.
