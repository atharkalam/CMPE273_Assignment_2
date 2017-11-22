import grpc
import Datastore_pb2
import argparse

PORT = 3000

class Test():
    def __init__(self, host='0.0.0.0', port=PORT):
        self.channel = grpc.insecure_channel('%s:%d' % (host, port))
        self.stub = Datastore_pb2.DatastoreStub(self.channel)

    def db_operation(self, operation, key, value):
        return self.stub.operation(Datastore_pb2.Request(operation=operation,key=key, value=value))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="test")
    args = parser.parse_args() 
    check = Test(host=args.host)
    print('Test 1')
    response = check.db_operation('put','1', 'One')
    print(response.data)
    print('Test 2')
    response = check.db_operation('put','2', 'Two')
    print(response.data)
    print('Test 3')
    response = check.db_operation('delete','2','Two')
    print(response.data)   

if __name__ == "__main__":
    main()


