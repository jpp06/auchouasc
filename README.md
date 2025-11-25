# ascensionAuctionator

## Utilisation

### Workflow complet

Pour générer les fichiers Obsidian à partir des données brutes :

```bash
./scripts/run.sh src/main.py convert
./scripts/run.sh src/main.py update-item-db
./scripts/run.sh src/main.py obsidian
```

### convert

Convertit les fichiers Lua en YAML.

```bash
./scripts/run.sh src/main.py convert [DAILIES]
```

Scanne tous les sous-répertoires de `dailies` (ou du répertoire spécifié) et convertit tous les fichiers Lua supportés trouvés :
- `Auctionator_Price_Database.lua`
- `TradeSkillMaster_Accounting.lua`
- `TradeSkillMaster_AuctionDB.lua`
- `TradeSkillMaster_Shopping.lua`

Les fichiers YAML générés sont placés dans `gen_dailies/<nom_du_sous_répertoire>/`.

Argument :
- `DAILIES` : Répertoire contenant les sous-répertoires avec les fichiers Lua (défaut: `dailies`)

### update-item-db

Met à jour les bases de données (items et prix).

```bash
./scripts/run.sh src/main.py update-item-db [--item-database-file DATAS/ITEMS.YAML] [--price-database-file DATAS/QNP.YAML] [--dailies-directory GEN_DAILIES]
```

Extrait les items depuis les fichiers `TradeSkillMaster_Accounting.yaml` et `TradeSkillMaster_Shopping.yaml`, puis les prix et quantités depuis `Auctionator_Price_Database.yaml` et `TradeSkillMaster_AuctionDB.yaml`.

Options :
- `--item-database-file` : Chemin vers le fichier de base de données des items (défaut: `datas/items.yaml`)
- `--price-database-file` : Chemin vers le fichier de base de données des prix et quantités (défaut: `datas/qnp.yaml`)
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

## Format des fichiers Lua

Les fichiers Lua sauvegardés par le script `dailyAuctionator.sh` sont des fichiers de variables sauvegardées (SavedVariables) des addons Auctionator et TradeSkillMaster pour World of Warcraft.

### Auctionator_Price_Database.lua

Base de données des prix moyens par item, organisée par serveur :

```lua
AUCTIONATOR_PRICE_DATABASE = {
    ["__dbversion"] = 2,
    ["Nom du Serveur"] = {
        ["Nom de l'Item"] = prix_en_cuivre,
        ...
    },
}
```

Les prix sont stockés en cuivre (unité de base de la monnaie WoW).

