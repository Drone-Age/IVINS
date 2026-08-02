# Gate сумісності OGRE loader для iVINS 2.0.0.0

Дата: 2026-07-28
Ціль: `rpi@192.168.144.106`
Платформа: Raspberry Pi 5 Model B, Debian 13, `aarch64`
Результат: **PASS**

## Реалізація

Пакет `ivins` володіє `/usr/share/ivins/activate.sh`. У clean shell
версійований hook активує iROS2j, рівно один раз додає
`/opt/iros2j/rviz_ogre_vendor/opt/rviz_ogre_vendor/lib/OGRE` на початок
`LD_LIBRARY_PATH`, а потім активує iMAVROS і VINS. Він не змінює, не патчить,
не замінює і не перепаковує iROS2j.

## Результати

| Тест | Результат | Evidence |
| --- | --- | --- |
| Детермінована та ідемпотентна активація clean shell | PASS | `native-install/clean-shell-activation.txt` |
| Розв'язання залежності `Plugin_OctreeZone` | PASS | `native-install/octree-ldd.txt` |
| Smoke завантаження shared object OGRE | PASS | `native-install/ogre-plugin-smoke.txt` |
| Повний аудит встановлених ELF | PASS, 435/435 | `native-install/elf-ldd-audit.txt`, порожній `native-install/elf-ldd-failures.txt` |
| Immutable встановлений payload iROS2j | PASS | Ідентичні `iros2j-installed-before.sha256` та `offline-reinstall-final/iros2j-installed-after-reinstall.sha256`; SHA-256 списку `837b603030ff1a5c0d829b371da2214fce8831c69626445a6e42d05a69c6e88d` |
| Immutable release inputs iROS2j | PASS | Ідентичні `iros2j-release-inputs-before.sha256` та `iros2j-release-inputs-after.sha256` |
| Clean reinstall із підписаного bundle | PASS | `offline-reinstall-final/clean-offline-reinstall.log` |
| ELF/OGRE gate після clean reinstall | PASS, 435/435 | `offline-reinstall-final/ogre-gate-after-reinstall/results.tsv` |

## Артефакти продукту

- `ivins_2.0.0.0-1+deb13_arm64.deb`:
  `9590c1615ceecd362a034d8e9ea17afe4d246096e490bb6ae828e65bba06ce6f`
- `ivins_2.0.0.0-1+deb13_arm64.tar.zst`:
  `94970a6ab5bdae7f7db7fda5497332fbbab68cd53a877e341447b536bb6d6ca6`

Цей gate усуває лише блокер OGRE loader. Незалежні блокери calibration та
camera workspace залишаються поза межами цієї задачі.
