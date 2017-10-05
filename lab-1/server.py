'''
################################## server.py #############################
# Lab1 gRPC RocksDB Server 
################################## server.py #############################
'''
import time
import grpc
import datastore_pb2
import datastore_pb2_grpc
import uuid
import rocksdb

from concurrent import futures

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class MyDatastoreServicer(datastore_pb2.DatastoreServicer):
    def __init__(self):
        self.db = rocksdb.DB("lab1.db", rocksdb.Options(create_if_missing=True))

    def put(self, request, context):
        print("put")
        #pyrocksdb does not take string literals so convertng them into byte strings(both key and value)
        key = uuid.uuid4().hex
        byte_key=key.encode()
        data=request.data
        byte_data=data.encode()
        self.db.put(byte_key,byte_data)
        # TODO - save key and value into DB converting request.data string to utf-8 bytes 
        
        return datastore_pb2.Response(data=key)

    def get(self, request, context):
        print("get")
        key=request.data
        byte_key=str.encode(key)
        byte_value=self.db.get(byte_key)
        # TODO - retrieve the value from DB by the given key. Needs to convert request.data string to utf-8 bytes. 
        value = byte_value.decode()

        return datastore_pb2.Response(data=value)

def run(host, port):
    '''
    Run the GRPC server
    '''
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    datastore_pb2_grpc.add_DatastoreServicer_to_server(MyDatastoreServicer(), server)
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