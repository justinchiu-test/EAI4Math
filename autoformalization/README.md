# autoformalization

## install
Get `uv` (fast conda replacement)
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## run
1. fetch multilingual autoformalization dataset (MMA) with
```
bash scripts/get_mma.sh
```
2. prepare mma data into lean
```
uv run python -m autoformalization.prepare_mma
```
