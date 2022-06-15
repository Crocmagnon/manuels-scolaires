# manuels-scolaires
Help librarian manage textbooks requests from colleagues

## Local development

```bash
pyenv virtualenv 3.10.4 manuels
pyenv local manuels
poetry install
cp envs/local.env.dist envs/local.env
echo 'export ENV_FILE=$(realpath "./envs/local.env")' > .envrc
direnv allow
inv test
```

# Reuse
If you do reuse my work, please consider linking back to this repository 🙂
