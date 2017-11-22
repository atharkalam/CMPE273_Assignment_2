import grpc
import Datastore_pb2
import argparse
import rocksdb

PORT = 3000

class Follower():
    def __init__(self, host='0.0.0.0', port=PORT):
        self.db = rocksdb.DB("follower.db", rocksdb.Options(create_if_missing=True))
        self.channel = grpc.insecure_channel('%s:%d' % (host, port))
        self.stub = Datastore_pb2.DatastoreStub(self.channel)

    def dbPush(self):
        queue_request = self.stub.getConnection(Datastore_pb2.ConnectionRequest())
        for req in queue_request:
            if req.operation == 'put':
                print("Put key = {} & value = {} to follower.db".format(req.key,req.value))
                self.db.put(req.key.encode(), req.value.encode())
            elif req.operation == 'delete':
                print("Delete key = {} from follower.db".format(req.key,req.value))
                self.db.delete(req.key.encode())
            elif req.operation == 'get':
                v=self.db.get(req.key.encode())
                print("For key = {} got value = {} from follower.db".format(req.key,v))                
            else:
                print("Trying Incorrect Operation")
                pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="follower")
    args = parser.parse_args()    
    follower = Follower(host=args.host)
    resp = follower.dbPush()

if __name__ == "__main__":
    main()

