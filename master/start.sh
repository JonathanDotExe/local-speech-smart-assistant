source ../venv/bin/activate
cd www
npm start &
cd ..
python app Production #> master_log.txt 2<&1
killall python --signal=SIGINT -q
