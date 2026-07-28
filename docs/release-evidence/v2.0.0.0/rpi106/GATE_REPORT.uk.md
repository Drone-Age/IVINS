# Звіт нативних перевірок iVINS 2.0.0.0

Дата: 2026-07-28
Ціль: `rpi@192.168.144.106`
Обладнання: Raspberry Pi 5 Model B
Платформа: Debian 13 Trixie, `aarch64`

## Обрана матриця

| Компонент | Версія | Коміт |
| --- | --- | --- |
| iROS2j | 1.0.3 / `v2.1.0.3` | `4e4f9e159365e8d14da185655a706ed1125dea39` |
| iMAVROS | 1.0.0.2 / `v1.0.0.2` | `10634b225fd540ab3c7ad1b87a768b215e229361` |
| VINS-NEO | 1.0.3.0 / `v1_00_03_00` | `34b2805099c77d35f5489007da9a7fe66b04b6d8` |
| iVINS | чернетка 2.0.0.0 | робоче дерево для Issue #7 |

## Ідентичність артефактів

- `ivins_2.0.0.0-1+deb13_arm64.deb`:
  `b8795aff2b9c6a141466647740ebad6afe1c62eeb058ad9e3f39f0a892bc497b`
- `ivins_2.0.0.0-1+deb13_arm64.tar.zst`:
  `dee1f7d365cae716b63290507969187b1c5bb8c287c36fa692ea891d75eef98d`

Це передрелізні артефакти. Вони не є публічними релізними активами та не
мають публікуватися, доки обов'язкова перевірка має результат `FAIL`,
`BLOCKED` або `NOT_RUN`.

## Результати

| Перевірка | Результат | Докази |
| --- | --- | --- |
| Валідація історичного manifest | PASS | `native-product-build.log` |
| Валідація schema 2 manifest та артефактів | PASS | `native-product-build.log` |
| Unit-тести | PASS (18 тестів) | `native-product-build.log` |
| Синтаксис shell | PASS | `native-product-build.log` |
| Складання та payload/dependency audit meta-package | PASS | `native-product-build.log` |
| Інвентар bundle, checksums, SBOM, ключ і підписані APT metadata | PASS | `native-product-build.log`, `clean-offline-install.log` |
| Очищення продуктових пакетів і file-only offline reinstall | PASS | `clean-offline-install.log` |
| Точні встановлені версії та порядок активації | PASS | `evidence/runtime/` |
| Власність `cv_bridge` у `/opt/iros2j` | PASS | `evidence/runtime/python-prefixes.txt` |
| Вибір Fast DDS і `ros2 doctor --report` | PASS | `evidence/runtime/` |
| Повний ELF `ldd` audit | PASS (435 із 435 ELF-файлів) | `ogre-compatibility/native-install/results.tsv` |
| Контрольований ROS 2 dataset | PASS | `evidence/dataset/` |
| FCU raw MAVLink/MAVROS/IMU telemetry | PASS | `evidence/imavros-hardware/` |
| OV5647 still capture | PASS | `evidence/vins-hardware/` |
| OV5647 ROS image topic | PASS (28,8 Hz) | `evidence/camera-ros/` |
| Калібрована інтеграція camera + FCU + VINS | BLOCKED | Див. блокери нижче |
| Стійкість після reboot | NOT_RUN | Заблокований реліз не кваліфікувався reboot-перевіркою |
| Публікація та перевірка публічних активів | NOT_RUN | Реліз не має права на публікацію |

## Обов'язкові блокери

1. Налаштована система OV5647/FCU не має активного
   `/etc/vins-neo/iVIN.yaml` або еквівалентної hardware-specific конфігурації
   camera intrinsics, distortion, camera-to-IMU extrinsics, time offset і
   rolling shutter. Пакетні VINS-конфігурації призначені для dataset або інших
   пристроїв і не можуть вважатися коректною калібровкою OV5647/FCU.
2. Наявний workspace `camera_ros` складено з legacy-посиланням на underlay
   `/opt/iros2_0/jazzy`. Камера успішно публікує після попереднього source
   iROS2j, але setup виконує заборонений legacy lookup і не є придатним
   релізним input.

## Рішення щодо релізу

Загальний результат: **BLOCKED**. Чернеткові tooling, package, підписаний
offline bundle, clean reinstall, повний ELF audit, контрольований dataset,
FCU і camera gates відтворюються, але calibrated live integration критерії не
виконані. Не встановлюйте manifest у `released`, не merge-те як реліз, не
створюйте незмінні теги та не публікуйте assets, доки два блокери не виправлено
і всі пов'язані native та post-release gates не повторено.
