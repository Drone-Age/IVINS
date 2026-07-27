# Передрелізний gate кінцевого продукту iVINS

> Legacy notice: цей документ описує gate iVINS 1.0.0.0 на основі
> `iros2-0`. Чинний регламент:
> [PRE_RELEASE_TESTING.uk.md](PRE_RELEASE_TESTING.uk.md).

Усі пункти обов’язкові. Пропущена перевірка має стан `BLOCKED` або `FAIL`,
але ніколи не вважається `PASS`.

## 1. Metadata gate

1. `VERSION`, release tag, Debian-версія та ім’я manifest узгоджені.
2. Manifest містить точні repository, commit і immutable tag кожного компонента.
3. Для кожного компонента зафіксовано immutable tag, package version, artifact
   URL та SHA-256.
4. Manifest має статус `draft` до завершення всіх перевірок.
5. `python3 scripts/validate-release.py <manifest>` завершується успішно.
6. `git diff --check` не знаходить помилок.

## 2. Component native gates

Кожний компонент проходить власний нормативний release gate на native
Raspberry Pi 5 / Debian 13 ARM64. iVINS приймає результат лише якщо evidence:

- містить точний component commit і SHA-256 committed component manifest;
- містить SHA-256 фактичного `.deb`;
- описує host, OS, architecture, toolchain і час;
- має фінальний стан `PASS`;
- не походить від іншого commit або перебудованого artifact.

Обов’язкові component gates:

- IROS2_0: native build, package audit, ROS base та clean-shell smoke;
- iMAVROS: metadata/native/package gate і MAVROS node smoke-test;
- VINS-NEO: metadata/native/package gate, `colcon test`, ELF audit і dataset test.

## 3. Product package gate

1. Зібрати `ivins` meta-package з committed root manifest.
2. Перевірити `Package`, `Version`, `Architecture` та точні `Depends`.
3. Перевірити, що пакет не дублює `/opt/iros2_0`, `/opt/imavros` або `/opt/vins`.
4. Перевірити embedded manifest і SHA-256 meta-package.
5. Сформувати offline bundle лише з перевірених component artifacts.
6. Перевірити checksum кожного файла після формування bundle.

## 4. Clean-install product gate

На чистій підтримуваній Raspberry Pi:

1. Завантажити опублікований bundle або packages, а не локальні build-файли.
2. Перевірити всі SHA-256.
3. Встановити `ivins` через APT і переконатися, що APT встановив точні версії
   `iros2-0`, `imavros` та `vins-mono-ros2`.
4. Запустити clean shell без успадкованих `AMENT_PREFIX_PATH`,
   `COLCON_PREFIX_PATH`, `CMAKE_PREFIX_PATH`, `LD_LIBRARY_PATH` і `ROS_DISTRO`.
5. Активувати overlays у нормативному порядку.
6. Перевірити `ros2 doctor --report`, MAVROS packages/nodes, VINS packages,
   версію estimator і всі ELF dependencies.

## 5. Інтеграційні та приймальні тести

1. Запустити iMAVROS із цільовим flight controller або затвердженим SITL.
2. Підтвердити стабільне отримання IMU та camera topics.
3. Запустити зафіксований dataset test VINS і перевірити визначені пороги.
4. Виконати hardware smoke-test із реальною камерою та IMU.
5. Зафіксувати topics, rates, QoS, frames, конфігурацію сенсорів і результати.
6. Перевірити reboot/login-shell сценарій.

## 6. Release criterion

Перед публікацією `release.status` змінюється на `released`, у manifest
записуються всі artifact checksums і посилання на evidence. Фінальна команда:

```bash
python3 scripts/validate-release.py \
  manifests/ivins-<version>.json --released
```

Тег заборонено створювати або переміщувати, якщо команда не пройшла.
