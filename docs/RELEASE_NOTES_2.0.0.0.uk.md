# Нотатки до релізу iVINS 2.0.0.0

Статус: draft.

## Матриця компонентів

| Компонент | Незмінний реліз |
|---|---|
| iROS2j | 1.0.3, tag `v2.1.0.3`, commit `4e4f9e159365e8d14da185655a706ed1125dea39` |
| iMAVROS | 1.0.0.2, tag `v1.0.0.2`, commit `10634b225fd540ab3c7ad1b87a768b215e229361` |
| VINS-NEO | 1.0.3.0, tag `v1_00_03_00`, commit `34b2805099c77d35f5489007da9a7fe66b04b6d8` |

Цей реліз замінює історичний монолітний контракт встановлення `iros2-0`
на signed split-package iROS2j APT snapshot у `/opt/iros2j`. Підтримуваний
порядок активації: `/opt/iros2j`, `/opt/imavros`, потім `/opt/vins`, із
`rmw_fastrtps_cpp`.

## Offline-постачання

Автономний bundle містить signed iROS2j APT snapshot і ключ, точні пакети
iMAVROS та VINS-NEO, payload-free iVINS meta-package, build-input manifest,
package inventory, SBOM, installer, release notes і `SHA256SUMS`. Installer
налаштовує лише bundled repository та відхиляє історичний package і prefix.

## Статус релізу

Meta-package, підписаний offline bundle, clean offline reinstall,
контрольований dataset, налаштований FCU та OV5647 gates пройшли на
авторизованому Raspberry Pi 5. Публікацію заблоковано через iROS2j 1.0.3 OGRE
ELF dependency failure, відсутність hardware-specific OV5647/FCU VINS
calibration та legacy-посилання доступного camera workspace на underlay
`/opt/iros2_0/jazzy`. Дивіться [версійований звіт native gates](release-evidence/v2.0.0.0/rpi106/GATE_REPORT.uk.md).
Цю чернетку не можна публікувати, доки кожен обов'язковий результат не матиме
`PASS`.
