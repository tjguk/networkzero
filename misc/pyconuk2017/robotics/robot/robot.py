#!python3
import os, sys
import queue
import shlex
import threading
import time

import zmq

from . import config
from . import logging
log = logging.logger(__package__)
from . import outputs

class RobotError(BaseException): pass

class NoSuchActionError(RobotError): pass

class Robot(object):
    
    def __init__(
        self,
        output,
        stop_event=None,
        listen_on_ip=config.LISTEN_ON_IP, listen_on_port=config.LISTEN_ON_PORT
    ):
        log.info("Setting up Robot on %s:%s", listen_on_ip, listen_on_port)
        log.info("Outputting to %s", output)
        self.stop_event = stop_event or threading.Event()
        self._init_socket(listen_on_ip, listen_on_port)
        self.output = output
        self.output._init()
    
    def _init_socket(self, listen_on_ip, listen_on_port):
        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://%s:%s" % (listen_on_ip, listen_on_port))
    
    def get_command(self):
        """Attempt to return a unicode object from the command socket
        
        If no message is available without blocking (as opposed to a blank 
        message), return None
        """
        try:
            message_bytes = self.socket.recv(zmq.NOBLOCK)
            log.debug("Received message: %r", message_bytes)
        except zmq.ZMQError as exc:
            if exc.errno == zmq.EAGAIN:
                return None
            else:
                raise
        else:
            return message_bytes.decode(config.CODEC)
    
    def send_response(self, response):
        """Send a unicode object as reply to the most recently-issued command
        """
        response_bytes = response.encode(config.CODEC)
        log.debug("About to send reponse: %r", response_bytes)
        self.socket.send(response_bytes)

    def parse_command(self, command):
        """Break a multi word command up into an action and its parameters
        """
        words = shlex.split(command.lower())
        return words[0], words[1:]
    
    def dispatch(self, command):
        """Pass a command along with its params to a suitable handler
        
        If the command is blank, succeed silently
        If the command has no handler, succeed silently
        If the handler raises an exception, fail with the exception message
        """
        log.info("Dispatch on %s", command)
        if not command:
            return "OK"
        
        action, params = self.parse_command(command)
        log.debug("Action = %s, Params = %s", action, params)
        try:
            function = getattr(self, "do_" + action, None)
            if function:
                function(*params)
            return "OK"
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            log.exception("Problem executing action %s", action)
            return "ERROR: %s" % exc
    
    def do_output(self, *args):
        """Pass a command directly to the current output processor
        """
        if args:
            action, params = args[0], args[1:]
            log.debug("Pass %s directly to output with %s", action, params)
            function = getattr(self.output, "do_" + action, None)
            if function:
                function(*params)
    
    def do_finish(self):
        self.stop_event.set()
    
    #
    # Main loop
    #
    def start(self):
        while not self.stop_event.is_set():
            try:
                command = self.get_command()
                if command is not None:
                    response = self.dispatch(command.strip())
                    self.send_response(response)
            except KeyboardInterrupt:
                log.warn("Closing gracefully...")
                self.stop_event.set()
                break
            except:
                log.exception("Problem in main loop")
                self.stop_event.set()
                raise

def main(args):
    output = args.output
    if not hasattr(outputs, args.output):
        raise RuntimeError("Invalid output: %s" % args.output)
    else:
        output = getattr(outputs, args.output)
    robot = Robot(output=output)
    robot.start()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="text")
    args = parser.parse_args()
    sys.exit(main(args))
