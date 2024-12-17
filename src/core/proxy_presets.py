PROXY_PRESETS = {
    'burp': {
        'name': 'Burp Suite',
        'type': 'http',
        'host': '127.0.0.1',
        'port': 8080,
        'auth': {
            'enabled': False
        }
    },
    'zap': {
        'name': 'OWASP ZAP',
        'type': 'http',
        'host': '127.0.0.1',
        'port': 8090,
        'auth': {
            'enabled': False
        }
    },
    'tor': {
        'name': 'Tor Network',
        'type': 'socks5',
        'host': '127.0.0.1',
        'port': 9050,
        'auth': {
            'enabled': False
        }
    }
} 