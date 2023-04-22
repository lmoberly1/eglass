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

    # functions = [stream.run_pi_video, app.run]
    functions = [stream.run_pi_video]
    processes = []
    print('Beginning Processing')

    parent_conn, child_conn = multiprocessing.Pipe()

    for worker in functions:
        p = multiprocessing.Process(target=worker, args=(child_conn,))
        processes.append(p)
        p.start()

    print('Processes are Started ', len(processes))
    data = parent_conn.recv()
    while (data):
        print('Received data', data)
        data = parent_conn.recv()

    # Wait for all processes to complete
    for p in processes:
        print('process')
        p.join()

    print('All workers finished')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        active = multiprocessing.active_children()
        for child in active:
            print('Killed process')
            child.terminate()