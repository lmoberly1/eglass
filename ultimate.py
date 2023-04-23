import multiprocessing
from bluetooth.advertisement import Advertisement
from bluetooth.service import Application, Service, Characteristic, Descriptor
from bluetooth.namedata import NameService, NameAdvertisement
from Stream import Stream

def main():
    parent_conn, child_conn = multiprocessing.Pipe()
    
    try:
        stream = Stream()
        app = Application()
        name_service = NameService(0, parent_conn)
        app.add_service(name_service)
        app.register()
        adv = NameAdvertisement(0)
        adv.register()

        print('Beginning Processing')

        p1 = multiprocessing.Process(target=stream.run_pi_video, args=(child_conn, ))
        p2 = multiprocessing.Process(target=app.run, args=())

        # Start the child processes
        p2.start()
        p1.start()

        # Wait for all processes to complete
        p1.join()
        p2.join()

        print('All workers finished')
    except:
        child_conn.close()
        active = multiprocessing.active_children()
        for child in active:
            print('Killed process')
            child.terminate()

if __name__ == '__main__':
    main()
    