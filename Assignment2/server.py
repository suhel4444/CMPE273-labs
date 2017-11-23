import time
import grpc
import queue
import rocksdb
import replicator_pb2
import replicator_pb2_grpc
from concurrent import futures

A_DAY_IN_SECONDS = 60 * 60 * 24

class ReplicateMaster(replicator_pb2.NodeReplicator):
    def __init__(self):
        self.db = rocksdb.DB("master.db", rocksdb.Options(create_if_missing=True))
        self.oper_queue = queue.Queue()

    def pass_to_slave(function):
        def decorator(self, req, context):
            op = replicator_pb2.Sync(
                    op=func.__name__, 
                    key=req.key.encode(), 
                    data=req.data.encode()
                 ) 
            self.oper_queue.put(op)
            return function(self, req, context)
        return decorator


    @pass_to_slave
    def delete(self, req, context):
        print("Delete {} from master db".format(req.key))
        self.db.delete(req.key.encode())
        return replicator_pb2.Response(data='test')

    @pass_to_slave
    def put(self, req, context):
        print("Put {}:{} to master db".format(req.key, req.data))
        self.db.put(req.key.encode(), req.data.encode())
        return replicator_pb2.Response(data='test')

   
        
    def get(self, req, context):
        print("Get {} from master db".format(req.key))
        value = self.db.get(req.key.encode())
        return replicator_pb2.Response(data=value)


    def sync(self, req, context):
        print("Slave connected")
        while True:
            result = self.oper_queue.get()
            print("Sending result ({}, {}, {}) to slave".format(result.op, result.key, result.data))
            yield result

def run(host, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    replicator_pb2_grpc.add_ReplicatorServicer_to_server(ReplicateMaster(), server)
    server.add_insecure_port('%s:%d' % (host, port))
    server.start()
    try:
        while True:
            print("Server started at %d" % port)
            time.sleep(A_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    run('0.0.0.0', 3000)



