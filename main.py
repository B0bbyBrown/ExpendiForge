import socket

from app import create_app

app = create_app()

def find_free_port(start_port=5000, max_port=5100):
    for port in range(start_port, max_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free ports found between {} and {}".format(start_port, max_port))

if __name__ == '__main__':
    port = find_free_port()
    print(f"Starting server on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
