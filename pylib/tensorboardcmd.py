import socket
from IPython.display import HTML

def tensorboard_cmd(logs):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    
    return HTML("""<p>Run at the command line:
    <tt>tensorboard --logdir={log}</tt><br />
    Then open <a href="http://{ip}:6006/" target="_blank">http://{ip}:6006/</a></p>""".format(log=logs, ip=ip))
