import multiprocessing
from bluetooth.advertisement import Advertisement
from bluetooth.service import Application, Service, Characteristic, Descriptor
from bluetooth.namedata import NameService, NameAdvertisement
from Stream import Stream

def main():
    stream = Stream()
    app = Application()
    app.add_service(NameService(0))
    app.register()
    adv = NameAdvertisement(0)
    adv.register()

    # data = parent_conn.recv()
    # while (data):
    #     print('Received data', data)
    #     data = parent_conn.recv()

    print('Beginning Processing')

    parent_conn, child_conn = multiprocessing.Pipe()
    p1 = multiprocessing.Process(target=stream.run_pi_video, args=(child_conn,))
    p2 = multiprocessing.Process(target=app.run, args=(parent_conn,))

    # Start the child processes
    p1.start()
    p2.start()

    # Wait for all processes to complete
    p1.join()
    p2.join()

    print('All workers finished')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        active = multiprocessing.active_children()
        for child in active:
            print('Killed process')
            child.terminate()