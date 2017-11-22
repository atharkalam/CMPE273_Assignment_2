# First create a docker image of rocksdb with the following command

docker build -t ubuntu-python3.6-rocksdb-grpc .

# Second generate the stubs for server and follower with the following commands

docker run -it --rm --name grpc-tools -v "$PWD":/usr/src/myapp -w /usr/src/myapp ubuntu-python3.6-rocksdb-grpc:latest python3.6 -m grpc.tools.protoc -I. --python_out=. --grpc_python_out=. Datastore.proto


# Third step create a bridge network with following command

docker network create -d bridge --subnet 192.168.0.0/24 --gateway 192.168.0.1 dockernet

# Then create a server container

docker run -p 3000:3000 -it --rm --name server -v "$PWD":/usr/src/myapp -w /usr/src/myapp ubuntu-python3.6-rocksdb-grpc:latest python3.6 server.py

# Then create a follower container. The connection between follower and server is always kept alive so that when any request is pased from the test script, the request is passed  to both server and follower

docker run -it --rm --name follower -v "$PWD":/usr/src/myapp -w /usr/src/myapp ubuntu-python3.6-rocksdb-grpc:latest python3.6 follower.py 192.168.0.1

# Then run the following command to run the test_script container

docker run -it --rm --name test-script-container -v "$PWD":/usr/src/myapp -w /usr/src/myapp ubuntu-python3.6-rocksdb-grpc:latest python3.6 test_script.py 192.168.0.1





