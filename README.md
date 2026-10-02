# Robot Run Audit

## Français

Alpha locale et en lecture seule pour vérifier la **continuité temporelle** d’un enregistrement robotique MCAP ou rosbag2 SQLite (`.db3`). Elle relève les sujets attendus absents, les grands intervalles et les fréquences moyennes insuffisantes. Le rapport JSON contient une empreinte SHA-256 du fichier, les mesures par sujet et les anomalies. Les seuils viennent d’un fichier explicite ; aucun seuil universel n’est supposé.

```sh
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests
.venv/bin/python fixtures/make_sample.py essai.mcap
.venv/bin/robot-run-audit essai.mcap fixtures/rules.json --locale=fr
.venv/bin/robot-run-audit trajet.mcap fixtures/rules.json --locale=fr --output=rapport.json
```

Copier `fixtures/rules.json` puis ajuster `min_hz` et `max_gap_ms` pour chaque sujet. Le code de sortie est 0 si les règles passent, 1 en présence d’anomalies et 2 pour une entrée invalide. Les données de démonstration dans les tests sont synthétiques. L’outil ne décode pas les messages, ne vérifie ni TF, ni l’étalonnage, ni la sûreté du robot. Une fréquence moyenne correcte peut masquer une défaillance brève : examiner aussi les intervalles et les traces brutes. Un seul fichier `.db3` est analysé à la fois ; les segments multiples nécessitent une étape de regroupement.

## English

Local, read-only alpha for checking the **timing continuity** of an MCAP or rosbag2 SQLite (`.db3`) robot recording. It flags missing expected topics, large gaps and low average rates. The JSON report includes the file’s SHA-256 hash, per-topic measurements and findings. Thresholds come from an explicit rules file; no universal threshold is assumed.

```sh
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests
.venv/bin/python fixtures/make_sample.py sample.mcap
.venv/bin/robot-run-audit sample.mcap fixtures/rules.json --locale=en
.venv/bin/robot-run-audit run.mcap fixtures/rules.json --locale=en --output=report.json
```

Copy `fixtures/rules.json` and set `min_hz` and `max_gap_ms` for each topic. Exit code 0 means the rules passed, 1 means findings, and 2 means invalid input. Test recordings are synthetic. The tool does not decode payloads or verify TF, calibration or robot safety. A good average rate can hide a short failure: inspect gaps and raw traces too. It checks one `.db3` file at a time; multi-file bags need a separate aggregation step.

## Español

Alfa local y de solo lectura para comprobar la **continuidad temporal** de una grabación robótica MCAP o rosbag2 SQLite (`.db3`). Señala temas esperados ausentes, intervalos excesivos y frecuencias medias bajas. El informe JSON incluye el hash SHA-256 del archivo, mediciones por tema y anomalías. Los límites proceden de reglas explícitas; no se supone un límite universal.

```sh
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests
.venv/bin/python fixtures/make_sample.py muestra.mcap
.venv/bin/robot-run-audit muestra.mcap fixtures/rules.json --locale=es
.venv/bin/robot-run-audit recorrido.mcap fixtures/rules.json --locale=es --output=informe.json
```

Copia `fixtures/rules.json` y ajusta `min_hz` y `max_gap_ms` para cada tema. El código de salida 0 indica que se cumplen las reglas, 1 indica anomalías y 2 indica una entrada no válida. Las grabaciones de prueba son sintéticas. La herramienta no decodifica mensajes ni verifica TF, calibración o seguridad del robot. Una frecuencia media correcta puede ocultar un fallo breve: revisa también los intervalos y las trazas originales. Analiza un solo archivo `.db3` cada vez; las grabaciones con varios segmentos requieren una agregación aparte.

MIT — [LICENSE](LICENSE).
