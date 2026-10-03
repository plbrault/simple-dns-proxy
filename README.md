# Simple DNS Proxy

A minimal DNS server that rewrites selected domains and forwards everything else to a real upstream resolver.

## Configuration

`config.json`:

```json
{
  "upstream": "1.1.1.1",
  "listen": "0.0.0.0",
  "port": 53,
  "rewrites": {
    "example.com": "192.168.1.10"
  }
}
```

- `upstream`: the real DNS server used for queries that have no rewrite.
- `listen` / `port`: address and UDP port the server binds to.
- `rewrites`: map of domain name to IP address. Exact matches only (case-insensitive).

## Docker

Build:

```sh
docker build -t simple-dns-proxy .
```

Run:

```sh
docker run -d --name dns -p 53:53/udp -v ./config.json:/app/config.json simple-dns-proxy
```

The config file is mounted as a volume, so edit it and restart the container to apply changes — no rebuild needed.

## Test

```sh
dig @127.0.0.1 example.com    # answered from rewrites
dig @127.0.0.1 google.com     # forwarded to upstream
```

## License

[MIT](./LICENSE)
