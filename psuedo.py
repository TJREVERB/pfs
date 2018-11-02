# uesr code

core.start_thread(listen)


# core
threads = []

def start_thread(target, name, args=(), kwargs={}, *a, **kw):
    t = threading.Thread(target=target, daemon=True, args=args, kwargs=kwargs, *a, **kw)
    t.start()
    thread.append({"thread": t, "name": name})


# manual restart
def restart_single_thread(name):
    threads[name].restart() # and/or just call the wrapper again

# run in thread
def restart_threads():
    while True: 
        # check for dead threads and restart
        for t in threads:
            if t.dead():
                restart(t)
        time.sleep(1)





t = threading.Thread(args=(a, b, c), kwargs={})


start_thread(func, args=(a, b, c), kwargs={})
