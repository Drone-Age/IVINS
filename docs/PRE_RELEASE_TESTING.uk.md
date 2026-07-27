# Стандарт передрелізного тестування iVINS

Кожен запланований тест має рівно один result:

- `PASS`;
- `FAIL`;
- `BLOCKED`;
- `SKIPPED_NOT_CONFIGURED`;
- `SKIPPED_NOT_APPLICABLE`;
- `NOT_RUN`.

Часткова, перервана, timed-out, skipped або blocked робота ніколи не є
`PASS`. Кожен result містить test ID, timestamps, host, target, точну команду,
root/component commits, manifest/artifact hashes, evidence location, причину
не-`PASS` та requirement effect.

## 1. Metadata та compatibility gate

1. Product/process versions, tags, manifest name, schema і changelog узгоджені.
2. Кожен компонент має immutable repository, commit, tag, version, asset URL,
   SHA-256 та gate-evidence link.
3. iROS2j APT snapshot signed, hash-pinned, Debian 13 ARM64 і фіксує точні
   package versions.
4. iMAVROS і VINS обирають той самий iROS2j release, prefix, RMW baseline та
   сумісний system ABI.
5. VINS не містить приватного ROS underlay package, особливо `cv_bridge`.
6. Історичні manifests і tags не змінені.
7. Static validators, unit tests, documentation pairing та `git diff --check`
   проходять.

## 2. Gate доказів компонентів

Приймайте component gate лише коли evidence відповідає вибраному commit,
manifest hash, artifact hash, native Raspberry Pi 5 identity, Debian 13,
`aarch64`, commands, timestamps і фінальному result.

- iROS2j: signed APT repository audit, install, clean-shell ROS/RMW smoke і
  downstream CMake consumer.
- iMAVROS: metadata, native build, package/ELF, clean install, MAVROS node і
  gate налаштованого FCU.
- VINS-NEO: metadata, native build, tests, package/ELF, clean install, runtime
  і controlled dataset gate.

## 3. Gate продуктового пакета й bundle

1. Зберіть `ivins` із committed root manifest.
2. Перевірте package metadata і точні dependencies на потрібні `iros2j-*`,
   `imavros` та `vins-mono-ros2` versions.
3. Підтвердьте, що meta-package не містить payload `/opt/iros2j`,
   `/opt/imavros` або `/opt/vins`.
4. Перевірте embedded manifest, SBOM, package hash, bundle inventory і hash
   кожного bundle file.
5. Підтвердьте наявність signed APT repository/keyring та відсутність
   unpinned network dependency або legacy `iros2-0` compatibility payload.

## 4. Gate чистого офлайн-встановлення

На чистій підтримуваній Raspberry Pi 5:

1. очистьте успадковані ROS/colcon/CMake/library environment variables;
2. перевірте bundle hashes, APT key identity і signed repository metadata;
3. встановіть із вимкненою мережею або доведіть відсутність network fallback;
4. перевірте точні installed package versions і Debian ownership;
5. доведіть відсутність `iros2-0` і `/opt/iros2_0/jazzy`;
6. доведіть, що `cv_bridge` вирішується лише в `/opt/iros2j`;
7. активуйте `/opt/iros2j`, `/opt/imavros`, потім `/opt/vins`;
8. виконайте `ros2 doctor --report`, package-prefix checks, version commands і
   повний ELF `ldd` audit.

## 5. Integration та acceptance gate

1. Використайте вибраний Fast DDS RMW, однаковий `ROS_DOMAIN_ID` і сумісну DDS
   discovery configuration для всіх процесів.
2. Запустіть iMAVROS із налаштованим flight controller.
3. Запустіть налаштований camera path і VINS.
4. Перевірте IMU/image topics, types, rates, QoS compatibility, timestamps,
   clock domain, frames, TF tree та відсутність duplicate publishers.
5. Перевірте, що VINS досяг потрібного operating state і публікує valid
   odometry.
6. Виконайте pinned dataset acceptance test і запишіть thresholds/results.
7. Виконайте configured-hardware smoke і reboot/login-shell persistence tests.

Hardware, відсутнє в authoritative configuration, може мати
`SKIPPED_NOT_CONFIGURED`; неочікувано недоступне configured hardware має
`BLOCKED` або `FAIL`. Обов’язковий skip не задовольняє release gate.

## 6. Release та post-release criterion

`FAIL` провалює gate. Інакше будь-який обов’язковий `BLOCKED`, `NOT_RUN` або
непогоджений skip блокує його. Звичайний `PASS` вимагає проходження кожного
застосовного обов’язкового тесту.

Після публікації завантажте public assets, повторіть signature/hash
verification, clean offline install, activation, ROS/RMW smoke, component
version checks і representative integration smoke. Release gate можуть
закрити лише перевірені public artifacts.
