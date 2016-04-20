import zmq

frontend_address = "tcp://127.0.0.1:50001"
backend_address = "tcp://127.0.0.1:50002"

c = zmq.Context()

router = c.socket(zmq.ROUTER)
router.bind(frontend_address)
dealer = c.socket(zmq.DEALER)
dealer.bind(backend_address)

req = c.socket(zmq.REQ)
rep = c.socket(zmq.REP)

rep.bind(address)
