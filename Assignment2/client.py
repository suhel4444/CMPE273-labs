import grpc
import replicator_pb2
import rocksdb

PORT = 3000

class Slave():
    def __init__(self, host='0.0.0.0', port=PORT):
        self.db = rocksdb.DB("slave.db", rocksdb.Options(create_if_missing=True))
        self.channel = grpc.insecure_channel('%s:%d' % (host, port))
        self.stub = replicator_pb2.ReplicatorStub(self.channel)

    def synchronize(self):
        obj = self.stub.sync(replicator_pb2.SyncRequest())
        print("Connected to server at 3000")
        for op in obj:
            if op.op == 'put':
                print("Putting {}:{} to slave db".format(op.key, op.data))
                self.db.put(op.key.encode(), op.data.encode())
            elif op.op == 'delete':
                print("Deleting {} from slave db".format(op.key))
                self.db.delete(op.key.encode())
            else:
                pass

def main():
    slave = Slave()
    resp = slave.synchronize()

if __name__ == "__main__":
    main()

