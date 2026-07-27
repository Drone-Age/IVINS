# Контракт сумісності компонентів iVINS

Ця політика визначає інтеграційну межу між iVINS, iROS2j, iMAVROS та
VINS-NEO. Локальні правила компонентів можуть бути суворішими, але не можуть
послаблювати цей контракт.

## Підтримувана ціль і матриця

Ціль: native Raspberry Pi 5, Debian 13 Trixie, `arm64`/`aarch64`, ROS 2 Jazzy.
Результати Docker, QEMU, емуляції, cross-compilation, AMD64 або іншого host не
є native product evidence.

Наступна матриця повинна вибрати незмінні релізи з такими контрактами:

| Компонент | Обов’язковий контракт |
|---|---|
| iROS2j | released signed APT snapshot; split-пакети `iros2j-*`; `/opt/iros2j`; поточний compatible baseline 1.0.3 / `v2.1.0.3` |
| iMAVROS | released ARM64 `.deb`, зібраний проти того самого точного iROS2j snapshot; `/opt/imavros`; поточний compatible baseline 1.0.0.2 |
| VINS-NEO | новий released ARM64 `.deb`, зібраний проти того самого iROS2j snapshot; `/opt/vins`; без приватних копій ROS dependencies |
| iVINS | meta-package без payload, manifest, installer, evidence та offline bundle |

VINS-NEO 1.0.2.0 є історичним і несумісним із цією матрицею: він залежить від
`iros2-0`, активує `/opt/iros2_0/jazzy` та вбудовує приватний `cv_bridge`.
До проходження власних gate новим VINS release нова продуктова матриця iVINS
має стан `BLOCKED`, а не released.

## Власність і залежності

- iROS2j володіє ROS underlay packages, включно з `cv_bridge`,
  `image_transport`, messages, TF2, RMW implementations і RViz.
- iMAVROS володіє лише overlay `/opt/imavros` та декларує точні потрібні
  Debian dependencies `iros2j-*`.
- VINS-NEO володіє лише overlay `/opt/vins` і споживає ROS dependencies з
  iROS2j. Він не повинен збирати чи постачати другий `cv_bridge`.
- iVINS не дублює payload компонентів. Його Debian dependencies та embedded
  manifest визначають точну installable matrix.

Root manifest фіксує iROS2j release tag/commit, signed APT asset URL і SHA-256,
repository metadata/key identity, точний набір packages і Debian versions;
iMAVROS та VINS release commits/tags, `.deb` URL і SHA-256; усі component gate
evidence.

## Активація середовища

Нормативний clean-shell порядок:

```bash
source /opt/iros2j/setup.bash
source /opt/imavros/setup.bash
source /opt/vins/setup.bash
```

Усі процеси використовують вибраний `RMW_IMPLEMENTATION` (Fast DDS для
поточного baseline), однаковий `ROS_DOMAIN_ID` і сумісні DDS discovery
settings. Integration gate перевіряє package resolution, topics, QoS,
timestamps, frames, TF та ELF library resolution після цієї активації.

## Офлайн-поставка

Bundle містить signed iROS2j APT repository snapshot і keyring,
iMAVROS/VINS/iVINS `.deb`, root manifest, installer, `SHA256SUMS`, SBOM,
release notes і gate evidence. Installer налаштовує лише bundled APT snapshot,
перевіряє hashes і signatures та встановлює через APT. Він не створює legacy
packages або compatibility prefixes.
