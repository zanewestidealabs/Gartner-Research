import subprocess, time, urllib.request, json
# Kill existing process
subprocess.run(['pkill', '-f', 'python3 /home/vm-ssh/gartner/app.py'])
time.sleep(2)
# Start fresh
subprocess.Popen(
    ['nohup', 'python3', '/home/vm-ssh/gartner/app.py'],
    cwd='/home/vm-ssh/gartner',
    stdout=open('/home/vm-ssh/gartner/app.log', 'a'),
    stderr=subprocess.STDOUT,
    preexec_fn=__import__('os').setsid,
)
time.sleep(7)
# Verify
try:
    r1 = json.loads(urllib.request.urlopen('http://127.0.0.1:5000/api/apef-report', timeout=5).read())
    r2 = json.loads(urllib.request.urlopen('http://127.0.0.1:5000/api/apef-graph', timeout=5).read())
    print(f"OK vendors={len(r1['vendors'])} nodes={len(r2['nodes'])} edges={len(r2['edges'])}")
except Exception as e:
    print(f"VERIFY_FAIL {e}")
