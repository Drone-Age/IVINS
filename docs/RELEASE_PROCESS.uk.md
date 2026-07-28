# Процес випуску iVINS

## 1. Планування та придатність

Створіть пов’язані GitHub Issue і ClickUp task із версією, scope, матрицею
компонентів, acceptance criteria, estimates та впорядкованими gate. Обирайте
лише опубліковані незмінні component releases із повними обов’язковими
evidence.

Для наступної матриці на iROS2j:

- iROS2j надає signed versioned Debian 13 ARM64 APT snapshot;
- iMAVROS випущений проти того самого точного snapshot;
- VINS-NEO випущений проти того самого snapshot без приватного `cv_bridge`;
- усі три component gate визначають точні release commits та artifacts.

Якщо потрібний VINS release ще не опубліковано, підготовка може тривати, але
продуктовий реліз залишається `BLOCKED`.

## 2. Root manifest

Створіть новий `manifests/ivins-<version>.json`; не змінюйте опублікований
manifest 1.0.0.0. Наступна матриця використовує `schema_version: 2`;
schema version 1 залишається чинною лише для перевірки історичного релізу
1.0.0.0. Нова schema повинна відрізняти:

- iROS2j APT repository artifact, SHA-256, signing-key identity,
  Release/InRelease metadata, package inventory і точні Debian versions;
- iMAVROS та VINS `.deb` із package metadata і SHA-256;
- iVINS meta-package та offline bundle;
- component, integration, dataset, hardware, publication і post-release
  evidence.

Manifest має статус `draft` до проходження всіх обов’язкових gate. `latest`
URLs, floating branches, mutable package feeds, inferred versions і локально
перезібрані замінники заборонені.

## 3. Metadata та tooling gate

До коміту й повторно з committed snapshot:

```bash
python3 scripts/validate-release.py manifests/ivins-<version>.json
python3 -m unittest discover -s tests -v
git diff --check
```

Validator, schema/tests, `packaging/control.in`, meta-package builder, offline
installer, bundle builder, audit scripts та SBOM generation повинні
підтримувати signed APT snapshot і split-package dependency model до
придатності нового manifest.

## 4. Component gate у порядку залежностей

Виконайте tracked native release workflow кожного компонента:

1. iROS2j signed APT snapshot і downstream-consumer gate;
2. iMAVROS build/package/hardware gate проти вибраного snapshot;
3. VINS-NEO build/package/dataset gate проти вибраного snapshot;
4. iVINS meta-package, offline bundle та integration gate.

Component `PASS` приймається лише для точних commit, manifest, artifact і hash,
вибраних root manifest.

## 5. Формування продукту

Meta-package `ivins` не містить component payload. Він декларує точні
dependencies на потрібні `iros2j-*`, точні Debian versions iMAVROS і VINS.
Bundle містить signed APT snapshot і keyring, component/meta `.deb`, root
manifest, installer, `SHA256SUMS`, SBOM, release notes та evidence.

Offline installer повинен:

1. перевірити hashes bundle та кожного файла;
2. перевірити bundled APT signing key і signed repository metadata;
3. налаштувати лише bundled repository;
4. встановити через APT без network fallback;
5. перевірити точні installed package versions і prefixes;
6. видалити тимчасову repository configuration без видалення installed state.

## 6. Приймання продукту

Виконайте `PRE_RELEASE_TESTING.md` на дозволеній Raspberry Pi 5. Кожен
запланований тест отримує явний result. Обов’язковий `FAIL`, `BLOCKED`,
`NOT_RUN` або непогоджений skip забороняє реліз.

Перед публікацією встановіть root manifest у `released`, додайте остаточні
artifact hashes та evidence URLs і виконайте validator у released mode.
Злийте reviewed commit, потім створіть незмінні product і process tags.
Публікуйте лише artifacts, створені перевіреним workflow.

## 7. Post-release

На чистій підтримуваній цілі завантажте public release assets, перевірте
signatures і hashes, встановіть лише з опублікованого bundle та повторіть
clean-install/runtime/integration smoke gate. Збережіть стійкі evidence.

Якщо перевірка не пройшла, позначте реліз defective або revoked. Не видаляйте,
не переміщуйте й не перевикористовуйте tag або version; виправляйте новим
релізом.
