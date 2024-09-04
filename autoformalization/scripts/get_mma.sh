curl -LJ https://github.com/albertqjiang/MMA/raw/main/data/MMA%20dataset.zip -o data/MMA.zip

mkdir -p data
pushd data
unzip MMA.zip
mv "MMA dataset" MMA
# cleanup
rm -rf __MACOSX
rm -rf data/MMA/__MACOSX
popd
