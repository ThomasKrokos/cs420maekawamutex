import Pyro5.api
import time
import Pyro5.server
# RUN THIS FILE AFTER nameserver.py

@Pyro5.server.expose
@Pyro5.server.behavior(instance_mode="single")
class Process(object):
    def __init__(self, pid, num_process, maekawa_manager):
        print(f"created process{pid}")
        self.pid = pid  # Process ID
        self.request_queue = []  # Queue of requests in waiting to be voted on
        self.votes_received = []  # List of processes that have voted
        self.process_num = num_process
        self.has_critical_section = False  # Indicator of critical section access
        self.maekawa_manager = maekawa_manager  # Shared MaekawaManager instance

    def set_maekawa_manager(self, maekawa_manager):
        self._maekawa_manager = maekawa_manager
        
    def request_critical_section(self):
        self.maekawa_manager.request(self.pid)

    def release_critical_section(self):
        if self.has_critical_section:
            print(f"process{self.pid} releasing from the critical section\n")
            self.maekawa_manager.release(self.pid)
            self.has_critical_section = False
            self.votes_received = []
            # self.receive_release(self.pid)
        else:
            print(f"process{self.pid} does not have access to the critical section, unable to give it up\n")

    def receive_request(self, request_pid):
        if not self.request_queue:
            print(f"process{self.pid} has received request from process{request_pid} and is immediately voting for it\n")
            self.request_queue.append((request_pid))
            self.maekawa_manager.vote(self.pid, request_pid)
        else:
            print(f"process{self.pid} has received request from process{request_pid} and is waiting since it has already cast its vote\n")
            self.request_queue.append((request_pid))

    def receive_release(self, released_pid):
        if self.request_queue and self.request_queue[0] == released_pid:
            self.request_queue.pop(0)  # Remove the top request from the queue
            if self.request_queue:
                next_request = self.request_queue[0]
                print(f"after receiving process{released_pid}'s release broadcast, process{self.pid} is now voting for process{next_request}'s request\n")
                self.maekawa_manager.vote(self.pid, next_request)

    def receive_vote(self, vote_pid):
        self.votes_received.append(vote_pid)
        print(f"process{self.pid} received a vote from process{vote_pid} for their critical access request.\n")
        if len(self.votes_received) >= 3:
            # Received enough votes, process can now enter the critical section
            self.access_critical_section()

    def access_critical_section(self):
        self.has_critical_section = True
        votes_list = ', '.join([f'Process{pid}' for pid in self.votes_received])
        print(f"{votes_list} have all voted for process{self.pid}'s request.\n")
        print(f"process{self.pid} has received it's 3 votes and is now entering the critical section.\n")
        # time.sleep(1)  # Simulate doing something in the critical section
        # print(f"Process{self.pid} finished its work in the critical section")
        # self.release_critical_section() <-- optional code for auto release instead of manual release

    def get_pid(self):
        return self.pid
    def has_critical_access(self):
        return self.has_critical_access

@Pyro5.server.expose
@Pyro5.server.behavior(instance_mode="single")
class MaekawaManager(object): 
    def __init__(self, process_num):
        self.process_num = process_num
        self.voting_sets ={
        '0': {'0', '1', '2'},
        '1': {'0', '1', '3'},
        '2': {'0', '2', '4'},
        '3': {'1', '3', '4'},
        '4': {'2', '3', '4'}
        }

    def request(self, pid):
        print(f"Broadcasting process{pid}'s request for the critical section to its constituents.\n")
        # Broadcast request to all processes via Pyro name server lookup
        key = f'{pid}'
        for i in self.voting_sets[key]:
            process_uri = f"PYRONAME:process.{i}"
            process = Pyro5.api.Proxy(process_uri)
            process.receive_request(pid)         
               
    def release(self, pid):
        
        print(f"Process{pid} asks MaekawaManager to broadcast release.\n")
        # Broadcast release to all processes
        key = f'{pid}'
        for i in self.voting_sets[key]:
            process_uri = f"PYRONAME:process.{i}"
            process = Pyro5.api.Proxy(process_uri)
            process.receive_release(pid)

    def vote(self, from_pid, to_pid):
        print(f"process{from_pid} is voting for process{to_pid} to get critical access.\n")
        process_uri = f"PYRONAME:process.{to_pid}"
        process = Pyro5.api.Proxy(process_uri)
        process.receive_vote(from_pid)

















@Pyro5.server.expose
class Process0(Process):
    def __init__(self, MaekawaManager):
        super().__init__(0,5, MaekawaManager)

@Pyro5.server.expose
class Process1(Process):
    def __init__(self, MaekawaManager):
        super().__init__(1,5, MaekawaManager)

@Pyro5.server.expose
class Process2(Process):
    def __init__(self, MaekawaManager):
        super().__init__(2,5, MaekawaManager)

@Pyro5.server.expose
class Process3(Process):
    def __init__(self, MaekawaManager):
        super().__init__(3,5, MaekawaManager)

@Pyro5.server.expose
class Process4(Process):
    def __init__(self, MaekawaManager):
        super().__init__(4,5, MaekawaManager)


if __name__ == "__main__":
    
    
    
    
    print("please run nameserver.py first")
    maekawa_manager = MaekawaManager(3)

    print("Registering processes and maekawa manager with pyro...")
    daemon = Pyro5.server.Daemon()         
    ns = Pyro5.api.locate_ns()             
    uri = daemon.register(MaekawaManager)   # register the process as a Pyro object
    ns.register(f"maekawamanager", uri) 
    print(f"registered maekawamanager")
    
    urip0 = daemon.register(Process0(maekawa_manager))   # register the process as a Pyro object
    ns.register(f"process.0", urip0) 
    print(f"registered process0")

    urip1 = daemon.register(Process1(maekawa_manager))   # register the process as a Pyro object
    ns.register(f"process.1", urip1) 
    print(f"registered process1")
    
    urip2 = daemon.register(Process2(maekawa_manager))   # register the process as a Pyro object
    ns.register(f"process.2", urip2) 
    print(f"registered process2")
        
    urip3 = daemon.register(Process3(maekawa_manager))   # register the process as a Pyro object
    ns.register(f"process.3", urip3) 
    print(f"registered process3")
        
    urip4 = daemon.register(Process4(maekawa_manager))   # register the process as a Pyro object
    ns.register(f"process.4", urip4) 
    print(f"registered process4")
    
    
    
    print("Server is ready.")
    daemon.requestLoop()
    
    