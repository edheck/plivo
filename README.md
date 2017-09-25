# plivo
Have tested the code with a local redis and postgres setup.
all the endpoints work as expected.
Tried creating an AWS account but it asked for a credit card, so ditched.
For deployment either provide your aws account credentials so that 
this could be deployed there OR follow the following steps for local deployment

# install and start redis server
1) wget http://download.redis.io/redis-stable.tar.gz
2) tar xvzf redis-stable.tar.gz
3) cd redis-stable
4) make
5) ./redis-server

# install and start postgres server, assuming mac, on another terminal, after downloading your data_dump
1) brew install postgresql
2) initdb -D /usr/local/var/postgres
3) pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start
4) psql -U postgres -d postgres < data_dump

# start the app server
1) git clone https://github.com/edheck/plivo.git
2) cd plivo
3) virtualenv .
4) source bin/activate
5) pip install -r requirements.txt
6) python app.py

By now, the app should be up and running.
You should now be able to test all the endpoints. Thanks!


