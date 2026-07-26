# Нотатки до випуску iVINS v1.0.0.0

Статус: **чернетка, не для публікації**.

## Склад випуску

iVINS v1.0.0.0 об'єднує окремі versioned Debian-пакети для Raspberry Pi 5 з
Debian 13 Trixie ARM64:

- `iros2-0 (= 0.1.2-1+deb13)`;
- `imavros (= 1.0.0.1-1+deb13)`;
- `vins-mono-ros2 (= 1.0.2.0)`;
- продуктовий meta-package `ivins (= 1.0.0.0-1+deb13)`.

Кінцева offline-поставка має містити чотири пакети, release manifest,
`SHA256SUMS`, SBOM, provenance/build logs і evidence для всіх обов'язкових
gate.

## Підтверджені входи

- IROS2_0 `v0.1.2`, commit
  `290eabe293289547e97dd07d967a24f25bbc81d6`, package SHA-256
  `96033cd5c1b8b09e92841d4f6693109699f5a961772a1fa13e91027d70c11a93`.
- iMAVROS `v1.0.0.1`, commit
  `b6a48765f482a772c35181621c382d2506a2f871`, package SHA-256
  `1aa85d135a1e843b794bf110a8665c57951567e90b2b94254a10e13418af3f25`.
- VINS-NEO `v1_00_02_00`, commit
  `69a1a747db5a88b8db2b348d90ca3051b35fdeb2`, package SHA-256
  `757d043393cdd956a4ecc9c2a2945a3415449ee3fcac2ee6c8f59b57c41d7bd6`.

Усі три versioned `.deb` завантажено з відповідних GitHub Releases і їхні
SHA-256 незалежно перевірено під час підготовки цієї чернетки.

## Блокери публікації

- Для всіх компонентів потрібне повне нормативне native-gate evidence.
- Для опублікованого VINS release оператор пропустив install/smoke і dataset
  tests. Власник явно дозволив використати незмінний пакет із наведеним вище
  SHA-256; це рішення зафіксовано в
  `docs/release-evidence/v1.0.0.0/GATE_EXCEPTIONS.md` і не перетворює
  пропущені перевірки на `PASS`.
- Не виконані product package, clean-install, integration, hardware,
  final-release та post-release gate.

Статус manifest не можна змінювати з `draft` на `released`, доки всі
перелічені перевірки не матимуть зафіксованого стану `PASS`.
