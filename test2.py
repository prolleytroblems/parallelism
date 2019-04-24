from bounce import bouncer, app
import time


def func(arg):
    ip = list(arg.keys())[0]
    arg = arg[ip]
    assert arg==1 or arg==0
    if arg==1:
        print("ping")
    elif arg==0:
        print('pong')

    time.sleep(3)

    return {ip: arg^1}

bouncer.inport=6000
bouncer.outport=5000
bouncer.callback=func

print(app)

bouncer.wait()
