# bigbrain-boss
Scripts used to download, tile, and ingest BigBrain into the Boss


### Step 1: Setup virtualenv

```
virtualenv boss -p python3.6
source boss/bin/activate
pip install boss-ingest intern
```

### Step 2: Get tiles

```
./get_slices.sh
```

### Step 3: Make tiles

```
python make_tiles bigbrain bigbrain_tiles
```

### Step 4: Create collection + experiment + channel
Use the console available at [api.boss.neurodata.io](https://api.boss.neurodata.io). You may need *resource manager*
permissions; ask your administrator if you don't have sufficient permissions.


### Step 5: Ingest

```
BOSS_API_TOKEN=your_token
boss-ingest --api-token ${BOSS_API_TOKEN} ./config.json
```
