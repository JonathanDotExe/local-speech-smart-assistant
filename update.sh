git pull

source venv/bin/activate
pip install --upgrade -r requirements.txt
pip install --upgrade git+https://github.com/Cupcakus/pafy

cd master
./install_plugins.sh
cd ..

cd www-util
npm i

cd ../slave/www
npm i

cd ../../master/www
npm i
