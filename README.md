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

### Empreinte de politique exécutable

`robot-policy-fingerprint` calcule une empreinte à partir des fichiers de poids et de normalisation **effectivement sélectionnés**, des autres fichiers de processeur déclarés et de la convention du contrôleur (nom, version, repère, unités). Il compare deux manifestes sans dépendre de leurs chemins locaux :

```sh
.venv/bin/robot-policy-fingerprint inspect fixtures/policy-a.json --locale=fr
.venv/bin/robot-policy-fingerprint compare fixtures/policy-a.json fixtures/policy-b.json --locale=fr
```

Le manifeste synthétique fournit `files.weights`, `files.normalization` et `controller`. Ajouter tout fichier de prétraitement ou post-traitement utilisé à `files`. Exporter les statistiques **résolues au moment de l’exécution** et les versions exactes du contrôleur ; cet outil ne peut pas prouver que le processus robotique a réellement chargé ces fichiers. La comparaison renvoie 0 si les empreintes concordent, 1 si elles diffèrent et 2 si une entrée est invalide.

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

### Executable policy fingerprint

`robot-policy-fingerprint` hashes the weight and normalization files **actually selected**, any other declared processor files, and the controller convention (name, version, frame, units). It compares two manifests independent of their local paths:

```sh
.venv/bin/robot-policy-fingerprint inspect fixtures/policy-a.json --locale=en
.venv/bin/robot-policy-fingerprint compare fixtures/policy-a.json fixtures/policy-b.json --locale=en
```

The synthetic manifest supplies `files.weights`, `files.normalization` and `controller`. Add every preprocessing or postprocessing file used to `files`. Export the statistics **resolved at runtime** and exact controller versions; this tool cannot prove the robot process actually loaded those files. Comparison returns 0 for matching fingerprints, 1 for differences and 2 for invalid input.

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

### Huella de la política ejecutable

`robot-policy-fingerprint` calcula una huella de los archivos de pesos y normalización **realmente seleccionados**, otros archivos de procesador declarados y la convención del controlador (nombre, versión, marco, unidades). Compara dos manifiestos con independencia de sus rutas locales:

```sh
.venv/bin/robot-policy-fingerprint inspect fixtures/policy-a.json --locale=es
.venv/bin/robot-policy-fingerprint compare fixtures/policy-a.json fixtures/policy-b.json --locale=es
```

El manifiesto sintético incluye `files.weights`, `files.normalization` y `controller`. Añade a `files` todos los archivos de preprocesamiento o posprocesamiento utilizados. Exporta las estadísticas **resueltas en ejecución** y las versiones exactas del controlador; esta herramienta no puede demostrar que el proceso robótico haya cargado esos archivos. La comparación devuelve 0 si las huellas coinciden, 1 si difieren y 2 ante una entrada no válida.

MIT — [LICENSE](LICENSE).
