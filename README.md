# protostar-coverage-poc

Demo on how to get coverage data for cairo codebases

## dependencies

- protostar 0.3.2
- python 3.7.12 environment with cairo-lang 0.9.1

## Installation after cloning repo

```
protostar install
```

## Utilisation

```
python cairo_instrument.py src/storage_contract.cairo && protostar test ./tests --disable-hint-validation
```

<img width="607" alt="Screenshot 2022-08-23 at 14 04 08" src="https://user-images.githubusercontent.com/5071029/186231822-067c8a48-7539-4291-9c06-45c7fabccf1e.png">
