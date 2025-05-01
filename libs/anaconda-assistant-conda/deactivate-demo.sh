export CONDA_CHANGEPS1=true

if alias conda &>/dev/null; then
  unalias conda
fi
echo "\nDEACTIVATED!\n\nIf you're using bash, run:\nsource ~/.bashrc\n\nIf using zsh, run:\nsource ~/.zshrc\n"