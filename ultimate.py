import multiprocessing
from bluetooth.advertisement import Advertisement
from bluetooth.service import Application, Service, Characteristic, Descriptor
from bluetooth.namedata import NameService, NameAdvertisement
from Stream import Stream

def main():
    stream = Stream()
    app = Application()
    name_service = NameService(0)
    app.add_service(name_service)
    app.register()
    adv = NameAdvertisement(0)
    adv.register()

    # data = parent_conn.recv()
    # while (data):
    #     print('Received data', data)
    #     data = parent_conn.recv()

    print('Beginning Processing')

    p1 = multiprocessing.Process(target=stream.run_pi_video, args=(name_service,))
    p2 = multiprocessing.Process(target=app.run, args=()) # NEED TO FIGURE OUT HOW TO GET THIS TO NAMEDATA.PY

    # Start the child processes
    p2.start()
    p1.start()

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