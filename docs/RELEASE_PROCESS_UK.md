# Процес складання та поставки iVINS

## 1. Планування

1. Створити release issue з версією, tag, scope і критеріями приймання.
2. Вибрати лише опубліковані component releases, окрім першого інтеграційного
   draft, де неопублікований компонент явно блокує фінальний release.
3. Оновити підмодулі до точних release commits.
4. Створити `manifests/ivins-<version>.json` і зафіксувати component commits,
   tags, Debian versions, artifact URL та SHA-256.
5. Оновити `VERSION`, `CHANGELOG.md` і release notes одним change.

## 2. Перевірка metadata

До commit:

```bash
python3 scripts/validate-release.py manifests/ivins-<version>.json
python3 -m unittest discover -s tests -v
git diff --check
```

Після commit команди повторюються для committed snapshot. Gitlink-и та manifest
мають входити до одного commit.

## 3. Збірка компонентів

Компоненти збираються у dependency order:

1. `IROS2_0`;
2. `iMAVROS`;
3. `VINS-NEO`;
4. `ivins` meta-package та offline bundle.

Для кожного компонента використовується тільки його tracked native release
entry point і власний gate. Локальна успішна збірка не замінює component
release evidence.

## 4. Product gate

На native Debian 13 ARM64:

```bash
scripts/build-meta-package.sh manifests/ivins-<version>.json artifacts
scripts/audit-meta-package.sh \
  artifacts/ivins_<debian-version>_arm64.deb \
  manifests/ivins-<version>.json
```

Після цього виконується весь
[передрелізний gate](PRE_RELEASE_TESTING_UK.md), включно з чистим встановленням
та інтеграційними тестами.

## 5. Фіксація evidence

Кожний evidence-файл повинен містити або однозначно посилатися на:

- root commit і SHA-256 root manifest;
- component commits, tags і artifact SHA-256;
- host identity, Debian release, architecture і timestamps;
- точну команду та exit status;
- результат `PASS`/`FAIL` без неявного пропуску тестів.

Усі evidence для фінального release мають бути незмінними та доступними разом
з release assets.

## 6. Публікація

1. Заповнити checksums і evidence у manifest.
2. Змінити `release.status` на `released`.
3. Виконати `validate-release.py --released`.
4. Злити перевірений commit у `main`.
5. Створити immutable annotated product tag на цьому commit.
6. Опублікувати versioned artifacts, offline bundle, manifest, `SHA256SUMS`,
   SBOM, release notes і gate evidence.
7. Не використовувати `latest` asset як вхід іншого release manifest.

## 7. Post-release

На чистому пристрої повторно завантажити assets із GitHub Release, перевірити
checksums, встановити продукт і повторити clean-install/runtime smoke gate.
Результат записати в release issue.

Якщо перевірка не пройшла, release відкликається. Tag не видаляється й не
переміщується; виправлення отримує нову версію.
