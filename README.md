# ascensionAuctionator

Outil pour convertir et analyser les données d'enchères de World of Warcraft Classic depuis l'addon AHScanner, et générer des visualisations dans Obsidian.

## Utilisation

### Workflow complet

Pour générer les fichiers Obsidian à partir des données brutes :

```bash
./scripts/run.sh src/main.py convert
./scripts/run.sh src/main.py update-item-db
./scripts/run.sh src/main.py obsidian
./scripts/run.sh src/main.py obsidian-auctions
```

### convert

Convertit les fichiers Lua en YAML.

```bash
./scripts/run.sh src/main.py convert [DAILIES]
```

Scanne tous les sous-répertoires de `dailies` (ou du répertoire spécifié) et convertit les fichiers Lua supportés trouvés :
- `AHScanner.lua`

Les fichiers YAML générés sont placés dans `gen_dailies/<nom_du_sous_répertoire>/`.

Argument :
- `DAILIES` : Répertoire contenant les sous-répertoires avec les fichiers Lua (défaut: `dailies`)

### update-item-db

Met à jour les bases de données (items, prix et enchères).

```bash
./scripts/run.sh src/main.py update-item-db [--item-database-file DATAS/ITEMS.YAML] [--price-database-file DATAS/QNP.YAML] [--auction-database-file DATAS/AUCTIONS.YAML] [--dailies-directory GEN_DAILIES]
```

Extrait les données depuis les fichiers `AHScanner.yaml` :
- Les prix et quantités sont ajoutés à la base de données des prix (`qnp.yaml`)
- Les données d'enchères détaillées sont ajoutées à la base de données des enchères (`auctions.yaml`)

Options :
- `--item-database-file` : Chemin vers le fichier de base de données des items (défaut: `datas/items.yaml`)
- `--price-database-file` : Chemin vers le fichier de base de données des prix et quantités (défaut: `datas/qnp.yaml`)
- `--auction-database-file` : Chemin vers le fichier de base de données des enchères (défaut: `datas/auctions.yaml`)
- `--dailies-directory` : Répertoire contenant les fichiers YAML générés (défaut: `gen_dailies`)

### obsidian

Génère les fichiers markdown Obsidian à partir des bases de données.

```bash
./scripts/run.sh src/main.py obsidian [--item-database-file DATAS/ITEMS.YAML] [--price-database-file DATAS/QNP.YAML] [--output-dir OBSIDIAN]
```

Génère les fichiers markdown pour chaque item avec des graphiques de prix et quantités.

Options :
- `--item-database-file` : Chemin vers le fichier de base de données des items (défaut: `datas/items.yaml`)
- `--price-database-file` : Chemin vers le fichier de base de données des prix et quantités (défaut: `datas/qnp.yaml`)
- `--output-dir` : Répertoire de sortie pour les fichiers Obsidian (défaut: `obsidian`)

### obsidian-auctions

Génère les fichiers markdown Obsidian pour les enchères détaillées.

```bash
./scripts/run.sh src/main.py obsidian-auctions [--item-database-file DATAS/ITEMS.YAML] [--auction-database-file DATAS/AUCTIONS.YAML] [--output-dir OBSIDIAN/AUCTIONS]
```

Génère les fichiers markdown pour les enchères avec des graphiques de distribution des prix et des statistiques détaillées.

Options :
- `--item-database-file` : Chemin vers le fichier de base de données des items (défaut: `datas/items.yaml`)
- `--auction-database-file` : Chemin vers le fichier de base de données des enchères (défaut: `datas/auctions.yaml`)
- `--output-dir` : Répertoire de sortie pour les fichiers Obsidian (défaut: `obsidian/auctions`)

## Format des fichiers Lua

Les fichiers Lua sauvegardés par le script `dailyAuctionator.sh` sont des fichiers de variables sauvegardées (SavedVariables) de l'addon AHScanner pour World of Warcraft Classic.

### AHScanner.lua

Base de données des enchères scannées, organisée par royaume et nom d'item :

```lua
AHScannerDB = {
    ["Nom du Royaume"] = {
        ["Nom de l'Item"] = {
            ["items"] = {
                {
                    ["buyoutUnit"] = prix_unitaire,
                    ["seller"] = "Nom du vendeur",
                    ["count"] = quantité,
                    ["buyout"] = prix_total,
                    ["minBid"] = enchère_minimale,
                    ...
                },
                ...
            }
        },
        ...
    },
}
```

Les prix sont stockés en cuivre (unité de base de la monnaie WoW).

