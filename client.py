from Pyro5.api import Proxy

# RUN THIS FILE AFTER server.py

if __name__ == "__main__":
    print("Pulling objects from pyro server \n")
    process0 = Proxy("PYRONAME:process.0")
    print(process0)
    process1 = Proxy("PYRONAME:process.1")
    print(process1)
    process2 = Proxy("PYRONAME:process.2")
    print(process2)
    process3 = Proxy("PYRONAME:process.3")
    print(process3)
    process4 = Proxy("PYRONAME:process.4")
    print(process4)
    maekawamanager = Proxy("PYRONAME:maekawamanager")
    print(maekawamanager)

    try:
        print("testing maekawa algorithm ...")
        process0.set_maekawa_manager(maekawamanager)
        process1.set_maekawa_manager(maekawamanager)
        process2.set_maekawa_manager(maekawamanager)
        process3.set_maekawa_manager(maekawamanager)
        process4.set_maekawa_manager(maekawamanager)
        process0.request_critical_section()
        process1.request_critical_section() 
        process2.request_critical_section() 
        process0.release_critical_section() # manually release critical section
        process3.request_critical_section()
        process4.request_critical_section()
        process0.request_critical_section()
        process0.release_critical_section() # manually release critical section
        process1.release_critical_section() # manually release critical section
        process2.release_critical_section() # manually release critical section
        process3.release_critical_section() # manually release critical section
        process4.release_critical_section() # manually release critical section
        process0.release_critical_section() # manually release critical section
        
        
        # release one more time to check that no process is in the critical section
        process0.release_critical_section() # manually release critical section
        process1.release_critical_section() # manually release critical section
        process2.release_critical_section() # manually release critical section
        process3.release_critical_section() # manually release critical section
        process4.release_critical_section() # manually release critical section
        print("ending tests of maekawa algorithm")
        
        
    except Exception as e:
        print(f"error: {e}")
    