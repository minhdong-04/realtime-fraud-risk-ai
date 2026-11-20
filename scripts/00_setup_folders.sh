#!/bin/bash
# {
#   script : 00_setup_folders.sh
#   desc   : Tao dung cau truc thu muc data/ va di chuyen files theo 05_DATA_ARCHITECTURE.md
#   run    : bash scripts/00_setup_folders.sh
# }
set -e

echo "Khoi tao cau truc thu muc data/..."
mkdir -p data/raw/{ieee_cis,ubl_creditcard,paysim}
mkdir -p data/processed/{ieee_cis,ubl_creditcard,paysim}
mkdir -p data/features/{ieee_cis,ubl_creditcard,paysim}
mkdir -p data/{splits,labels}

echo "Tao data/.gitignore..."
cat > data/.gitignore << 'EOF'
# Large data files
*.csv
*.parquet
*.pkl
*.joblib
*.h5

# Giu lai structure va configs
!.gitignore
!.gitkeep
!splits/*.json
!raw/*/README.md
!features/*/feature_names.json
EOF

echo "Setup hoan tat!"
