# Minimalist Python HTTP Server

This project aims to create a simple HTTP server using Python. The server processes GET and POST requests from clients, writes or reads request data to a file, and offers an option to block scraping tools like curl.

## Features

- **GET and POST Support:** Handles GET and POST requests from clients.
- **File Operations:** Writes and reads request data to/from `sunucu_veri.txt`.
- **HTTP Responses:** Generates HTTP responses for valid or invalid request formats.
- **Curl Blocking:** Provides an option to block client-side scraping.

## Installation

Ensure Python 3.x is installed. To run the project, follow these steps:

```bash
git clone https://github.com/erendrcnn/minimal-http-server
cd sunucu
python sunucu.py
```

## Usage

The server runs on `localhost` at port 8080 by default.

### Start the Server

To start the server:

```bash
python sunucu.py
```

To prevent curl scraping:

```bash
python sunucu.py --prevent-scraping
```

### Send Requests

To send a GET request to the server:

```bash
curl http://localhost:8080
```

To send a POST request to the server:

```bash
curl -X POST -d "data=example" http://localhost:8080
```

## Contributing

We welcome contributions. Please submit a pull request or open an issue.

## License

This project is licensed under the MIT License.
