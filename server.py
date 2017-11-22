import time
import grpc
import Datastore_pb2
import Datastore_pb2_grpc
import queue
import rocksdb

from concurrent import futures

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class MyDatastoreServicer(Datastore_pb2.DatastoreServicer):
    def __init__(self):
        self.db = rocksdb.DB("server.db", rocksdb.Options(create_if_missing=True))
        self.connection_queue = queue.Queue()      
    
    def replicate_follower(func):
        def wrapper(self, request, context):
            operation = Datastore_pb2.ConnectionResponse(
                    operation=request.operation, 
                    key=request.key.encode(), 
                    value=request.value.encode()
                 ) 
            self.connection_queue.put(operation)
            return func(self, request, context)
        return wrapper
            

    @replicate_follower
    def operation(self, request, context):
        if request.operation == 'put':
            print("Put key = {} & value = {} to server.db".format(request.key,request.value))
            self.db.put(request.key.encode(), request.value.encode())
            return Datastore_pb2.Response(data='Put operation done with key = {} & value = {}'.format(request.key,request.value))
        elif request.operation == 'delete':
            print("Delete key = {} from server.db".format(request.key))
            self.db.delete(request.key.encode())
            return Datastore_pb2.Response(data='Delete operation done with key = {}'.format(request.key))
        elif request.operation == 'get':
            print("Get key = {} value from server.db".format(request.key))
            v=self.db.get(request.key.encode())
            return Datastore_pb2.Response(data='Get operation done with key = {} and value = {}'.format(request.key,v))
        else:
            print("Trying Incorrect Operation")
            return Datastore_pb2.Response(data='Trying Incorrect Operation')

            
    def getConnection(self, request, context):
        print('Follower Connected to Server')
        while True:            
            value_queue = self.connection_queue.get()
            print('Got a request to perform {} operation'.format(value_queue.operation))
            yield value_queue

def run(host, port):    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    Datastore_pb2_grpc.add_DatastoreServicer_to_server(MyDatastoreServicer(), server)
    server.add_insecure_port('%s:%d' % (host, port))
    server.start()

    try:
        while True:
            print("Server started at...%d" % port)
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    run('0.0.0.0', 3000)

